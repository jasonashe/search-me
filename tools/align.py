# -*- coding: utf-8 -*-
"""Align the yig cha to each commentary by monotone anchor chaining.

Retrieval by wording answers "where does this phrase occur".  What an analyst
actually does is different: they go to *the corresponding place* in a parallel
text — Gyaltsab on the same lemma, the companion mtha' dpyod on the same
question — and read there.  Those passages need share no wording with the
paragraph at all, which is why lexical retrieval misses them.

Every text here comments on the Abhisamayalamkara and follows its order, so the
correspondence is monotone.  That is a strong prior and it is exploitable: rare
shingles shared between the yig cha and a commentary are anchor points, and the
longest increasing chain through them is an alignment.  Interpolating along the
chain turns "paragraph p120" into "somewhere near character 10,500 of the gser
phreng", which is a region to read rather than a file to search.

The chain is built from *rare* shingles only.  A shingle occurring hundreds of
times is a stock phrase and pins nothing; one occurring once in each text is a
real correspondence.
"""
import bisect
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tibetan as T                                          # noqa: E402

N = 5                  # shingle length in syllables
MAX_REPEAT = 3         # a shingle occurring more often than this pins nothing


def positions(text, n=N, max_repeat=MAX_REPEAT):
    """shingle -> [offsets], keeping only shingles rare enough to be anchors."""
    syl = T.syllables(text)
    forms = [s for s, _ in syl]
    offs = [o for _, o in syl]
    out = collections.defaultdict(list)
    for i in range(len(forms) - n + 1):
        out[''.join(forms[i:i + n])].append(offs[i])
    return {k: v for k, v in out.items() if len(v) <= max_repeat}


def anchors(left, right):
    """Candidate (left offset, right offset) correspondences, sorted."""
    pts = []
    for shingle, ls in left.items():
        rs = right.get(shingle)
        if not rs:
            continue
        for a in ls:
            for b in rs:
                pts.append((a, b))
    pts.sort()
    return pts


def chain(points):
    """Longest strictly increasing chain in the second coordinate.

    Patience sorting, O(n log n).  Ties in the first coordinate are resolved by
    taking the points in order, which is what a monotone alignment wants.
    """
    tails, tail_idx, back = [], [], []
    for i, (_, b) in enumerate(points):
        j = bisect.bisect_left(tails, b)
        back.append(tail_idx[j - 1] if j else -1)
        if j == len(tails):
            tails.append(b)
            tail_idx.append(i)
        else:
            tails[j] = b
            tail_idx[j] = i
    out, k = [], (tail_idx[-1] if tail_idx else -1)
    while k >= 0:
        out.append(points[k])
        k = back[k]
    return out[::-1]


class Alignment:
    """A monotone map from yig cha offset to commentary offset."""

    def __init__(self, pairs):
        self.xs = [a for a, _ in pairs]
        self.ys = [b for _, b in pairs]

    def __len__(self):
        return len(self.xs)

    def at(self, x):
        """Predicted commentary offset for a yig cha offset, or None."""
        if not self.xs:
            return None
        i = bisect.bisect_left(self.xs, x)
        if i == 0:
            return self.ys[0]
        if i >= len(self.xs):
            return self.ys[-1]
        x0, x1 = self.xs[i - 1], self.xs[i]
        y0, y1 = self.ys[i - 1], self.ys[i]
        if x1 == x0:
            return y0
        return int(y0 + (y1 - y0) * (x - x0) / (x1 - x0))

    def support(self, x, span):
        """How many anchors back the prediction within `span` of x — the
        honest confidence signal.  A region interpolated across a long gap
        with no anchors is a guess and must be reported as one."""
        lo = bisect.bisect_left(self.xs, x - span)
        hi = bisect.bisect_right(self.xs, x + span)
        return hi - lo


def build(yigcha_text, commentary_text, left=None):
    """`left` is the yig cha's shingle positions; pass it in when aligning
    against many commentaries so it is computed once rather than once per
    commentary — it is the expensive half."""
    if left is None:
        left = positions(yigcha_text)
    return Alignment(chain(anchors(left, positions(commentary_text))))
