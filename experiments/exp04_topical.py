# -*- coding: utf-8 -*-
"""Experiment 04 — topical BM25 against the same gold quotes as exp02/03."""
import collections
import json
import os
import pickle
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
import topical as X                                          # noqa: E402

VIEWER = '/Users/tegchok/སྐབས་དང་པོ།-viewer'
SLACK = 600           # a hit counts if the quote sits within this of the window


def gold():
    out, seen = [], set()
    for path in ('Explanations/quotes/index.json',
                 'Explanations/Need to be merged/quotes/index.json'):
        full = os.path.join(VIEWER, path)
        if not os.path.exists(full):
            continue
        for q in json.load(open(full, encoding='utf-8')).values():
            key = (q['paragraph'], q['source']['file'], q['location']['offset'])
            if key in seen:
                continue
            seen.add(key)
            out.append({'paragraph': q['paragraph'], 'file': q['source']['file'],
                        'offset': q['location']['offset'], 'tier': q.get('tier'),
                        'id': q['id']})
    return out


def main():
    c = pickle.load(open('experiments/cache/topical.pkl', 'rb'))
    files, windows, postings, qt = c['files'], c['windows'], c['postings'], c['qt']
    avg = sum(w[3] for w in windows) / len(windows)
    order = [p['id'] for p in json.load(
        open(os.path.join(VIEWER, 'app/data/text.json'), encoding='utf-8'))['paragraphs']]
    pos = {pid: i for i, pid in enumerate(order)}

    truth = gold()
    by_para = collections.defaultdict(list)
    for q in truth:
        by_para[q['paragraph']].append(q)

    print(f'{len(truth)} gold quotes, {len(windows)} windows\n')
    print(f'{"variant":<26}{"top5":>7}{"top10":>7}{"top25":>7}{"top50":>7}'
          f'{"top100":>8}{"top200":>8}')
    best = {}
    for label, span in (('paragraph only', 0), ('paragraph +-1', 1),
                        ('paragraph +-2', 2), ('paragraph +-5', 5)):
        hit = collections.Counter()
        ranks = {}
        for pid, quotes in by_para.items():
            i = pos[pid]
            q_terms = []
            for j in range(max(0, i - span), min(len(order), i + span + 1)):
                q_terms += qt[order[j]]
            results = X.score(q_terms, windows, postings, avg, top=200)
            for q in quotes:
                rank = None
                for r_i, r in enumerate(results, start=1):
                    if files[r['file_id']] == q['file'] and \
                       r['offset'] - SLACK <= q['offset'] <= r['end_offset'] + SLACK:
                        rank = r_i
                        break
                ranks[q['id']] = rank
                for k in (5, 10, 25, 50, 100, 200):
                    if rank and rank <= k:
                        hit[k] += 1
        n = len(truth)
        print(f'{label:<26}' + ''.join(
            f'{100*hit[k]/n:>6.0f}%' for k in (5, 10, 25, 50)) +
            ''.join(f'{100*hit[k]/n:>7.0f}%' for k in (100, 200)))
        best[label] = ranks

    # per tier, for the best variant
    ranks = best['paragraph only']
    tot = collections.Counter(q['tier'] for q in truth)
    got = collections.Counter(q['tier'] for q in truth
                              if ranks.get(q['id']) and ranks[q['id']] <= 50)
    print('\nrecall@50 by tier (paragraph-only query):')
    for tier in sorted(tot, key=lambda x: (x is None, x)):
        print(f'  tier {str(tier):>4}: {got[tier]:>3}/{tot[tier]:<3} '
              f'({100*got[tier]/tot[tier]:.0f}%)')
    still = [q for q in truth if not ranks.get(q['id'])]
    print(f'\nstill missed at 200: {len(still)}')
    for q in still[:25]:
        print(f"  {q['paragraph']:>5} {q['id']:<10} tier {str(q['tier']):>4} "
              f"off {q['offset']:>8}  {q['file'][:40]}")
    json.dump(best, open('experiments/exp04_topical.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
