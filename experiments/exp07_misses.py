# -*- coding: utf-8 -*-
"""Experiment 07 — what kind of thing does retrieval miss?

Fusion plateaus at ~53% recall. Tuning further is guesswork until we know what
the other half *is*.  Each missed gold quote is classified by where it sits and
what it looks like, because different kinds need different machinery and some
need none at all.
"""
import collections
import json
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
sys.path.insert(0, HERE)
import shingle as S                                          # noqa: E402
import topical as X                                          # noqa: E402
import tibetan as T                                          # noqa: E402
import gold as G                                             # noqa: E402

HALF = 1200


def main():
    sh = pickle.load(open('experiments/cache/index.pkl', 'rb'))
    tp = pickle.load(open('experiments/cache/topical.pkl', 'rb'))
    files = sh['files']
    idfs = S.idf(sh['postings'], sum(len(v) for v in sh['postings'].values()))
    avg = sum(w[3] for w in tp['windows']) / len(tp['windows'])
    sizes = {f: os.path.getsize(os.path.join('Commentaries', f))
             for f in os.listdir('Commentaries') if f.endswith('.txt')}

    truth = G.load()
    found = set()
    for pid in {q['paragraph'] for q in truth}:
        cands = []
        for r, p in enumerate(S.retrieve(sh['per'][pid], files, sh['postings'],
                                         idfs, top=60), start=1):
            cands.append((p['file'], p['offset']))
        for r, p in enumerate(X.score(tp['qt'][pid], tp['windows'],
                                      tp['postings'], avg, top=60), start=1):
            cands.append((files[p['file_id']], p['offset']))
        for q in (x for x in truth if x['paragraph'] == pid):
            if any(f == q['file'] and abs(o - q['offset']) <= HALF * 2
                   for f, o in cands):
                found.add(q['id'])

    missed = [q for q in truth if q['id'] not in found]
    print(f'{len(missed)} of {len(truth)} gold quotes missed by shingle+topical\n')

    def classify(q):
        size = sizes.get(q['file'], 1)
        if q['offset'] < 1200:
            return 'title line / opening of a work'
        if q['offset'] > size - 3000:
            return 'colophon / end of a work'
        if 'རྣམ་ཐར' in q['file']:
            return "biography (author's life, not doctrine)"
        return 'body of a commentary'

    kinds = collections.Counter(classify(q) for q in missed)
    total = collections.Counter(classify(q) for q in truth)
    print(f'{"kind":<44}{"missed":>8}{"of":>6}{"":>4}')
    for k, n in kinds.most_common():
        print(f'  {k:<42}{n:>8}{total[k]:>6}')

    print('\n\nMissed quotes in the body of a commentary — the hard residue:')
    srcs = {}
    for q in missed:
        if classify(q) != 'body of a commentary':
            continue
        if q['file'] not in srcs:
            srcs[q['file']] = open(os.path.join('Commentaries', q['file']),
                                   encoding='utf-8').read()
        text = srcs[q['file']][q['offset']:q['offset'] + min(q['length'], 90)]
        print(f"  {q['paragraph']:>5} {q['id']:<10} t{q['tier']}  "
              f"{q['file'][:34]:<34}  {text}")

    # does the paragraph explicitly cite a source? that is a different query
    print('\n\nExplicit citation markers in the gold paragraphs:')
    paras = {p['id']: p['text'] for p in json.load(
        open('/Users/tegchok/སྐབས་དང་པོ།-viewer/app/data/text.json',
             encoding='utf-8'))['paragraphs']}
    markers = ('ལས།', 'ལས༑', 'ཞེས་གསུངས', 'ཞེས་སོ', 'ཞེས་བཤད', 'ཞེས་པ')
    for pid in sorted({q['paragraph'] for q in truth}, key=lambda p: int(p[1:])):
        f = T.folded(paras[pid])
        hits = {m: f.count(m) for m in markers if f.count(m)}
        print(f'  {pid:>5}  ' + '  '.join(f'{m}×{n}' for m, n in hits.items()))

    json.dump([q['id'] for q in missed],
              open('experiments/exp07_misses.json', 'w'), ensure_ascii=False)


if __name__ == '__main__':
    main()
