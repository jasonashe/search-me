# Lorig Defender Harness

A self-contained Tibetan Buddhist debate arena: a hardened AI **Defender**
("Damcawa") that debates in strict Tibetan debate form (rigs lam,
consequence style) on Purchok Jampa Tsultrim Gyatso's *Lorig*
(*Blo rig gi rnam bzhag*, "Awarenesses and Knowers"), plus the deterministic
referee and fact base that judge every move.

The Defender in this package is **defender_v10** — the current version from
a 35-iteration adversarial evolution loop in which Challenger agents tried
to trap it into contradicting its own concessions, the root thesis, or
Purchok's text. It survived iteration 35 (six matches) with no violations,
no contradictions, and no upheld Khor lo! / Tsa! against it.

**The challenge:** play the Challenger against this Defender and win —
where "win" is defined mechanically by the referee (see *What counts as a
win* below), not by anyone's impression of the debate.

## Contents

| Path | What it is |
|---|---|
| `agents/defender_v10.md` | The Defender's complete instructions (system prompt). This is the opponent, unabridged. |
| `harness/referee.py` | Deterministic referee, v2.3 (Python 3, standard library only). Validates move syntax, evaluates minor premises and pervasions against the fact base, maintains the Defender's concession ledger, judges Khor lo! / Tsa! calls, and scores the match. |
| `harness/justification.py` | Referee support module (scores the Defender's per-turn justification payloads when a transcript carries them). |
| `knowledge/facts.json` | The fact base: canonical subjects and predicates (exact strings), `is_a` facts, pervasions (with counterexamples where a pervasion is false), set relations, non-existent subjects. |
| `knowledge/matrix.md` | The taxonomy of awarenesses and knowers: definitions and divisions, each quotation verified against the etext at recorded character offsets. |
| `knowledge/definitions.json` | Definitions of 24 terms in clause form (definiens, divisions, illustration). |
| `knowledge/glossary_tibetan.json` | Tibetan stems of the canonical terms, used by the referee to verify quotation moves. |
| `knowledge/quote_registry.json` | 153 pre-classified spans of the etext used to settle whether a quoted consequence stands in Purchok's own voice or an opponent's. |
| `sources/S06857E4_blo_rig.txt` | Purchok's *Lorig* itself — the Unicode Tibetan etext (public-domain historical text). The ground truth of the debate. |
| `examples/example_match_defender_survives.json` | A complete moves-only transcript of a real match the Defender survived, in referee format. Use it to test your installation (see below). |
| `CHALLENGER_PROMPT.md` | A ready-to-paste prompt that turns any capable LLM into the Challenger, with the complete rules, move forms, vocabulary and win conditions — and no strategy advice. |

Deliberately **not** included: the evolved Challenger prompts, the
Challenger's debate archive, and the fault-line analyses produced during
the evolution loop. Those are one particular Challenger's accumulated
strategy. This package gives a new Challenger the rules, the text, and the
fact base — finding the winning line is its own work. (Napper's English
translation of the *Lorig*, used as a secondary reference during the loop,
is a modern copyrighted translation and is likewise not redistributed
here; the Tibetan etext above is the ground truth.)

## Quick test

Requires Python 3, nothing else.

```
python3 harness/referee.py score examples/example_match_defender_survives.json
```

Expected headline result (last line of the output):

```
== iter035-match2-moves-only-example: compliance 1.0 | fidelity 1.0 | ledger 1.0 | trap 0.0 | contradictions 0 | valid C4 0 | longest chain 0
```

## How to run a debate

You need two separate conversations (two chats, or two agents), so that
neither side sees the other's private reasoning:

1. **Set up the Defender chat.** Give it `agents/defender_v10.md` as its
   system prompt / project instructions, word for word, unedited. Then
   send it a brief in this form:

   > Root thesis: the subject, [SUBJECT], is [PREDICATE]. You uphold this
   > thesis. The Challenger will open. Answer each Challenger move with
   > your payload followed by your move, exactly as your instructions
   > specify.

   A standard root thesis (the one used in the loop's free matches) is:
   *the second moment of an omniscient exalted wisdom is a prime
   cognizer.* Any subject/predicate pair from `knowledge/facts.json` can
   be used; the Defender upholds the thesis as stated.

2. **Set up the Challenger chat.** Paste `CHALLENGER_PROMPT.md` into a
   separate conversation (for example, a fresh Claude chat), together with
   access to this repository's files.

3. **Relay the moves.** The Challenger moves first. Copy each side's
   **move text only** to the other chat:
   - From the Challenger: its whole reply is move text — copy it as-is.
   - From the Defender: copy only the move (the plain-text response its
     instructions define), **not** its JSON payload, state, or reasoning
     blurb. Those are the Defender's private record; the Challenger must
     play from the public moves alone.
   - Never edit, paraphrase, or "helpfully" reformat a move in transit.
     The exact wording is what the referee judges.

4. **End of match.** A match lasts at most 24 turns (12 moves each) unless
   a win occurs earlier. When it ends, assemble the transcript (format
   below), score it with the referee, and read the verdict from the
   referee's output — see *What counts as a win*.

## Transcript format

```json
{
  "match_id": "my-match-1",
  "topic": "free debate",
  "root_thesis": {"subject": "the second moment of an omniscient exalted wisdom",
                  "predicate": "prime cognizer"},
  "match_type": "A",
  "turns": [
    {"turn": 1, "role": "challenger", "text": "<move text only>"},
    {"turn": 2, "role": "defender",   "text": "<move text only>"}
  ]
}
```

Score it with:

```
python3 harness/referee.py score <transcript.json>
```

The referee prints a full JSON report followed by a one-line summary:
rule compliance, textual fidelity, ledger consistency, trap complexity,
the number of ledger contradictions, and the number of valid C4 calls
(Khor lo! / Tsa!).

## The debate in brief

**Challenger moves** (plain text only, exactly these forms):

- **C1** — "The subject, [X], it follows that it is [Y]."
  (negated forms allowed; a bare conditional "If something is [Z], it
  follows that it is necessarily [Y]." is also a C1)
- **C2** — "The subject, [X], it follows that it is [Y], because of being [Z]."
- **C3** — "Posit an example." (only immediately after "Reason not
  established" or "No pervasion", and in exactly these words)
- **C4** — "Khor lo! …" (the Defender's latest move contradicts its own
  earlier concessions) or "Tsa! …" (it contradicts the root thesis or
  Purchok's text) — in both cases **followed by a demonstration** naming
  the earlier concession and the contradicting statement.
- **C5a / C5b** — escape-challenges, legal when the Defender has accepted
  a thesis for one subject and denied the parallel thesis for a parallel
  subject: C5a demands the difference between the two subjects; C5b
  demands the Defender's reason for the denial. (Exact forms are in
  `CHALLENGER_PROMPT.md` and in the Defender's instructions.)
- **C6** — the quotation move: quoting Purchok verbatim (with the passage
  recorded in the transcript's `text_cite` offsets) to repair a pervasion
  or minor premise the Defender has just denied. A pervasion counts as
  established by quotation only if the consequence stands in Purchok's
  own voice, not in an opponent's assertion.

**Defender responses:**

- to C1: `Accept` (if the thesis is true, or already entailed by its
  concessions) or `Why`
- to C2: `Accept`; `Already accepted`; `Reason not established. [X] is
  not [Z].` (the minor premise is false); `No pervasion. If it is [Z], it
  is not necessarily [Y].` (minor premise true, pervasion false)
- to C3: posit the example it is committed to
- to C4: `Accept` if the demonstrated contradiction is genuine; if it is
  unfounded, repeat its previous valid response verbatim
- to a malformed move: `State your thesis or reason in valid debate form.`

**Ledger rules both sides play under:**

- The Defender is bound by its own concessions (dam bca'), explicit and
  implicit, even against the text.
- "No pervasion" implicitly concedes the minor premise.
- A "Reason not established" answer to a negated reason asserts the
  positive core ("[X] is [Z]"), and that assertion is a concession.
- Accepting a bare conditional concedes both the pervasion and its
  contrapositive.
- **The automatic-Tsa rule:** if the Defender answers `Accept` to a C2
  whose thesis contradicts the root thesis or Purchok's text, that Accept
  is itself the loss — no C4 call is needed.
- Non-existent subjects (a rabbit's horns, the son of a barren woman, a
  sky flower, …) take every negative predicate and no positive one.

**Vocabulary discipline:** the referee can only evaluate subjects and
predicates that appear, in their exact canonical strings, in
`knowledge/facts.json` (`canonical_subjects`, `canonical_predicates`).
Moves phrased in other wording may be legal debate, but they score as
unevaluable and cannot produce a referee-valid win.

## What counts as a win

The Challenger wins if and only if the referee's report on the final
transcript shows at least one of:

1. `valid_khorlo_tsa_count` ≥ 1 — a Khor lo! or Tsa! the referee upholds:
   the Defender's move contradicts the closure of its own concession
   ledger (Khor lo!), or entails the negation of the root thesis /
   directly contradicts Purchok's text as recorded in the fact base
   (Tsa!);
2. a recorded forced-Accept failure / ledger contradiction produced by
   the Defender answering `Accept` to a reasoned consequence (C2) whose
   thesis contradicts the root thesis or the text (the automatic-Tsa
   rule);
3. `epistemic_forfeit: true` in a transcript that carries the Defender's
   justification payloads (its stated reasoning failed the referee's
   justification checks outright).

Anything else — including a debate that merely "looks" lost, a Defender
answer someone judges wrong without a referee finding, or a win claimed
on non-canonical wording the referee cannot evaluate — is not a win.
If the 24 turns end without one of the above, the Defender has survived;
report that honestly.

## Background

The Defender was hardened over 35 iterations: Challenger versions were
mutated after every iteration, a deterministic referee replaced
impressionistic judging, and design changes were worked out with an
external engineering consultant. Its known biography in one line: the
only Defender loss between iterations 2 and 35 was a single match in
iteration 11, against a predecessor version; defender_v10 itself has
never lost. The full iteration log lives in the parent project and is not
needed to use this package.
