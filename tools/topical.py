# -*- coding: utf-8 -*-
"""Topical retrieval over the commentaries: BM25 on syllable unigrams+bigrams.

Shingle retrieval (tools/shingle.py) answers "where does this exact wording
occur".  That is the wrong question for most of what an analyst quotes: they
quote the *same topic treated elsewhere*, in different words.  Measured on the
hand-made analyses, near-duplicate retrieval finds about a fifth of what they
used.

This asks the other question — "where is this subject matter discussed" — by
scoring fixed windows of each commentary with BM25 over content terms.  A
Tibetan word is usually one or two syllables, so syllable unigrams and bigrams
stand in for words without needing a segmenter.
"""
import collections
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tibetan as T                                          # noqa: E402

WIN = 220             # window length in syllables (~1200 chars, a page-ish)
STRIDE = 110
K1, B = 1.2, 0.6
DF_CAP = 0.06         # a term in more than this fraction of windows is a stopword


def terms(syls):
    """Content terms of a syllable list: unigrams and adjacent bigrams."""
    out = list(syls)
    out += [syls[i] + syls[i + 1] for i in range(len(syls) - 1)]
    return out


def query_terms(text):
    return terms([s for s, _ in T.syllables(text)])


def build(commentaries_dir, wanted, progress=None):
    """Window index over the corpus, restricted to the wanted vocabulary."""
    files = sorted(f for f in os.listdir(commentaries_dir) if f.endswith('.txt'))
    windows = []                                   # (file id, char offset, length in syl)
    postings = collections.defaultdict(list)       # term -> [(window id, tf), …]
    for fid, name in enumerate(files):
        text = open(os.path.join(commentaries_dir, name), encoding='utf-8').read()
        syl = T.syllables(text)
        forms = [s for s, _ in syl]
        offs = [o for _, o in syl]
        for start in range(0, max(1, len(syl) - 1), STRIDE):
            chunk = forms[start:start + WIN]
            if len(chunk) < 40:
                continue
            wid = len(windows)
            windows.append((fid, offs[start],
                            offs[min(start + WIN, len(offs)) - 1], len(chunk)))
            counts = collections.Counter(t for t in terms(chunk) if t in wanted)
            for term, tf in counts.items():
                postings[term].append((wid, tf))
        if progress:
            progress(name, len(syl), len(windows))
    cap = DF_CAP * len(windows)
    postings = {t: p for t, p in postings.items() if len(p) <= cap}
    return files, windows, postings


def score(query, windows, postings, avg_len, top=60):
    n = len(windows)
    counts = collections.Counter(query)
    acc = collections.defaultdict(float)
    for term, qtf in counts.items():
        posting = postings.get(term)
        if not posting:
            continue
        idf = math.log(1 + (n - len(posting) + 0.5) / (len(posting) + 0.5))
        for wid, tf in posting:
            length = windows[wid][3]
            acc[wid] += idf * (tf * (K1 + 1)) / (
                tf + K1 * (1 - B + B * length / avg_len))
    ranked = sorted(acc.items(), key=lambda x: (-x[1], x[0]))[:top]
    return [{'window': wid, 'score': s, 'file_id': windows[wid][0],
             'offset': windows[wid][1], 'end_offset': windows[wid][2]}
            for wid, s in ranked]
