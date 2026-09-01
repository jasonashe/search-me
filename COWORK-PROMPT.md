Work in this repository. Write the analysis for **p80**.

*(Replace `p80` with whichever paragraph you want. Everything below is written to
work unchanged for any id from `p1` to `p426`.)*

---

## What you are producing

Exactly two files, returned **in the chat**. Nothing else — no status notes, no
scratch files, no logs, no summaries written to disk.

| file | what it is |
|---|---|
| `p80.md` | the analysis, in the six sections of `analysis_rubric.md`, with `<!--line a-b-->` anchors in section 2 |
| `p80.json` | the quotations the analysis uses, in the shape below |

Both go straight into a viewer application that already exists, so their shape is
a contract, not a preference. `tools/verify.py` checks both against that contract
and you must not hand anything over until it passes.

## Before anything else

Read, completely:

1. **`packs/p80.md`** — the evidence pack for this paragraph. It has the
   paragraph itself, the two either side, its place in the text's own sa bcad,
   the Ornament lemma its section is commenting on, **where the sūtras and
   śāstras it quotes live in the canon and the collected works**, the anchor menu, and the
   passages an offline search found. It was built by reading the sources, so
   everything in it is really in the file it names.
2. **`analysis_rubric.md`** — what an analysis contains. It is the authority on
   the six sections and their headings.
3. **`example/p119.md`** and **`example/p119.json`** — a finished analysis written
   and checked by a person, before this set-up existed. Match that depth, that
   use of sources, that format. (`example/p80.*` is the same thing produced by
   this set-up; read `example/README.md` for what each one is for.)

Then open the chat by quoting the paragraph's **first clause in Tibetan** and
naming its page, before you analyse anything. If that is not the passage the
human meant, they find out in one line rather than after merging. *(This matters:
an older segmentation of this text is still in circulation in which the ids are
shifted — `p80` here is not `p80` there.)*

## The procedure

### 1 · Read the paragraph and its neighbours

Section 1 of the rubric asks what precedes and what follows. Say what they
actually contain. "The preceding discussion" is not an answer, and the pack gives
you both neighbours in full so there is no excuse for one.

### 2 · Read around every passage you intend to use

The pack gives each passage with an offset and a short window. **That window is
for triage, not for quoting.** Before you use a passage, open it:

```sh
python3 tools/read_source.py "སེང་གེ་བཟང་པོ་_འགྲེལ་པ་དོན་གསལ།.txt" 3732
```

You are asking one question: *does this passage actually bear on this paragraph?*
The pack says how a passage was found — shared wording, shared subject, the same
citation, the corresponding place. That is a mechanical fact and says nothing
about whether it bears on the argument. Roughly half of what an automated search
surfaces does not, and reading a page either side settles it in a minute.

Keep a passage when it does one of these:

- states the position this paragraph states, from a named master
- states a position this paragraph is refuting, so the opponent can be named
- disagrees with the paragraph — which is what section 5 exists for
- supplies the root verse, sūtra passage or lemma the paragraph is citing

Drop it otherwise, silently. Five quotations that carry the argument beat twenty
that decorate it. Do not argue with the search in the text of the analysis.

**Two probes are required, not optional.** Before you write section 3, open the
lemma offsets the pack gives — the Ornament and Haribhadra's འགྲེལ་པ་དོན་གསལ།
at the aligned place — and read them. What Haribhadra does *not* raise there is
as reportable as what he does, and you cannot say either from an excerpt.

### 3 · Attribute canonical citations to the canonical text

When the paragraph quotes a sūtra, a tantra or an Indian śāstra — anything
introduced with ལས། or ཞེས་གསུངས — the pack's **Canonical sources** section
tells you where that passage actually lives in the Kangyur, the Tengyur or the
Sungbum collections, with the work, the volume and the character offset. Open it
and cite it from there:

```sh
python3 tools/read_source.py "TD03824" 378
```

