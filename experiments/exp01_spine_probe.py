# -*- coding: utf-8 -*-
"""Experiment 01 — can the Abhisamayalamkara root verses serve as an alignment spine?

Claim under test: the yig cha quotes the Ornament's verses at topic boundaries, and
Haribhadra / gser phreng / Gyaltsab embed the same verses as lemmata, so the verse
line is a key that aligns all of them.

Measured: for each of the 426 viewer paragraphs, does any run of >= MIN_SYL
consecutive syllables of an Ornament verse line appear verbatim (folded) in it?
And for each verse line, does it appear in each structural commentary?
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
import tibetan as T                                          # noqa: E402

VIEWER = '/Users/tegchok/སྐབས་དང་པོ།-viewer/app/data/text.json'
COMM = 'Commentaries'
ROOT = 'བྱམས་པ་མགོན་པོ་_མངོན་པར་རྟོགས་པའི་རྒྱན།.txt'
KARIKA = 'བྱམས་པ་མགོན་པོ་_མངོན་རྟོགས་རྒྱན་གྱི་ཚིག་ལེའུར་བྱས་པ།.txt'
STRUCTURAL = [
    'སེང་གེ་བཟང་པོ་_འགྲེལ་པ་དོན་གསལ།.txt',
    'ཙོང་ཁ་པ་བློ་བཟང་གྲགས་པ་_ལེགས་བཤད་གསེར་ཕྲེང་སྟོད་ཆ།.txt',
    'ཙོང་ཁ་པ་བློ་བཟང་གྲགས་པ་_ལེགས་བཤད་གསེར་ཕྲེང་སྨད་ཆ།.txt',
    'རྒྱལ་ཚབ་དར་མ་རིན་ཆེན་_རྣམ་བཤད་སྙིང་པོའི་རྒྱན།.txt',
]
MIN_SYL = 5          # a verse fragment this long is a real citation, not a coincidence


def read(name):
    return open(os.path.join(COMM, name), encoding='utf-8').read()


def verse_lines(text):
    """The root text as shad-delimited verse lines of at least MIN_SYL syllables."""
    out = []
    for chunk in text.replace('།།', '།\n').split('\n'):
        chunk = chunk.strip()
        syl = T.syllables(chunk)
        if len(syl) >= MIN_SYL:
            out.append((chunk, T.folded(chunk)))
    return out


def main():
    paras = json.load(open(VIEWER, encoding='utf-8'))['paragraphs']
    lines = verse_lines(read(ROOT))
    print(f'root text: {len(lines)} verse lines of >= {MIN_SYL} syllables')

    # index every MIN_SYL-syllable window of every verse line -> line number
    windows = {}
    for i, (_, f) in enumerate(lines):
        syl = T.syllables(f)
        for j in range(len(syl) - MIN_SYL + 1):
            key = ''.join(s for s, _ in syl[j:j + MIN_SYL])
            windows.setdefault(key, set()).add(i)
    print(f'{len(windows)} distinct {MIN_SYL}-syllable windows')

    hit_paras, total_hits = 0, 0
    per_para = {}
    for p in paras:
        f = T.folded(p['text'])
        syl = T.syllables(f)
        found = set()
        for j in range(len(syl) - MIN_SYL + 1):
            key = ''.join(s for s, _ in syl[j:j + MIN_SYL])
            found |= windows.get(key, set())
        if found:
            hit_paras += 1
            total_hits += len(found)
        per_para[p['id']] = sorted(found)
    print(f'\nparagraphs containing an Ornament verse fragment: '
          f'{hit_paras}/{len(paras)} ({100*hit_paras/len(paras):.0f}%)')
    print(f'mean distinct verse lines hit per hitting paragraph: '
          f'{total_hits/max(1,hit_paras):.1f}')

    print('\nverse-line reach into the structural commentaries:')
    for name in STRUCTURAL:
        text = T.folded(read(name))
        present = sum(1 for _, f in lines if f and f in text)
        print(f'  {present:>4}/{len(lines)} lines verbatim   {name[:52]}')

    with open('experiments/exp01_spine.json', 'w', encoding='utf-8') as fh:
        json.dump({'verse_lines': [l for l, _ in lines], 'per_paragraph': per_para},
                  fh, ensure_ascii=False)
    print('\nwrote experiments/exp01_spine.json')


if __name__ == '__main__':
    main()
