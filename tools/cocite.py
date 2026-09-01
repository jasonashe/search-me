# -*- coding: utf-8 -*-
"""Co-citation retrieval: find everyone else who quotes what this paragraph quotes.

A yig cha paragraph argues by citing — a sūtra line, a kārikā, a lemma of
Haribhadra — and marks the citation with ཞེས / ཅེས.  The passages an analyst
most wants are the *other* places in the corpus that cite the same words, because
that is where another master takes a position on the same evidence.

Whole-passage ranking cannot find these.  The shared span is six or eight
syllables inside a paragraph of two hundred, so a window containing it scores
below windows that share a lot of ordinary vocabulary; measured on the gold
analyses, that is most of what the rankers miss.  Searching the citation *on its
own* is a different query, and it is the one the analyst actually ran.

The score is the length of the shared run in syllables.  Nothing is scored by
similarity: a hit is a verbatim shared span or it is not a hit.
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tibetan as T                                          # noqa: E402

# ཞེས and ཅེས (with their ཤེས variant after a suffix) close a quotation
CLOSERS = re.compile(r'(ཞེས|ཅེས|ཤེས་བྱ་བ)')

# A citation's left edge is where the source is named — ལས། for a text, ན་རེ།
# for a speaker.  Falling back to the nearest shad is not enough on its own: a
# quoted verse is itself full of shads, so the shad immediately before ཞེས sits
# *inside* the verse and yields a seven-syllable tail rather than the quotation.
# The source marker is tried first, however far back it is.
MARKERS = re.compile(r'(ལས།|ལས༑|ལས་ཀྱང་།|ན་རེ།|ཏུ་ཡང་།|དུ་ཡང་།)')
SHADS = re.compile(r'།')
MIN_SYL, MAX_SYL = 5, 48


def citations(paragraph_text):
    """The passages this paragraph presents as quotations, longest first.

    Bounded by an explicit closer on the right and, on the left, by the nearest
    citation opener — a source named with ལས། , a speaker named with ན་རེ།, or
    failing those a shad.  The left edge is the uncertain one, so several
    lengths are returned and the longest verified run wins downstream.
    """
    folded = T.folded(paragraph_text)
    out = []
    for m in CLOSERS.finditer(folded):
        left = folded[:m.start()]
        marked = [mm.end() for mm in MARKERS.finditer(left)]
        shads = [mm.end() for mm in SHADS.finditer(left)]
        starts = marked[-2:] + shads[-2:]          # source marker first
        for start in starts:
            span = left[start:]
            n = len(T.syllables(span))
            if MIN_SYL <= n <= MAX_SYL:
                out.append(span)
    seen, uniq = set(), []
    for s in sorted(out, key=len, reverse=True):
        if s not in seen:
            seen.add(s)
            uniq.append(s)
    return uniq


def runs(citation, postings, n=4, min_run=3):
    """Where else in the corpus this citation's wording occurs.

    Consecutive shingles that land at consecutive syllable positions in the same
    file are one shared span; `min_run` consecutive shingles means a shared run
    of min_run + n - 1 syllables, which at the default is seven — long enough
    that a coincidence is unlikely and short enough to survive OCR damage
    elsewhere in the line.
    """
    syl = [s for s, _ in T.syllables(citation)]
    keys = [''.join(syl[i:i + n]) for i in range(len(syl) - n + 1)]

    # Shingle j of the citation matching at syllable i of a file puts the hit on
    # diagonal d = i - j.  Consecutive shingles of one shared span all sit on the
    # same diagonal, so a run is a stretch of consecutive j on one diagonal.
    diagonals = collections.defaultdict(dict)     # (file, d) -> j -> offset
    for j, key in enumerate(keys):
        for fid, i, off in postings.get(key, ()):
            diagonals[(fid, i - j)][j] = off

    out = []
    for (fid, _), js in diagonals.items():
        order = sorted(js)
        start = prev = order[0]
        for j in order[1:] + [None]:
            if j is not None and j == prev + 1:
                prev = j
                continue
            length = prev - start + 1
            if length >= min_run:
                out.append({'file_id': fid, 'offset': js[start],
                            'syllables': length + n - 1})
            if j is not None:
                start = prev = j
    return sorted(out, key=lambda r: (-r['syllables'], r['file_id'],
                                      r['offset']))


def retrieve(paragraph_text, files, postings, top=40):
    hits = {}
    for cite in citations(paragraph_text):
        for r in runs(cite, postings):
            key = (r['file_id'], r['offset'])
            if r['syllables'] > hits.get(key, {'syllables': 0}).get('syllables', 0):
                hits[key] = {'file': files[r['file_id']], 'offset': r['offset'],
                             'syllables': r['syllables'], 'citation': cite}
    return sorted(hits.values(),
                  key=lambda h: (-h['syllables'], h['file'], h['offset']))[:top]
