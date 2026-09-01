# -*- coding: utf-8 -*-
"""Experiment 10 — free ranking signals, before paying a model to rerank.

exp09 showed the candidates are there (84% at rank 400) and the ranking buries
them.  Three priors cost nothing to try:

  alignment   prefer passages near the corresponding place  (exp09: +5 points)
  tier        prefer texts close to this curriculum
  size        a 3 MB text offers more chances to match by accident than a
              100 KB one, so normalise the credit a big file gets
"""
import collections
import json
import math
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
NAMES = json.load(open('Commentaries/commentary_names.json', encoding='utf-8'))


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
    sizes = {f: os.path.getsize(os.path.join('Commentaries', f)) for f in files}
    truth = G.load()

    def ranked(pid, w_align, w_tier, w_size, deep=120):
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
        x = para_at.get(pid)
        for k in list(acc):
            fn = k[0]
            if w_align:
                al = aligns.get(fn)
                if al is not None and len(al) and x is not None:
                    err = abs(al.at(x) - origin[k])
                    if err < 20000:
                        acc[k] += w_align * (1 - err / 20000) / RRF_K
            if w_tier:
                tier = NAMES.get(fn, {}).get('tier')
                if isinstance(tier, int):
                    acc[k] += w_tier * (6 - tier) / 5 / RRF_K
            if w_size:
                acc[k] -= w_size * math.log(sizes.get(fn, 1e5) / 1e5) / RRF_K
        out = sorted(acc.items(), key=lambda kv: -kv[1])
        return [(k[0], origin[k]) for k, _ in out]

    def measure(split, *w):
        sub = [q for q in truth if q['paragraph'] in split]
        hits = collections.Counter()
        for pid in split:
            cands = ranked(pid, *w)
            for q in (x for x in sub if x['paragraph'] == pid):
                rank = next((i for i, (f, o) in enumerate(cands, 1)
                             if f == q['file']
                             and abs(o - q['offset']) <= HALF * 2), None)
                for b in (20, 30, 50):
                    if rank and rank <= b:
                        hits[b] += 1
        return {b: 100 * hits[b] / len(sub) for b in (20, 30, 50)}

    settings = [('none', 0, 0, 0), ('align', 1.0, 0, 0),
                ('align+tier', 1.0, 0.5, 0), ('align+size', 1.0, 0, 0.3),
                ('align+tier+size', 1.0, 0.5, 0.3),
                ('align+tier+size (strong)', 1.5, 1.0, 0.5)]
    print(f'{"priors":<28}' + ''.join(
        f'{s + " @" + str(b):>13}' for s in ('tune',) for b in (20, 30, 50)) +
        ''.join(f'{s + " @" + str(b):>15}' for s in ('held',) for b in (20, 30, 50)))
    for label, *w in settings:
        t = measure(G.TUNE, *w)
        h = measure(G.HELD_OUT, *w)
        print(f'{label:<28}' + ''.join(f'{t[b]:>12.0f}%' for b in (20, 30, 50)) +
              ''.join(f'{h[b]:>14.0f}%' for b in (20, 30, 50)))


if __name__ == '__main__':
    main()
