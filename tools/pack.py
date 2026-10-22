# -*- coding: utf-8 -*-
"""Assemble one paragraph's candidate passages from all four retrievers.

Each retriever answers a different question and they are fused by reciprocal
rank, with two priors that measured as worth having (experiments/exp09, exp10):

  alignment prior   prefer passages near where this paragraph corresponds to in
                    that commentary; worth about +5 points of recall
  size prior        a 3 MB commentary gets more accidental matches than a 100 KB
                    one, so discount the credit its length buys it

A tier prior was tried and did not help — see FINDINGS.md.  Tier is carried on
every candidate regardless, because it is what the analyst weighs evidence by
even though it is not what finds the evidence.
"""
import collections
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import align as A                                            # noqa: E402
import cocite as CC                                          # noqa: E402
import shingle as S                                          # noqa: E402
import tibetan as T                                          # noqa: E402
import topical as X                                          # noqa: E402

# Tibetan tokenises at about 1.2 tokens per character, so context is expensive:
# a 1,200-character window costs ~1,400 tokens and twenty-four of them fill a
# context window on their own.  The pack's job is triage; depth comes from
# tools/read_source.py, which the prompt requires before any passage is quoted.
HALF = 700             # half-width of the context shown around a passage
RRF_K = 20
W_ALIGN, W_SIZE = 1.0, 0.3
# Catalogue keys are normalised once at load: a catalogue written in NFD form
# must still match the NFC filenames the indexers return, and vice versa.
NAMES = {T.norm_name(k): v for k, v in
         json.load(open('Commentaries/commentary_names.json',
                        encoding='utf-8')).items()}
YIGCHA = 'རྗེ་བཙུན་ཆོས་ཀྱི་རྒྱལ་མཚན་_སྐབས་དང་པོའི་སྤྱི་དོན།.txt'


class Retrievers:
    def __init__(self, cache=None):
        import pickle
        needed = ('index.pkl', 'topical.pkl', 'aligns.pkl', 'offsets.json')
        if cache is None:
            # only prefer build/ once it is complete — a half-finished rebuild
            # must not be picked up silently
            complete = all(os.path.exists(os.path.join('build', n))
                           for n in needed)
            cache = 'build' if complete else 'experiments/cache'
        missing = [n for n in needed
                   if not os.path.exists(os.path.join(cache, n))]
        if missing:
            raise SystemExit(
                f'{cache}/ is missing {", ".join(missing)}.\n'
                'The indexes are derived and are not committed — the packs in '
                'packs/ are.\nYou only need these to *rebuild* the packs:\n'
                '    python3 tools/build_index.py     # ~10 min\n'
                '    python3 tools/build_canon.py     # ~12 min\n'
                '    python3 tools/build_packs.py     # ~6 min')
        sh = pickle.load(open(os.path.join(cache, 'index.pkl'), 'rb'))
        tp = pickle.load(open(os.path.join(cache, 'topical.pkl'), 'rb'))
        raw = pickle.load(open(os.path.join(cache, 'aligns.pkl'), 'rb'))
        self.files = sh['files']
        self.postings = sh['postings']
        self.per = sh['per']
        self.idfs = S.idf(sh['postings'],
                          sum(len(v) for v in sh['postings'].values()))
        self.windows, self.wpost, self.qt = tp['windows'], tp['postings'], tp['qt']
        self.avg = sum(w[3] for w in self.windows) / len(self.windows)
        self.aligns = {}
        for fn, (xs, ys) in raw.items():
            al = A.Alignment([])
            al.xs, al.ys = xs, ys
            self.aligns[fn] = al
        self.sizes = {f: os.path.getsize(os.path.join('Commentaries', f))
                      for f in self.files}
        offsets = os.path.join(cache, 'offsets.json')
        if not os.path.exists(offsets):
            offsets = 'experiments/exp05_alignment.json'
        self.para_at = json.load(
            open(offsets, encoding='utf-8'))['paragraph_offsets']
        self._text = {}

    def source(self, filename):
        if filename not in self._text:
            self._text[filename] = open(os.path.join('Commentaries', filename),
                                        encoding='utf-8').read()
        return self._text[filename]

    def candidates(self, pid, paragraph_text, top=120, deep=120,
                   exclude_self=True):
        """`exclude_self` drops the paragraph's own text where it sits in the
        yig cha file — it always ranks first and is not evidence for itself."""
        acc = collections.defaultdict(float)
        origin, methods = {}, collections.defaultdict(set)

        def add(key, offset, weight, rank, method):
            acc[key] += weight / (RRF_K + rank)
            origin.setdefault(key, offset)
            methods[key].add(method)

        for r, p in enumerate(S.retrieve(self.per[pid], self.files,
                                         self.postings, self.idfs, top=deep), 1):
            add((p['file'], p['offset'] // HALF), p['offset'], 1.0, r, 'wording')
        for r, p in enumerate(X.score(self.qt[pid], self.windows, self.wpost,
                                      self.avg, top=deep), 1):
            add((self.files[p['file_id']], p['offset'] // HALF), p['offset'],
                1.0, r, 'subject')
        for r, h in enumerate(CC.retrieve(paragraph_text, self.files,
                                          self.postings, top=deep), 1):
            add((h['file'], h['offset'] // HALF), h['offset'], 1.6, r,
                'same citation')
        x = self.para_at.get(pid)
        for key in list(acc):
            fn = key[0]
            al = self.aligns.get(fn)
            if al is not None and len(al) and x is not None:
                err = abs(al.at(x) - origin[key])
                if err < 20000:
                    acc[key] += W_ALIGN * (1 - err / 20000) / RRF_K
            acc[key] -= W_SIZE * math.log(
                self.sizes.get(fn, 1e5) / 1e5) / RRF_K

        if exclude_self and x is not None:
            for key in [k for k in acc
                        if T.norm_name(k[0]) == T.norm_name(YIGCHA)]:
                if abs(origin[key] - x) < 4000:
                    del acc[key]

        # ties broken by file then offset, so a rebuild is byte-identical
        ordered = sorted(acc.items(),
                         key=lambda kv: (-kv[1], kv[0][0], kv[0][1]))
        out = []
        for (fn, _), score in ordered[:top]:
            offset = origin[(fn, _)]
            text = self.source(fn)
            meta = NAMES.get(T.norm_name(fn), {})
            start = max(0, offset - HALF // 3)
            out.append({
                'file': fn,
                'title': meta.get('title', fn),
                'author': (meta.get('author') or '').strip(),
                'tier': meta.get('tier'),
                'offset': offset,
                'found_by': sorted(methods[(fn, _)]),
                'score': round(score, 5),
                'context': text[start:offset + HALF],
                'context_offset': start,
            })
        return out
