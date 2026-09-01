# -*- coding: utf-8 -*-
"""Clause spans for a paragraph, so translation anchors cannot be miscounted.

The viewer's checker requires the `<!--line a-b-->` anchors in section 2 to tile
the paragraph exactly: forward, non-overlapping, no gaps, from character 0 to the
last character.  Asking a model to compute those offsets by counting characters
in Tibetan — where one visible syllable is several code points — fails often, and
fails silently in a way that puts the reader on the wrong line.

So the offsets are computed here, once, and shipped with the paragraph.  The
analyst never counts: it picks a *run of consecutive clauses* and the anchor is
the first clause's start and the last clause's end.  Tiling is then true by
construction, because the clauses themselves tile the paragraph.
"""
import re

# a clause ends at a shad (in any of its forms) together with whatever spacing
# follows it, so the spans join up with no gap between them
BOUNDARY = re.compile(r'[།༎༏༐༑]+\s*')

# a few paragraphs — the title page, verse colophons — run for hundreds of
# characters without a shad.  One span that long is useless as an anchor, so it
# is subdivided at tsheg boundaries, which never splits a syllable.
# The cap adapts to the paragraph: a 200-character title page needs finer
# spans than a 2,000-character argument, and the analyst wants roughly ten to
# twenty units either way.
MAX_SPAN, MIN_SPAN, TARGET_SPANS = 180, 55, 14
TSHEG = re.compile(r'[་\s]')


def span_cap(text):
    return max(MIN_SPAN, min(MAX_SPAN, len(text) // TARGET_SPANS))


def clauses(text):
    """[(start, end, text)] covering the paragraph exactly, in order."""
    spans, at = [], 0
    for m in BOUNDARY.finditer(text):
        end = m.end()
        if end > at:
            spans.append((at, end))
            at = end
    if at < len(text):
        spans.append((at, len(text)))
    if not spans:
        spans = [(0, len(text))]
    # a shad-only fragment is not a clause; fold it into the one before it
    merged = []
    for start, end in spans:
        if merged and not re.sub(r'[།༎༏༐༑\s]', '', text[start:end]):
            merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))
    out = []
    for start, end in merged:
        out += _subdivide(text, start, end)
    return [(s, e, text[s:e]) for s, e in out]


def _subdivide(text, start, end):
    """Break an over-long span at tsheg boundaries, still tiling exactly."""
    cap = span_cap(text)
    if end - start <= cap:
        return [(start, end)]
    cuts, at = [], start
    while end - at > cap:
        target = at + cap
        here = None
        for m in TSHEG.finditer(text, at, min(end, target + 60)):
            if m.end() > at + cap // 3:
                here = m.end()
                if here >= target:
                    break
        if here is None or here >= end:
            break
        cuts.append((at, here))
        at = here
    cuts.append((at, end))
    return cuts


def check_tiling(text, spans):
    """The invariant, asserted rather than assumed."""
    if not spans:
        return ['no spans']
    problems = []
    if spans[0][0] != 0:
        problems.append(f'starts at {spans[0][0]}, not 0')
    if spans[-1][1] != len(text):
        problems.append(f'ends at {spans[-1][1]}, not {len(text)}')
    for (a, b), (c, d) in zip(spans, spans[1:]):
        if b != c:
            problems.append(f'gap or overlap between {a}-{b} and {c}-{d}')
    return problems
