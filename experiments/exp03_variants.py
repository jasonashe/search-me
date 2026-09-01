# -*- coding: utf-8 -*-
"""Experiment 03 — why paragraph-as-query fails, and what beats it.

exp02 measured 21% recall@50 for a paragraph queried against itself.  The
hypothesis this tests: the gold quotes are not lexically similar to the
paragraph.  They are the *same topic treated elsewhere* — the companion
mtha' dpyod at the corresponding place, Gyaltsab at the corresponding place,
Haribhadra at the aligned lemma.  If that is right, widening the query from the
paragraph to its topical neighbourhood should move recall a long way, and no
amount of tuning the paragraph-only query will.
"""
import collections
import json
import os
import pickle
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
import shingle as S                                          # noqa: E402

VIEWER = '/Users/tegchok/སྐབས་དང་པོ།-viewer'
WINDOW = 1500


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
    cache = pickle.load(open('experiments/cache/index.pkl', 'rb'))
    files, postings, per = cache['files'], cache['postings'], cache['per']
    idfs = S.idf(postings, sum(len(v) for v in postings.values()))
    order = [p['id'] for p in json.load(
        open(os.path.join(VIEWER, 'app/data/text.json'), encoding='utf-8'))['paragraphs']]
    pos = {pid: i for i, pid in enumerate(order)}

    truth = gold()
    by_para = collections.defaultdict(list)
    for q in truth:
        by_para[q['paragraph']].append(q)

    def query_for(pid, span):
        i = pid if isinstance(pid, int) else pos[pid]
        lo, hi = max(0, i - span), min(len(order), i + span + 1)
        out = set()
        for j in range(lo, hi):
            out |= per.get(order[j], set())
        return out

    print(f'{len(truth)} gold quotes\n')
    print(f'{"variant":<34}{"top5":>7}{"top25":>7}{"top50":>7}{"top100":>8}'
          f'{"top200":>8}')
    rows = {}
    for label, span, top in (('paragraph only', 0, 200),
                             ('paragraph +-1', 1, 200),
                             ('paragraph +-2', 2, 200),
                             ('paragraph +-5', 5, 200),
                             ('paragraph +-10', 10, 200)):
        hit = collections.Counter()
        detail = {}
        for pid, quotes in by_para.items():
            results = S.retrieve(query_for(pid, span), files, postings, idfs,
                                 top=top)
            for q in quotes:
                rank = None
                for i, r in enumerate(results, start=1):
                    if r['file'] == q['file'] and \
                       r['offset'] - WINDOW <= q['offset'] <= r['end_offset'] + WINDOW:
                        rank = i
                        break
                detail[q['id']] = rank
                for k in (5, 25, 50, 100, 200):
                    if rank and rank <= k:
                        hit[k] += 1
        n = len(truth)
        rows[label] = detail
        print(f'{label:<34}' + ''.join(
            f'{100*hit[k]/n:>6.0f}%' if k < 100 else f'{100*hit[k]/n:>7.0f}%'
            for k in (5, 25, 50, 100, 200)))

    # where do the gold quotes actually sit? cluster analysis
    print('\nDo gold quotes for neighbouring paragraphs cluster in the same '
          'region of a commentary?')
    for fname in ('རྗེ་བཙུན་ཆོས་ཀྱི་རྒྱལ་མཚན་_སྐབས་དང་པོའི་མཐའ་དཔྱོད།.txt',
                  'རྒྱལ་ཚབ་དར་མ་རིན་ཆེན་_རྣམ་བཤད་སྙིང་པོའི་རྒྱན།.txt',
                  'ཙོང་ཁ་པ་བློ་བཟང་གྲགས་པ་_ལེགས་བཤད་གསེར་ཕྲེང་སྟོད་ཆ།.txt'):
        pts = sorted((pos[q['paragraph']], q['offset'])
                     for q in truth if q['file'] == fname)
        if not pts:
            continue
        print(f'  {fname[:46]}')
        grouped = collections.defaultdict(list)
        for p, o in pts:
            grouped[p].append(o)
        for p in sorted(grouped):
            print(f'    {order[p]:>5}: ' +
                  ' '.join(f'{o:,}' for o in sorted(grouped[p])))
    json.dump({k: v for k, v in rows.items()},
              open('experiments/exp03_variants.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
