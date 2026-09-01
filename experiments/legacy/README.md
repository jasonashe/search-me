# Superseded tools

These are the scripts the archive arrived with. They are kept so the experiments in
`experiments/` can be re-run and so the reasoning can be retraced — not because the
set-up uses them.

- `candidates.py` — built a brief from the 50,000-candidate pool in `quotes/`, re-checking
  each against its source. The set-up does not use the pool at all: retrieval was rebuilt
  from the commentaries rather than laundered, so the pool's 4-in-5 error rate stops
  being something to manage. `experiments/gold.py` still imports `quotes.py` from here.
- `quotes.py` — the viewer's locator. `tools/verify.py` replaces it, comparing syllable
  sequences rather than folded strings so that edition differences in spacing and shad do
  not reject a real quotation.
- `quotebank.py`, `explanations.py` — the **viewer's** tools, not this repository's. They
  run on the human's side after merging, and they assume viewer paths. They are the
  contract this set-up writes to; do not run them here.
- `resegment.py`, `drive_export.py`, `electron-smoke.js`, `test.js` — belong to the
  viewer's own build and delivery, and are out of scope here.
