# -*- coding: utf-8 -*-
"""Closed-query shingle retrieval over the commentaries.

The set of queries is closed: 426 paragraphs, all known at build time.  So the
index does not need to cover the corpus — it only needs to cover the shingles
that some paragraph actually asks about.  Collecting those first turns an
84 MB inverted index into a few megabytes and one linear pass.

  syllable shingles of length N, taken from the folded text (tools/tibetan.py)
  postings: shingle -> [(file id, syllable index), …] for shingles the
            paragraphs ask about and that are not corpus-wide boilerplate

Scoring a candidate window is idf-weighted overlap: a shingle that occurs in
three places across 84 MB is worth far more than one that occurs in nine
thousand, and OCR damage costs only the N shingles that straddle the damage.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tibetan as T                                          # noqa: E402

N = 4                    # shingle length in syllables
MAX_DF = 4000            # a shingle in more places than this is boilerplate


def paragraph_texts(viewer_json):
    doc = json.load(open(viewer_json, encoding='utf-8'))
    return [(p['id'], p['text']) for p in doc['paragraphs']]


def shingle_set(text, n=N):
    syl = [s for s, _ in T.syllables(text)]
    return {''.join(syl[i:i + n]) for i in range(len(syl) - n + 1)}


def build(commentaries_dir, wanted, n=N, max_df=MAX_DF, progress=None):
    """One pass over the corpus, keeping only the wanted shingles."""
    files = sorted(f for f in os.listdir(commentaries_dir) if f.endswith('.txt'))
    postings = {}
    syllables_per_file = {}
    for fid, name in enumerate(files):
        text = open(os.path.join(commentaries_dir, name), encoding='utf-8').read()
        syl = T.syllables(text)
        syllables_per_file[name] = len(syl)
        forms = [s for s, _ in syl]
        offs = [o for _, o in syl]
        for i in range(len(forms) - n + 1):
            key = ''.join(forms[i:i + n])
            if key in wanted:
                postings.setdefault(key, []).append((fid, i, offs[i]))
        if progress:
            progress(name, len(syl), len(postings))
    postings = {k: v for k, v in postings.items() if len(v) <= max_df}
    return files, postings, syllables_per_file


def idf(postings, total_positions):
    return {k: math.log(1 + total_positions / len(v)) for k, v in postings.items()}


def retrieve(query_shingles, files, postings, idfs, gap=60, top=50):
    """Cluster a paragraph's shingle hits into candidate passages.

    Positions that fall within `gap` syllables of one another in the same file
    are one passage.  A passage's score is the summed idf of the *distinct*
    shingles it contains, so a passage that repeats one common phrase five
    times does not outrank one that shares five rare ones.
    """
    hits = {}
    for sh in query_shingles:
        for fid, i, off in postings.get(sh, ()):
            hits.setdefault(fid, []).append((i, off, sh))
    passages = []
    for fid, items in hits.items():
        items.sort()
        run = []
        for item in items:
            if run and item[0] - run[-1][0] > gap:
                passages.append((fid, run))
                run = []
            run.append(item)
        if run:
            passages.append((fid, run))
    scored = []
    for fid, run in passages:
        seen = {sh for _, _, sh in run}
        score = sum(idfs.get(sh, 0.0) for sh in seen)
        scored.append({
            'file': files[fid],
            'score': score,
            'shingles': len(seen),
            'syl_start': run[0][0],
            'syl_end': run[-1][0],
            'offset': run[0][1],
            'end_offset': run[-1][1],
        })
    # ties broken by file and offset: the query is a set, so iteration order
    # varies between runs and an unbroken tie makes the build non-reproducible
    scored.sort(key=lambda p: (-p['score'], p['file'], p['offset']))
    return scored[:top]