**This matters and it is easy to get wrong.** A verse of Nāgārjuna's is very
often quoted by Tsongkhapa, by Gyaltsab and by Chökyi Gyaltsen too, and the
retrieval will happily hand you all three. Attributing the verse to a commentary
that quotes it, when the root text is right there, is exactly the kind of
sloppiness about who says what that this work cannot afford. Name the work whose
words they are.

If the pack found nothing for a citation, search:

```sh
python3 tools/find.py "བདག་ལས་མ་ཡིན་གཞན་ལས་མིན" --canon --in "DBU MA"
```

Narrow it with `--in` — the section names are in the pack's canonical-sources
lines, and unfiltered that is nearly a gigabyte and takes minutes.

**Every source in this archive is quotable and every one links.** Put such a
passage in `p80.json` with the **full path** as the `file`, exactly as the pack
gives it:

```json
{ "file": "Tengyur/04 DBU MA_Middle Way School (Madhyamaka)/VOL 1 (TZA)/TD03824_DBU MA RTZA BA'I TSIG LE'UR BYAS PA SHES RAB CES BYA BA (Prajñā Nāma Mūla Madhyamaka Kārikā)_unicode.txt",
  "text": "…", "citation": "…", "why": "…" }
```

A commentary keeps its bare filename; anything else carries its path from the
collection down — `Kangyur/…`, `Tengyur/…`, `Sungbum/…`,
`རྗེ་ཙོང་ཁ་པ། ཡབ་སྲས། Sungbum/…`. All of them verify, all of them link, and the
viewer opens all of them.

A passage in the canon may be quoted there rather than original there. If a
citation turns up in four works, say which one you take it to belong to, and why.

### 4 · Find what the pack is missing

The pack is what an automated search found. It is not a survey, and measured
against fifteen hand-made analyses it finds a little over half of what a good
analyst reaches for. **Expect to search for yourself**; a batch in which you
found nothing by hand is a batch you did not work at.

```sh
python3 tools/find.py "སྟོང་པ་ཉིད་སྨོས་པའི་རྣམ་པས"
python3 tools/find.py "རྒྱལ་བའི་ཡུམ་རྣམ་པ་གསུམ" --in "འགྲེལ་པ་དོན་གསལ"
```

Search **short distinctive phrases**. These files carry OCR damage and a long
string will miss where a six-syllable one hits.

**Never write a Tibetan quotation from memory.** Not a root verse you are sure
of, not a line of Haribhadra you have read a hundred times. Search for it; if the
search finds nothing, write that the source was not located. That sentence is a
finding. A remembered quotation is a fabrication even when it happens to be
right, because nobody downstream can tell the difference.

### 5 · Freeze the quote file first

Write `p80.json` **before** you write the links in the analysis. Quote ids are
**positional**: the first entry of the array is `p80-q01`, the second `p80-q02`,
and so on. Reorder the array afterwards and every link in the analysis silently
points at the wrong quotation.

```json
{
  "paragraph": "p80",
  "quotes": [
    {
      "file": "ཙོང་ཁ་པ་བློ་བཟང་གྲགས་པ་_ལེགས་བཤད་གསེར་ཕྲེང་སྟོད་ཆ།.txt",
      "text": "the passage, copied from what tools/read_source.py printed",
      "citation": "ལེགས་བཤད་གསེར་ཕྲེང་། — where in that work, in your own words",
      "why": "One sentence, for the reader, on what this quotation is doing here."
    }
  ]
}
```

- `file` — exactly as it appears in `Commentaries/`.
- `text` — **copied from the source**, never retyped from the pack summary and
  never from memory. It is looked up again when you verify.
- `why` — shows in the viewer's source panel, so write it for a reader.

### 6 · Write the analysis

`p80.md`, following `analysis_rubric.md`, with its six headings in order.

**Anchors.** Section 2 translates the paragraph clause by clause, and each unit
carries the anchor for the span it translates. The pack gives you an **anchor
menu**: the paragraph split into clause spans with exact offsets, which tile it
exactly. Build each anchor from a **run of consecutive spans** — the first
span's start, the last span's end — and use every span exactly once, in order:

