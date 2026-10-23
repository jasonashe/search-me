# The set-up

How to get an analysis of any paragraph of སྐབས་དང་པོའི་སྤྱི་དོན། out of Claude Cowork,
what is in the repository that makes it work, and where it is weak.

The numbers behind every claim here are in `FINDINGS.md`; the experiments that produced
them are in `experiments/`.

---

## 1 · How you use it

Push this repository to GitHub, connect it in Cowork, and paste `COWORK-PROMPT.md` with
the paragraph id changed. That is the whole interface. Cowork returns two files in the
chat:

| file | goes to |
|---|---|
| `p80.md` | `Explanations/p80.md` in the viewer |
| `p80.json` | `Explanations/quotes/_selected/p80.json` in the viewer |

Then, in the viewer repository:

```sh
python3 tools/quotebank.py build p80     # re-verifies and files the quotations
python3 tools/explanations.py p80        # checks the analysis
```

Both pass on the worked example in `example/`, which was produced by this set-up and
merged into a copy of the viewer to confirm it (`9 quotes filed under 6 commentaries`,
`anchors cover 100.0%`, `75 stored quotes, 0 wrong`).

**Paragraph ids: read this once.** `paragraphs.tsv`, which earlier versions of this
archive treated as the unit of analysis, is a **different and stale segmentation** — 397
rows against the viewer's 426, and 108 of the shared ones differ in text even after
folding whitespace and shad variants. The viewer's numbering is canonical here. In
practice: **`p80` in this repository is `p80` in the viewer, and is *not* the `p80` of
the old tsv** (which is the viewer's p82). The prompt makes Cowork echo the paragraph's
first clause before it starts, so a mismatch shows up in one line rather than after a
merge. `paragraphs.json` is the canonical text.

---

## 2 · What is in the repository

| | size | what it is |
|---|---|---|
| `Commentaries/` | 93 MB | the 53 commentary texts, unchanged, with `commentary_names.json` |
| `Kangyur/`, `Tengyur/`, `Sungbum/`, `རྗེ་ཙོང་ཁ་པ། ཡབ་སྲས། Sungbum/` | 964 MB | the rest of the archive — 2,388 files. Large on disk, **roughly 120 MB in the clone**: Tibetan text deflates about eight to one, and git stores it deflated |
| `packs/` | 33 MB | **426 evidence packs**, one per paragraph — the thing that makes this work |
| `build/canon.json` | 2.8 MB | where each paragraph's citations sit in the collections, precomputed — 2,966 locations across 275 of the 426 paragraphs |
| `paragraphs.json` | 1.2 MB | the canonical 426 paragraphs and the 687-entry outline |
| `tools/` | 280 KB | thirteen scripts (§4) |
| `example/` | 36 KB | the worked example: `p80.md` and `p80.json` |
| `COWORK-PROMPT.md`, `analysis_rubric.md` | 24 KB | the prompt and the rubric |
| **total** | **≈1.08 GB on disk, ≈235 MB cloned** | |

**Every corpus in the archive is a quote source, and every one of them links.** That is a
deliberate requirement rather than a convenience: a quotation is only worth having if the
reader can open the text it came from, so nothing is indexed that cannot also be reached.

Not committed: the 256 MB `quotes/` candidate pool (§3), and the rest of `build/`
(derived; regenerate with `tools/build_index.py` in about ten minutes and
`tools/build_canon.py` in about ten).

A gigabyte in the working tree is the price of that. If it proves too much to clone, the
lever is `sources.json` in the viewer, which lets the collections live outside the
repository — but then Cowork cannot read them, so the retrieval would have to be rebuilt
elsewhere. I would keep them in.

---

## 3 · Why packs, and why the old pool is gone

**The set of questions is closed.** There are 426 paragraphs and they are all known now.
So retrieval does not have to happen in Cowork at all: it can run offline, against the
whole corpus, with every hit checked in the file it came from, and what ships is the
answer rather than the machinery. That makes the design degrade well — a Claude that can
only read files still has everything — and it moves the recall problem to where there is
no context limit.

Each pack carries, in this order:

1. **the paragraph**, with its length, since the anchors must tile it exactly;
2. **the two neighbouring paragraphs in full**, because section 1 of the rubric asks what
   precedes and follows and "the preceding discussion" is not an answer;
3. **its place in the text's own sa bcad** — the outline path, not just the nearest
   heading. The viewer already carried a 687-entry outline with levels and paragraph ids,
   so this did not have to be re-derived from the prose;
4. **the Ornament lemma** the section is commenting on, where the outline announces one,
   resolved to exact offsets in the root text and its Indian glosses. This works because
   85% of the Ornament's 1,113 pādas occur verbatim in Haribhadra's འགྲེལ་པ་དོན་གསལ།;
5. **the canonical sources** — where the sūtras, tantras and śāstras it quotes actually
   live in the Kangyur, the Tengyur or the Sungbum collections, with work, volume and
   offset (§5);
6. **the anchor menu** — clause spans with exact offsets that tile the paragraph (§6);
7. **the evidence** — 16 passages with context, then 40 further leads as one-liners;
8. **a coverage note** saying which tiers returned nothing, so silence is visible.

**The 50,000-candidate pool is not used and not shipped.** Four in five of its entries are
not in the file they name. Rather than filter it, retrieval was rebuilt from
`Commentaries/` directly, which makes the pool's error rate stop being something anyone
has to manage. A consequence worth noting: the 29 paragraphs the old scan never covered
are no longer special, because nothing depends on the scan.

### What finds the passages

Four retrievers, fused by reciprocal rank, each answering a different question:

- **wording** — syllable shingles, idf-weighted: where this *phrasing* occurs;
- **subject** — BM25 over syllable unigrams and bigrams: where this *subject* is discussed;
- **same citation** — the words a paragraph presents as a quotation, searched on their
  own: *who else cites what this paragraph cites*. This finds passages the other two
  cannot, because the shared span is six syllables inside two hundred and drowns in any
  whole-passage score;
- **alignment** — a monotone chain of rare shared shingles between the yig cha and each
  commentary, giving *the corresponding place*. It is used only as a ranking prior, for
  the reason in §7.

Held-out recall against the 157 quotations the fifteen hand-made analyses used:
**53% at rank 20, 58% at 30, 63% at 50.**

**That number is the most important thing on this page, and it is why the prompt is
written the way it is.** Roughly two in five of the quotations a good analyst reaches for
will not be in the pack. The pack is labelled as leads, not as a survey; the prompt says
so in as many words, requires two live probes before section 3 can be written, and says
that a session in which nothing was found by hand is a session that did not work at it.

---

## 4 · The tools

Five are for Cowork to run; the rest build the thing.

| | |
|---|---|
| `read_source.py` | read any source file — commentary or canon volume — around an offset; *the* live probe |
| `find.py` | search the commentaries, and with `--canon` every other collection |
| `verify.py` | **the gate**: re-locate every quotation, check the sections, the anchor tiling and the links |
| `tibetan.py` | the one canonical fold (§7) |
| `anchors.py` | the clause spans behind the anchor menu |
| `outline.py`, `lemma.py` | the outline path and the root-text lemma |
| `shingle.py`, `topical.py`, `cocite.py`, `align.py` | the four retrievers |
| `canon.py`, `build_canon.py` | resolving the paragraph's citations in the Kangyur, Tengyur and Sungbum collections |
| `pack.py`, `build_index.py`, `build_packs.py` | assembly |

**`verify.py` is what makes fabrication impossible rather than merely discouraged.** It
looks every quotation up again in the file it names and derives the offset from that
file; a quotation that is not there is refused, and the message tells the analyst to
search for the real passage or drop it — not to work around the refusal. Comparison is by
syllable sequence, not raw string, so edition differences in spacing and shad do not
reject a real quotation. **One caveat you should know about, because it changes where the guarantee lives.** I
tested this by appending a fabricated line to the worked example — one whose opening
syllables really do occur in Gyaltsab. My verifier accepted it at first, as a prefix
match; that is fixed (a partial match now needs 85% of the quotation, minimum ten
syllables) and the line is refused. But **the viewer's own `quotebank.py` still accepts
it**, because its locator falls back to matching the opening few characters and then files
*the source's own reading at that offset* — a different passage under the analyst's
attribution. So the guarantee is not "two independent gates"; it is `tools/verify.py`,
run before hand-over, which is why the prompt makes that a condition of returning the
files. The viewer's `Source.find` should be tightened the same way; I have not touched
that repository.

---

## 5 · What was rejected, and why

**The canon is included, and I had recommended against it.** Worth setting out, because
the reasoning matters more than the conclusion.

I measured how many of the yig cha's 1,797 explicit citations resolve in the canon *and
not* in `Commentaries/`: fifteen, 0.8%, and those fifteen were coincidental short matches.
On that number I recommended shipping neither. The human overruled it, on the ground that
many paragraphs quote sūtras, tantras and Indian śāstras directly and those should be
citable from their own source.

**They are right and the measurement was answering the wrong question.** Coverage asks
"can this citation be found somewhere"; the analyst's question is "*whose text is this*".
Those come apart completely. p80 cites བདག་ལས་མ་ཡིན་གཞན་ལས་མིན།… — a verse my retrieval
happily located in Tsongkhapa, in Gyaltsab, and in Chökyi Gyaltsen's own Madhyamaka
textbook, which is why it scored as "already covered". It is Nāgārjuna's, and it is in the
Tengyur at `TD03824 … (Prajñā Nāma Mūla Madhyamaka Kārikā)`, character 378. Citing the
root text is not the same scholarly act as citing someone who quotes it, and no coverage
count can see the difference.

So `Kangyur/`, `Tengyur/` and both Sungbum collections are committed, and
`tools/build_canon.py` precomputes, for every paragraph, where its citations live in them — a run of at least **ten**
syllables must agree, since six-syllable matches across a gigabyte are constant noise
(that was the flaw in the original 0.8% test's counterpart figure). Each pack carries a
**Canonical sources** section naming the work, section, volume and offset.

**The viewer has been extended so that a passage from any of these collections links like
any other quotation.** That repository was read-only reference under the original brief;
the human lifted that and asked for the change, then generalised it: whenever a file in
this archive is used to obtain a quotation, that quotation must be clickable in the
viewer. What was done there is described in §9.

**Embeddings were not bought.** The passages lexical retrieval misses are mostly parallel
treatments in different words — which the alignment prior and co-citation partly recover
— plus two classes that are not similarity problems at all: looking a *work* up by its
title, and going to a biography for a fact about the author. Spending the budget
embedding 84 MB of OCR-damaged scholastic Tibetan to chase that residual did not look
worthwhile. **This is the weakest claim in the deliverable: it is a judgement, not a
measurement.** The cheap way to settle it is to embed only the tier-1 and tier-2 files
(~8 MB) and score against the held-out gold.

**Model reranking was tested and rejected on its numbers.** Cheap models make it *worse*
(`gemini-2.5-flash-lite` cost 12 points of recall); mid-tier models gain three points at
rank 20–30 and nothing at rank 50. Running it over 426 paragraphs would cost about $4 and
put a paid API in the build for a gain that vanishes at the budget the packs ship at. The
reranking judgement is left to Cowork, which is a far stronger model and is reading the
pack anyway.

**A tier prior in the ranking was tested and dropped.** Tier is what an analyst *weighs*
evidence by; it is not what *finds* it, and adding it to the ranking did not help.

---

## 6 · The context budget

Measured, not estimated: **Tibetan tokenises at about 0.83 characters per token** —
roughly 1.2 tokens per character. The first draft of a pack was 67,000 tokens.

| | |
|---|---|
| a pack, as shipped | ~70 KB, **~31,000 tokens** |
| passages with full context | 16, at 700 characters each |
| further leads | 40, one line each |
| rubric + prompt | ~6,000 tokens |
| the analysis Cowork writes | ~10,000 tokens |

Which leaves comfortable room for the live reads the prompt requires. The 700-character
window is deliberately for **triage**: it is enough to judge whether a passage bears on
the paragraph, and not enough to quote from — which is the point, since the prompt
requires opening the source before quoting.

---

## 7 · Two mechanical decisions worth knowing about

**One fold function.** Tibetan here differs edition to edition in whitespace and shad
style, and this archive additionally contains an OCR artefact where a vowel sign lands
after its tsheg (`་ི` for `ི་`). `tools/tibetan.py` folds all of that away and keeps an
index back to true offsets, and the index builder, the verifier and the anchor checker all
use it. If they folded differently you would get quotations that retrieve and then fail
to verify, which is the worst failure shape available here. (During development I had a
version where the index reported *folded* offsets while the ground truth used real ones —
a drift of 13,553 characters by the end of a 3 MB file. It made retrieval look half as
good as it was. Hence: one fold, one place.)

**Anchors are assembled, not counted.** The viewer requires section 2's `<!--line a-b-->`
anchors to tile the paragraph exactly, and a model counting character offsets in Tibetan
gets that wrong often and silently. So each pack ships the paragraph pre-split into clause
spans that tile it, and the prompt has Cowork build each anchor from a *run of consecutive
spans*. Tiling is then true by construction. Validation: **95% of the 320 anchor endpoints
in the fifteen hand-made analyses already fall exactly on these clause boundaries**, and
13 of the 15 are at 100%.

A related trap the prompt handles explicitly: quote ids are **positional** — the nth entry
of the JSON array is `pNN-qNN` — so reordering the array silently re-points every link in
the analysis. The prompt requires freezing the JSON before writing the markdown.

---

## 8 · Known limits

- **Retrieval finds a little over half of what a good analyst uses.** The rest depends on
  Cowork actually searching, which the prompt requires but cannot enforce. This is the
  set-up's main dependency on the model's diligence.
- **The tidy-pack risk.** A neat brief can make a model stop looking. The defences are
  procedural — the pack is labelled as leads, two live probes are required, the coverage
  note makes silence visible — and I cannot demonstrate that they work, because
  demonstrating it means running the whole set-up many times and judging the output.
- **The alignment is unevenly reliable and there is no confidence signal for it.** It is
  accurate to a few thousand characters for texts commenting on the Ornament in its own
  order, and useless for texts on a different root. I tried to gate it on local anchor
  density; that failed, so it contributes only a weak ranking prior and is never presented
  to Cowork as "read here".
- **Only 11 of the 254 outline labels announce an Ornament lemma.** Where none does, the
  pack says so and the rubric requires marking the position unclear. That is honest but it
  means section 3 is thinner for most paragraphs than it is for the ones inside a named
  excursus.
- **The viewer's own quote locator is looser than this one** and will accept a passage
  whose opening matches, storing a different reading under the analyst's attribution
  (§4). One line in the viewer's `tools/quotes.py` would close it; I have not changed that
  behaviour, only the source resolution around it.
- **The repository is about a gigabyte in the working tree.** That is the cost of every
  source being reachable; see §2 for the lever if it proves too much.
- **The rubric's six sections could not be tested against alternatives**, because the
  viewer's checker requires exactly those headings in that order. Only the guidance inside
  them was revised.
- **Nothing here has been run at scale.** One paragraph has been taken end to end. The
  packs for all 426 exist and are well-formed, but the claim that this produces good
  analyses rests on that one worked example and on the retrieval numbers behind it.

---

## 9 · The change made to the viewer

The original brief said the viewer repository was read-only reference. The human lifted
that and asked for canon passages to be linkable — then widened it: **any file in the
archive used to obtain a quotation must produce a clickable link.** So
`/Users/tegchok/སྐབས་དང་པོ།-viewer` was modified. Five files, and the design principle throughout is that **a commentary
record is unchanged** — every existing quotation still works exactly as before.

**How a source is named.** A commentary keeps its bare filename
(`སེང་གེ་བཟང་པོ་_འགྲེལ་པ་དོན་གསལ།.txt`). A canon passage carries a path whose first
segment is the collection
(`Tengyur/04 DBU MA…/VOL 1 (TZA)/TD03824_….txt`). The presence of a `/` is what
distinguishes them, so nothing about the old records had to be migrated.

| file | change |
|---|---|
| `sources.json` *(new)* | where the collections live. Paths relative to the repository or absolute, searched before its own copies. This exists so a gigabyte does not have to be duplicated |

**How the two repositories are wired together right now.** This one sits at
`/Users/tegchok/search-me`; the viewer at `/Users/tegchok/སྐབས་དང་པོ།-viewer`. The
viewer's `sources.json` points at `../search-me/Kangyur`, `../search-me/Tengyur`,
`../search-me/Sungbum` and `../search-me/རྗེ་ཙོང་ཁ་པ། ཡབ་སྲས། Sungbum`, so the collections
are read from here rather than copied. Relative paths there are resolved **against the
viewer's own root, not the working directory**, so the tools behave the same whatever
directory they are invoked from. If either repository moves, that one file is what needs
changing.
| `tools/quotes.py` | `source_for(name)` resolves such a path and opens it **lazily** — there are 2,388 of these files, and enumerating them the way `sources()` enumerates the commentaries would read a gigabyte into memory on every invocation |
| `tools/quotebank.py` | accepts them, derives title/collection/volume from the path, files them under a per-collection slug |
| `app/main.js` | `resolveSource()` maps a record's `file` to a real path across the configured roots, keeping the existing containment check — `Tengyur/../../etc/passwd` is refused |
| `app/renderer/bridge.js` | the browser fallback encodes each path segment. In a browser only files inside the repository are reachable, so an outside root configured in `sources.json` works in the Electron app only |
| `app/renderer/lib/quote.js` | shows collection and volume for such a source |

**No tier is recorded for these sources, deliberately.** The tiers measure distance from
*this yig cha's interpretive tradition*; a sūtra or an Indian root text does not sit on
that scale, and putting it there would say something false in both directions — maximally
distant, maximally authoritative. The panel shows the collection and volume instead.

Verified end to end on the worked example: `10 quotes filed under 7 commentaries`,
`anchors cover 100.0%`, `76 stored quotes, 0 wrong`, with `p80-q01` resolving to
`.../Tengyur/.../TD03824_...` and the text at the recorded offset matching the stored
quotation exactly.

**Two things you should know about that repository, which I did not touch.** Its working
tree is missing a number of files that are present in git — `app/renderer/app.js`,
`app/renderer/index.html`, most of `app/renderer/lib/`, and `tools/offsets.py`,
`tools/build_data.py`, `tools/extract_pdf.py`, `tools/repair_text.py`, `tools/serve.js`
— all showing as deleted-but-uncommitted. The app cannot start in that state, and I could
not run the UI to see the quote panel render a canon source; the data path is tested, the
pixels are not. `git checkout -- app tools` would restore them if the deletions were
accidental, but that is your call, not mine. Separately, `Explanations/p7`–`p10` and
`p119`–`p123` are untracked and their quote records sit unmerged in
`Explanations/Need to be merged/`, which is why `tools/explanations.py` reports unresolved
quote links for those nine paragraphs.