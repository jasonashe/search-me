# -*- coding: utf-8 -*-
"""Experiment 05 — does monotone alignment locate what lexical retrieval misses?

For every gold quote, the alignment predicts one offset in the commentary it
came from.  The question is how wide a band around that prediction you must
read to contain the quote.  A band of a few thousand characters is a page or
two — a region an analyst can actually read.  A band of a hundred thousand is
no better than searching the file.
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
sys.path.insert(0, HERE)
import align as A                                            # noqa: E402
import tibetan as T                                          # noqa: E402
import gold as G                                             # noqa: E402

VIEWER = '/Users/tegchok/སྐབས་དང་པོ།-viewer'
YIGCHA = 'རྗེ་བཙུན་ཆོས་ཀྱི་རྒྱལ་མཚན་_སྐབས་དང་པོའི་སྤྱི་དོན།.txt'
BANDS = (2000, 5000, 10000, 20000, 50000)


def paragraph_offsets(yig_text):
    """Where each viewer paragraph sits in the yig cha commentary file.

    353 of 426 are found verbatim; the rest are OCR-divergent and get an offset
    interpolated between their located neighbours, which is enough to drive an
    alignment that is itself only accurate to a page.
    """
    paras = json.load(open(os.path.join(VIEWER, 'app/data/text.json'),
                          encoding='utf-8'))['paragraphs']
    folded, index = T.fold(yig_text)
    found, order = {}, []
    at = 0
    for p in paras:
        order.append(p['id'])
        pf = T.folded(p['text'])
        hit = -1
        for cut in (160, 100, 60, 36):
            if len(pf) < cut:
                continue
            hit = folded.find(pf[:cut], max(0, at - 2000))
            if hit >= 0:
                break
        if hit >= 0:
            found[p['id']] = index[hit]
            at = hit
    for i, pid in enumerate(order):                      # interpolate the rest
        if pid in found:
            continue
        before = next((found[order[j]] for j in range(i - 1, -1, -1)
                       if order[j] in found), None)
        after = next((found[order[j]] for j in range(i + 1, len(order))
                      if order[j] in found), None)
        if before is None and after is None:
            continue
        found[pid] = (before + after) // 2 if before is not None and after is not None \
            else (before if before is not None else after)
    return found, order


def main():
    yig = open(os.path.join('Commentaries', YIGCHA), encoding='utf-8').read()
    offsets, order = paragraph_offsets(yig)
    print(f'{len(offsets)}/{len(order)} paragraphs placed in the yig cha file')

    truth = G.load()
    wanted_files = sorted({q['file'] for q in truth})
    print(f'{len(truth)} gold quotes across {len(wanted_files)} commentary files\n')

    left = A.positions(yig)
    aligns, support_stats = {}, {}
    for fn in wanted_files:
        if fn == YIGCHA:
            continue
        text = open(os.path.join('Commentaries', fn), encoding='utf-8').read()
        al = A.build(yig, text)
        aligns[fn] = al
        print(f'  {len(al):>6} anchors   {fn[:52]}')

    print(f'\n{"split":<10}{"n":>5}' +
          ''.join(f'{"±" + str(b // 1000) + "k":>8}' for b in BANDS))
    rows = {}
    for label, split in (('tune', G.TUNE), ('held out', G.HELD_OUT),
                         ('all', G.TUNE + G.HELD_OUT)):
        sub = [q for q in truth if q['paragraph'] in split]
        hits = collections.Counter()
        detail = []
        for q in sub:
            al = aligns.get(q['file'])
            x = offsets.get(q['paragraph'])
            if al is None or x is None:
                detail.append((q['id'], q['file'], None))
                continue
            pred = al.at(x)
            err = abs(pred - q['offset'])
            detail.append((q['id'], q['file'], err))
            for b in BANDS:
                if err <= b:
                    hits[b] += 1
        rows[label] = detail
        print(f'{label:<10}{len(sub):>5}' +
              ''.join(f'{100*hits[b]/len(sub):>7.0f}%' for b in BANDS))

    errs = sorted(e for _, _, e in rows['all'] if e is not None)
    if errs:
        print(f'\nmedian error {errs[len(errs)//2]:,} chars   '
              f'quartiles {errs[len(errs)//4]:,} / {errs[3*len(errs)//4]:,}')

    print('\nalignment error by commentary (median, all splits):')
    per = collections.defaultdict(list)
    for _, fn, e in rows['all']:
        if e is not None:
            per[fn].append(e)
    for fn in sorted(per, key=lambda f: sorted(per[f])[len(per[f]) // 2]):
        v = sorted(per[fn])
        print(f'  {v[len(v)//2]:>9,}  (n={len(v):>3})  {fn[:50]}')

    json.dump({'bands': BANDS,
               'paragraph_offsets': offsets,
               'errors': {k: [(i, f, e) for i, f, e in v] for k, v in rows.items()}},
              open('experiments/exp05_alignment.json', 'w', encoding='utf-8'),
              ensure_ascii=False)


if __name__ == '__main__':
    main()
