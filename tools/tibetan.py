# -*- coding: utf-8 -*-
"""One canonical fold for Tibetan text, shared by every stage.

The index builder, the quote verifier and the anchor checker must agree
character for character about what "the same passage" means, or a quote can
retrieve and then fail to verify — the worst failure available here.  So the
fold lives in exactly one place.

What it folds away, and why:

  * NFC normalisation                 — the archive mixes composed forms
  * whitespace                        — line-wrapping differs edition to edition
  * ༑ ༎ ༏ ༐ ༔  ->  །                  — shad style differs edition to edition
  * ་ + vowel sign  ->  vowel sign + ་ — an OCR artefact present in this archive:
                                        paragraphs.tsv writes ་ི where the
                                        viewer writes ི་, which silently shifts
                                        every offset downstream

`fold()` returns the folded string together with an index mapping each folded
character back to its offset in the original, so a hit found in folded space is
always reported at a true offset in the real file.
"""
import re
import unicodedata

SHADS = {'༑': '།', '༎': '།', '༏': '།', '༐': '།', '༔': '།'}
TSHEG = '་'


def _reorder_tsheg_vowel(text):
    """Move a combining sign that OCR left stranded after its tsheg back in
    front of it, so ་ི and ི་ compare equal."""
    out = list(text)
    i = 0
    while i < len(out) - 1:
        if out[i] == TSHEG and unicodedata.combining(out[i + 1]):
            out[i], out[i + 1] = out[i + 1], out[i]
            if i:
                i -= 1
                continue
        i += 1
    return ''.join(out)


def fold(text):
    """(folded text, index back into `text`)."""
    text = unicodedata.normalize('NFC', text)
    text = _reorder_tsheg_vowel(text)
    out, index = [], []
    for i, ch in enumerate(text):
        if ch.isspace():
            continue
        out.append(SHADS.get(ch, ch))
        index.append(i)
    return ''.join(out), index


def folded(text):
    return fold(text)[0]


SYLLABLE_SPLIT = re.compile(f'[{TSHEG}།]+')


def syllables(text):
    """The folded text as a list of (syllable, offset in `text`).

    The offset is into the *original* string, not the folded one — folding
    removes 3-4% of the characters, which by the far end of a 3 MB commentary
    is a drift of thirteen thousand characters.  Everything downstream records
    real offsets, so the drift is resolved here, once.
    """
    f, index = fold(text)
    out, at = [], 0
    for m in SYLLABLE_SPLIT.finditer(f):
        piece = f[at:m.start()]
        if piece:
            out.append((piece, index[at]))
        at = m.end()
    if f[at:]:
        out.append((f[at:], index[at]))
    return out


def shingles(text, n=4):
    """Overlapping n-syllable shingles with their offsets in `text`."""
    syl = syllables(text)
    return [(''.join(s for s, _ in syl[i:i + n]), syl[i][1])
            for i in range(max(0, len(syl) - n + 1))]
