# -*- coding: utf-8 -*-
"""Experiment 06 — do the three retrievers fuse, and can alignment be gated safely?

Three ways of finding a passage, each good at something different:

  shingle    near-verbatim wording          finds citations the paragraph makes
  topical    subject matter (BM25)          finds discussions of the same thing
  alignment  the corresponding place        finds parallel passages sharing no words

Two questions. (1) Does the alignment's error predict itself — is local anchor
support a usable confidence signal, so a bad alignment can be withheld rather
than shipped as a confident wrong answer? (2) Under a fixed budget of passages
(the real constraint: context window), what does fusing them recover?
"""
import collections
import json
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
sys.path.insert(0, HERE)
import align as A                                            # noqa: E402
import shingle as S                                          # noqa: E402
import topical as X                                          # noqa: E402
import gold as G                                             # noqa: E402

VIEWER = '/Users/tegchok/སྐབས་དང་པོ།-viewer'
YIGCHA = 'རྗེ་བཙུན་ཆོས་ཀྱི་རྒྱལ་མཚན་_སྐབས་དང་པོའི་སྤྱི་དོན།.txt'
HALF = 1200            # half-width of a passage shown to the analyst
RRF_K = 20


def load_alignments(yig, files):
    cache = 'experiments/cache/aligns.pkl'
    if os.path.exists(cache):
        return pickle.load(open(cache, 'rb'))
    out = {}
    for fn in files:
        if fn == YIGCHA:
            continue
        text = open(os.path.join('Commentaries', fn), encoding='utf-8').read()
        al = A.build(yig, text)
        out[fn] = (al.xs, al.ys)
    pickle.dump(out, open(cache, 'wb'), protocol=4)
    return out


def main():
    yig = open(os.path.join('Commentaries', YIGCHA), encoding='utf-8').read()
    prev = json.load(open('experiments/exp05_alignment.json', encoding='utf-8'))
    para_at = prev['paragraph_offsets']

    sh = pickle.load(open('experiments/cache/index.pkl', 'rb'))
    tp = pickle.load(open('experiments/cache/topical.pkl', 'rb'))
    files = sh['files']
    idfs = S.idf(sh['postings'], sum(len(v) for v in sh['postings'].values()))
    avg = sum(w[3] for w in tp['windows']) / len(tp['windows'])

    truth = G.load()
    aligns_raw = load_alignments(yig, sorted(set(files)))
    aligns = {}
    for fn, (xs, ys) in aligns_raw.items():
        al = A.Alignment([])
        al.xs, al.ys = xs, ys
        aligns[fn] = al

    # ---- Q1: does local anchor support predict alignment error? -------------
    print('Q1 · alignment error vs local anchor support (all splits)\n')
    buckets = collections.defaultdict(list)
    for q in truth:
        al, x = aligns.get(q['file']), para_at.get(q['paragraph'])
        if al is None or x is None or not len(al):
            continue
        sup = al.support(x, 8000)
        err = abs(al.at(x) - q['offset'])
        band = 0 if sup == 0 else 1 if sup < 5 else 2 if sup < 20 else 3
        buckets[band].append(err)
    labels = {0: 'no anchors within ±8k', 1: '1-4 anchors', 2: '5-19 anchors',
              3: '20+ anchors'}
    print(f'{"local support":<26}{"n":>5}{"median err":>13}{"within ±5k":>12}')
    for b in sorted(buckets):
        v = sorted(buckets[b])
        near = sum(1 for e in v if e <= 5000)
        print(f'{labels[b]:<26}{len(v):>5}{v[len(v)//2]:>13,}'
              f'{100*near/len(v):>11.0f}%')

    # ---- Q2: fusion under a passage budget ---------------------------------
    def candidates(pid, use):
        """Ranked passages from the requested methods, fused by reciprocal rank."""
        ranked = collections.defaultdict(float)
        origin = {}
        if 'shingle' in use:
            for r, p in enumerate(S.retrieve(sh['per'][pid], files, sh['postings'],
                                             idfs, top=60), start=1):
                key = (p['file'], p['offset'] // HALF)
                ranked[key] += 1.0 / (RRF_K + r)
                origin.setdefault(key, ('shingle', p['offset']))
        if 'topical' in use:
            for r, p in enumerate(X.score(tp['qt'][pid], tp['windows'],
                                          tp['postings'], avg, top=60), start=1):
                key = (files[p['file_id']], p['offset'] // HALF)
                ranked[key] += 1.0 / (RRF_K + r)
                origin.setdefault(key, ('topical', p['offset']))
        if 'align' in use:
            x = para_at.get(pid)
            scored = []
            for fn, al in aligns.items():
                if x is None or not len(al):
                    continue
                sup = al.support(x, 8000)
                if sup < 5:                     # gate: withhold unsupported guesses
                    continue
                scored.append((sup, fn, al.at(x)))
            scored.sort(reverse=True)
            for r, (_, fn, off) in enumerate(scored, start=1):
                key = (fn, off // HALF)
                ranked[key] += 1.0 / (RRF_K + r)
                origin.setdefault(key, ('align', off))
        out = sorted(ranked.items(), key=lambda kv: -kv[1])
        return [(k[0], origin[k][1], origin[k][0]) for k, _ in out]

    print('\n\nQ2 · recall at a fixed passage budget '
          f'(a passage is ±{HALF} chars)\n')
    combos = [('shingle',), ('topical',), ('align',),
              ('shingle', 'topical'), ('shingle', 'align'),
              ('topical', 'align'), ('shingle', 'topical', 'align')]
    budgets = (10, 20, 30, 50)
    for split_name, split in (('tune', G.TUNE), ('held out', G.HELD_OUT)):
        sub = [q for q in truth if q['paragraph'] in split]
        print(f'  {split_name} split ({len(sub)} quotes)')
        print(f'    {"methods":<28}' +
              ''.join(f'{"@" + str(b):>8}' for b in budgets))
        for use in combos:
            hits = collections.Counter()
            for pid in split:
                cands = candidates(pid, use)
                for q in (x for x in sub if x['paragraph'] == pid):
                    rank = None
                    for i, (fn, off, _) in enumerate(cands, start=1):
                        if fn == q['file'] and abs(off - q['offset']) <= HALF * 2:
                            rank = i
                            break
                    for b in budgets:
                        if rank and rank <= b:
                            hits[b] += 1
            print(f'    {"+".join(use):<28}' +
                  ''.join(f'{100*hits[b]/len(sub):>7.0f}%' for b in budgets))
        print()


if __name__ == '__main__':
    main()
