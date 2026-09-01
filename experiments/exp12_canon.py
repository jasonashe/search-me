# -*- coding: utf-8 -*-
"""Experiment 12 — does the canon add anything the commentaries do not already have?

The brief asks whether pulling sūtra and Indian-śāstra citations into the
analysis measurably improves it.  Two facts already bear on it: the viewer's
locator only ever opens files in `Commentaries/`, so a canon passage cannot be
verified or linked by the machinery that consumes this work; and none of the 157
quotations in the fifteen hand-made analyses came from the canon.

This tests the remaining question on the merits.  The yig cha cites its sources
explicitly.  Take every such citation from all 426 paragraphs and ask where it
can be found: in the commentaries, in the canon, in both, or nowhere.  A
citation that resolves *only* in the canon is something the current set-up
cannot reach; the count of those is the value of indexing 964 MB.
"""
import collections
import json
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
sys.path.insert(0, HERE)
import cocite as CC                                          # noqa: E402
import tibetan as T                                          # noqa: E402

CORPORA = ['Kangyur', 'Tengyur', 'Sungbum', 'རྗེ་ཙོང་ཁ་པ། ཡབ་སྲས། Sungbum']
N, MIN_RUN = 4, 3


def canon_files():
    out = []
    for root in CORPORA:
        for dirpath, _, names in os.walk(root):
            for n in names:
                if n.endswith('.txt'):
                    out.append(os.path.join(dirpath, n))
    return sorted(out)


def main():
    paras = json.load(open('/Users/tegchok/སྐབས་དང་པོ།-viewer/app/data/text.json',
                           encoding='utf-8'))['paragraphs']
    cites = {}
    for p in paras:
        c = CC.citations(p['text'])
        if c:
            cites[p['id']] = c
    print(f'{sum(len(v) for v in cites.values())} citations extracted from '
          f'{len(cites)} of {len(paras)} paragraphs', flush=True)

    wanted = {}
    for pid, spans in cites.items():
        for si, span in enumerate(spans):
            syl = [s for s, _ in T.syllables(span)]
            for i in range(len(syl) - N + 1):
                wanted.setdefault(''.join(syl[i:i + N]), []).append((pid, si, i))
    print(f'{len(wanted)} distinct citation shingles', flush=True)

    files = canon_files()
    total_bytes = sum(os.path.getsize(f) for f in files)
    print(f'{len(files)} canon files, {total_bytes/1e6:.0f} MB', flush=True)

    found = collections.defaultdict(set)          # (pid, si) -> {canon file}
    for k, path in enumerate(files):
        try:
            text = open(path, encoding='utf-8', errors='ignore').read()
        except OSError:
            continue
        syl = T.syllables(text)
        forms = [s for s, _ in syl]
        diag = collections.defaultdict(set)
        for i in range(len(forms) - N + 1):
            key = ''.join(forms[i:i + N])
            for pid, si, j in wanted.get(key, ()):
                diag[(pid, si, i - j)].add(j)
        for (pid, si, _), js in diag.items():
            order = sorted(js)
            run = best = 1
            for a, b in zip(order, order[1:]):
                run = run + 1 if b == a + 1 else 1
                best = max(best, run)
            if best >= MIN_RUN:
                found[(pid, si)].add(path)
        if k % 250 == 0:
            print(f'  {k}/{len(files)} files, {len(found)} citations placed',
                  flush=True)

    sh = pickle.load(open('experiments/cache/index.pkl', 'rb'))
    in_comm = set()
    for pid, spans in cites.items():
        for si, span in enumerate(spans):
            if CC.runs(span, sh['postings'], n=N, min_run=MIN_RUN):
                in_comm.add((pid, si))

    allc = {(pid, si) for pid, spans in cites.items()
            for si in range(len(spans))}
    canon = set(found)
    print(f'\n{len(allc)} citations total')
    print(f'  found in Commentaries/           {len(in_comm):>5}'
          f'  ({100*len(in_comm)/len(allc):.0f}%)')
    print(f'  found in the canon               {len(canon):>5}'
          f'  ({100*len(canon)/len(allc):.0f}%)')
    print(f'  found in BOTH                    {len(in_comm & canon):>5}')
    print(f'  found ONLY in the canon          {len(canon - in_comm):>5}'
          f'  <- what indexing 964 MB would add')
    print(f'  found nowhere                    {len(allc - in_comm - canon):>5}')

    only = sorted(canon - in_comm)
    print('\na sample of the citations only the canon has:')
    for pid, si in only[:20]:
        span = cites[pid][si]
        where = sorted(found[(pid, si)])[0]
        print(f'  {pid:>5}  {span[:52]}\n         {where[:96]}')

    json.dump({'only_canon': [[p, s] for p, s in only],
               'in_comm': [[p, s] for p, s in sorted(in_comm)],
               'canon': {f'{p}|{s}': sorted(v)[:4] for (p, s), v in found.items()}},
              open('experiments/exp12_canon.json', 'w', encoding='utf-8'),
              ensure_ascii=False)


if __name__ == '__main__':
    main()
