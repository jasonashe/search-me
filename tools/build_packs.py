# -*- coding: utf-8 -*-
"""Build one evidence pack per paragraph.

The set of questions is closed — 426 paragraphs, all known now — so the
retrieval runs here, once, where there is no context limit and every hit can be
checked against the file it came from.  What ships is the answer, not the
machinery to compute it.

Each pack is Markdown, so a Claude that can only read files still gets
everything.  It carries, in this order:

  the paragraph, and the two either side, because section 1 of the rubric asks
      what precedes and follows and "the preceding discussion" is not an answer
  its place in the text's own sa bcad, with the Ornament lemma the section is
      commenting on resolved into the root text and its Indian glosses
  the canonical sources — where the sūtras, tantras and Indian śāstras this
      paragraph quotes actually live in the Kangyur and Tengyur, so a citation
      can be attributed to its own text rather than to a commentary that
      happens to repeat it
  the anchor menu — clause spans with exact offsets, so section 2's anchors are
      assembled from a list rather than counted out by hand
  the evidence: passages with full context, then further leads as one-liners
  a coverage report saying which tiers returned nothing, so silence is visible

Every passage was located in its source file at build time.  Nothing here is
asserted; it was all read out of the text.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anchors as AN                                         # noqa: E402
import lemma as LM                                           # noqa: E402
import outline as OL                                         # noqa: E402
import pack as PK                                            # noqa: E402

# The paragraph document now lives in the repo itself (paragraphs.json at the
# repo root — same 'paragraphs' + 'toc' structure the viewer exported), so the
# builder no longer depends on the Mac viewer's data directory.
VIEWER = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'paragraphs.json')
OUT = 'packs'
# Budget, measured with the token counter rather than guessed: Tibetan runs at
# ~1.2 tokens per character, so 16 passages at 900 characters is ~17K tokens and
# the whole pack lands near 26K — leaving room for the rubric, an exemplar and a
# ten-thousand-token analysis inside a comfortable working context.
FULL, LEADS = 16, 40          # passages with context; further leads


def tier_note(tier):
    return {1: 'tier 1 — this yig cha, or Chökyi Gyaltsen elsewhere',
            2: 'tier 2', 3: 'tier 3', 4: 'tier 4',
            5: 'tier 5 — furthest from this curriculum'}.get(
                tier, 'tier unknown — no catalogue entry, ranks below tier 5')


def render(pid, paras, order, paths, cands, lemma_info, canon, canon_cites):
    p = paras[pid]
    i = order.index(pid)
    out = [f"# {pid} · page {p.get('page')} · evidence pack", '']
    out += ['## The paragraph', '',
            f"{len(p['text'])} characters. Anchors in section 2 of the analysis "
            f"must tile 0–{len(p['text'])} exactly.", '', '```',
            p['text'], '```', '']

    out += ['## Neighbours', '']
    for label, j in (('preceding', i - 1), ('following', i + 1)):
        if 0 <= j < len(order):
            q = paras[order[j]]
            out += [f"**{label} — {q['id']}, page {q.get('page')}**", '',
                    '```', q['text'][:700] +
                    ('…' if len(q['text']) > 700 else ''), '```', '']
        else:
            out += [f'**{label}** — none; this is the edge of the text.', '']

    out += ['## Where this sits in the text', '']
    path = paths.get(pid) or []
    if path:
        for step in path:
            out.append(f"{'  ' * step['level']}- {step['label']}"
                       f"  *(opens at {step['paraId']}, page {step['page']})*")
    else:
        out.append('- No outline entry covers this paragraph. Say so in '
                   'section 3 rather than inventing a position for it.')
    out.append('')

    if lemma_info:
        out += ['### The Ornament lemma this section comments on', '',
                f"The section opening above announces its lemma: "
                f"**{lemma_info['lemma']}**", '',
                'Located verbatim at:', '']
        for f in lemma_info['found']:
            out.append(f"- `{f['file']}` at character **{f['offset']}** "
                       f"({f['syllables']} syllables matched)")
        out += ['', 'Read around those offsets before writing section 3. What '
                    'Haribhadra does *not* raise there is as reportable as what '
                    'he does.', '']
    else:
        out += ['### The Ornament lemma', '',
                'No lemma is announced in this paragraph\'s outline path. Its '
                'position against the root verses has to be argued, or marked '
                'unclear.', '']

    hits = canon.get(pid) or []
    cites = canon_cites.get(pid) or []
    if hits:
        out += ['## Canonical sources', '',
                'The passages this paragraph presents as quotations, located in '
                'the Kangyur and Tengyur. A run of at least ten syllables had to '
                'agree, so these are citations rather than coincidences — but '
                'open one before relying on it, and note that a passage found in '
                'several works may be quoted rather than original there.', '']
        by_cite = {}
        for h in hits:
            by_cite.setdefault(h['citation'], []).append(h)
        for si in sorted(by_cite):
            quoted = cites[si] if si < len(cites) else ''
            out += [f'**Quoted in the paragraph:** {quoted}', '']
            for h in by_cite[si]:
                out.append(f"- *{h['work']}* — {h['collection']}, "
                           f"{h['section']}, {h['volume']}, "
                           f"character **{h['offset']}** "
                           f"({h['syllables']} syllables matched)")
                out.append(f"  `{h['path']}`")
            out.append('')
        out += ['These cannot be linked as `quote:` references — the viewer '
                'resolves quotations only against `Commentaries/`. Cite them in '
                'the prose, naming the work and where it sits.', '']
    elif cites:
        out += ['## Canonical sources', '',
                f'This paragraph presents {len(cites)} passage(s) as '
                'quotations, and none of them was located in the Kangyur or '
                'Tengyur at the ten-syllable threshold. They may be citations '
                'of commentaries rather than of canonical works, or the '
                'wording may have drifted. `tools/find.py --canon` will search '
                'again if you want to narrow it by section.', '']

    spans = AN.clauses(p['text'])
    out += ['## Anchor menu', '',
            f'The paragraph splits into these {len(spans)} clause spans. They '
            'tile it exactly. Build each section-2 anchor from a **run of '
            'consecutive spans** — first span\'s start, last span\'s end — and '
            'use every span exactly once, in order. Done that way the anchors '
            'cannot gap, overlap or overrun.', '', '```']
    for s, e, t in spans:
        out.append(f'{s:>5} {e:>5}  {t.strip()}')
    out += ['```', '']

    out += ['## Evidence', '',
            f'{len(cands)} passages, each located in its source file at build '
            'time. They are leads, not conclusions: open the ones you intend to '
            'use and read around them before quoting. The stated reason a '
            'passage was found is mechanical and says nothing about whether it '
            'bears on the argument.', '']
    for n, c in enumerate(cands[:FULL], 1):
        out += [f"### {n} · {c['author']} · {c['title']}", '',
                f"`{c['file']}` at character **{c['offset']}** · "
                f"{tier_note(c['tier'])} · found by {', '.join(c['found_by'])}",
                '', '```', c['context'], '```', '']
    if len(cands) > FULL:
        out += ['### Further leads', '',
                'Ranked below the passages above and shown without context. '
                'Open any that look relevant.', '', '```']
        for n, c in enumerate(cands[FULL:], FULL + 1):
            head = c['context'][:80].replace('\n', ' ')
            out.append(f"{n:>3}. t{c['tier']} @{c['offset']:<8} "
                       f"{c['author'][:14]:<14} {head}")
        out += ['```', '']

    seen = {c['tier'] for c in cands}
    missing = [t for t in (1, 2, 3, 4, 5) if t not in seen]
    out += ['## Coverage', '',
            f'{len(cands)} passages from {len({c["file"] for c in cands})} '
            'commentaries.']
    if missing:
        out.append(f"**Nothing was found at tier {', '.join(map(str, missing))}.** "
                   'That is a fact about the evidence, not a gap to paper over — '
                   'if the case rests only on distant texts, say so.')
    if not cands:
        out.append('**No passages were found at all.** Do not pad. Search for '
                   'what the paragraph cites, and if nothing is located, write '
                   'the analysis saying the commentarial literature does not '
                   'engage this passage.')
    out.append('')
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('paragraphs', nargs='*')
    ap.add_argument('--out', default=OUT)
    args = ap.parse_args()

    doc = json.load(open(VIEWER, encoding='utf-8'))
    paras = {p['id']: p for p in doc['paragraphs']}
    order = [p['id'] for p in doc['paragraphs']]
    paths = OL.load(VIEWER)
    sources = {fn: open(os.path.join('Commentaries', fn), encoding='utf-8').read()
               for fn in [LM.ROOT] + LM.GLOSSES}
    lemma_cache = {}
    R = PK.Retrievers()
    canon, canon_cites = {}, {}
    if os.path.exists('build/canon.json'):
        blob = json.load(open('build/canon.json', encoding='utf-8'))
        canon, canon_cites = blob['found'], blob['citations']
    else:
        print('  (build/canon.json missing — run tools/build_canon.py to add '
              'canonical sources to the packs)')

    os.makedirs(args.out, exist_ok=True)
    todo = args.paragraphs or order
    for k, pid in enumerate(todo):
        info = None
        for step in reversed(paths.get(pid) or []):
            if step['label'] in lemma_cache:
                info = lemma_cache[step['label']]
            elif LM.lemma_of(step['label']):
                info = LM.resolve(step['label'], sources)
                lemma_cache[step['label']] = info
            if info:
                break
        cands = R.candidates(pid, paras[pid]['text'], top=FULL + LEADS)
        text = render(pid, paras, order, paths, cands, info, canon,
                      canon_cites)
        with open(os.path.join(args.out, f'{pid}.md'), 'w',
                  encoding='utf-8') as fh:
            fh.write(text)
        if k % 25 == 0 or k == len(todo) - 1:
            print(f'  {k + 1}/{len(todo)}  {pid}  {len(text) / 1024:.0f} KB',
                  flush=True)


if __name__ == '__main__':
    main()
