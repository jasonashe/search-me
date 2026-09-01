# Findings

What was tested, what won, what lost, and what it cost. Every number here comes from a
script in `experiments/` that can be re-run.

Two conventions. **Recall** is measured against the 157 quotations the fifteen hand-made
analyses actually used — a recall benchmark only, since a retrieved passage that the
analyst did not happen to use is not thereby wrong, so precision is not claimed. And the
split between the tune and held-out paragraphs was **declared before tuning**, in
`experiments/EVAL-SET.md`; headline numbers are held-out.

---

## 0 · Two things that were wrong before any retrieval was tested

**`paragraphs.tsv` is not the text the viewer uses, and following it would have broken
almost every analysis.** The archive's `paragraphs.tsv` has 397 rows; the viewer has 426
paragraphs. Only 43 of the 397 that map are byte-identical; 289 more agree once
whitespace and shad variants are folded; **108 still differ**, by inserted spaces and by
a systematic `་ི` / `ི་` reordering. Since the viewer requires section 2's anchors to
tile the paragraph from character 0 to its last character, anchors computed against the
tsv fail on most paragraphs and land the reader on the wrong line. `p80` also names
different paragraphs in the two schemes. **The viewer's segmentation is canonical here**
(the human confirmed this), and it is shipped as `paragraphs.json`.

**I measured my own retrieval wrongly at first, and the corrected numbers are much
better.** The first three experiments compared *folded* offsets against the gold's *real*
offsets. Folding removes 3–4% of characters, which by the end of a 3 MB commentary is a
drift of 13,553 characters — far beyond the tolerance I was allowing. Shingle recall@50
read 21% and was really 45%. `tools/tibetan.py` now returns real offsets everywhere and
every experiment was re-run. The lesson generalises: **one fold function, used by the
index, the verifier and the checker alike**, or passages retrieve and then fail to
verify.

---

## 1 · Retrieval

Four retrievers were built, each answering a different question.

| | question it answers | held-out recall@50 |
|---|---|---|
| **wording** (syllable shingles, idf-weighted) | where does this *phrasing* occur | 52% |
| **subject** (BM25 over syllable uni/bigrams) | where is this *subject* discussed | 53% |
| **same citation** (co-citation) | who else quotes what this paragraph quotes | 27% |
| **alignment** (monotone anchor chaining) | where is the *corresponding place* | 15% |

**The single most useful finding is that paragraph-as-query retrieval hits a wall around
half.** Fusing all four by reciprocal rank, with the priors below, gives **53% at rank 20,
58% at 30, 63% at 50** on held-out paragraphs. Query expansion to neighbouring paragraphs
was tried at ±1, ±2, ±5 and ±10 and made things worse at every useful budget.

**Why it stalls.** `experiments/exp07` classifies the misses. They are not near-misses of
wording; they are the *same question treated in different words somewhere else* —
Gyaltsab on the corresponding lemma, the companion mtha' dpyod on the same dispute — plus
two classes that are not passage retrieval at all: **title lines** of works (13 of 24
such gold quotes missed; the analyst was looking a *work* up by name) and **biography**
(7 of 8 missed; the analyst went to a rnam thar to establish a fact about the author).
Those are lookups driven by the analysis's needs, not by the paragraph's words, and no
ranking function will produce them.

**The ceiling is 84%.** At rank 400, held-out recall reaches 84%, and 87% with no cutoff.
So the passages *are* being retrieved and then buried by ranking. That gap is what made a
reranker worth paying to test (§4).

### Co-citation was the one clear win, and it nearly did not happen

Searching a paragraph's *embedded citations* on their own — the words between a source
marker and ཞེས — finds passages whole-paragraph ranking cannot, because the shared span
is six or eight syllables inside two hundred and drowns. For p119 it returns Gyaltsab at
36,842 and Khedrup at 12,110; the gold quotes sit at 36,804 and 12,083. Both were misses
for every other method.

