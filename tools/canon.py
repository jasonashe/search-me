# -*- coding: utf-8 -*-
"""Resolve the sūtra and śāstra passages the yig cha quotes to their own canonical source.

The yig cha argues by citing, and a great many of those citations are to sūtras,
tantras and Indian śāstras rather than to the commentaries.  Finding the *same
words* inside a commentary that happens to quote them is not the same thing as
being able to open the sūtra itself and read the passage in its own context, and
an analysis that attributes a line to a sūtra should be able to point at the
sūtra.

So this indexes every non-commentary corpus in the archive — `Kangyur/`,
`Tengyur/` and the two Sungbum collections — for exactly one question: **where does
the passage this paragraph quotes live in the canon?**  It is citation
resolution, not browsing — the query set is the citations already extracted from
the 426 paragraphs, so the pass is linear and the index only has to cover what is
actually asked about.

The bar is deliberately high.  A six-syllable agreement across a gigabyte of
Tibetan happens by accident constantly; a run of MIN_RUN syllables does not.  The
matched length is recorded on every hit so the analyst can judge for themselves.
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tibetan as T                                          # noqa: E402

CORPORA = ['Kangyur', 'Tengyur', 'Sungbum', 'རྗེ་ཙོང་ཁ་པ། ཡབ་སྲས། Sungbum']
N = 4                    # shingle length in syllables
MIN_RUN = 10             # syllables that must agree before a hit is reported
MAX_PER_CITATION = 4

# TD04420A_LEGS BSHAD ... (Sanskrit)_unicode.txt  ->  LEGS BSHAD ... (Sanskrit)
STEM = re.compile(r'^(?:[A-Z]{2}[0-9A-Za-z-]*_)?(.*?)(?:_@)?(?:_unicode)?$')


def files():
    out = []
    for root in CORPORA:
        if not os.path.isdir(root):
            continue
        for dirpath, _, names in os.walk(root):
            for n in sorted(names):
                if n.endswith('.txt'):
                    out.append(os.path.join(dirpath, n))
    return sorted(out)


def describe(path):
    """A readable provenance line: collection, section, volume, work."""
    parts = path.split(os.sep)
    stem = STEM.match(parts[-1][:-4]).group(1)
    section = parts[1] if len(parts) > 2 else ''
    section = section.split('_', 1)[-1] if '_' in section else section
    volume = parts[2] if len(parts) > 3 else ''
    return {'collection': parts[0], 'section': section, 'volume': volume,
            'work': stem}


def resolve(citations_by_paragraph, min_run=MIN_RUN, progress=None):
    """{paragraph: [hit]} — every canon location of every citation asked about.

    `citations_by_paragraph` maps a paragraph id to its list of citation strings.
    """
    wanted = collections.defaultdict(list)
    for pid, spans in citations_by_paragraph.items():
        for si, span in enumerate(spans):
            syl = [s for s, _ in T.syllables(span)]
            for i in range(len(syl) - N + 1):
                wanted[''.join(syl[i:i + N])].append((pid, si, i))

    found = collections.defaultdict(list)
    paths = files()
    for k, path in enumerate(paths):
        try:
            text = open(path, encoding='utf-8', errors='ignore').read()
        except OSError:
            continue
        syl = T.syllables(text)
        forms = [s for s, _ in syl]
        offs = [o for _, o in syl]
        diag = collections.defaultdict(dict)
        for i in range(len(forms) - N + 1):
            key = ''.join(forms[i:i + N])
            for pid, si, j in wanted.get(key, ()):
                diag[(pid, si, i - j)][j] = offs[i]
        for (pid, si, _), js in diag.items():
            order = sorted(js)
            start = prev = order[0]
            for j in order[1:] + [None]:
                if j is not None and j == prev + 1:
                    prev = j
                    continue
                length = prev - start + 1 + N - 1
                if length >= min_run:
                    found[pid].append({'citation': si, 'path': path,
                                       'offset': js[start],
                                       'syllables': length,
                                       **describe(path)})
                if j is not None:
                    start = prev = j
        if progress:
            progress(k, len(paths), sum(len(v) for v in found.values()))

    # The Prajnaparamita volumes repeat formulaic passages heavily, so one
    # citation can match in hundreds of places inside a single sutra.  Keep the
    # longest match per *work*, then the best few works — which is what tells an
    # analyst where a passage lives, rather than how often it recurs.
    for pid, hits in found.items():
        per_work = {}
        for h in hits:
            key = (h['citation'], h['path'])
            if h['syllables'] > per_work.get(key, {'syllables': 0})['syllables']:
                per_work[key] = h
        ordered = sorted(per_work.values(),
                         key=lambda h: (h['citation'], -h['syllables'],
                                        h['path']))
        best, seen = [], collections.Counter()
        for h in ordered:
            if seen[h['citation']] >= MAX_PER_CITATION:
                continue
            seen[h['citation']] += 1
            h['works_matching'] = sum(
                1 for k in per_work if k[0] == h['citation'])
            best.append(h)
        found[pid] = best
    return dict(found)
