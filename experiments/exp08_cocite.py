# -*- coding: utf-8 -*-
"""Experiment 08 — co-citation retrieval, alone and fused."""
import collections
import json
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
sys.path.insert(0, HERE)
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
    truth = G.load()

    print('citations extracted per gold paragraph:')
    for pid in sorted({q['paragraph'] for q in truth}, key=lambda p: int(p[1:])):
        c = CC.citations(paras[pid])
        print(f'  {pid:>5}  {len(c):>2} spans   ' +
              (c[0][:56] if c else '(none)'))

    def ranked(pid, use):
        acc, origin = collections.defaultdict(float), {}
        if 'shingle' in use:
            for r, p in enumerate(S.retrieve(sh['per'][pid], files,
                                             sh['postings'], idfs, top=60), 1):
                k = (p['file'], p['offset'] // HALF)
                acc[k] += 1 / (RRF_K + r)
                origin.setdefault(k, p['offset'])
        if 'topical' in use:
            for r, p in enumerate(X.score(tp['qt'][pid], tp['windows'],
                                          tp['postings'], avg, top=60), 1):
                k = (files[p['file_id']], p['offset'] // HALF)
                acc[k] += 1 / (RRF_K + r)
                origin.setdefault(k, p['offset'])
        if 'cocite' in use:
            for r, h in enumerate(CC.retrieve(paras[pid], files,
                                              sh['postings'], top=40), 1):
                k = (h['file'], h['offset'] // HALF)
                acc[k] += 1.6 / (RRF_K + r)      # a verbatim shared citation is
                origin.setdefault(k, h['offset'])  # stronger evidence than a rank
        out = sorted(acc.items(), key=lambda kv: -kv[1])
        return [(k[0], origin[k]) for k, _ in out]

    budgets = (10, 20, 30, 50)
    combos = [('cocite',), ('shingle',), ('shingle', 'topical'),
              ('shingle', 'cocite'), ('shingle', 'topical', 'cocite')]
    print('\n\nrecall at a fixed passage budget\n')
    for name, split in (('tune', G.TUNE), ('held out', G.HELD_OUT)):
        sub = [q for q in truth if q['paragraph'] in split]
        print(f'  {name} split ({len(sub)} quotes)')
        print(f'    {"methods":<30}' + ''.join(f'{"@"+str(b):>8}' for b in budgets))
        for use in combos:
            hits = collections.Counter()
            for pid in split:
                cands = ranked(pid, use)
                for q in (x for x in sub if x['paragraph'] == pid):
                    rank = next((i for i, (f, o) in enumerate(cands, 1)
                                 if f == q['file']
                                 and abs(o - q['offset']) <= HALF * 2), None)
                    for b in budgets:
                        if rank and rank <= b:
                            hits[b] += 1
            print(f'    {"+".join(use):<30}' +
                  ''.join(f'{100*hits[b]/len(sub):>7.0f}%' for b in budgets))
        print()


if __name__ == '__main__':
    main()