It first measured **0%**, which was a bug in my run-chaining, not a result. Worth
recording: a retriever that scores exactly zero is almost always broken.

### The alignment: a good idea that half worked

Every text here comments on the Abhisamayālaṃkāra and follows its order, so the
correspondence between the yig cha and a commentary should be monotone, and rare shared
shingles chained into a longest increasing sequence should give an alignment. 353 of 426
paragraphs were located verbatim in the yig cha's own file, all in increasing order, and
the chains built cleanly.

The result is **strongly bimodal and the bimodality is predictable from the texts, not
from the data**. Median error by commentary: 246 characters for the Ornament, 2,661 for
Gyaltsab, 3,109 for the gser phreng stod cha — against 273,218 for
དྲང་ངེས་རྣམ་འབྱེད་ཀྱི་སྤྱི་དོན and 858,800 for the Jagaddala commentary. The alignment
holds for texts commenting on the *same root in the same order* and is meaningless for
texts on a different root, which is obvious in hindsight and was not obvious to me before
measuring.

I tried to gate it on local anchor support so that unsupported guesses could be withheld.
**That failed:** median error is 7,536 characters with 20+ anchors nearby and 8,193 with
none, and the "within ±5k" rate is 40–47% regardless. Support does not predict accuracy,
so there is no honest confidence signal and the alignment is not shipped as a source of
passages. It is shipped only as a **ranking prior**, where it is worth about +5 points.

### The priors, measured

| priors | tune @20/30/50 | held out @20/30/50 |
|---|---|---|
| none | 43 / 49 / 54% | 48 / 55 / 58% |
| alignment | 46 / 46 / 56% | 53 / 56 / 63% |
| alignment + size | 46 / 48 / 55% | **53 / 58 / 63%** |
| alignment + size + tier | 43 / 48 / 53% | 53 / 58 / 63% |
| all three, stronger | 43 / 48 / 51% | 52 / 56 / 61% |

**Tier does not help retrieval.** This surprised me, and it is worth saying plainly
because the tier metadata is the most curated thing in the archive: it is what an analyst
should *weigh* evidence by, and it is not what *finds* the evidence. It is carried on
every candidate and excluded from the ranking. Size normalisation earns its place — a
3 MB commentary matches by accident more often than a 100 KB one.

### What was not tried, and why

**Embeddings.** Not bought, on the residual argument: the passages lexical retrieval
misses are mostly parallel treatments that the alignment prior and co-citation partly
recover, plus title-line and biography lookups that are not similarity problems at all.
Embedding 84 MB of OCR-damaged scholastic Tibetan — off-distribution for every embedding
model available — to chase a residual of that shape did not look like a good use of the
budget, and the reranking result below (§4) is evidence that off-the-shelf models handle
this material poorly. **This is a judgement, not a measurement, and it is the weakest
claim in this document.** If the human wants it settled, the honest experiment is to
embed only the tier-1 and tier-2 files (~8 MB) and score against the held-out gold.

---

## 2 · Verification

Verification is not a ranking problem and was never in doubt; it just has to be built so
that fabrication is impossible rather than discouraged.

`tools/verify.py` looks every quotation up again in the file it names and derives the
offset from that file. Comparison is by **syllable sequence**, not raw string, so that
edition differences in spacing and shad do not reject a real quotation — and a quotation
that is not there is refused with a message that tells the analyst to search or drop it,
not to work around it. The same fold is used by the index builder, so a passage that
retrieves will verify.

Measured on the worked example: 9 of 9 quotations verified exact, and the viewer's own
independent tooling then re-verified all 9 and filed them (`75 stored quotes, 0 wrong`).

### A hole I found in my own verifier, and one that is still open in the viewer's

I tested the guarantee rather than asserting it, by appending a fabricated line to the
worked example's quote file — well-formed, in the right register, and beginning with
syllables that really do occur in Gyaltsab:

