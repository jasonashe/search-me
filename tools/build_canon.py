# -*- coding: utf-8 -*-
"""Resolve every paragraph's citations in the Kangyur and Tengyur.

  python3 tools/build_canon.py        # ~8 minutes, writes build/canon.json

The result is small (a few hundred KB) and is committed, so the packs can name
canonical sources without anyone re-reading 622 MB.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import canon as C                                            # noqa: E402
import cocite as CC                                          # noqa: E402


def main():
    t0 = time.time()
    paras = json.load(open('paragraphs.json', encoding='utf-8'))['paragraphs']
    cites = {}
    for p in paras:
        c = CC.citations(p['text'])
        if c:
            cites[p['id']] = c
    print(f'{sum(len(v) for v in cites.values())} citations from {len(cites)} '
          f'of {len(paras)} paragraphs', flush=True)

    def progress(k, n, hits):
        if k % 200 == 0:
            print(f'  {k}/{n} canon files, {hits} hits  '
                  f'[{time.time() - t0:.0f}s]', flush=True)

    found = C.resolve(cites, progress=progress)
    os.makedirs('build', exist_ok=True)
    json.dump({'min_run': C.MIN_RUN, 'citations': cites, 'found': found},
              open('build/canon.json', 'w', encoding='utf-8'),
              ensure_ascii=False)
    n = sum(len(v) for v in found.values())
    print(f'\n{n} canon locations for {len(found)} paragraphs '
          f'({100 * len(found) / len(paras):.0f}% of the text), '
          f'{os.path.getsize("build/canon.json") / 1e6:.2f} MB  '
          f'[{time.time() - t0:.0f}s]')


if __name__ == '__main__':
    main()
