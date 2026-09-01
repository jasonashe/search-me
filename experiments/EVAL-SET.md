# The evaluation set, fixed before tuning

Declared 2026-08-31, before any parameter of the retrieval was tuned. The numbers in
`experiments/exp01`–`exp04` were first runs on default parameters over *all* gold
paragraphs; from this point on, tuning happens on the tune split only and every headline
number is reported on the held-out split.

## Ground truth for retrieval (157 quotes, 15 paragraphs)

Every quotation the fifteen hand-made analyses actually used, with the commentary file and
character offset the viewer's own tooling verified. This is a **recall** benchmark only: it
says what a good analyst reached for, not what they could have reached for. A retrieved
passage that is not in the gold set is not thereby wrong, so precision cannot be scored
this way and is not claimed.

| split | paragraphs | quotes |
|---|---|---|
| tune | p1, p3, p5, p7, p9, p119, p121, p123 | 95 |
| held out | p2, p4, p6, p8, p10, p120, p122 | 62 |

The split is by paragraph, not by quote, so a paragraph's whole evidence problem stays on
one side of the line. It deliberately splits both runs (p1–p10 front matter, p119–p123
drang nges) across tune and held-out, because those two runs pose different problems: the
front matter identifies works and masters, the drang nges run argues a position.

## End-to-end evaluation set (10 paragraphs)

For judging the finished set-up, not retrieval alone. Chosen to span the text and to
include the cases the brief names.

| id | page | why it is here |
|---|---|---|
| p2 | 37 | front matter, lineage verses, **no candidate pool at all**; held-out gold |
| p6 | 41 | structural/outline passage; the runbook's own worked example; held-out gold |
| p10 | 44 | rich in quotation; held-out gold |
| p80 | 84 | the paragraph the brief names; mid-text, cites Nāgārjuna's root verses |
| p120 | 108 | dense argument, held-out gold |
| p122 | 109 | held-out gold |
| p200 | ~150 | no gold, mid-text, unseen |
| p300 | ~220 | no gold, later text, unseen |
| p410 | ~300 | **past the scan's coverage — empty candidate pool** |
| p426 | 322 | the printing colophon — expected to cite nothing at all |

The worked example delivered with the set-up will be one of the paragraphs that was never
tuned on.
