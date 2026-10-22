# -*- coding: utf-8 -*-
"""Rebuild everything the pack builder needs, from Commentaries/ alone.

The packs are committed, so nobody needs to run this to *use* the set-up. It
exists so the set-up can be rebuilt — when a commentary is corrected, when the
segmentation changes, or when someone wants to check that the packs really do
follow from the corpus.

    python3 tools/build_index.py       # ~4 minutes, writes build/
    python3 tools/build_packs.py       # ~5 minutes, writes packs/

`build/` is a derived artefact and is not committed: it is 68 MB and
regenerating it is cheaper than storing it.
"""
import json
import os
import pickle
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import align as A                                            # noqa: E402
import shingle as S                                          # noqa: E402
import tibetan as T                                          # noqa: E402
import topical as X                                          # noqa: E402

PARAGRAPHS = 'paragraphs.json'
COMM = 'Commentaries'
OUT = 'build'
YIGCHA = 'རྗེ་བཙུན་ཆོས་ཀྱི་རྒྱལ་མཚན་_སྐབས་དང་པོའི་སྤྱི་དོན།.txt'


def paragraph_offsets(yig_text, paras):
    """Where each paragraph sits in the yig cha's own commentary file.

    353 of 426 are found verbatim — the rest diverge in OCR between the PDF
    extraction and the etext — and the remainder are interpolated between their
    located neighbours, which is accurate enough to drive an alignment that is
    itself only good to a page.
    """
    folded, index = T.fold(yig_text)
    found, order, at = {}, [p['id'] for p in paras], 0
    for p in paras:
        pf = T.folded(p['text'])
        hit = -1
        for cut in (160, 100, 60, 36):
            if len(pf) >= cut:
                hit = folded.find(pf[:cut], max(0, at - 2000))
                if hit >= 0:
                    break
        if hit >= 0:
            found[p['id']] = index[hit]
            at = hit
    exact = len(found)
    for i, pid in enumerate(order):
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
    return found, exact


def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    paras = json.load(open(PARAGRAPHS, encoding='utf-8'))['paragraphs']
    print(f'{len(paras)} paragraphs')

    per = {p['id']: S.shingle_set(p['text']) for p in paras}
    wanted = set().union(*per.values())
    print(f'{len(wanted)} distinct shingles asked about — indexing only these')
    files, postings, syl_per = S.build(COMM, wanted)
    pickle.dump({'files': files, 'postings': postings, 'syl_per': syl_per,
                 'per': per}, open(f'{OUT}/index.pkl', 'wb'), protocol=4)
    print(f'  wording index: {len(postings)} shingles, '
          f'{sum(len(v) for v in postings.values())} postings  '
          f'[{time.time() - t0:.0f}s]')

    qt = {p['id']: X.query_terms(p['text']) for p in paras}
    vocab = set()
    for v in qt.values():
        vocab |= set(v)
    tf, tw, tp = X.build(COMM, vocab)
    pickle.dump({'files': tf, 'windows': tw, 'postings': tp, 'qt': qt},
                open(f'{OUT}/topical.pkl', 'wb'), protocol=4)
    print(f'  subject index: {len(tw)} windows, {len(tp)} terms  '
          f'[{time.time() - t0:.0f}s]')

    yig = open(T.resolve_path(os.path.join(COMM, YIGCHA)),
               encoding='utf-8').read()
    offsets, exact = paragraph_offsets(yig, paras)
    json.dump({'paragraph_offsets': offsets},
              open(f'{OUT}/offsets.json', 'w', encoding='utf-8'),
              ensure_ascii=False)
    print(f'  placed {exact}/{len(paras)} paragraphs verbatim in the yig cha '
          f'file, rest interpolated')

    aligns = {}
    left = A.positions(yig)                    # computed once, not once per file
    for name in sorted(os.listdir(COMM)):
        if not name.endswith('.txt') or \
                T.norm_name(name) == T.norm_name(YIGCHA):
            continue
        text = open(os.path.join(COMM, name), encoding='utf-8').read()
        al = A.build(yig, text, left=left)
        aligns[name] = (al.xs, al.ys)
    pickle.dump(aligns, open(f'{OUT}/aligns.pkl', 'wb'), protocol=4)
    print(f'  alignments: {len(aligns)} commentaries  [{time.time() - t0:.0f}s]')
    print(f'\ndone in {time.time() - t0:.0f}s — now run tools/build_packs.py')


if __name__ == '__main__':
    main()
