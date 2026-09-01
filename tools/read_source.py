# -*- coding: utf-8 -*-
"""Read a commentary around a character offset.

The packs give offsets; this is how you look at what is actually there.  Read
before you quote — the reason a passage was retrieved is mechanical and says
nothing about whether it bears on the argument.

  python3 tools/read_source.py "སེང་གེ་བཟང་པོ་_འགྲེལ་པ་དོན་གསལ།.txt" 3732
  python3 tools/read_source.py <file> <offset> --width 3000

Works on the canon too — pass the path the pack gives you, or any distinctive
part of it:

  python3 tools/read_source.py "TD03824" 41022
  python3 tools/read_source.py "Kangyur/4. BRGYAD STONG.../KL00012E_....txt" 8891
"""
import argparse
import os
import sys

SOURCES = 'Commentaries'
CANON = ['Kangyur', 'Tengyur', 'Sungbum', 'རྗེ་ཙོང་ཁ་པ། ཡབ་སྲས། Sungbum']


def resolve(wanted):
    """A commentary filename, or any distinctive part of a canon path."""
    if os.path.exists(wanted):
        return wanted
    names = [n for n in sorted(os.listdir(SOURCES)) if n.endswith('.txt')]
    for n in names:
        if n == wanted:
            return os.path.join(SOURCES, n)
    hits = [os.path.join(SOURCES, n) for n in names if wanted in n]
    for root in CANON:
        if not os.path.isdir(root):
            continue
        for dirpath, _, files in os.walk(root):
            for n in files:
                if n.endswith('.txt') and wanted in os.path.join(dirpath, n):
                    hits.append(os.path.join(dirpath, n))
    if len(hits) > 1:
        print(f'{len(hits)} files match {wanted!r}; using the first:')
        for h in hits[:6]:
            print(' ', h)
        print()
    return hits[0] if hits else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('offset', type=int)
    ap.add_argument('--width', type=int, default=2000)
    args = ap.parse_args()

    name = resolve(args.file)
    if name is None:
        print(f'nothing matching {args.file!r} in Commentaries/, Kangyur/ or '
              'Tengyur/. The commentaries are:')
        for n in sorted(os.listdir(SOURCES)):
            if n.endswith('.txt'):
                print(' ', n)
        return 1
    text = open(name, encoding='utf-8').read()
    start = max(0, args.offset - args.width // 2)
    end = min(len(text), args.offset + args.width // 2)
    print(f'{name}  characters {start}–{end} of {len(text)}\n')
    print(text[start:args.offset], end='')
    print(f'\n>>> character {args.offset} <<<\n')
    print(text[args.offset:end])
    return 0


if __name__ == '__main__':
    sys.exit(main())
