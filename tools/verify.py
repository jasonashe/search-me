# -*- coding: utf-8 -*-
"""Check an analysis and its quote file before they are handed over.

Two jobs, and the first matters more.

**Nothing unverified may ship.** Every quotation is looked up again in the
commentary file it names, and the offset is derived from that file rather than
taken on trust. A quotation that is not there is refused, and the analysis does
not pass. This is what makes a fabricated Tibetan passage impossible rather than
merely discouraged: it does not depend on anyone's good intentions, and it
cannot be satisfied by a quotation that is *almost* right.

**The analysis has to work in the reader.** The six rubric sections in order;
`<!--line a-b-->` anchors that tile the paragraph exactly, because a gap is a
stretch of text the reader can select and get nothing for; and every
`[…](quote:pNN-qMM)` link resolving to a quote that exists.

  python3 tools/verify.py p80          # expects p80.md and p80.json here
  python3 tools/verify.py p80 --analysis example/p80.md --quotes example/p80.json
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tibetan as T                                          # noqa: E402

PARAGRAPHS = 'paragraphs.json'
SOURCES = 'Commentaries'
# Every corpus in this archive is a valid source for a quotation.  A commentary
# keeps its bare filename; anything else is named by a path whose first segment
# is the collection — "Tengyur/04 DBU MA…/VOL 1 (TZA)/TD03824_….txt".  None of
# them is ever enumerated: a file is opened only when a quotation names it.
CANON_ROOTS = ('Kangyur', 'Tengyur', 'Sungbum', 'རྗེ་ཙོང་ཁ་པ། ཡབ་སྲས། Sungbum')
ANCHOR = re.compile(r'<!--\s*line\s+(\d+)\s*-\s*(\d+)\s*-->')
QUOTE_REF = re.compile(r'\]\(quote:([A-Za-z0-9_-]+)\)')
SECTIONS = ['Passage & Context', 'Translation & Breakdown', 'Structural Context',
            'Philosophical Exposition', 'Bones of Contention', 'Key Terminology']
MIN_BYTES = 2500

# How much of a quotation must actually be in the source before it is accepted.
# A prefix match is not enough: "རྡོ་རྗེ་གཟེགས་མའི་གཏན་ཚིགས་" followed by an
# invented continuation shares its opening five syllables with a real passage,
# and accepting that would attach a claim to a passage that does not make it.
# So a partial match is allowed only for damage at the tail — most of the
# quotation present, and enough of it to be unmistakable.
MIN_SYL = 5              # shorter than this cannot be placed at all
PARTIAL_FRACTION = 0.85  # of the quotation's syllables
PARTIAL_MINIMUM = 10     # syllables, whichever is larger

_cache = {}


def source_path(filename):
    """Where a quotation's `file` actually is, or None.

    A quote file written on macOS may name the source in NFD form while the
    checkout stores it NFC, so the root check compares normalised names and
    the path itself is resolved through T.resolve_path rather than a naive
    os.path.exists().
    """
    name = filename.replace('\\', '/')
    if '/' in name:
        if T.norm_name(name.split('/', 1)[0]) not in \
                {T.norm_name(r) for r in CANON_ROOTS}:
            return None
        return T.resolve_path(name)
    return T.resolve_path(os.path.join(SOURCES, name))


def locate(text, filename):
    """(offset, length, exactness) of `text` in a commentary, or None.

    Compared as syllable sequences so that spacing and shad style, which differ
    edition to edition, do not decide whether a real quotation is accepted.
    """
    path = source_path(filename)
    if path is None:
        return None
    if filename not in _cache:
        source = open(path, encoding='utf-8').read()
        syl = T.syllables(source)
        index = {}
        for i, (form, _) in enumerate(syl):
            index.setdefault(form, []).append(i)
        _cache[filename] = (source, syl, index)
    source, syl, index = _cache[filename]
    forms = [s for s, _ in syl]
    want = [s for s, _ in T.syllables(text)]
    if len(want) < MIN_SYL:
        return None
    best = None
    for i in index.get(want[0], ()):
        n = 0
        while n < len(want) and i + n < len(forms) and forms[i + n] == want[n]:
            n += 1
        if best is None or n > best[1]:
            best = (i, n)
    if best is None or best[1] < MIN_SYL:
        return None
    i, n = best
    if n < len(want) and n < max(PARTIAL_MINIMUM, PARTIAL_FRACTION * len(want)):
        return None                      # a prefix is not the quotation
    start = syl[i][1]
    last = syl[min(i + n, len(syl)) - 1]
    end = last[1] + len(last[0])
    while end < len(source) and source[end] not in ' \n་།༑༎':
        end += 1
    return start, end - start, n == len(want)


def check_quotes(entries):
    problems, records = [], []
    for i, entry in enumerate(entries, start=1):
        qid = f'q{i:02d}'
        filename, text = entry.get('file'), entry.get('text')
        if not filename or not text:
            problems.append(f'quote {i}: needs both "file" and "text"')
            continue
        if not (entry.get('why') or '').strip():
            problems.append(f'quote {i}: needs a "why" — one sentence on what '
                            'this quotation is doing')
        got = locate(text, filename)
        if got is None:
            problems.append(
                f'quote {i} REFUSED: not found in {filename}. '
                f'«{text[:48]}…» — the passage is not there, or only its '
                'opening is and the rest does not follow. Do not work around '
                'this: either find the real passage with tools/find.py and use '
                'exactly what it returns, or drop the quotation and say the '
                'source was not located.')
            continue
        offset, length, whole = got
        source = _cache[filename][0]
        records.append({'ref': qid, 'file': filename, 'offset': offset,
                        'length': length, 'exact': whole,
                        'found': source[offset:offset + length]})
        if not whole:
            problems.append(
                f'quote {i}: {filename} agrees for most of this but not all of '
                'it — OCR damage, or a variant reading. The text recorded is '
                'the source\'s own, which is what the reader should see. Open '
                'it and check it is still the passage you meant.')
    return records, problems


def check_analysis(text, paragraph, quote_ids):
    problems = []
    heads = re.findall(r'^#{1,6}\s+(.*)$', text, re.M)
    seen = -1
    for wanted in SECTIONS:
        where = next((i for i, h in enumerate(heads)
                      if wanted.lower() in h.lower()), None)
        if where is None:
            problems.append(f'no section heading for "{wanted}"')
        elif where < seen:
            problems.append(f'section "{wanted}" is out of order')
        else:
            seen = where
    if len(text) < MIN_BYTES:
        problems.append(f'only {len(text)} bytes — too thin for a full analysis')

    length = len(paragraph)
    spans = [(int(a), int(b)) for a, b in ANCHOR.findall(text)]
    if not spans:
        problems.append('no <!--line a-b--> anchors, so nothing can be looked up')
    last_end, last_start = 0, -1
    for start, end in spans:
        if end <= start:
            problems.append(f'anchor {start}-{end} is empty')
            continue
        if end > length:
            problems.append(f'anchor {start}-{end} runs past the paragraph '
                            f'({length} characters)')
        if start < last_start:
            problems.append(f'anchor {start}-{end} goes backwards')
        if start > last_end:
            problems.append(f'characters {last_end}-{start} are in no anchor — '
                            'the reader can select that stretch and gets nothing')
        elif start < last_end:
            problems.append(f'anchor {start}-{end} overlaps the one before it '
                            f'(which ends at {last_end})')
        last_start, last_end = start, max(last_end, min(end, length))
    if spans and last_end < length:
        problems.append(f'characters {last_end}-{length} are in no anchor')

    for ref in QUOTE_REF.findall(text):
        if ref not in quote_ids:
            problems.append(f'link quote:{ref} has no such quote in the quote '
                            'file. Ids are positional: the nth entry of the '
                            '"quotes" array is q{n:02d}, so reordering the '
                            'array silently re-points every link.')
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('paragraph')
    ap.add_argument('--analysis')
    ap.add_argument('--quotes')
    ap.add_argument('--paragraphs', default=PARAGRAPHS)
    args = ap.parse_args()

    pid = args.paragraph
    analysis = args.analysis or f'{pid}.md'
    quotes = args.quotes or f'{pid}.json'
    paras = {p['id']: p['text'] for p in
             json.load(open(args.paragraphs, encoding='utf-8'))['paragraphs']}
    if pid not in paras:
        print(f'no paragraph {pid}')
        return 2

    if not os.path.exists(quotes):
        print(f'no quote file at {quotes}')
        return 2
    payload = json.load(open(quotes, encoding='utf-8'))
    entries = payload.get('quotes') or []
    records, qproblems = check_quotes(entries)

    if not os.path.exists(analysis):
        print(f'no analysis at {analysis}')
        return 2
    text = open(analysis, encoding='utf-8').read()
    ids = {f'{pid}-{r["ref"]}' for r in records}
    aproblems = check_analysis(text, paras[pid], ids)

    print(f'{pid}: {len(entries)} quotations, {len(records)} verified, '
          f'{len(entries) - len(records)} refused')
    for r in records:
        mark = 'exact' if r['exact'] else 'opening run'
        print(f"  {pid}-{r['ref']}  {mark:<12} {r['file'][:40]:<40} "
              f"@{r['offset']}")
    problems = qproblems + aproblems
    if problems:
        print('\nproblems:')
        for p in problems:
            print(f'  - {p}')
        print('\nNOT READY. Fix these and run again.')
        return 1
    print('\nall checks pass — the analysis and its quotations are ready to hand over.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