> རྡོ་རྗེ་གཟེགས་མའི་གཏན་ཚིགས་ཀྱིས་མྱུ་གུ་དོན་དམ་པར་མི་སྐྱེ་བར་ལེགས་པར་གྲུབ་བོ། །

**My verifier accepted it**, as an "opening-run" match at offset 25512, with only a
warning. That is not good enough: the analyst's claim would have been attached to a
passage that does not make it, which is exactly the "sloppiness about who holds which
view" the brief calls a serious defect. Fixed: a partial match is now accepted only when
it covers **85% of the quotation's syllables and at least ten of them** — enough to
tolerate OCR damage at the tail, not enough to accept a real prefix with an invented
continuation. The line is now **refused**, and both worked examples still pass unchanged.

**The same test against the viewer's own `quotebank.py` shows it still accepts the
fabricated line.** Its locator falls back to matching the opening 72/56/40/28/24
characters, files the quote, and stores *the source's own reading at that offset* — a
different passage from the one claimed, presented under the analyst's attribution:

```
p80: 10 quotes filed under 6 commentaries
viewer stored p80-q10: YES   match kind: opening-run
  text it actually stored: རྡོ་རྗེ་གཟེགས་མའི་གཏན་ཚིགས་ལ་སོགས་པའི་རྟགས་ལ་བརྟེན་པའི་ཚད་མས་…
```

I have not touched the viewer repository, so this is a recommendation rather than a fix:
`Source.find` in the viewer's `tools/quotes.py` should require the same fraction before
returning a non-exact hit. Until it does, **the anti-fabrication guarantee lives in
`tools/verify.py` and depends on it being run before hand-over** — which is why the prompt
makes running it a condition of returning the files at all.

---

## 3 · The canon: I recommended against it, and I was wrong

The brief asks whether pulling sūtra and śāstra citations from the ~1 GB of
Kangyur/Tengyur/Sungbum measurably improves the analysis. Three pieces of evidence, and
they agree.

**Structural.** The viewer's locator only ever opens files in `Commentaries/`. A canon
passage cannot be verified or linked by the machinery that consumes this work, whatever
else is true about it.

**Historical.** All **157** quotations across the fifteen hand-made analyses come from
the 46 commentary files. **Zero** come from the canon. 112 of the first 113 are exact
matches, so this is not a story about the canon being hard to cite.

**Direct.** `experiments/exp12` extracted every explicit citation the yig cha makes —
1,797 of them, from 313 of the 426 paragraphs — and looked for each in both corpora:

| | |
|---|---|
| found in `Commentaries/` (84 MB) | 1,714 (95%) |
| found in the canon (1,004 MB) | 1,727 (96%) |
| found in both | 1,712 |
| **found only in the canon** | **15 (0.8%)** |
| found nowhere | 68 |

And the 15 do not survive inspection: they are short generic phrases —
`རྣམ་པ་ཐམས་ཅད་མཁྱེན་ཉིད་ལམ།།`, `ཤེས་རབ་ཀྱི་ཕ་རོལ་ཏུ་ཕྱིན་པ།` — matching in the Vinaya
and a tantra volume at the six-syllable threshold. They are coincidences, not citations.

On that I recommended shipping neither corpus. **The human overruled it, and the
correction is worth recording in full, because the mistake was in the experiment's
question rather than in its arithmetic.**

Coverage asks *can this citation be found somewhere*. The analyst's question is *whose
text is this*. Those come apart completely, and the worked example is the demonstration.
p80 cites བདག་ལས་མ་ཡིན་གཞན་ལས་མིན།…, and my retrieval found that verse in Tsongkhapa's
gser phreng, in Gyaltsab, and in Chökyi Gyaltsen's own Madhyamaka textbook — so it counted
as "already covered in `Commentaries/`" and contributed nothing to the 0.8%. It is
Nāgārjuna's, and it sits in the Tengyur at
`TD03824 … (Prajñā Nāma Mūla Madhyamaka Kārikā)`, character 378. **Attributing a verse to
the root text that contains it is a different scholarly act from attributing it to
somebody who quotes it, and a coverage count is blind to the difference.** Every
`ལས།`-marked citation in this text names a work; the point of the canon is to put the
analyst in that work.

