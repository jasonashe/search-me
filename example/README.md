# Two worked examples

**`p119.md` / `p119.json` — hand-made.** Written and checked by a person before this
set-up existed, and copied here from the viewer repository. Its prose is unchanged; four of its eleven quote
entries referred to the old candidate brief by id rather than carrying the passage itself,
and those were resolved into the self-contained `file` + `text` form this set-up uses, so
that the example teaches the right shape. This is the quality
bar. Its section 3 does something worth studying: it observes that Haribhadra *does not*
raise the question the yig cha spends fifteen paragraphs on, which is an argument from
absence and is only available to someone who went and read the aligned passage.

**`p80.md` / `p80.json` — produced by this set-up**, working from `packs/p80.md` and
nothing else, following `COWORK-PROMPT.md`. It is the paragraph the brief names, and it
was never used to tune anything (`experiments/EVAL-SET.md`).

Both pass `python3 tools/verify.py`. `p80` was additionally merged into a copy of the
viewer repository, where the viewer's own independent tooling accepted it:

```
p80: 9 quotes filed under 6 commentaries
p80   17977 bytes   9 quotes  anchors cover 100.0%   all checks pass
75 stored quotes, 0 wrong
```