```markdown
<!--line 8-102-->
> **དོན་དམ་བདེན་པ་དངོས་བསྟན་བསྟན་བྱའི་གཙོ་བོར་བྱས་ནས་སྟོན་པའི་མདོ། ངེས་དོན་གྱི་མདོའི་མཚན་ཉིད་དང་།**
>
> a sūtra that teaches by making ultimate truth the principal object of
> exposition among what it explicitly teaches is the definition of a
> definitive-meaning sūtra;
```

Done that way the anchors cannot gap, overlap or overrun — which is the failure
the checker catches most often when they are counted out by hand. **Do not
compute offsets yourself.** Group a whole quoted verse as one unit, not four.
Anchors appear **only in section 2**; one anywhere else competes with section 2's
and lands the reader on the wrong line.

**Links.** A quotation becomes clickable like this:

```markdown
[རྟེན་དང་དབང་དུ་བྱ་བ་དང་། ། ལས་ནི་སྒོམ་པ་དང་བཅས་པ།](quote:p80-q03)
```

Link the Tibetan when you are showing the quotation; link a few English words
when you are describing it. Both work.

### 7 · Verify, and do not hand over until it passes

```sh
python3 tools/verify.py p80
```

It looks every quotation up again in the file it names and derives the offset
from that file. **A quotation it cannot find is refused.** Do not work around a
refusal — either find the real passage with `tools/find.py` and use what that
returns, or drop the quotation and say the source was not located. It also
checks the six sections, the anchor tiling and the links.

Fix and re-run until it passes. Then return the two files in the chat.

## What "good" looks like

- **Name who holds what.** Never "some commentators hold". Name the master, name
  the text, and say how far that text stands from this curriculum. "Gyaltsab Je,
  within the same Gelug transmission" and "an Indian commentary at some remove
  from this yigcha" are different kinds of support.
- **Use the tiers as weight, not as truth.** Lead with the strongest tier that
  says the thing. But where texts genuinely conflict, **report the conflict** —
  never resolve it silently by preferring the higher tier. That conflict is what
  section 5 is for.
- **Say where it sits.** Section 3 wants four locations: the root verses,
  Haribhadra, this text's own outline, and the argumentative role. The pack gives
  you the outline path and the lemma; the rest you read for yourself. Where a
  passage has no counterpart in the Indian commentaries — common in the
  preliminaries, which are a Tibetan addition — say so, and say what it implies.
- **Say when the evidence is thin.** If the whole case rests on tier 4 and 5
  material while the yig cha tradition is silent, write that down. It is a
  finding about the passage, not a defect in your work.
- **Say when you are unsure.** A passage whose place in the outline is genuinely
  unclear should be marked unclear. An analysis that reads uniformly confident is
  less useful than one that marks its own edges.

### When the pack is thin or empty

Some paragraphs have no passages at all — the title page, the salutation verses,
the colophon, and everything the earlier scan never covered. The pack says so
plainly, and the coverage note tells you which tiers returned nothing.

Treat them identically, except that step 3 does all the work: read the paragraph,
identify what it cites or alludes to, and search for each thing. If a paragraph
genuinely cites nothing — colophon verses, for instance — write the analysis
without quotations and say in section 4 that the passage is not one the
commentarial literature engages. That is true and worth knowing.

**Do not pad.** An empty pack is not permission to fill the space with
plausible-sounding attribution. An analysis with no `quote:` links passes the
checker, and a short honest section beats a long invented one.

## Signs the work has gone lazy

- section 5 says the passage is uncontroversial, for a paragraph that opens
  ཁ་ཅིག … ཞེས་ཟེར་ན
- section 6 defines ཕྱིར or ཐལ — the rubric says skip vocabulary a Sera Jey monk
  already knows
- the analysis uses only the first two or three passages in the pack
- section 2 has three anchors for a two-thousand-character paragraph
- nothing was found by your own search
- a verse of Nāgārjuna's or a line of a sūtra is attributed to a commentary that
  quotes it, when the pack names the canonical work it belongs to
- section 3 asserts a position in the outline that the pack did not give you and
  you did not check
