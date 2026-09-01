# search-me

A retrieval and prompting set-up for writing scholarly analyses of
**སྐབས་དང་པོའི་སྤྱི་དོན།**, Jetsun Chökyi Gyaltsen's Prajñāpāramitā textbook as taught at
Sera Jey Monastery.

It is not a collection of analyses. It is the machinery that lets a language model — in
practice Claude Cowork, working from this repository — write one good analysis of any
paragraph of the text, with every Tibetan quotation verified against the file it came
from.

## Start here

| | |
|---|---|
| **[`COWORK-PROMPT.md`](COWORK-PROMPT.md)** | the prompt to paste. Change the paragraph id and go |
| **[`SETUP.md`](SETUP.md)** | the design: what is here, how it is used, what was rejected and why, what it costs, where it is weak |
| **[`FINDINGS.md`](FINDINGS.md)** | the experiments, with numbers — including the ones that failed |
| **[`example/`](example/)** | two finished analyses: one written by hand, one produced by this set-up |

## What is in it

- `Commentaries/` — 46 commentary texts, 81 MB, with author, title and tier for each
- `Kangyur/`, `Tengyur/`, `Sungbum/`, `རྗེ་ཙོང་ཁ་པ། ཡབ་སྲས། Sungbum/` — 2,388 more source
  files. Every one of them is quotable, and every quotation links back to its own text
- `packs/` — **426 evidence packs**, one per paragraph: the paragraph and its neighbours,
  its place in the text's own sa bcad, the Ornament lemma its section comments on, where
  the sūtras and śāstras it cites actually live, a clause menu for the translation
  anchors, and the passages an offline search found
- `paragraphs.json` — the canonical 426 paragraphs and the 687-entry outline
- `tools/` — the retrievers, the pack builder, and `verify.py`, which refuses any
  quotation that is not really in the source it names

## The one rule

**No Tibetan quotation may be written from memory.** Everything quoted is located in a
file in this archive at a recorded character offset, and `tools/verify.py` re-derives that
offset from the file rather than trusting it. A passage that is not there is refused, not
warned about.

```sh
python3 tools/find.py "སྟོང་པ་ཉིད་སྨོས་པའི་རྣམ་པས"    # search the sources
python3 tools/read_source.py "འགྲེལ་པ་དོན་གསལ" 3732     # read around an offset
python3 tools/verify.py p80                              # check an analysis before use
```

## Rebuilding

The packs are committed, so nothing has to be run to use this. To rebuild them from the
sources:

```sh
python3 tools/build_index.py     # ~10 min
python3 tools/build_canon.py     # ~12 min
python3 tools/build_packs.py     # ~6 min
```

The finished analyses are merged into a separate viewer application, which reads them and
opens each quotation at its place in the source. `SETUP.md` §1 and §9 describe that side.
