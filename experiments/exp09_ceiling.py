# -*- coding: utf-8 -*-
"""Experiment 09 — the ceiling, and whether alignment works better as a prior.

Two free questions before any money is spent on reranking.

1. What is recall at a *large* budget?  A reranker can only promote what
   retrieval already surfaced, so recall@400 is the hard ceiling on anything a
   model could do downstream.  If the ceiling is near the budgeted recall there
   is nothing to buy.

2. The alignment failed as a source of ranked passages (exp06).  It may still
   work as a *prior*: not "read here" but "of the passages already retrieved,
   prefer the ones near where this paragraph corresponds to".
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
import cocite as CC                                          # noqa: E402
import shingle as S                                          # noqa: E402
import topical as X                                          # noqa: E402
import gold as G                                             # noqa: E402

HALF, RRF_K = 1200, 20


def main():
    sh = pickle.load(open('experiments/cache/index.pkl', 'rb'))
    tp = pickle.load(open('experiments/cache/topical.pkl', 'rb'))
    files = sh['files']
    idfs = S.idf(sh['postings'], sum(len(v) for v in sh['postings'].values()))
    avg = sum(w[3] for w in tp['windows']) / len(tp['windows'])
    paras = {p['id']: p['text'] for p in json.load(
        open('/Users/tegchok/སྐབས་དང་པོ།-viewer/app/data/text.json',
             encoding='utf-8'))['paragraphs']}
    para_at = json.load(open('experiments/exp05_alignment.json',
                             encoding='utf-8'))['paragraph_offsets']
    raw = pickle.load(open('experiments/cache/aligns.pkl', 'rb'))
    aligns = {}
    for fn, (xs, ys) in raw.items():
        al = A.Alignment([])
        al.xs, al.ys = xs, ys
        aligns[fn] = al
    truth = G.load()

    def ranked(pid, deep, prior=0.0):
        acc, origin = collections.defaultdict(float), {}
        for r, p in enumerate(S.retrieve(sh['per'][pid], files, sh['postings'],
                                         idfs, top=deep), 1):
            k = (p['file'], p['offset'] // HALF)
            acc[k] += 1 / (RRF_K + r)
            origin.setdefault(k, p['offset'])
        for r, p in enumerate(X.score(tp['qt'][pid], tp['windows'],
                                      tp['postings'], avg, top=deep), 1):
            k = (files[p['file_id']], p['offset'] // HALF)
            acc[k] += 1 / (RRF_K + r)
            origin.setdefault(k, p['offset'])
        for r, h in enumerate(CC.retrieve(paras[pid], files, sh['postings'],
                                          top=deep), 1):
            k = (h['file'], h['offset'] // HALF)
            acc[k] += 1.6 / (RRF_K + r)
            origin.setdefault(k, h['offset'])
        if prior:
            x = para_at.get(pid)
            for k in list(acc):
                al = aligns.get(k[0])
                if al is None or not len(al) or x is None:
                    continue
                err = abs(al.at(x) - origin[k])
                if err < 20000:                  # near the corresponding place
                    acc[k] += prior * (1 - err / 20000) / RRF_K
        out = sorted(acc.items(), key=lambda kv: -kv[1])
        return [(k[0], origin[k]) for k, _ in out]

    def measure(split, deep, prior, budgets):
        sub = [q for q in truth if q['paragraph'] in split]
        hits = collections.Counter()
        for pid in split:
            cands = ranked(pid, deep, prior)
            for q in (x for x in sub if x['paragraph'] == pid):
                rank = next((i for i, (f, o) in enumerate(cands, 1)
                             if f == q['file']
                             and abs(o - q['offset']) <= HALF * 2), None)
                for b in budgets:
                    if rank and rank <= b:
                        hits[b] += 1
        return {b: 100 * hits[b] / len(sub) for b in budgets}, len(sub)

    budgets = (20, 30, 50, 100, 200, 400, 10000)
    print('The ceiling — recall as the budget grows (deep retrieval, no prior)\n')
    print(f'{"split":<12}' + ''.join(
        f'{("@" + str(b)) if b < 10000 else "all":>8}' for b in budgets))
    for name, split in (('tune', G.TUNE), ('held out', G.HELD_OUT)):
        got, n = measure(split, 400, 0.0, budgets)
        print(f'{name:<12}' + ''.join(f'{got[b]:>7.0f}%' for b in budgets))

    print('\n\nAlignment as a prior rather than a source of passages\n')
    print(f'{"split":<12}{"prior":<8}' +
          ''.join(f'{"@" + str(b):>8}' for b in (20, 30, 50)))
    for name, split in (('tune', G.TUNE), ('held out', G.HELD_OUT)):
        for prior in (0.0, 0.5, 1.0, 2.0):
            got, _ = measure(split, 60, prior, (20, 30, 50))
            print(f'{name:<12}{prior:<8}' +
                  ''.join(f'{got[b]:>7.0f}%' for b in (20, 30, 50)))


if __name__ == '__main__':
    main()
