# -*- coding: utf-8 -*-
"""Search the commentaries for a passage, live.

The packs are what an automated search found; they are not a survey.  When the
paragraph cites something the pack does not cover — a root verse, a line of
Haribhadra, a passage of the gser phreng — search for it here and quote what
comes back.  If nothing comes back, say the source was not located.  Never write
a Tibetan quotation from memory.

  python3 tools/find.py "སྟོང་པ་ཉིད་སྨོས་པའི་རྣམ་པས"
  python3 tools/find.py "…" --in "འགྲེལ་པ་དོན་གསལ"

To search the rest of the archive — the Kangyur, the Tengyur and the two Sungbum
collections — add --canon. **Narrow it.** Unfiltered that is nearly a gigabyte
and takes minutes; with a filter it takes seconds, and the pack tells you which section a
citation was found in:

  python3 tools/find.py "…" --canon --in "SHER PHYIN"
  python3 tools/find.py "…" --canon --in "DBU MA"

Search *short distinctive phrases*.  These files carry OCR damage and a long
string will miss where a six-syllable one hits.
"""
import argparse
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tibetan as T                                          # noqa: E402

SOURCES = 'Commentaries'
CANON = ['Kangyur', 'Tengyur', 'Sungbum', 'རྗེ་ཙོང་ཁ་པ། ཡབ་སྲས། Sungbum']
MIN_SYL = 5


def corpus(canon=False, only=None):
    paths = [os.path.join(SOURCES, n) for n in sorted(os.listdir(SOURCES))
             if n.endswith('.txt')]
    if canon:
        for root in CANON:
            if not os.path.isdir(root):
                continue
            for dirpath, _, names in os.walk(root):
                paths += [os.path.join(dirpath, n) for n in sorted(names)
                          if n.endswith('.txt')]
    return [p for p in paths if not only or only in p]


def search(needle, only=None, min_syl=MIN_SYL, canon=False):
    """Longest verbatim run of `needle` in each file, best first."""
    want = [s for s, _ in T.syllables(needle)]
    if len(want) < min_syl:
        return [], f'search for at least {min_syl} syllables'
    hits = []
    for path in corpus(canon, only):
        name = path
        text = open(path, encoding='utf-8', errors='ignore').read()
        syl = T.syllables(text)
        forms = [s for s, _ in syl]
        where = collections.defaultdict(list)
        for i, f in enumerate(forms):
            where[f].append(i)
        best = None
        for start in range(len(want)):
            for i in where.get(want[start], ()):
                n = 0
                while (start + n < len(want) and i + n < len(forms)
                       and forms[i + n] == want[start + n]):
                    n += 1
                if n >= min_syl and (best is None or n > best[1]):
                    best = (syl[i][1], n)
        if best:
            hits.append({'file': name, 'offset': best[0], 'syllables': best[1],
                         'text': text[best[0]:best[0] + best[1] * 8],
                         'whole': best[1] == len(want)})
    hits.sort(key=lambda h: (-h['syllables'], h['file']))
    return hits, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('needle')
    ap.add_argument('--in', dest='only', default=None)
    ap.add_argument('--canon', action='store_true',
                    help='also search Kangyur/ and Tengyur/ (slow unless --in '
                         'narrows it)')
    args = ap.parse_args()
    if args.canon and not args.only:
        print('# searching the whole archive unfiltered — this takes minutes. '
              'Narrow it with --in if you can.\n')
    hits, problem = search(args.needle, args.only, canon=args.canon)
    if problem:
        print(problem)
        return 1
    if not hits:
        where = 'any commentary or canon volume searched' if args.canon \
            else 'any commentary (try --canon for sūtra and śāstra passages)'
        print(f'not found in {where}. Say the source was not located; '
              'do not reconstruct it from memory.')
        return 1
    for h in hits[:12]:
        mark = 'whole phrase' if h['whole'] else f"{h['syllables']} syllables"
        print(f"{h['file']}\n  offset {h['offset']}  ({mark})\n"
              f"  {h['text'][:150]}\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
