# -*- coding: utf-8 -*-
"""The ground truth: every quotation the fifteen hand-made analyses actually used.

Eleven of them are in the viewer's built quote index, with offsets the viewer's
own tool derived.  Four (p7-p10) exist only as selection files, so their text is
re-located here through the same locator the viewer uses, which is what the
build step would do anyway.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'legacy'))
import quotes as Q                                           # noqa: E402

VIEWER = '/Users/tegchok/སྐབས་དང་པོ།-viewer'
NAMES = json.load(open('Commentaries/commentary_names.json', encoding='utf-8'))


def load():
    out, seen = [], set()
    for path in ('Explanations/quotes/index.json',
                 'Explanations/Need to be merged/quotes/index.json'):
        full = os.path.join(VIEWER, path)
        if not os.path.exists(full):
            continue
        for q in json.load(open(full, encoding='utf-8')).values():
            key = (q['paragraph'], q['source']['file'], q['location']['offset'])
            if key in seen:
                continue
            seen.add(key)
            out.append({'paragraph': q['paragraph'], 'file': q['source']['file'],
                        'offset': q['location']['offset'],
                        'length': q['location']['length'],
                        'tier': q.get('tier'), 'id': q['id']})

    sources = Q.sources()
    folder = os.path.join(VIEWER, 'Explanations/Need to be merged')
    for name in sorted(os.listdir(folder)):
        if not name.endswith('.json'):
            continue
        sel = json.load(open(os.path.join(folder, name), encoding='utf-8'))
        pid = sel.get('paragraph')
        if not pid or any(q['paragraph'] == pid for q in out):
            continue
        for i, entry in enumerate(sel.get('quotes') or [], start=1):
            fn, text = entry.get('file'), entry.get('text')
            if not fn or not text or fn not in sources:
                continue
            found = sources[fn].find(text)
            if not found:
                continue
            offset, length, _ = found
            key = (pid, fn, offset)
            if key in seen:
                continue
            seen.add(key)
            out.append({'paragraph': pid, 'file': fn, 'offset': offset,
                        'length': length, 'tier': NAMES.get(fn, {}).get('tier'),
                        'id': f'{pid}-q{i:02d}'})
    return out


# declared before any tuning; see experiments/EVAL-SET.md
TUNE = ['p1', 'p3', 'p5', 'p7', 'p9', 'p119', 'p121', 'p123']
HELD_OUT = ['p2', 'p4', 'p6', 'p8', 'p10', 'p120', 'p122']


if __name__ == '__main__':
    import collections
    g = load()
    c = collections.Counter(q['paragraph'] for q in g)
    print(f'{len(g)} gold quotes over {len(c)} paragraphs')
    for pid in sorted(c, key=lambda p: int(p[1:])):
        where = 'tune' if pid in TUNE else 'held out' if pid in HELD_OUT else '?'
        print(f'  {pid:>5}  {c[pid]:>2} quotes   {where}')
    print('tune quotes:', sum(v for k, v in c.items() if k in TUNE))
    print('held-out quotes:', sum(v for k, v in c.items() if k in HELD_OUT))
