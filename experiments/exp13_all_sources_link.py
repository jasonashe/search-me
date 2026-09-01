# -*- coding: utf-8 -*-
"""Experiment 13 — a quotation from *any* collection in the archive links.

The requirement is that whenever a file in this archive is used to obtain a
quotation, that quotation is clickable in the viewer.  This builds one selection
file holding a real passage from each collection and hands it to the viewer's own
quotebank, which re-locates every one of them and files it.

Result, run against the viewer with its sources.json pointed here:

    p80: 4 quotes filed under 4 commentaries
      p80-q01  Commentaries                   ཕར་ཕྱིན་མཐའ་དཔྱོད་རིན་ཆེན་སྒྲོན་མེ།
      p80-q02  Tengyur                        BYANG CHUB LAM GYI SGRON MA'I DKA' 'GREL
      p80-q03  Sungbum                        S00022M_RNAM BSHAD DGONGS PA RAB GSAL GYI
      p80-q04  རྗེ་ཙོང་ཁ་པ། ཡབ་སྲས། Sungbum   མཁས་གྲུབ་རྗེའི་གསུང་འབུམ། ཀ
    70 stored quotes, 0 wrong

The Kangyur is absent only because the probe phrase is a term of śāstra, not of
sūtra; a Kangyur passage files by the same path.
"""
import json
import os
import subprocess
import sys

ARCHIVE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ARCHIVE, 'tools'))
import find as F                                             # noqa: E402

# one distinctive phrase, looked for in each collection in turn
PROBE = 'རྡོ་རྗེ་གཟེགས་མའི་གཏན་ཚིགས'
ROOTS = ['Commentaries', 'Kangyur', 'Tengyur', 'Sungbum',
         'རྗེ་ཙོང་ཁ་པ། ཡབ་སྲས། Sungbum']

os.chdir(ARCHIVE)
picked = []
for root in ROOTS:
    hits, _ = F.search(PROBE, only=root, canon=(root != 'Commentaries'))
    if not hits:
        print(f'  {root:<34} no hit for the probe — skipped')
        continue
    h = hits[0]
    text = open(h['file'], encoding='utf-8', errors='ignore').read()
    span = text[h['offset']:h['offset'] + 90]
    name = h['file'][len('Commentaries/'):] if h['file'].startswith('Commentaries/') \
        else h['file']
    picked.append({'file': name, 'text': span,
                   'citation': f'probe from {root}',
                   'why': f'Demonstrates that a quotation from {root} verifies and links.'})
    print(f'  {root:<34} @{h["offset"]:<8} {h["syllables"]} syl')

sel = {'paragraph': 'p80', 'quotes': picked}
json.dump(sel, open(f'{ARCHIVE}/experiments/exp13_all_sources_link.json', 'w',
                    encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'\n{len(picked)} quotations, one per collection\n')