What changed as a result:

- `Kangyur/`, `Tengyur/` and both Sungbum collections are committed — 964 MB on disk, but
  Tibetan text deflates about eight to one, so roughly **120 MB in the clone**. The human
  then generalised the requirement: *any* file in the archive used to obtain a quotation
  must be clickable in the viewer, so no collection is indexed that cannot also be
  reached.
- `tools/build_canon.py` precomputes, per paragraph, where each of its citations sits in
  the canon, and each pack carries a **Canonical sources** section naming work, section,
  volume and character offset.
- **The threshold is ten syllables, not six.** The 96% canon figure in the table above is
  itself mostly noise at six syllables — the Prajñāpāramitā volumes repeat formulaic
  phrases relentlessly, and within 600 files the six-syllable pass had already produced
  39,467 hits. At ten syllables, and keeping the longest match per *work* rather than per
  location, what comes back is citations.
- `tools/find.py --canon` and `tools/read_source.py` both reach into the canon, so a
  passage the precomputation missed can still be searched for and read live. Narrowed by
  section (`--in "DBU MA"`) that takes about 20 seconds.

**The viewer was then extended so a passage from any of these collections links like any
other quotation** — the
human lifted the read-only instruction and asked for it. The design and the five files
touched are in `SETUP.md` §9. The worked example now cites MMK 1.1 from the Tengyur
itself (`TD03824`, character 378) as `p80-q01`, and the viewer's own tooling files and
re-verifies it: `10 quotes filed under 7 commentaries`, `76 stored quotes, 0 wrong`.

---

## 4 · Reranking with a model: not worth its cost

The ceiling analysis (84% at rank 400 vs 58% at rank 30) made this the one place where
paying a model plausibly bought something. The economics work because the query set is
closed: one long-context call per paragraph, 426 calls, done once at build time.

(The baseline row is this experiment's own candidate list, generated with a wider context
window than the shipped packs use, so it sits a couple of points above the 53/58/63 in §1.
What matters is the *difference* each model makes to its own baseline.)

| model | held-out @20 | @30 | @50 |
|---|---|---|---|
| baseline (no rerank) | 55% | 58% | 65% |
| `gemini-2.5-flash-lite` | 48% | 50% | 53% |
| `qwen3.7-flash` | — | — | — |
| `gemini-2.5-flash` | 58% | 61% | 65% |
| `gemini-3.1-flash-lite` | 58% | 61% | 65% |

**The cheap tier makes it actively worse.** `gemini-2.5-flash-lite` scored all 100
candidates and cost 12 points of recall doing it. `qwen3.7-flash` mostly failed to emit
parseable output at all (0–2 of 100 candidates scored on most paragraphs); its apparent
"improvement" was the original ordering surviving untouched, and it is not a result.

**The mid tier gains +3 points and stops there.** Two independent models agree at
58/61/65, which is +3 at ranks 20 and 30 and **nothing at all at rank 50** — they promote
a few passages the priors had ranked 30th to 50th, and find nothing new.

Running that over 426 paragraphs would cost roughly **$4**, add a paid-API dependency to
the build, and buy three points that vanish at the budget the packs actually ship. **Not
adopted.** The reranking judgement belongs to Cowork, which is a far stronger model, is
reading the pack anyway, and is instructed to discard what does not bear on the argument.

---

## 5 · The rubric

The six section headings are **a hard contract, not a design choice**: the viewer's
checker requires them, in order, and rejects a document that is missing one. So "test
rubric variations" is bounded — the sections cannot move without breaking the reader.
What can change is the guidance inside them, and two changes are substantive:

