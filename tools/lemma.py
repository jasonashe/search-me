# -*- coding: utf-8 -*-
"""Resolve the Ornament lemma an outline node is commenting on.

Sections of this yig cha open by naming the words of the Abhisamayalamkara they
are about — `རྣམ་པ་ཐམས་ཅད་སྐྱེ་བ་མེད་པ་ཐུགས་སུ་ཆུད་པ། ཞེས་སོགས་ཀྱི་སྐབས་སུ།` —
and those announcements survive into the outline labels.  That gives the one
thing lexical retrieval could never supply: where in the root text, and hence
where in Haribhadra, this stretch of the yig cha belongs.

It works because the Indian commentaries embed the root text as lemmata.
Measured: 85% of the Ornament's 1,113 pādas occur verbatim in Haribhadra's
འགྲེལ་པ་དོན་གསལ།, 70% in Dharmamitra.  So matching the announced words against
those files locates the passage being glossed.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tibetan as T                                          # noqa: E402

MARKER = re.compile(r'(ཞེས་སོགས|ཞེས་པ|ཅེས་སོགས|ཅེས་པ|ཞེས་བྱ་བ)')
ROOT = 'བྱམས་པ་མགོན་པོ་_མངོན་པར་རྟོགས་པའི་རྒྱན།.txt'
GLOSSES = [
    'སེང་གེ་བཟང་པོ་_འགྲེལ་པ་དོན་གསལ།.txt',
    'ཆོས་ཀྱི་བཤེས་གཉེན་_འགྲེལ་བཤད་ཚིག་རབ་ཏུ་གསལ་བ།.txt',
    'སེང་གེ་བཟང་པོ་_རྒྱན་སྣང་།.txt',
    'རྒྱལ་ཚབ་དར་མ་རིན་ཆེན་_རྣམ་བཤད་སྙིང་པོའི་རྒྱན།.txt',
    'ཙོང་ཁ་པ་བློ་བཟང་གྲགས་པ་_ལེགས་བཤད་གསེར་ཕྲེང་སྟོད་ཆ།.txt',
]
MIN_SYL = 6          # a five-syllable run matches by accident too often


def lemma_of(label):
    """The quoted root-text words in an outline label, or None."""
    folded = T.folded(label)
    m = MARKER.search(folded)
    if not m:
        return None
    span = folded[:m.start()].lstrip('།')
    syl = T.syllables(span)
    if len(syl) < MIN_SYL:
        return None
    return span


def locate(lemma, source_text, min_syl=MIN_SYL, _cache={}):
    """Longest verbatim run of the lemma in a source; (offset, syllables).

    Both sides are compared as *syllable sequences*, not as raw folded strings:
    the outline label and the source differ in tsheg and shad placement even
    when the words are identical, and a raw string comparison misses every time.
    """
    key = id(source_text)
    if key not in _cache:
        syl = T.syllables(source_text)
        index = {}
        forms = [s for s, _ in syl]
        for i in range(len(forms)):
            index.setdefault(forms[i], []).append(i)
        _cache[key] = (forms, [o for _, o in syl], index)
    forms, offs, index = _cache[key]

    want = [s for s, _ in T.syllables(lemma)]
    best = None
    for start in range(len(want)):
        for i in index.get(want[start], ()):
            length = 0
            while (start + length < len(want) and i + length < len(forms)
                   and forms[i + length] == want[start + length]):
                length += 1
            if length >= min_syl and (best is None or length > best[1]):
                best = (offs[i], length)
    return best


def resolve(label, sources):
    """Where this outline node's lemma sits in the root text and its glosses."""
    lemma = lemma_of(label)
    if not lemma:
        return None
    out = {'lemma': lemma, 'found': []}
    for fn in [ROOT] + GLOSSES:
        text = sources.get(fn)
        if text is None:
            continue
        got = locate(lemma, text)
        if got:
            out['found'].append({'file': fn, 'offset': got[0],
                                 'syllables': got[1]})
    return out
