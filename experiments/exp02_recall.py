# -*- coding: utf-8 -*-
"""Experiment 02 — does closed-query shingle retrieval find the gold quotes?

Ground truth: the 113 quotations the hand-made analyses actually used, each with
the commentary file and the character offset the viewer's own tool verified.

A gold quote counts as retrieved at rank K if some passage in the top K comes
from the same file and its span, widened by the context the analyst would be
shown anyway, contains the quote's offset.
"""
import json
import os
import pickle
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
import shingle as S                                          # noqa: E402
import tibetan as T                                          # noqa: E402

VIEWER = '/Users/tegchok/སྐབས་དང་པོ།-viewer'
WINDOW = 1500          # chars of source shown around a passage in the brief


def gold():
    out = []
    for path in ('Explanations/quotes/index.json',
                 'Explanations/Need to be merged/quotes/index.json'):
        full = os.path.join(VIEWER, path)
        if os.path.exists(full):
            for q in json.load(open(full, encoding='utf-8')).values():
                out.append({'paragraph': q['paragraph'],
                            'file': q['source']['file'],
                            'offset': q['location']['offset'],
                            'length': q['location']['length'],
                            'tier': q.get('tier'),
                            'id': q['id']})
    seen, uniq = set(), []
    for q in out:
        key = (q['paragraph'], q['file'], q['offset'])
        if key not in seen:
            seen.add(key)
            uniq.append(q)
    return uniq


def main():
    cache = pickle.load(open('experiments/cache/index.pkl', 'rb'))
    files, postings, per = cache['files'], cache['postings'], cache['per']
    total_positions = sum(len(v) for v in postings.values())
    idfs = S.idf(postings, total_positions)

    truth = gold()
    by_para = {}
    for q in truth:
        by_para.setdefault(q['paragraph'], []).append(q)
    print(f'{len(truth)} gold quotes over {len(by_para)} paragraphs\n')

    ranks = {k: 0 for k in (5, 10, 25, 50)}
    missed, found_rank = [], []
    for pid, quotes in sorted(by_para.items(), key=lambda x: int(x[0][1:])):
        if pid not in per:
            continue
        results = S.retrieve(per[pid], files, postings, idfs, top=50)
        for q in quotes:
            rank = None
            for i, r in enumerate(results, start=1):
                if r['file'] != q['file']:
                    continue
                if r['offset'] - WINDOW <= q['offset'] <= r['end_offset'] + WINDOW:
                    rank = i
                    break
            if rank is None:
                missed.append(q)
            else:
                found_rank.append((pid, q['id'], rank, q['tier']))
                for k in ranks:
                    if rank <= k:
                        ranks[k] += 1

    n = len(truth)
    print('recall of gold quotes by rank cutoff:')
    for k in sorted(ranks):
        print(f'  top {k:>3}: {ranks[k]:>3}/{n}  ({100*ranks[k]/n:.0f}%)')
    print(f'  missed entirely: {len(missed)}/{n} ({100*len(missed)/n:.0f}%)')

    print('\nby tier (recall @50):')
    import collections
    tot = collections.Counter(q['tier'] for q in truth)
    got = collections.Counter(t for _, _, _, t in found_rank)
    for tier in sorted(tot, key=lambda x: (x is None, x)):
        print(f'  tier {str(tier):>4}: {got[tier]:>3}/{tot[tier]:<3} '
              f'({100*got[tier]/tot[tier]:.0f}%)')

    print('\nmissed:')
    for q in missed:
        print(f"  {q['paragraph']:>5} {q['id']:<10} tier {str(q['tier']):>4}  "
              f"off {q['offset']:>8}  {q['file'][:44]}")
    json.dump({'ranks': ranks, 'n': n,
               'missed': missed,
               'found': found_rank},
              open('experiments/exp02_recall.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