- **The old rubric told the analyst the quotes arrive strongest-tier-first. They do not**,
  and they did not in the previous pipeline either — they arrive in match order. An
  analyst who believes the ordering is authoritative will over-weight whatever matched
  best, which is a mechanical fact about string overlap. Corrected, with the tier's real
  job (weighing evidence, not finding it) stated explicitly.
- **Section 3 now has the outline path and the Ornament lemma supplied**, resolved to
  exact offsets, instead of being reconstructed from memory. Where the pack has no lemma,
  the rubric requires saying the position is unclear rather than inventing one.

Also added: an explicit statement of how much the search actually finds (a little over
half), so that "the pack did not have it" is not mistaken for "it does not exist."

I did **not** run an A/B of analysis quality across rubric variants. With the sections
fixed by contract, the remaining variable is prose guidance, and a model-judged A/B on
three or four paragraphs would not have separated the variants reliably enough to be
worth $4–5 of the budget. That is a judgement about what the money would have bought, and
the human may disagree; the worked example is offered instead as the evidence that the
guidance produces work at the standard of the existing analyses.

---

## 6 · Precomputation vs. live work

Settled by measurement rather than taste. **Tibetan tokenises at about 0.83 characters
per token** — roughly 1.2 tokens per character, measured with the token counter, not
estimated. A pack at the first draft's size was 67,000 tokens, which is not a brief, it
is a book.

| | |
|---|---|
| pack size, as shipped | ~70 KB, **~31,000 tokens** |
| passages with context | 16, at 700 characters each |
| further leads, one line each | 40 |
| all 426 packs | 31 MB |

Everything that can be computed once is: the paragraph text, the neighbours, the outline
path, the lemma resolution, the anchor menu, the retrieval. What stays live is what
depends on judgement — reading around a passage before quoting it, searching for what the
pack missed, and verification.

---

## 7 · Failure modes

- **No candidate pool.** 29 paragraphs (p1, p2, p400–p426) have no counterpart in the old
  scan at all. They still get a pack: paragraph, neighbours, outline, anchor menu, and
  whatever the four retrievers find directly — which for p2 is a full pack, because the
  retrieval does not depend on the old pool. The pool is not used at all; it was rebuilt
  rather than laundered.
- **Nothing found.** The pack says so in a coverage note naming which tiers returned
  nothing, and the prompt's instruction is explicit: an analysis with no quotations passes
  the checker, and a short honest section beats a long invented one.
- **The tidy-pack risk** — that a neat brief makes Cowork stop looking. Three defences,
  all procedural: the pack is labelled as leads and states that it finds about half of
  what is needed; two live probes are *required* before section 3 can be written; and the
  coverage note makes silence visible. This is the risk I remain least able to
  demonstrate a fix for, because it can only be measured by running the whole set-up many
  times.
- **The anchor tiling**, which is the most likely mechanical failure, is removed by
  construction rather than checked: the pack ships clause spans that tile the paragraph,
  and anchors are built from runs of consecutive spans. Validation: **95% of the 320
  anchor endpoints in the fifteen hand-made analyses already fall exactly on these clause
  boundaries**, 13 of 15 paragraphs at 100%.
- **Positional quote ids.** `pNN-qMM` is assigned by position in the JSON array, so
  reordering the array silently re-points every link. The prompt requires freezing the
  JSON before writing the markdown, and the verifier catches unresolved links.

---

## 8 · What it cost

| | |
|---|---|
| OpenRouter, budget $9 | **$0.60 spent**, $8.40 unspent |
| — reranking trial, four models, 59 calls | $0.60 |
| Anthropic API (design conversation with Claude Fable 5, one turn) | $0.56 |
| token counting | negligible |

Nothing was spent to re-derive something a grep could settle: the candidate pool was
rebuilt rather than model-scored, the canon was answered by an index pass, and
verification is mechanical throughout. The budget is left largely unspent because the two
experiments worth buying both returned negative results, and the second one returned it
cheaply enough that there was nothing left to buy.
