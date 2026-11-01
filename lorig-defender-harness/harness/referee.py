#!/usr/bin/env python3
"""Referee harness v2.3 for the Lorig debate arena (deterministic, stdlib only).

v2.3 (2026-10-28): the Challenger debate archive (Part 5 of the
user's redesign; Argon consultation 012, with the coordinator
adaptations recorded there governing). A Challenger turn may carry
an "archive_ref" (entry id, step index, mode, substitution map,
detector) claiming the move replays a stored debate from
knowledge/debate_archive.json. The referee verifies the ref: the
entry exists; the step index is in range (a summary-only entry
admits only a CONFIRM_POSITIVE_ANCHOR); the stored step's template,
instantiated under the substitution map (unmapped slots fall back to
their bound values), parses to the same move (kind, subject,
predicate, reason) as the turn played; and every substituted subject
slot stays inside the entry's transferable divisions (the
substituted subject's fact-base ancestors must meet the entry's
applicability list; an entry listing no divisions admits no subject
substitution). An invalid ref is NOT a violation — it is recorded in
the report's "archive_use" block and the turn scores normally. A C5
whose escape_ref carries "archive_entry" with t_pos null claims its
positive side from the bank instead of this match's ledger and is
verified under the two-tier ruling: Tier 1 direct arming requires
the archived atom in the entry's ledger snapshot, version continuity
(the transcript's defender_version is among the versions the entry
troubled) OR the atom standing in the Defender's first payload state
snapshot, and no intervening revision defeating a node that names
the pair. A Tier-1 pass records the episode with mode "ARCHIVE" and
arming "ARCHIVE_TIER1" and proceeds through the ordinary answer
machinery; a failure takes the ordinary unfounded path with arming
"ARCHIVE_FAILED". The "archive_use" block (refs with per-ref
verdicts, cross-match C5 log, the count of transcript-level
"archive_consultations") appears only when a ref or an archive-armed
C5 occurs, so transcripts without archive use score bit-identically
to v2.2. The bank path is a monkeypatchable module constant with a
resettable cache, like the v2.2 registry/glossary; a missing bank
makes every check "unverifiable" (refs invalid, Tier 1 failed)
without violations.

v2.2 (2026-10-28): the quotation move C6 (Part 4 of the user's redesign;
Argon consultation 011, with the coordinator adaptations recorded
there governing). A C6 is an authority move legal ONLY as a repair:
pervasion-repair after a "No pervasion" answer, minor-premise repair
after a "Reason not established" answer — including when the answered
consequence is a refutation C2 inside an open Part 3 escape episode,
which the adjacency rule covers because a refutation consequence is
an ordinary C2 answered by an ordinary denial. The C6 turn carries a
text_cite (the Tibetan passage, verified against the etext) and a
quote_claim (repair target, target turn, subject/predicate/reason,
voice claimed, inference mode). Deterministic layers: (a) substring;
(b) consequence markers by inference mode (an implicit-consequence
claim needs thal + phyir/pa markers, an explicit-pervasion claim a
khyab term) and term presence — the quote is transliterated to Wylie
with the built-in transliterator below and searched for the glossary
stems of the claimed reason/predicate (plus the subject for
minor-premise repairs), because knowledge/glossary_tibetan.json's
stems are Wylie strings, and its keys are matrix.md headings that may
carry parenthetical qualifiers (the lookup is tolerant: exact key,
key-base before " (", claim-base before " ("); (c) voice — a
pre-classified span of knowledge/quote_registry.json overlapping the
cite (OWN verifies the voice; OPPONENT_FRAMED / OPPONENT_BOUND /
DENIED are known-opponent; CONTESTED is contested), else a window
scan of [start-400, end+300] (a downstream pervasion-denial settles
it as denied; upstream "some say" framing without rang lugs makes it
opponent-framed; rang lugs upstream makes it own). Failures at (a) or
(b) are MIS_CITATION; a failed context check is INVALID_CONTEXT with
no cascade and no fidelity item. The Defender answers with exactly
three forms — Accept-the-quotation (the pervasion, and for
pervasion-repair the cascaded thesis, enter the ledger tagged "C6
text-established" via the usual ledger machinery; accepting a
known-opponent / window-denied span or a factually false pervasion is
an OVER_ACCEPTANCE), an opponent-voice claim (void without a verified
context_cite in the window or containing both terms' stems; a
deterministically settled voice decides the episode on the spot), or
an interpretation (riding the sense-ruling channel: cap 2 per match,
a second needs a verified contrast cite, and a TERM_SENSE_SHIFT
modifier claimed in the payload must actually occur in the span).
Contests the deterministic layers cannot settle stay PENDING_JUDGE
for the blind judge pass; a Defender who closes a deflection by
Accepting after the refutation turn has its deflection recorded as
failed (UPHELD_AFTER_REFUTE, cascade). Caps: two C6 per match, and a
span may not be re-quoted (>50% overlap) for the same pervasion. The
report gains a "quote_episodes" block only when a C6 is attempted;
transcripts without C6 score bit-identically to v2.1.

v2.1 (2026-10-28): escape-challenges (Part 3 of the user's redesign;
Argon consultation 010, with the coordinator adaptations recorded
there governing). Challenger moves C5a (difference-demand) and C5b
(reason-demand) challenge a distinction the Defender used to escape:
an asymmetric pair in the match's own ledger — (S_pos is P) accepted
(an Accept, an NPV-conceded minor premise, or an RNE assertion) while
(S_neg is P) stands denied (a Why, an RNE/NPV refusal of that thesis,
or an Accept of the negated thesis) — under a taxonomic proximity
guard; a single RNE / sense-ruling turn is a Mode 3 pair by itself.
The challenge turn names its pair in the transcript field
"escape_ref". Defender answers: D-Diff (a canonical difference D —
S_pos has it, S_neg lacks it, D relevant to P by the payload-declared
route SUFFICIENT / NECESSARY / DEFINIENS_CLAUSE), D-Reason (a reason
for the denial's thesis, locked like a type B reason), D-Concede (the
distinction is withdrawn; the denied thesis counts accepted) and
D-Unfounded (available only when the pair is not in the ledger;
answering it to a founded challenge is a Defender violation, and an
unfounded challenge is a Challenger violation). D-Diff / D-Reason
lock their claims into the ledger (sources "D-Diff" / "D-Reason")
and fold into textual fidelity as single fractional items (D-Reason
as the 0.5/0.5 minor/pervasion split); a non-canonical D scores 0,
and any fault-line-contested field reports "contested" and leaves
the item unscored. Episodes close CONCEDED / REFUTED (a window
Accept contradicting the locked claims, or a DISTINCTION_WITHDRAWAL
revision in the window) / EPOS_RETRACTED (the withdrawal retracts a
positive entry while the denied entry is the root thesis) / STOOD,
with the revision charge cross-checked against the payloads. Cap:
two challenges per match, refunded only by an immediate concession;
a pair that stood is locked against re-challenge. The report gains
an "escape_challenges" block only when a C5 move occurs; transcripts
without C5 moves score bit-identically to v2.0.

v2.0 (2026-10-28): match types B and C (Part 2 of the user's redesign;
Argon consultation 009, with the coordinator adaptations recorded
there governing). A transcript may carry "match_type": "B" or "C"
(absent = "A"). For B/C, turns 1-2 follow the opening grammar — B:
Challenger demand "Establish the thesis: the subject, [S], is [P].
State your reason." / Defender reason statement "The subject, [S], is
[P], because of being [R]."; C: Challenger demand "State the meaning
of [T]." / Defender three-line meaning (Definiens / Divisions /
Illustration) — and are scored by the dedicated report blocks type_b /
type_c instead of the standard fidelity paths; standard scoring
resumes from turn 3 with the opening commitments injected into the
ledger (B: minor premise, pervasion, thesis, in that order; C:
illustration atom, then one atom per stated division — sources tagged
so telemetry treats them as explicit Defender acts). Type B turn-1
fidelity splits into minor-premise and pervasion halves evaluated
against stated facts plus the horn-clause closure (Facts.eval_atom_full
/ eval_pervasion_full, compiled as in harness/discrepancy_probe.py);
the logged challenger_prep receipt is re-validated with the same
semantics harness/prep_check.py uses pre-match. Type C turn-1 scoring
is clause recall/precision against knowledge/definitions.json plus an
illustration-truth check. Any turn (any type) may carry a text_cite
{start, end, quote}, verified against sources/S06857E4_blo_rig.txt;
verified cites are listed in report["text_cites"] (the key is omitted
when no cite exists) and an unverified cite is a rule-compliance
violation. ALL legacy behaviour is bit-identical for type A
transcripts, with and without defender payloads.

v1.9 (2026-10-28): deterministic justification scoring (Part 1 of the
user's redesign; Argon consultation 008, Stage A — the LLM-judge stage
is wired in with Part 2). Defender prompt v6 emits a private JSON
payload per turn (EpistemicState snapshot + derivation blurb), carried
in transcripts as turn["defender_payload"]. When a transcript carries
at least one payload, harness/justification.py scores them (DET_1-4,
state-diff audit, revision accounting) and the report gains four
additive fields: justification_detail, justification_det,
hard_justification_failures, epistemic_forfeit. Payloads never feed
the four legacy metrics, and payload-less transcripts produce
bit-identical values in every pre-existing field (the new fields just
take their null/zero defaults).

v1.8 (iteration 20, 2026-10-28): bare conditional C1 parsing — a
Challenger move of the form "If it is X, it follows it is Y." parses
as kind C1_COND (a pervasion thesis, not an atom thesis). This is the
form challenger_v19's T32 prescribes and defender_v4's
Pervasion-Acceptance Audit already treats as a C1; v1.7 flagged it
malformed, which cost iteration-20 match 1 two compliance turns
(turns 21–22) for a purely formal reason. An Accepted C1_COND enters
the ledger as a conceded pervasion (polarity rules as for a C2
Accept); a "Why" denies it. C1_COND is kept out of the atom-scoring
paths (challenger fidelity, telemetry, forced-Accept detection).

v1.7 (iteration 18, 2026-10-28): FL_01 sufficiency pattern restricted to
the incomplete 3-limb wording (see Facts.fault_line_pervasion); a
complete 4-limb wording carrying the other-knower limb is no longer
matched as the contested pervasion.

v1.6 (iteration 15, 2026-10-27): the four-valued fault-line lattice
(Argon consultations 006 §3 and 007 §2). Three fault-line nodes are
recognised by term patterns (documented in knowledge/facts.json's
fault_lines block and in Facts.fault_line_pervasion / fault_line_atom):
FL_01 (mental-perception definition completeness — the sufficiency
pervasion from the worded definiens, and the exclusion pervasion
"mental direct perceiver -> not self-knower": branch A LITERAL_3LIMB,
branch B CONTEXTUAL_4LIMB), FL_02 (the unmixed-ascertainment bridge:
A KHEDRUP_JETSUN_VERSE, B PURCHOK_ENGAGEMENT_QUALIFIER), FL_03 (the
self-knower's dominant condition: SILENT_DOCTRINAL). A Defender
response that asserts a contested pervasion's value LOCKS that fault
line's frame for the match (first-touch commitment) and scores
correct on the locking turn; a later assertion against the locked
value scores fidelity-incorrect and is recorded in frame_flips.
Challenger assertions of a contested pervasion evaluate under the
locked branch once bound, else under the static base. FL_03: denying
a positively-stated silent atom (Why on the C1, or RNE on the minor
premise) is fidelity-correct; asserting one (RNE on a negated reason)
stays unscored — a voluntary ledger concession, excluded from the
denominator, per Argon 007. Coordinator's deviation from Argon 007's
letter, recorded deliberately: a cross-frame assertion is NOT also
appended to contradictions[] — in the only corpus case (iter015
match 1, turn 24) the flip-shaped move is a gate blemish against a
locked-frame-true pervasion, already priced by fidelity, and the
ledger score keeps measuring concession clashes only. Two additive
report fields support the audits: fidelity_turns (every fid() call
with its turn) and frame_locks / frame_flips. Legacy scores are
unchanged on every turn that touches no fault line (verified by the
full-corpus rescore diff against v1.5).

v1.5 (iteration 13, 2026-10-27): RNE fidelity symmetry fix (Argon
consultation 005). The D_RNE branch scored its fidelity as
fid(eval_atom(minor) is False): when the fact base cannot evaluate the
minor-premise atom (None — a coverage gap), the boolean was False and a
correct denial was counted INCORRECT, while the D_NPV branch passed
None through unscored. Iteration-13 match 3 measured the cost exactly:
defender_v5's line beat the dossier gold line (ledger 1.000 vs 0.917)
yet scored fidelity 0.400 vs gold's 0.571, the whole gap being three
trained RNE denials on unevaluable atoms. The branch now mirrors the
NPV three-valued handling: correct iff the minor premise evaluates
False, unscored iff None, incorrect iff True. No partial credit or
penalty for the None case (Argon 005 §1b — either would re-create the
asymmetry or train RNE-spam). Two additive diagnostics are emitted
alongside fidelity_detail: coverage.fidelity_coverage (evaluated /
all fidelity records) and coverage.unscored_rne_atoms (the fact-base
expansion queue). No other scoring changes: the precedence check
already fires only when the minor premise is False AND the pervasion
is False, so a None minor was never precedence-penalised, and the
fidelity denominator already returns None when nothing is evaluable.
All prior matches re-scored under v1.5 (matchN_score_v15.json files
alongside the originals); only matches containing an RNE on an
unevaluable atom change fidelity.

v1.4 (iteration 11, 2026-10-27): telemetry (Argon consultations 003 + 004,
reconciled — see compute_telemetry notes in code). scores{} is UNCHANGED:
the four legacy metrics keep their exact v1.3 formulas, so every prior
match re-scores identically on them. A new, additive trap_telemetry block
reports forced-Accept and gate-blemish events derived inside the referee
from the move transcript + fact base only (never from scratchpads):
  - SOFT_KHOR_LO: Defender Accepts a thesis the prior ledger entails and
    the fact base POSITIVELY contradicts (KB value False, never merely
    unentailed — the coverage-gap guard from consultation 003's header
    flag). Weight 0.75, DAG leaf weights, contrapositive bridge x1.25,
    guards B1 (non-trivial inference) and B2 (novel false leaves).
  - FORCED_ROOT_ACCEPT: same, but the thesis is the negation of the root
    thesis. Weight 1.00 (consultation 004).
  - GATE_BLEMISH: Defender DENIES a thesis the prior ledger entails and
    the fact base positively contradicts (the defender_v4 automatic-Tsa
    gate trading a ledger blemish for an automatic Tsa). Base 0.85 plus
    consultation-004 bonuses (seed distance, assertion harvest, implicit
    harvest, contrapositive close). No B1 depth gate: a 0-step denial of
    an explicitly accepted thesis is exactly the blemish shape.
extended_trap_complexity = legacy trap_complexity + sum(event scores).
It drives selection; scores.trap_complexity stays the headline metric.

v1.3 (iteration 7, 2026-10-27): negated-reason RNE polarity fix — "Reason not
established" denies the minor premise AS STATED, so its ledger commitment is
the negation of the minor premise, not always False. The old code always
committed (subject, reason, False): for a negated-reason C2 ("... because of
not being an awareness") that recorded the very falsehood being denied, and
scored a correct denial as a ledger contradiction plus a fidelity error
(iter007 match 2, turn 24). RNE now commits (subject, reason, not reason_pol)
and its fidelity check evaluates the minor premise with its own polarity;
positive-reason behaviour is unchanged. A second RNE surface form is parsed
("Reason not established. [X] is [Z].") so a correctly worded denial of a
negated reason is legal at all — the old "is not" form was the only one
parsed, which forced the false wording (see defender_v3).

v1.2 (iteration 2, 2026-10-27): ledger polarity fix — Accepting a negated C1/C2
used to record its thesis atom, minor premise, and pervasion with positive
polarity regardless of negation, which let a negated Accept (iter002 match 1,
turn 11) transitively entail a false pervasion and falsely flag a correct
"No pervasion" (turn 18) plus a phantom contradiction (turn 20). Accepted
commitments are now recorded with their true polarity; a both-negated
pervasion (not-Z -> not-Y) is stored in its contrapositive positive form
(Y -> Z), which the closure's modus tollens handles exactly. Mixed-polarity
pervasions are recorded with polarity False (ignored by the closure) rather
than as false positive pervasions.

Implements the user's Section 3 rules (move formulas C1-C4, responses D1-D5) with the
ledger architecture from Argon consultation 001:
  - the ledger distinguishes EXPLICIT atoms (only these justify "Already accepted")
    from deductive closure over accepted atoms + pervasions (this triggers Khor lo!/Tsa!);
  - "No pervasion" implicitly concedes the minor premise (entered into accepted, not explicit);
  - if the Defender answers "No pervasion" when the minor premise is also false, a procedural
    (precedence) error is recorded AND the implicit concession still enters the ledger;
  - a valid Khor lo! = the Defender's last move contradicts the closure of the prior ledger
    (or was a false "Already accepted"); a valid Tsa! = the last move entails the negation
    of the root thesis or directly contradicts Purchok's text (facts.json);
  - an unfounded C4 obliges the Defender to repeat its previous valid response verbatim;
  - non-existent subjects: positive predicates are never established, negative ones always are;
  - trap complexity = MUC chain depth + 1.5 x modus-tollens edges + 2.0 x extra distinct
    subjects in the core + 1.5 if the trap used an implicit concession (NPV / D3).

CLI: python3 harness/referee.py score <transcript.json>
Transcript format: {"match_id": str, "topic": str,
  "root_thesis": {"subject": str, "predicate": str},
  "turns": [{"turn": int, "role": "challenger"|"defender", "text": str}, ...]}
"""
import json, os, re, sys

import justification

FACTS_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "facts.json")

ALIASES = {
    "valid cognizer": "prime cognizer",
    "an inferential valid cognizer": "inferential cognizer",
    "inferential valid cognizer": "inferential cognizer",
    "awareness to which the object appears but is not ascertained": "awareness to which an object appears but is not ascertained",
    "awareness to which an object appears but which is not ascertained": "awareness to which an object appears but is not ascertained",
    "subsequent cognizers": "subsequent cognizer",
    "doubting consciousness": "doubt",
    "a doubting consciousness": "doubt",
    "knower that is a new realizer": "new realizer",
    "new incontrovertible knower": "prime cognizer",
}

MARKDOWN_CHARS = set("*_#`>~|")

def norm_term(s):
    s = s.strip().lower().rstrip(".")
    s = re.sub(r"\s+", " ", s)
    for art in ("the ", "a ", "an "):
        if s.startswith(art):
            s = s[len(art):]
            break
    return ALIASES.get(s, s)

def _member_norm(s):
    """Set-relation pair members carry glosses ('awareness (blo)');
    strip a trailing parenthetical before normalising, as
    discrepancy_probe.norm does (v2.0 closure machinery)."""
    s = re.sub(r"\s*\([^)]*\)\s*$", "", str(s).strip())
    return norm_term(s)

def split_neg(s):
    """Return (term, polarity) where polarity True = positive mention."""
    s = s.strip()
    if s.lower().startswith("not "):
        return norm_term(s[4:]), False
    return norm_term(s), True

# ---------------------------------------------------------------- facts

class Facts:
    def __init__(self, path=FACTS_PATH):
        d = json.load(open(path, encoding="utf-8"))
        self.is_a = {}
        for f in d["is_a"]:
            self.is_a[(norm_term(f["subject"]), norm_term(f["predicate"]))] = f["value"]
        self.perv = {}
        for f in d["pervasions"]:
            self.perv[(norm_term(f["reason"]), norm_term(f["predicate"]))] = f["value"]
        # v2.0: raw canonical lists and set relations, kept for the
        # horn-clause entailment closure (eval_atom_full /
        # eval_pervasion_full) and for modules that read them off the
        # Facts object (justification canonical terms).
        self.canonical_subjects = list(d.get("canonical_subjects") or [])
        self.canonical_predicates = list(d.get("canonical_predicates") or [])
        self._set_relations = list(d.get("set_relations") or [])
        self._closure_cache = None
        self._equiv_cache = None
        self.nonexistent = {norm_term(s) for s in d["nonexistent_subjects"]}
        self.disjoint = set()
        for r in d["set_relations"]:
            if "'gal ba" in r["relation"] and len(r["pair"]) >= 2:
                a = norm_term(r["pair"][0]); b = norm_term(r["pair"][1])
                # pair entries may carry glosses; keep only leading canonical term before ' ('
                a = a.split(" (")[0]; b = b.split(" (")[0]
                self.disjoint.add((a, b)); self.disjoint.add((b, a))
        # derived disjointness: subsets of a term disjoint from c are disjoint from c
        changed = True
        while changed:
            changed = False
            for (a, b), v in list(self.perv.items()):
                if v:
                    for (x, y) in list(self.disjoint):
                        if x == b and (a, y) not in self.disjoint:
                            self.disjoint.add((a, y)); self.disjoint.add((y, a)); changed = True

    def eval_atom(self, subj, pred, pol=True):
        """Truth of the proposition 'subj is [not] pred'. True/False/None(unknown)."""
        s, p = norm_term(subj), norm_term(pred)
        if s in self.nonexistent:
            base = False
        elif (s, p) in self.is_a:
            base = self.is_a[(s, p)]
        elif (s, p) in self.perv:
            base = self.perv[(s, p)]
        elif s == p:
            base = True
        else:
            return None
        return base if pol else (not base)

    def eval_pervasion(self, z, y, zpol=True, ypol=True):
        """Truth of 'whatever is [not] z is necessarily [not] y'."""
        z, y = norm_term(z), norm_term(y)
        if zpol and ypol:
            if z == y:
                return True
            return self.perv.get((z, y))
        if (not zpol) and (not ypol):  # contrapositive
            if z == y:
                return True
            return self.perv.get((y, z))
        if zpol and (not ypol):  # mutual exclusion
            if (z, y) in self.disjoint:
                return True
            if self.perv.get((z, y)) is True:
                return False
            return None
        return None  # (not z) -> y : not determinable from the fact base in general

    # ------------------------------------------------ v1.6 fault lines
    def fault_line_pervasion(self, z, y, zpol=True, ypol=True):
        """Contested fault-line pervasions (Argon 006 §3 / 007 §2).
        Returns (fl_id, value_if_branch_A, value_if_branch_B) or None.
        Patterns are stated-form, on normalized terms."""
        z, y = norm_term(z), norm_term(y)
        if zpol and ypol and "mental faculty as its uncommon dominant condition" in z \
                and "other-knowing" not in z \
                and y in ("mental direct perceiver", "mental direct prime cognizer"):
            # FL_01 sufficiency of the worded definiens:
            # A LITERAL_3LIMB True; B CONTEXTUAL_4LIMB False.
            # v1.7: the pattern is the INCOMPLETE (3-limb) wording only.
            # A wording carrying the other-knower limb is the complete
            # definition, whose sufficiency is True under BOTH branches
            # (under A it follows a fortiori from the 3-limb sufficiency),
            # so it is not a contested pervasion at all and must not
            # match here: iteration 18 match 1 turn 10's Accept of the
            # 4-limb sufficiency was falsely flagged as a flip against
            # the 3-limb lock at turn 4. Falling through returns None
            # and the assertion scores via the static base (unscored
            # for this long-form pervasion), not as a frame flip.
            return ("FL_01", True, False)
        if zpol and (not ypol) and z == "mental direct perceiver" and y == "self-knower":
            # FL_01 exclusion pervasion: A False; B True.
            return ("FL_01", False, True)
        if zpol and ypol and "unmixed" in z and "as arisen" in y:
            # FL_02 bridge: A KHEDRUP_JETSUN_VERSE True;
            # B PURCHOK_ENGAGEMENT_QUALIFIER False.
            return ("FL_02", True, False)
        return None

    def fault_line_atom(self, subj, pred):
        """SILENT_DOCTRINAL atoms (Argon 007 §2). FL_03: the faculty /
        dominant-condition atom about a self-knower subject — Purchok
        states neither side, so the static base stays silent."""
        s, p = norm_term(subj), norm_term(pred)
        if "mental faculty as its uncommon dominant condition" in p and "self-knowing" in s:
            return "FL_03"
        return None

    # ------------------------------------------------ v2.0 closure
    def _build_closure(self):
        """Horn-clause entailment closure over is_a + pervasions,
        compiled exactly as harness/discrepancy_probe.py compiles it
        (True pervasions as modus ponens / modus tollens, don gcig
        classes in both directions over canonical predicates, 'gal ba
        exclusion True -> False on the other side). Fixpoint; a
        conflict keeps the first-derived value. Cached on the Facts
        object; keys are referee-normalized terms."""
        if self._closure_cache is not None:
            return
        canon = {norm_term(p) for p in self.canonical_predicates}
        equivalences, exclusions = [], []
        for rel in self._set_relations:
            members = [m for m in (_member_norm(m) for m in rel["pair"]) if m in canon]
            if "don gcig" in rel["relation"]:
                if len(members) >= 2:
                    equivalences.append(set(members))
            elif "'gal ba" in rel["relation"]:
                for i in range(len(members)):
                    for j in range(i + 1, len(members)):
                        exclusions.append((members[i], members[j]))
        perv_true = [(a, b) for (a, b), v in self.perv.items() if v]
        known = dict(self.is_a)

        def set_value(s, p, value):
            key = (s, p)
            if key in known:
                return False
            known[key] = value
            return True

        changed = True
        while changed:
            changed = False
            for (s, p), value in list(known.items()):
                if value:
                    for (a, q) in perv_true:
                        if a == p and set_value(s, q, True):
                            changed = True
                else:
                    for (a, q) in perv_true:
                        if q == p and set_value(s, a, False):
                            changed = True
                for eq in equivalences:
                    if p in eq:
                        for q in eq:
                            if q != p and set_value(s, q, value):
                                changed = True
                if value:
                    for (a, b) in exclusions:
                        other = b if a == p else (a if b == p else None)
                        if other is not None and set_value(s, other, False):
                            changed = True
        self._closure_cache = known
        self._equiv_cache = equivalences

    def eval_atom_full(self, subj, pred, pol=True):
        """v2.0: stated value, else horn-closure value, for
        'subj is pred' (pol applies to the underlying fact, as in
        eval_atom). Used by the type B/C turn-1 blocks and prep
        validation — the same entailment harness/prep_check.py runs."""
        v = self.eval_atom(subj, pred, pol)
        if v is not None:
            return v
        self._build_closure()
        base = self._closure_cache.get((norm_term(subj), norm_term(pred)))
        if base is None:
            return None
        return base if pol else (not base)

    def eval_pervasion_full(self, z, y):
        """v2.0: stated pervasion value, else entailed value: True when
        the consequent is reachable from the antecedent through True
        pervasions and don gcig classes; False when the atom closure
        holds a counterexample pair ((s is z) True, (s is y) False);
        otherwise None."""
        v = self.eval_pervasion(z, y)
        if v is not None:
            return v
        z, y = norm_term(z), norm_term(y)
        self._build_closure()
        reach = {z}
        perv_true = [(a, b) for (a, b), val in self.perv.items() if val]
        changed = True
        while changed:
            changed = False
            for (a, b) in perv_true:
                if a in reach and b not in reach:
                    reach.add(b); changed = True
            for eq in self._equiv_cache:
                if eq & reach and not eq <= reach:
                    reach |= eq; changed = True
        if y in reach:
            return True
        for (s, q), val in self._closure_cache.items():
            if q == z and val and s not in self.nonexistent \
                    and self._closure_cache.get((s, y)) is False:
                return False
        return None

# ---------------------------------------------------------------- parsing

class Move:
    def __init__(self, kind, **kw):
        self.kind = kind
        self.__dict__.update(kw)
    def __repr__(self):
        return f"<Move {self.kind} {self.__dict__}>"

def has_markdown(text):
    return any(c in MARKDOWN_CHARS for c in text) or "\n" in text.strip("\n") and text.count("\n") > 0 and False

def _clean_slot(s):
    return s.strip()

# v2.1 escape-challenge forms (defender_v8 / challenger_v36). The
# predicate slot may itself be negated ("it is not [P]"); split_neg at
# the call site recovers (term, polarity) as elsewhere.
C5A_RE = re.compile(r"^The subject, (.+?), it follows that it is (not )?(.+?), because (.+?) is (not )?(.+?) and the reasoning is the same\. State the difference\.$")
C5B_RE = re.compile(r"^The subject, (.+?), it follows that it is (not )?(.+?), because\? State the reason\.$")

# v2.2 quotation forms (defender_v9 / challenger_v37). The C6 surface
# carries an English rendering in single quotes; the machine data
# (text_cite, quote_claim) rides in turn fields.
C6_PERV_RE = re.compile(r"^If something is (.+?), it follows that it is necessarily (.+?), because Purchok states in his own voice: '.+'\.$")
C6_MINOR_RE = re.compile(r"^The subject, (.+?), it follows that it is (.+?), because Purchok states in his own voice: '.+'\.$")

def parse_challenger(text):
    """Return (Move, syntax_ok, problems[])."""
    problems = []
    t = text.strip()
    if any(c in MARKDOWN_CHARS for c in t):
        problems.append("markdown characters present")
    if "\n" in t and not t.startswith(("Khor lo!", "Tsa!")):
        problems.append("multiple lines / extra prose")
    if t == "Posit an example.":
        return Move("C3"), not problems, problems
    if t.startswith("Khor lo!") or t.startswith("Tsa!"):
        call = "Khor lo!" if t.startswith("Khor lo!") else "Tsa!"
        rest = t[len(call):].strip()
        if not rest:
            problems.append("C4 without the required contradiction demonstration")
        return Move("C4", call=call, demonstration=rest), not problems, problems
    m = C6_PERV_RE.match(t)
    if m:
        # v2.2 pervasion-repair quotation: the surface names the
        # pervasion claimed (reason -> predicate); the debate subject
        # rides in the turn's quote_claim, not in the sentence.
        reason, rpol = split_neg(m.group(1))
        pred, ppol = split_neg(m.group(2))
        return Move("C6_PERV", subject=None, reason=reason, reason_pol=rpol,
                    predicate=pred, pred_pol=ppol), not problems, problems
    m = C6_MINOR_RE.match(t)
    if m:
        # v2.2 minor-premise repair: the predicate slot carries the
        # target C2's REASON (the atom being established).
        pred, ppol = split_neg(m.group(2))
        return Move("C6_MINOR", subject=_clean_slot(m.group(1)),
                    predicate=pred, pred_pol=ppol), not problems, problems
    if t.startswith("The passage stands in Purchok's own voice:"):
        # v2.2 refutation turn inside a quotation episode.
        return Move("C6_REFUTE"), not problems, problems
    if t.startswith("If it is "):
        # v1.8: bare conditional C1 ("If it is X, it follows it is Y."),
        # the pervasion thesis form defender_v4's audit already treats
        # as a C1 and challenger_v19's T32 prescribes. Stored as a
        # pervasion (antecedent -> consequent), not an atom thesis.
        for marker in (", it follows it is ", ", it follows that it is "):
            i = t.find(marker)
            if i >= 0:
                break
        if i < 0:
            problems.append("conditional C1 missing 'it follows it is'")
            return Move("INVALID"), False, problems
        ant_s = _clean_slot(t[len("If it is "):i])
        cons_s = _clean_slot(t[i + len(marker):])
        if not cons_s.endswith("."):
            problems.append("conditional C1 does not end with a period")
        ant, apol = split_neg(ant_s)
        cons, cpol = split_neg(cons_s.rstrip("."))
        return Move("C1_COND", subject=None, reason=ant, reason_pol=apol,
                    predicate=cons, pred_pol=cpol), not problems, problems
    m = C5A_RE.match(t)
    if m:
        # v2.1 difference-demand: the subject slot is the DENIED case;
        # the positive case rides in the because-clause. The predicate
        # (with its polarity) is shared by both entries of the pair.
        pred, ppol = split_neg(((m.group(2) or "") + m.group(3)).strip())
        pos_pred, pos_ppol = split_neg(((m.group(5) or "") + m.group(6)).strip())
        return Move("C5A", subject=_clean_slot(m.group(1)), predicate=pred,
                    pred_pol=ppol, pos_subject=_clean_slot(m.group(4)),
                    pos_predicate=pos_pred, pos_pred_pol=pos_ppol), not problems, problems
    m = C5B_RE.match(t)
    if m:
        # v2.1 reason-demand: the surface names the thesis the Defender
        # stands on (the negation of the denied thesis).
        pred, ppol = split_neg(((m.group(2) or "") + m.group(3)).strip())
        return Move("C5B", subject=_clean_slot(m.group(1)), predicate=pred,
                    pred_pol=ppol), not problems, problems
    if t.startswith("The subject, "):
        marker = ", it follows that it is "
        i = t.find(marker)
        if i < 0:
            problems.append("missing 'it follows that it is'")
            return Move("INVALID"), False, problems
        subj = _clean_slot(t[len("The subject, "):i])
        rest = t[i + len(marker):]
        # C2 reason forms: ", because of being Z" and ", because of not being Z"
        # (the negated form is explicitly permitted by challenger_v1.md; referee
        # v1 missed it and misparsed such moves as contaminated C1s — fixed v1.1,
        # iteration 1, after Match 1 turns 1 and 3 were flagged as artifacts).
        bmarker = ", because of being "
        nbmarker = ", because of not being "
        j = rest.find(bmarker)
        nj = rest.find(nbmarker)
        if nj >= 0 and (j < 0 or nj < j):
            pred_s = _clean_slot(rest[:nj])
            reason_s = _clean_slot(rest[nj + len(nbmarker):])
            if not reason_s.endswith("."):
                problems.append("C2 does not end with a period")
            reason_s = reason_s.rstrip(".")
            pred, ppol = split_neg(pred_s)
            reason, _ = split_neg(reason_s)
            return Move("C2", subject=subj, predicate=pred, pred_pol=ppol,
                        reason=reason, reason_pol=False), not problems, problems
        if j >= 0:
            pred_s = _clean_slot(rest[:j])
            reason_s = _clean_slot(rest[j + len(bmarker):])
            if not reason_s.endswith("."):
                problems.append("C2 does not end with a period")
            reason_s = reason_s.rstrip(".")
            pred, ppol = split_neg(pred_s)
            reason, rpol = split_neg(reason_s)
            return Move("C2", subject=subj, predicate=pred, pred_pol=ppol,
                        reason=reason, reason_pol=rpol), not problems, problems
        if "because" in rest:
            problems.append("C1 form contaminated with a reason")
            return Move("INVALID"), False, problems
        pred_s = _clean_slot(rest)
        if not pred_s.endswith("."):
            problems.append("C1 does not end with a period")
        pred, ppol = split_neg(pred_s.rstrip("."))
        return Move("C1", subject=subj, predicate=pred, pred_pol=ppol), not problems, problems
    problems.append("does not match any of C1-C4")
    return Move("INVALID"), False, problems

def parse_defender(text, context):
    """context: dict with prev challenger Move, defender's previous response text,
    and the defender move before that (for C3/D3 binding)."""
    problems = []
    t = text.strip()
    if any(c in MARKDOWN_CHARS for c in t):
        problems.append("markdown characters present")
    if t == "Accept":
        return Move("D_ACC"), not problems, problems
    if t == "Why":
        return Move("D_WHY"), not problems, problems
    if t == "Already accepted":
        return Move("D_ALR"), not problems, problems
    if t == "State your thesis or reason in valid debate form.":
        return Move("D_SYN"), not problems, problems
    m = re.match(r"^Reason not established\. (.+) is not (.+)\.$", t)
    if m:
        return Move("D_RNE", subject=_clean_slot(m.group(1)), reason=norm_term(m.group(2))), not problems, problems
    # v1.3: correctly worded denial of a NEGATED reason ("... because of not
    # being Z" is denied by "X is Z", not "X is not Z"). Tried after the
    # "is not" form so "is not" sentences still take the first branch.
    m = re.match(r"^Reason not established\. (.+) is (.+)\.$", t)
    if m:
        return Move("D_RNE", subject=_clean_slot(m.group(1)), reason=norm_term(m.group(2))), not problems, problems
    m = re.match(r"^No pervasion\. If it is (not )?(.+), it is not necessarily (not )?(.+)\.$", t)
    if m:
        return Move("D_NPV", reason=norm_term(m.group(2)), reason_pol=not m.group(1),
                    predicate=norm_term(m.group(4)), pred_pol=not m.group(3)), not problems, problems
    m = re.match(r"^(.+) is (.+) but not (.+)\.$", t)
    if m:
        return Move("D3B", example=_clean_slot(m.group(1)), reason=norm_term(m.group(2)),
                    predicate=norm_term(m.group(3))), not problems, problems
    m = re.match(r"^(.+) is not (.+)\.$", t)
    if m:
        return Move("D3A", example=_clean_slot(m.group(1)), reason=norm_term(m.group(2))), not problems, problems
    prev = context.get("prev_defender_text")
    if prev is not None and t == prev.strip():
        return Move("D_REPEAT"), not problems, problems
    problems.append("does not match any of D1-D5")
    return Move("INVALID"), False, problems

def validate_syntax(role, text, context=None):
    """Spec-named API: returns (ok, move, problems)."""
    context = context or {}
    if role == "challenger":
        mv, ok, probs = parse_challenger(text)
        return ok, mv, probs
    mv, ok, probs = parse_defender(text, context)
    return ok, mv, probs

# ------------------------------------------------------ v2.0 openings
# Match types B and C open with fixed forms (defender_v7 / challenger_v35).
# The parsers return (Move, problems, data); score_match applies the
# problems through its own violate() and uses data for the ledger
# injection and the type blocks.
B_DEMAND_RE = re.compile(r"^Establish the thesis: the subject, (.+), is (.+)\. State your reason\.$")
C_DEMAND_RE = re.compile(r"^State the meaning of (.+)\.$")
B_REASON_RE = re.compile(r"^The subject, (.+), is (.+), because of being (.+)\.$")

def parse_opening_demand(match_type, text):
    """Type B/C turn 1: returns (Move, problems)."""
    t = text.strip()
    if match_type == "B":
        m = B_DEMAND_RE.match(t)
        if not m:
            return Move("INVALID"), ["malformed type B opening: expected 'Establish the thesis: the subject, [S], is [P]. State your reason.'"]
        return Move("B_DEMAND", subject=_clean_slot(m.group(1)),
                    predicate=_clean_slot(m.group(2))), []
    m = C_DEMAND_RE.match(t)
    if not m:
        return Move("INVALID"), ["malformed type C opening: expected 'State the meaning of [T].'"]
    return Move("C_DEMAND", term=_clean_slot(m.group(1))), []

def parse_opening_statement(match_type, text, opening):
    """Type B/C turn 2: returns (Move, problems, data). `opening` is
    the turn-1 demand Move (or a Move of another kind / None)."""
    t = text.strip()
    if match_type == "B":
        m = B_REASON_RE.match(t)
        if not m:
            return Move("INVALID"), ["malformed type B reason statement: expected 'The subject, [S], is [P], because of being [R].'"], {}
        s = _clean_slot(m.group(1)); p = _clean_slot(m.group(2)); r = _clean_slot(m.group(3))
        problems = []
        if opening is not None and opening.kind == "B_DEMAND":
            if norm_term(s) != norm_term(opening.subject) or norm_term(p) != norm_term(opening.predicate):
                problems.append("type B reason statement does not restate the demanded subject and predicate")
        return (Move("STATE_REASON", subject=s, predicate=p, reason=r), problems,
                {"subject": s, "predicate": p, "reason": r})
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
    problems = []
    d_text = ill = None
    divisions = []
    if (len(lines) != 3 or not lines[0].startswith("Definiens:")
            or not lines[1].startswith("Divisions:")
            or not lines[2].startswith("Illustration:")):
        problems.append("malformed type C meaning statement: expected three lines 'Definiens:' / 'Divisions:' / 'Illustration:'")
    else:
        d_text = lines[0][len("Definiens:"):].strip()
        div_raw = lines[1][len("Divisions:"):].strip()
        ill = lines[2][len("Illustration:"):].strip()
        if div_raw.lower() != "none stated":
            divisions = [x.strip() for x in div_raw.split(";") if x.strip()]
    term = getattr(opening, "term", None) if opening is not None else None
    return (Move("STATE_MEANING", term=term, definiens=d_text,
                 divisions=divisions, illustration=ill), problems,
            {"term": term, "definiens": d_text, "divisions": divisions,
             "illustration": ill})

# ------------------------------------------------------ v2.0 text cites
_ETEXT_PATH = os.path.join(os.path.dirname(__file__), "..", "sources",
                           "S06857E4_blo_rig.txt")
_etext_cache = None

def _etext():
    global _etext_cache
    if _etext_cache is None:
        with open(_ETEXT_PATH, encoding="utf-8") as fh:
            _etext_cache = fh.read()
    return _etext_cache

def _verify_text_cite(cite):
    """A cite verifies iff the root-text slice [start:end] equals the
    quoted string exactly (offsets are into S06857E4, the matrix's
    offset base). Malformed cites verify False."""
    if not isinstance(cite, dict):
        return False
    start, end, quote = cite.get("start"), cite.get("end"), cite.get("quote")
    if not (isinstance(start, int) and isinstance(end, int) and isinstance(quote, str)):
        return False
    if start < 0 or end < start:
        return False
    try:
        return _etext()[start:end] == quote
    except OSError:
        return False

# --------------------------------------------- v2.0 clause matching (C)
_DEFS_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge",
                          "definitions.json")
_defs_cache = None

def _definitions():
    global _defs_cache
    if _defs_cache is None:
        try:
            with open(_DEFS_PATH, encoding="utf-8") as fh:
                _defs_cache = json.load(fh).get("terms", {})
        except (OSError, ValueError):
            _defs_cache = {}
    return _defs_cache

def _canonical_def(term):
    """definitions.json entry for a term: exact key, else the key whose
    normalized form matches."""
    terms = _definitions()
    if term in terms:
        return terms[term]
    nt = norm_term(term)
    for key, val in terms.items():
        if norm_term(key) == nt:
            return val
    return None

def _clause_tokens(s):
    return set(re.findall(r"[a-z0-9]+", (s or "").lower()))

def _clause_match(stated, canonical):
    """A stated clause matches a canonical clause iff token Jaccard
    >= 0.5 or either token set is a subset of the other."""
    a, b = _clause_tokens(stated), _clause_tokens(canonical)
    if not a or not b:
        return False
    if a <= b or b <= a:
        return True
    return len(a & b) / len(a | b) >= 0.5

# ------------------------------------------- v2.1 escape-challenges
# The four Defender answers to a C5 (defender_v8). A D-Reason has the
# STATE_REASON surface shape (B_REASON_RE) with an optionally negated
# predicate slot; it is only an answer in C5B context, so
# _parse_c5_answer is called from score_match, never from the general
# parse_defender path (legacy transcripts cannot grow these kinds).
DDIFF_RE = re.compile(r"^There is a difference: (.+?) is (.+), whereas (.+?) is not (.+), and being (.+) is relevant to being (.+)\.$")
DCONCEDE_RE = re.compile(r"^I concede the distinction: the subject, (.+), is (.+)\.$")
DUNF_RE = re.compile(r"^(?:Distinction challenge unfounded|Reason demand unfounded): at turn \d+ I did not (?:accept|deny) that .+ is .+\.$")

def _parse_c5_answer(text, c5_kind):
    """Parse a Defender answer to a C5 challenge; returns a Move of
    kind D_DIFF / D_REASON / D_CONCEDE / D_UNFOUNDED, or None when the
    text matches none of the four forms (an OTHER answer, which the
    standard defender path then scores)."""
    t = text.strip()
    if c5_kind == "C5A":
        m = DDIFF_RE.match(t)
        if m:
            d_pos = m.group(2).strip()
            # the three D mentions must name the same difference
            if norm_term(d_pos) == norm_term(m.group(4)) == norm_term(m.group(5)):
                p, ppol = split_neg(m.group(6))
                return Move("D_DIFF", subject_pos=_clean_slot(m.group(1)),
                            difference=d_pos,
                            subject_neg=_clean_slot(m.group(3)),
                            predicate=p, pred_pol=ppol)
    if c5_kind == "C5B":
        m = B_REASON_RE.match(t)
        if m:
            p, ppol = split_neg(m.group(2))
            return Move("D_REASON", subject=_clean_slot(m.group(1)),
                        predicate=p, pred_pol=ppol,
                        reason=_clean_slot(m.group(3)))
    m = DCONCEDE_RE.match(t)
    if m:
        p, ppol = split_neg(m.group(2))
        return Move("D_CONCEDE", subject=_clean_slot(m.group(1)),
                    predicate=p, pred_pol=ppol)
    if DUNF_RE.match(t):
        return Move("D_UNFOUNDED")
    return None

def _resolve_difference(d_raw, canonical_norms):
    """Resolve a stated difference D (v2.1): a canonical predicate,
    "not [D]", or "[D1] and [D2]" of canonical predicates. Returns
    {parts, pol, resolved} — parts are normalized base terms; pol is
    the single-term polarity (True for a conjunction). No fallback:
    an unresolvable D is non-canonical and its answer item scores 0."""
    dn = norm_term(d_raw)
    if dn in canonical_norms:
        return {"parts": [dn], "pol": True, "resolved": True}
    if dn.startswith("not "):
        core = dn[len("not "):]
        if core in canonical_norms:
            return {"parts": [core], "pol": False, "resolved": True}
        parts = [x.strip() for x in core.split(" and ")]
        if len(parts) > 1 and all(x in canonical_norms for x in parts):
            return {"parts": parts, "pol": False, "resolved": True}
        return {"parts": [core], "pol": False, "resolved": False}
    parts = [x.strip() for x in dn.split(" and ")]
    if len(parts) > 1 and all(x in canonical_norms for x in parts):
        return {"parts": parts, "pol": True, "resolved": True}
    return {"parts": [dn], "pol": True, "resolved": False}

def _eval_difference(facts, subj, dres):
    """Truth of 'subj is D' under the difference transform: negation
    flips the single value; a conjunction is True iff every part is,
    False iff any part is, else None. Stated facts plus the horn
    closure (the v2.0 turn-1 convention)."""
    vals = [facts.eval_atom_full(subj, part, True) for part in dres["parts"]]
    if len(vals) == 1:
        v = vals[0]
    elif all(x is True for x in vals):
        v = True
    elif any(x is False for x in vals):
        v = False
    else:
        v = None
    if not dres["pol"] and v is not None:
        v = not v
    return v

def _diff_contested(facts, subj, dres):
    """Any part of D sitting on a fault line (FL_03 atom pattern) for
    this subject makes the checked field 'contested'."""
    return any(facts.fault_line_atom(subj, part) is not None
               for part in dres["parts"])

def _eval_relevance(facts, route, dres, d_raw, p_base, p_pol):
    """The relevance claim of a D-Diff, by the route declared in the
    Defender's payload. Returns (value, contested). SUFFICIENT: D
    pervades P (a conjunction pervades when any part does — the
    stronger antecedent inherits the part's pervasion; no sound
    False is derivable from the parts alone). NECESSARY: P pervades
    D (a conjunction consequent needs every part). DEFINIENS_CLAUSE:
    D token-matches a clause of P's canonical definition. An undeclared
    or unknown route evaluates to None (unscored component)."""
    parts, pol = dres["parts"], dres["pol"]
    if route == "SUFFICIENT":
        if len(parts) == 1:
            contested = facts.fault_line_pervasion(parts[0], p_base, pol, p_pol) is not None
            v = facts.eval_pervasion_full(parts[0], p_base) if (pol and p_pol) \
                else facts.eval_pervasion(parts[0], p_base, pol, p_pol)
            return v, contested
        contested = any(facts.fault_line_pervasion(x, p_base, True, p_pol) is not None
                        for x in parts)
        vals = [facts.eval_pervasion_full(x, p_base) if p_pol
                else facts.eval_pervasion(x, p_base, True, p_pol) for x in parts]
        return (True if any(x is True for x in vals) else None), contested
    if route == "NECESSARY":
        if len(parts) == 1:
            contested = facts.fault_line_pervasion(p_base, parts[0], p_pol, pol) is not None
            v = facts.eval_pervasion_full(p_base, parts[0]) if (pol and p_pol) \
                else facts.eval_pervasion(p_base, parts[0], p_pol, pol)
            return v, contested
        contested = any(facts.fault_line_pervasion(p_base, x, p_pol, True) is not None
                        for x in parts)
        vals = [facts.eval_pervasion_full(p_base, x) if p_pol
                else facts.eval_pervasion(p_base, x, p_pol, True) for x in parts]
        if all(x is True for x in vals):
            return True, contested
        if any(x is False for x in vals):
            return False, contested
        return None, contested
    if route == "DEFINIENS_CLAUSE":
        entry = _canonical_def(p_base)
        clauses = (entry or {}).get("clauses") or []
        if not clauses:
            return None, False
        return any(_clause_match(d_raw, c) for c in clauses), False
    return None, False

def _history_maps(history):
    """Per-Defender-turn context from the ledger history: the
    Challenger move each Defender turn answered, and the Defender
    move itself, keyed by turn number."""
    prev_c_map, def_move_map = {}, {}
    last_c = None
    for (tn, role, mv, _text) in history:
        if role == "challenger":
            last_c = mv
        else:
            prev_c_map[tn] = last_c
            def_move_map[tn] = mv
    return prev_c_map, def_move_map

def _ancestors(facts, subj):
    """Canonical predicates Q with (subj is Q) True in facts (stated
    or closure-entailed), minus the top universals 'established base'
    and 'knowable object' — the proximity guard's taxonomic reach."""
    out = set()
    for q in facts.canonical_predicates:
        if facts.eval_atom_full(subj, q) is True:
            out.add(norm_term(q))
    return out - {"established base", "knowable object"}

# ------------------------------------------- v2.2 quotation move (C6)
_REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge",
                              "quote_registry.json")
_GLOSSARY_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge",
                              "glossary_tibetan.json")
_registry_cache = None
_glossary_cache = None

def _quote_registry():
    """Spans of knowledge/quote_registry.json (pre-classified voice
    tags). A missing or unreadable registry yields [] — every span
    then takes the window-scan path in _c6_voice_status."""
    global _registry_cache
    if _registry_cache is None:
        try:
            with open(_REGISTRY_PATH, encoding="utf-8") as fh:
                _registry_cache = json.load(fh).get("spans", [])
        except (OSError, ValueError):
            _registry_cache = []
    return _registry_cache

def _glossary():
    global _glossary_cache
    if _glossary_cache is None:
        try:
            with open(_GLOSSARY_PATH, encoding="utf-8") as fh:
                _glossary_cache = json.load(fh).get("terms", {})
        except (OSError, ValueError):
            _glossary_cache = {}
    return _glossary_cache

def _glossary_stems(term):
    """Wylie stems for a canonical claim term, or None when the term
    has no glossary entry (its term-presence check is then skipped,
    never failed). Glossary keys are matrix.md heading names verbatim
    and may carry parenthetical qualifiers ("prime cognizer (valid
    cognizer)") while claim terms are canonical ("prime cognizer"),
    so the lookup is tolerant: (1) the exact claim term, (2) any
    glossary key whose base before " (" equals the claim term,
    (3) the claim term's own base before " (" matched against keys."""
    terms = _glossary()
    if not terms or term is None:
        return None
    def _stems_of(val):
        stems = (val or {}).get("stems") or []
        return list(stems) or None
    if term in terms:
        return _stems_of(terms[term])
    nt = norm_term(term)
    for key, val in terms.items():
        if norm_term(key) == nt:
            return _stems_of(val)
    for key, val in terms.items():
        if norm_term(key.split(" (")[0]) == nt:
            return _stems_of(val)
    base = norm_term(str(term).split(" (")[0])
    if base != nt:
        for key, val in terms.items():
            if norm_term(key) == base or norm_term(key.split(" (")[0]) == base:
                return _stems_of(val)
    return None

def _wylie_norm(s):
    """Normalize a Wylie string for substring search: lowercase,
    collapse whitespace, no leading/trailing space."""
    return re.sub(r"\s+", " ", (s or "").lower()).strip()

def _stem_variants(stem):
    """Searchable variants of one glossary stem: the full stem, its
    base before a parenthetical, and the parenthetical content itself
    (a stem may list alternates as 'bcad shes (dpyad shes)')."""
    out = []
    full = _wylie_norm(stem)
    if full:
        out.append(full)
    base = _wylie_norm(str(stem).split(" (")[0])
    if base and base not in out:
        out.append(base)
    m = re.search(r"\(([^)]*)\)", str(stem))
    if m:
        inner = _wylie_norm(m.group(1))
        if inner and inner not in out:
            out.append(inner)
    return out

def _stems_present(wylie_text, stems):
    """True iff at least one variant of at least one stem occurs in
    the (already transliterated, normalized) text."""
    return any(v in wylie_text for st in stems for v in _stem_variants(st))

# ------------------------------------------- v2.3 debate archive
_ARCHIVE_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge",
                             "debate_archive.json")
_archive_cache = None

def _debate_archive():
    """The debate-archive bank as {entry_id: entry}, or None when the
    bank file is missing or unreadable (every archive check then
    records 'unverifiable' instead of failing or passing on evidence
    that does not exist). Tolerates the bank's container shapes: a
    top-level list of entries, {"entries": [...]}, {"entries": {...}},
    or a bare {entry_id: entry} mapping."""
    global _archive_cache
    if _archive_cache is None:
        try:
            with open(_ARCHIVE_PATH, encoding="utf-8") as fh:
                raw = json.load(fh)
        except (OSError, ValueError):
            return None
        entries = raw.get("entries", raw) if isinstance(raw, dict) else raw
        bank = {}
        if isinstance(entries, dict):
            items = entries.items()
        elif isinstance(entries, list):
            items = ((e.get("entry_id"), e) for e in entries
                     if isinstance(e, dict))
        else:
            items = ()
        for eid, entry in items:
            if isinstance(eid, str) and isinstance(entry, dict):
                bank[eid] = entry
        _archive_cache = bank
    return _archive_cache

# ------------------------------------------- v2.2 quotation move (C6)
# The glossary's stems are WYLIE transliteration (matrix.md gives the
# Tibetan in Wylie), so term-presence searches transliterate the quote
# first. The transliterator is the standard Wylie algorithm restricted
# to what this corpus needs: per tsheg-delimited syllable, choose a
# parse (superscript / plain root / prefix+root) whose tail is a legal
# syllable tail, and emit the conventional spellings. Every Tibetan
# character below is written as a codepoint or \u escape so the tables
# are unambiguous.

_T = chr
_W_BASE_NAMES = (
    "ka", "kha", "ga", "gha", "nga", "ca", "cha", "ja", None, "nya",
    "Ta", "Tha", "Da", "Dha", "Na", "ta", "tha", "da", "dha", "na",
    "pa", "pha", "ba", "bha", "ma", "tsa", "tsha", "dza", "dzha", "wa",
    "zha", "za", "'a", "ya", "ra", "la", "sha", "sa", "sa", "ha",
    "a", "kSa", "Ra")
_W_BASE = {_T(0x0F40 + i): n for i, n in enumerate(_W_BASE_NAMES) if n}
_W_SUBJ_NAMES = (
    "k", "kh", "g", "gh", "ng", "c", "ch", "j", None, "ny",
    "T", "Th", "D", "Dh", "N", "t", "th", "d", "dh", "n",
    "p", "ph", "b", "bh", "m", "ts", "tsh", "dz", "dzh", "w",
    "zh", "z", "", "y", "r", "l", "sh", "s", "s", "h",
    "", "kS", "R", "r", "l")
_W_SUBJ = {_T(0x0F90 + i): n for i, n in enumerate(_W_SUBJ_NAMES)
           if n is not None}
_W_SUBJ_BASE = {_T(0x0F90 + i): _T(0x0F40 + i)
                for i in range(len(_W_SUBJ_NAMES))
                if _W_SUBJ_NAMES[i] is not None}
_W_VOWEL = {_T(c): v for c, v in (
    (0x0F71, "A"), (0x0F72, "i"), (0x0F73, "I"), (0x0F74, "u"),
    (0x0F75, "U"), (0x0F76, "Ri"), (0x0F77, "RI"), (0x0F78, "lI"),
    (0x0F79, "lI"), (0x0F7A, "e"), (0x0F7B, "ai"), (0x0F7C, "o"),
    (0x0F7D, "au"), (0x0F80, "Ri"), (0x0F81, "RI"))}
# prefix letters ga da ba ma 'a; superscribed ra la sa; suffix letters
# ga nga da na ba ma 'a ra la sa.
_W_PREFIX = {_T(0x0F42), _T(0x0F51), _T(0x0F56), _T(0x0F58), _T(0x0F60)}
_W_SUPER = {_T(0x0F62): "r", _T(0x0F63): "l", _T(0x0F65): "s"}
_W_SUFFIX = {_T(0x0F42), _T(0x0F44), _T(0x0F51), _T(0x0F53), _T(0x0F56),
             _T(0x0F58), _T(0x0F60), _T(0x0F62), _T(0x0F63), _T(0x0F65),
             _T(0x0F66)}
_A_CHUNG = _T(0x0F60)
_NGA = _T(0x0F44)
_WA_SUBJ = _T(0x0FAD)

def _wylie_tail(tail):
    """Validate the post-stack tail of a syllable parse and split it
    into (vowel_str, suffix_chars). A legal tail: vowel signs and at
    most two suffix bases; a vowel sign may not follow a suffix base
    other than a-chung (ma'i, pa'i are written with the vowel sign
    after the ' suffix); subjoined letters are illegal here; all other
    marks (shad, punctuation) ride along free. Returns None when the
    tail is not a legal syllable tail."""
    vow, sfx = [], []
    for c in tail:
        if c in _W_VOWEL:
            if sfx and sfx[-1] != _A_CHUNG:
                return None
            vow.append(_W_VOWEL[c])
        elif c in _W_BASE:
            if c not in _W_SUFFIX or len(sfx) >= 2:
                return None
            sfx.append(c)
        elif c in _W_SUBJ:
            return None
    return "".join(vow), sfx

def _wylie_try(syl, kind, root_char, root_at):
    """Attempt one parse of the syllable; return its Wylie or None."""
    j = root_at + 1
    stack_chars = []
    while j < len(syl) and syl[j] in _W_SUBJ:
        stack_chars.append(syl[j])
        j += 1
    tt = _wylie_tail(syl[j:])
    if tt is None:
        return None
    vow, sfx = tt
    stack = "".join(_W_SUBJ[c] for c in stack_chars)
    if kind == "super":
        head = _W_SUPER[syl[0]]
    elif kind == "prefix":
        p = _W_BASE[syl[0]]
        head = p[:-1] if p.endswith("a") else p
        if stack_chars and stack_chars[0] == _WA_SUBJ:
            head += "."  # d.wa, g.wa: the prefix stays disambiguated
    else:
        head = "".join(_W_SUBJ.get(c, "") for c in syl[:root_at])
    body = _W_BASE[root_char]
    has_a = body.endswith("a")
    # The cluster is head + root-minus-inherent-'a' + stack letters;
    # the 'a' itself surfaces after the stack when no vowel sign
    # replaces it (khyab, skad), and before an a-chung suffix when a
    # vowel sign follows it (ma'i, pa'i).
    cluster = head + (body[:-1] if has_a else body) + stack
    sfx_str = "".join(
        "'" if c == _A_CHUNG
        else _W_BASE[c][:-1] if _W_BASE[c].endswith("a") else _W_BASE[c]
        for c in sfx)
    if vow and sfx == [_A_CHUNG]:
        return cluster + ("a" if has_a else "") + "'" + vow
    if vow:
        return cluster + vow + sfx_str
    return cluster + ("a" if has_a else "") + sfx_str

def _wylie_syllable(syl):
    """Transliterate one Tibetan syllable (no tsheg) to Wylie."""
    syl = syl.strip("\u0f0d\u0f0e\u0f11\u0f08 ")
    if not syl:
        return ""
    base_at = [i for i, c in enumerate(syl) if c in _W_BASE]
    if not base_at:
        return syl if re.search(r"[a-zA-Z]", syl) else ""
    cands = []
    if syl[0] in _W_SUPER and len(syl) > 1 and syl[1] in _W_SUBJ_BASE \
            and syl[1] != _WA_SUBJ:
        cands.append(("super", _W_SUBJ_BASE[syl[1]], 1))
    root_cand = ("root", syl[base_at[0]], base_at[0])
    prefix_cand = None
    if base_at[0] == 0 and len(base_at) >= 2 and base_at[1] == 1 \
            and syl[0] in _W_PREFIX:
        prefix_cand = ("prefix", syl[1], 1)
    # Tie-breaks where orthography alone is ambiguous, resolved the
    # way the lexicon resolves them: a syllable ending in a-chung
    # whose second letter is a prefix-taking root (and not nga, the
    # suffix specialist) is prefix+root+' (dga', mda', bka'), not
    # root+suffix+'; and a three-base syllable with no vowel sign is
    # prefix+root+suffix (bdag, dbang), not root+suffix+suffix.
    ends_a = syl[-1] == _A_CHUNG and prefix_cand is not None \
        and syl[base_at[1]] != _NGA
    bare3 = len(base_at) == 3 and base_at == [0, 1, 2] \
        and not any(c in _W_VOWEL for c in syl) \
        and prefix_cand is not None
    if prefix_cand is not None and (ends_a or bare3):
        cands.extend([prefix_cand, root_cand])
    else:
        cands.append(root_cand)
        if prefix_cand is not None:
            cands.append(prefix_cand)
    for kind, root_char, root_at in cands:
        out = _wylie_try(syl, kind, root_char, root_at)
        if out is not None:
            return out
    # No legal parse (a fragment, e.g. a span cut mid-syllable):
    # render the first base with its raw stack/vowel letters.
    body = _W_BASE[syl[base_at[0]]]
    rest = "".join(_W_SUBJ.get(c) or _W_VOWEL.get(c) or ""
                   for c in syl[base_at[0] + 1:])
    return body + rest

_WYLIE_SPLIT = re.compile(r"[\u0f0b\s]+")

def to_wylie(text):
    """Transliterate Tibetan text to Wylie (space-separated syllables,
    punctuation dropped)."""
    if not text:
        return ""
    parts = []
    for syl in _WYLIE_SPLIT.split(text):
        if not syl:
            continue
        w = _wylie_syllable(syl)
        if w:
            parts.append(w)
    return " ".join(parts)

def _c6_markers_ok(mode, quote):
    """Layer (b) consequence structure, by the claim's inference mode:
    an implicit consequence needs a consequence marker AND a reason
    marker in the span; an explicit pervasion needs a pervasion term;
    a direct assertion needs nothing. (par thal / bar thal; phyir /
    pas; khyab.)"""
    if mode == "IMPLICIT_CONSEQUENCE":
        return (("\u0f54\u0f62\u0f0b\u0f50\u0f63" in quote)
                or ("\u0f56\u0f62\u0f0b\u0f50\u0f63" in quote)) \
            and (("\u0f55\u0fb1\u0f72\u0f62" in quote)
                 or ("\u0f54\u0f66\u0f0b" in quote))
    if mode == "EXPLICIT_PERVASION":
        return "\u0f41\u0fb1\u0f56" in quote
    if mode == "DIRECT_ASSERTION":
        return True
    return False

def _c6_term_match(claim, repair_target, quote):
    """Layer (b) term presence: the Wylie stems of the claimed reason
    and predicate — and of the subject too for a minor-premise repair
    (Purchok's own subject differs from the debate's in a pervasion
    repair, so it is not required there) — must occur in the quote's
    transliteration. Terms absent from the glossary are skipped.
    Returns True (all checked terms present), False (a checked term
    absent), or None (nothing checkable)."""
    terms = [claim.get("reason"), claim.get("predicate")]
    if repair_target == "MINOR_PREMISE":
        terms.append(claim.get("subject"))
    wylie = None
    checked = 0
    for term in terms:
        if not term:
            continue
        stems = _glossary_stems(term)
        if stems is None:
            continue
        checked += 1
        if wylie is None:
            wylie = " " + _wylie_norm(to_wylie(quote)) + " "
        if not _stems_present(wylie, stems):
            return False
    return True if checked else None

def _c6_window_voice(start, end):
    """Layer (c) fallback: scan the standing context window
    [start-400, end+300] of the etext. A downstream pervasion-denial
    (ma khyab ste / khyab pa ma byung) settles the span as denied;
    a rang lugs la marker upstream makes it own-voice; upstream
    opponent framing (kha cig na re and kin) without rang lugs makes
    it opponent-framed; otherwise no signal."""
    try:
        text = _etext()
    except OSError:
        return "NO_SIGNAL"
    down = text[end:end + 300]
    if "\u0f58\u0f0b\u0f41\u0fb1\u0f56\u0f0b\u0f66\u0f9f\u0f7a" in down \
            or "\u0f41\u0fb1\u0f56\u0f0b\u0f54\u0f0b\u0f58\u0f0b\u0f56\u0fb1\u0f74\u0f44" in down:
        return "WINDOW_DENIED"
    up = text[max(0, start - 400):start]
    if "\u0f62\u0f44\u0f0b\u0f63\u0f74\u0f42\u0f66\u0f0b\u0f63" in up:
        return "WINDOW_OWN"
    opp = any(m in up for m in (
        "\u0f41\u0f0b\u0f45\u0f72\u0f42\u0f0b\u0f53\u0f0b\u0f62\u0f7a",
        "\u0f42\u0f5e\u0f53\u0f0b\u0f51\u0f42\u0f0b\u0f53\u0f0b\u0f62\u0f7a",
        "\u0f63\u0f0b\u0f63\u0f0b\u0f53\u0f0b\u0f62\u0f7a",
        "\u0f5e\u0f7a\u0f66\u0f0b\u0f5f\u0f7a\u0f62\u0f0b\u0f53"))
    if opp:
        return "WINDOW_OPPONENT_FRAMED"
    return "NO_SIGNAL"

def _c6_voice_status(start, end):
    """Layer (c): (voice_status, registry_voice). A registry span
    whose [start,end] overlaps the cite's by at least 0.8 * the
    shorter span decides: OWN -> VERIFIED_OWN; OPPONENT_FRAMED /
    OPPONENT_BOUND / DENIED -> KNOWN_OPPONENT; CONTESTED ->
    CONTESTED. An UNCLASSIFIED match (or no match at all, including
    when the registry file is missing) falls through to the window
    scan."""
    best, best_ov = None, -1
    for span in _quote_registry():
        try:
            s1, e1 = int(span["start"]), int(span["end"])
        except (KeyError, TypeError, ValueError):
            continue
        ov = min(e1, end) - max(s1, start)
        shorter = max(1, min(e1 - s1, end - start))
        if ov >= 0.8 * shorter and ov > best_ov:
            best, best_ov = span, ov
    if best is not None:
        voice = best.get("voice")
        if voice == "OWN":
            return "VERIFIED_OWN", voice
        if voice in ("OPPONENT_FRAMED", "OPPONENT_BOUND", "DENIED"):
            return "KNOWN_OPPONENT", voice
        if voice == "CONTESTED":
            return "CONTESTED", voice
        return _c6_window_voice(start, end), voice
    return _c6_window_voice(start, end), None

def _modifier_present(modifier, quote):
    """TERM_SENSE_SHIFT gate: the payload's claimed modifier may be
    given in Tibetan script (substring-check the raw quote) or in
    Wylie (transliterate the quote and substring-check that)."""
    if not modifier:
        return False
    if any("\u0f00" <= c <= "\u0fff" for c in modifier):
        return modifier in quote
    return _wylie_norm(modifier) in _wylie_norm(to_wylie(quote))

# ---------------------------------------------------------------- ledger

class Commitment:
    def __init__(self, kind, key, polarity, turn, implicit=False, source=""):
        self.kind = kind            # 'atom' | 'perv'
        self.key = key              # atom: (subj, pred); perv: (antecedent, consequent)
        self.polarity = polarity
        self.turn = turn
        self.implicit = implicit
        self.source = source
    def sig(self):
        return (self.kind, self.key, self.polarity)

class Ledger:
    def __init__(self, root_thesis=None):
        self.explicit_atoms = set()     # (subj, pred, polarity) accepted via Accept / root
        self.commitments = []           # all Commitment records, in order
        self.history = []               # (turn, role, move, text)
        self.last_valid_d_text = None
        self.last_valid_d_move = None
        if root_thesis:
            s, p = norm_term(root_thesis["subject"]), norm_term(root_thesis["predicate"])
            self.explicit_atoms.add((s, p, True))
            self.commitments.append(Commitment("atom", (s, p), True, 0, False, "root thesis"))

    def atoms(self, upto_turn=None):
        return [c for c in self.commitments if c.kind == "atom" and (upto_turn is None or c.turn < upto_turn)]

    def pervs(self, upto_turn=None):
        return [c for c in self.commitments if c.kind == "perv" and (upto_turn is None or c.turn < upto_turn)]

    def add(self, kind, key, polarity, turn, implicit=False, source=""):
        key = (norm_term(key[0]), norm_term(key[1]))
        self.commitments.append(Commitment(kind, key, polarity, turn, implicit, source))
        return self.commitments[-1]

def closure(commitments):
    """Forward-chain atoms+pervasions. Returns (atoms_derived, deriv_info, contradiction).
    atoms_derived: dict (subj,pred,polarity) -> deriv record {steps, mt_edges, subjects, implicit}."""
    atoms = {}
    pervs_pos = []
    for c in commitments:
        if c.kind == "atom":
            k = (c.key[0], c.key[1], c.polarity)
            if k not in atoms:
                atoms[k] = {"steps": 0, "mt_edges": 0, "subjects": {c.key[0]}, "implicit": c.implicit}
        elif c.polarity:
            pervs_pos.append(c)
    # pervasion transitivity (positive)
    perv_set = {(c.key[0], c.key[1]): c for c in pervs_pos}
    changed = True
    while changed:
        changed = False
        for (a, b) in list(perv_set):
            for (b2, c2) in list(perv_set):
                if b == b2 and (a, c2) not in perv_set:
                    perv_set[(a, c2)] = perv_set[(a, b)]
                    changed = True
    changed = True
    while changed:
        changed = False
        for (z, y), pc in list(perv_set.items()):
            for (x, p, pol) in list(atoms):
                info = atoms[(x, p, pol)]
                if p == z and pol:  # modus ponens
                    nk = (x, y, True)
                    cand = {"steps": info["steps"] + 1, "mt_edges": info["mt_edges"],
                            "subjects": info["subjects"] | {x}, "implicit": info["implicit"] or pc.implicit}
                    if nk not in atoms or cand["steps"] < atoms[nk]["steps"]:
                        atoms[nk] = cand; changed = True
                if p == y and not pol:  # modus tollens (ldog khyab)
                    nk = (x, z, False)
                    cand = {"steps": info["steps"] + 1, "mt_edges": info["mt_edges"] + 1,
                            "subjects": info["subjects"] | {x}, "implicit": info["implicit"] or pc.implicit}
                    if nk not in atoms or cand["steps"] < atoms[nk]["steps"]:
                        atoms[nk] = cand; changed = True
    contradiction = None
    for (s, p, pol) in atoms:
        if (s, p, not pol) in atoms:
            contradiction = (s, p)
            break
    return atoms, perv_set, contradiction

# ---------------------------------------------------------------- telemetry (v1.4)
# Leaf weights (Argon 003): explicit Accept 0.2, NPV implicit minor 1.0,
# C3 witness classification 1.5, root thesis 0.0 (KB axiom). RNE assertions
# and Why-denial atoms are explicit acts: 0.2. Pervasion concessions from
# an Accept are explicit acts: 0.2. Denied pervasions (polarity False)
# are not rules and never enter a DAG.

def _leaf_for_commitment(c):
    """Return (leaf_id, kind_label, weight) for a commitment, or None if
    it cannot be a DAG leaf. leaf_id identifies the proposition, used
    for the B2 consumed-false-leaf set."""
    if c.kind == "atom":
        src = c.source or ""
        if src == "root thesis":
            return (("atom", c.key, c.polarity), "ROOT", 0.0)
        if src == "NPV implicit concession":
            return (("atom", c.key, c.polarity), "IMPLICIT", 1.0)
        if src == "D3 example":
            return (("atom", c.key, c.polarity), "C3", 1.5)
        return (("atom", c.key, c.polarity), "EXPLICIT", 0.2)
    if c.kind == "perv" and c.polarity:
        return (("perv", c.key), "EXPLICIT", 0.2)
    return None

def minimal_dag(prior_commitments, target):
    """Canonical minimal derivation of target atom (s, p, pol) from prior
    commitments, or None. Derivations minimise (leaf_weight_sum,
    rule_count, sorted leaf turns, sorted rule ids) — Argon 003's Knuth
    hyperpath key — so the result is unique and deterministic, and
    padded redundant leaves cannot inflate credit (a cheaper derivation
    always wins). Rules: perv transitivity, modus ponens, modus tollens.
    Returns dict(leaves=[(turn, kind, weight, leaf_id, commitment)],
    rules, contrapositive_steps, leaf_weight_sum, leaf_turns)."""
    import heapq
    # base nodes
    best = {}   # node -> deriv dict
    pq = []
    def offer(node, deriv):
        key = (round(deriv["leaf_weight_sum"], 6), deriv["rules"],
               tuple(sorted(deriv["leaf_turns"])),
               tuple(sorted(deriv["rule_ids"])))
        if node not in best or key < best[node]["key"]:
            deriv = dict(deriv); deriv["key"] = key
            best[node] = deriv
            heapq.heappush(pq, (key, node))
    for c in prior_commitments:
        lf = _leaf_for_commitment(c)
        if lf is None:
            continue
        leaf_id, kind, w = lf
        if c.kind == "atom":
            node = ("atom", c.key[0], c.key[1], c.polarity)
        else:
            node = ("perv", c.key[0], c.key[1])
        offer(node, {"leaves": [(c.turn, kind, w, leaf_id, c)],
                     "rules": 0, "contrapositive_steps": 0,
                     "leaf_weight_sum": w, "leaf_turns": [c.turn],
                     "rule_ids": []})
    def merge(d1, d2, rule_id, cp):
        seen = {}
        for leaf in d1["leaves"] + d2["leaves"]:
            seen[(leaf[0], leaf[3])] = leaf
        leaves = list(seen.values())
        return {"leaves": leaves,
                "rules": d1["rules"] + d2["rules"] + 1,
                "contrapositive_steps": d1["contrapositive_steps"] + d2["contrapositive_steps"] + (1 if cp else 0),
                "leaf_weight_sum": sum(l[2] for l in leaves),
                "leaf_turns": [l[0] for l in leaves],
                "rule_ids": sorted(set(d1["rule_ids"]) | set(d2["rule_ids"]) | {rule_id})}
    while pq:
        key, node = heapq.heappop(pq)
        if best[node]["key"] != key:
            continue
        d = best[node]
        # perv transitivity: perv(a,b) + perv(b,c) -> perv(a,c)
        if node[0] == "perv":
            a, b = node[1], node[2]
            for node2, d2 in list(best.items()):
                if node2[0] == "perv" and node2[1] == b:
                    offer(("perv", a, node2[2]),
                          merge(d, d2, "TR:%s->%s->%s" % (a, b, node2[2]), False))
        # modus ponens: atom(x,z,True) + perv(z,y) -> atom(x,y,True)
        if node[0] == "atom" and node[3] is True:
            x, z = node[1], node[2]
            for node2, d2 in list(best.items()):
                if node2[0] == "perv" and node2[1] == z:
                    offer(("atom", x, node2[2], True),
                          merge(d, d2, "MP:%s->%s" % (z, node2[2]), False))
        # modus tollens: atom(x,y,False) + perv(z,y) -> atom(x,z,False)
        if node[0] == "atom" and node[3] is False:
            x, y = node[1], node[2]
            for node2, d2 in list(best.items()):
                if node2[0] == "perv" and node2[2] == y:
                    offer(("atom", x, node2[1], False),
                          merge(d, d2, "MT:%s->%s" % (node2[1], y), True))
    tgt = ("atom", target[0], target[1], target[2])
    return best.get(tgt)

def _false_leaves_of_dag(dag, facts):
    """Leaf propositions the fact base positively contradicts."""
    out = set()
    for (turn, kind, w, leaf_id, c) in dag["leaves"]:
        if c.kind == "atom":
            if facts.eval_atom(c.key[0], c.key[1], c.polarity) is False:
                out.add(leaf_id)
        else:
            if facts.eval_pervasion(c.key[0], c.key[1]) is False:
                out.add(leaf_id)
    return out

# ---------------------------------------------------------------- scoring

def score_match(transcript, facts=None):
    facts = facts or Facts()
    ledger = Ledger(transcript.get("root_thesis"))
    turns = transcript["turns"]
    violations = []
    n_turns = len(turns)
    compliant_turns = set()
    fid_correct = fid_wrong = fid_unknown = 0
    unscored_rne = 0
    frame_state = {}        # v1.6: fl_id -> (branch, lock_turn)
    frame_locks = []        # v1.6 report: [{turn, fault_line, branch}]
    frame_flips = []        # v1.6 report: assertions against a locked frame
    fidelity_turns = []     # v1.6 report: every fid() call, with its turn
    contradictions = []
    c4_results = []
    prev_c = None            # last challenger Move
    prev_c_ok = True
    prev_c_illegal = False   # last challenger turn accrued any violation (incl. mistimed C3)
    prev_d = None            # last defender Move
    prev_d_text = None
    d_before_c3 = None       # defender move that a C3 refers back to
    forced_events = []
    telemetry_events = []
    consumed_false_leaves = set()
    root = transcript.get("root_thesis") or {}
    root_key = (norm_term(root.get("subject", "")), norm_term(root.get("predicate", "")))

    # v2.1 escape-challenge bookkeeping. accepted_at / denied_at are
    # the match's treatment record, keyed by proposition (subject,
    # predicate, polarity): accepted_at holds every thesis the
    # Defender's acts establish (Accepts, NPV-conceded minor premises,
    # RNE assertions, D-Concede reversals); denied_at holds every
    # thesis refused (Why on a C1, RNE/NPV on a C2) plus the negation
    # of every Accepted thesis. Trigger verification reads only these.
    accepted_at = {}
    denied_at = {}
    all_accepts = []        # (turn, s, p, pol): theses Accepted on C1/C2
    turns_by_no = {t.get("turn", i + 1): t for i, t in enumerate(turns)}
    match_has_payloads = any(isinstance(t, dict) and t.get("defender_payload")
                             for t in turns)
    canonical_norms = {norm_term(p) for p in facts.canonical_predicates}
    escape_episodes = []    # finalized episode report dicts, in order
    stood_triples = set()   # (s_pos, s_neg, pred, pol) pairs that stood
    open_episode = None
    c5_count = 0
    concede_first_count = 0
    ep_seq = 0
    # v2.2 quotation bookkeeping: finalized episode dicts; a pending
    # episode awaiting the Defender's response; an "await" record for
    # a deflection (voice claim / interpretation) awaiting the
    # optional refutation turn and the Defender's closing.
    quote_episodes = []
    qep_seq = 0
    c6_count = 0
    c6_spans = []           # (start, end, norm reason, norm predicate)
    interp_count = 0
    c6_pending = None
    c6_await = None
    # v2.3 debate-archive bookkeeping: per-ref verdicts and the
    # cross-match C5 log; both feed the report's archive_use block,
    # which exists only when at least one of them is non-empty.
    archive_refs = []
    archive_c5_log = []

    def fid(record):
        nonlocal fid_correct, fid_wrong, fid_unknown
        fidelity_turns.append({"turn": turn_no, "value": record})
        if record is None:
            fid_unknown += 1
        elif record:
            fid_correct += 1
        else:
            fid_wrong += 1

    def fid_item(score):
        """v2.1: fold one fractional Defender item (a D-Diff / D-Reason
        answer) into textual fidelity — `score` of its mass lands on
        the correct side, the rest on the incorrect side. Only called
        in matches with escape episodes, so legacy denominators are
        untouched."""
        nonlocal fid_correct, fid_wrong
        if score is None:
            return
        fidelity_turns.append({"turn": turn_no, "value": round(score, 3)})
        fid_correct += score
        fid_wrong += (1.0 - score)

    def perv_value_framed(z, y, zpol, ypol):
        """v1.6: effective value of a pervasion for assertion-side
        evaluation — the locked branch's value once a fault line is
        bound, else the static fact base."""
        fl = facts.fault_line_pervasion(z, y, zpol, ypol)
        if fl is None:
            return facts.eval_pervasion(z, y, zpol, ypol)
        fl_id, val_a, val_b = fl
        if fl_id in frame_state:
            return val_a if frame_state[fl_id][0] == "A" else val_b
        return facts.eval_pervasion(z, y, zpol, ypol)

    def defender_perv_fid(z, y, zpol, ypol, asserted):
        """v1.6: fidelity value for a Defender response asserting the
        stated pervasion's truth == asserted (Accept: True; NPV:
        False). On a contested pervasion, an unbound frame LOCKS to
        the branch consistent with the assertion and scores correct;
        against a locked frame, a mismatching assertion is a frame
        flip: recorded in frame_flips and scored incorrect."""
        fl = facts.fault_line_pervasion(z, y, zpol, ypol)
        if fl is None:
            v = facts.eval_pervasion(z, y, zpol, ypol)
            return None if v is None else (v == asserted)
        fl_id, val_a, val_b = fl
        if fl_id in frame_state:
            locked = val_a if frame_state[fl_id][0] == "A" else val_b
            if asserted != locked:
                frame_flips.append({"turn": turn_no, "fault_line": fl_id,
                                    "locked_branch": frame_state[fl_id][0],
                                    "asserted_value": asserted})
                return False
            return True
        branch = "A" if asserted == val_a else "B"
        frame_state[fl_id] = (branch, turn_no)
        frame_locks.append({"turn": turn_no, "fault_line": fl_id, "branch": branch})
        return True

    def note_contradiction(at_turn):
        """Record a ledger contradiction first arising at `at_turn`
        (the closure over commitments strictly before it does not yield
        the same pair). The standard Defender branch calls this after
        each move; v2.0 also calls it after the Type B/C opening
        ledger injection."""
        _atoms, _, contra = closure(ledger.commitments)
        if contra and (not contradictions or contradictions[-1]["pair"] != contra):
            prev_contra = None
            if at_turn > 1:
                _, _, prev_contra = closure([c for c in ledger.commitments if c.turn < at_turn])
            if prev_contra != contra:
                contradictions.append({"turn": at_turn, "pair": contra})

    def _episode_outcome(ep, end_turn):
        """Deterministic episode outcome over the window (answer turn,
        end_turn]: REFUTED when the Defender Accepted a thesis
        contradicting the answer's locked claims, or a
        DISTINCTION_WITHDRAWAL revision appears in a window payload;
        EPOS_RETRACTED when that withdrawal defeats a node tied to the
        positive entry while the denied entry is the root thesis;
        else STOOD. Returns (outcome, charge_turn)."""
        lo = ep["answer_turn"]
        window_accepts = [a for a in all_accepts if lo < a[0] <= end_turn]
        accept_refuted, refute_turn = False, None
        lock = ep.get("lock") or {}
        if lock.get("kind") == "diff":
            parts, pol = lock["parts"], lock["pol"]
            if len(parts) == 1:
                base = parts[0]
                for (tn, s, p, pl) in window_accepts:
                    if (s, p, pl) == (lock["s_neg"], base, pol) \
                            or (s, p, pl) == (lock["s_pos"], base, not pol):
                        accept_refuted, refute_turn = True, tn
                        break
            else:
                neg_parts = {}
                for (tn, s, p, pl) in window_accepts:
                    if s == lock["s_pos"] and pl is False and p in parts:
                        accept_refuted, refute_turn = True, tn
                        break
                    if s == lock["s_neg"] and pl is True and p in parts:
                        neg_parts[p] = tn
                if not accept_refuted and len(neg_parts) == len(parts):
                    accept_refuted, refute_turn = True, max(neg_parts.values())
        elif lock.get("kind") == "reason":
            R, P, tpol, s_neg = lock["reason"], lock["predicate"], \
                lock["thesis_pol"], lock["s_neg"]
            for (tn, s, p, pl) in window_accepts:
                if (s, p, pl) == (s_neg, R, False):
                    accept_refuted, refute_turn = True, tn
                    break
            if not accept_refuted:
                r_subs = {s for (tn, s, p, pl) in window_accepts if p == R and pl is True}
                p_subs = {s for (tn, s, p, pl) in window_accepts if p == P and pl == (not tpol)}
                common = r_subs & p_subs
                if common:
                    accept_refuted = True
                    refute_turn = max(tn for (tn, s, p, pl) in window_accepts if s in common)
        withdrawals = []
        for tn in range(lo + 1, end_turn + 1):
            pl = (turns_by_no.get(tn) or {}).get("defender_payload")
            if isinstance(pl, dict):
                rev = pl.get("state_revision")
                if isinstance(rev, dict) and rev.get("trigger") == "DISTINCTION_WITHDRAWAL":
                    withdrawals.append((tn, rev, pl))
        if withdrawals and ep["s_pos"] and root_key == (ep["s_neg"], ep["predicate"]):
            for (tn, rev, pl) in withdrawals:
                snap = pl.get("state_snapshot") or {}
                node = None
                for sec in ("definitions", "stances", "commitments"):
                    cand = (snap.get(sec) or {}).get(rev.get("defeated_node"))
                    if isinstance(cand, dict):
                        node = cand
                        break
                if node is None:
                    continue
                ntext = re.sub(r"\s+", " ", " ".join(
                    str(node.get(f, "")) for f in
                    ("term", "definiens", "text", "issue", "chosen_side"))).lower()
                if ep["s_pos"] in ntext and ep["predicate"] in ntext:
                    return "EPOS_RETRACTED", tn
        if accept_refuted:
            return "REFUTED", refute_turn
        if withdrawals:
            return "REFUTED", withdrawals[0][0]
        return "STOOD", None

    def _finalize_episode(ep, end_turn):
        """Close an episode: compute its outcome and revision-charge
        cross-check, append its report dict, and lock its triple when
        the distinction stood."""
        nonlocal open_episode
        resp = ep["defender_response"]
        if resp == "D_CONCEDE":
            outcome, charge_turn = "CONCEDED", ep["answer_turn"]
        elif resp == "D_UNFOUNDED":
            outcome, charge_turn = (None, None) if ep["trigger_valid"] \
                else ("UNFOUNDED", None)
        elif ep["answered"]:
            outcome, charge_turn = _episode_outcome(ep, end_turn)
        else:
            outcome, charge_turn = None, None
        charged = outcome in ("CONCEDED", "REFUTED", "EPOS_RETRACTED")
        if not charged:
            missing = False
        elif not match_has_payloads:
            missing = None
        else:
            pl = (turns_by_no.get(charge_turn) or {}).get("defender_payload")
            rev = pl.get("state_revision") if isinstance(pl, dict) else None
            missing = not (isinstance(rev, dict)
                           and rev.get("trigger") == "DISTINCTION_WITHDRAWAL")
        ep_report = {
            "episode_id": ep["episode_id"],
            "kind": ep["kind"],
            "mode": ep["mode"],
            "trigger_pair": {"t_pos": ep["t_pos"], "s_pos": ep["s_pos"],
                             "t_neg": ep["t_neg"], "s_neg": ep["s_neg"],
                             "predicate": ep["predicate"]},
            "trigger_valid": ep["trigger_valid"],
            "defender_response": resp,
            "stated": ep["stated"],
            "canonical_resolved": ep["canonical_resolved"],
            "kb_verification": ep["kb_verification"],
            "outcome": outcome,
            "revision_charged": charged,
            "revision_charge_missing": missing,
        }
        # v2.3: archive-armed episodes record how they were armed;
        # ordinary episodes carry no such key (legacy identity).
        if ep.get("arming") is not None:
            ep_report["arming"] = ep["arming"]
        escape_episodes.append(ep_report)
        if outcome == "STOOD":
            stood_triples.add(ep["triple"])
        if open_episode is ep:
            open_episode = None

    def _archive_node_text(node):
        """The searchable text of one EpistemicState node (the same
        fields the episode-outcome audit reads)."""
        return re.sub(r"\s+", " ", " ".join(
            str(node.get(f, "")) for f in
            ("term", "definiens", "text", "issue", "chosen_side"))).lower()

    def _verify_c5_archive(mv, ref):
        """v2.3: Tier 1 verification for an archive-armed C5 — the
        escape_ref names an archive entry and t_pos is null, so the
        positive side is claimed from the bank instead of this match's
        ledger. Returns _verify_c5's info shape with mode "ARCHIVE"
        and arming ARCHIVE_TIER1 (all conditions hold) or
        ARCHIVE_FAILED (the challenge then takes the ordinary
        unfounded path)."""
        s_neg = norm_term(mv.subject)
        pred, pol = mv.predicate, mv.pred_pol
        if mv.kind == "C5B":
            # The pair's shared proposition is the DENIED thesis (the
            # negation of the thesis the C5b surface states), exactly
            # as in the intra-match C5B verification.
            eff_pol = not pol
            want_subj = None
        else:
            eff_pol = pol
            want_subj = norm_term(mv.pos_subject)
        t_neg = ref.get("t_neg")
        info = {"mode": "ARCHIVE", "valid": False,
                "s_pos": want_subj, "s_neg": s_neg,
                "predicate": pred, "t_pos": None,
                "t_neg": t_neg if (isinstance(t_neg, int)
                                   and not isinstance(t_neg, bool)) else None,
                "triple": (want_subj, s_neg, pred, eff_pol),
                "arming": "ARCHIVE_FAILED"}
        entry_id = ref.get("archive_entry")
        bank = _debate_archive()
        if bank is None:
            return info
        entry = bank.get(entry_id) if isinstance(entry_id, str) else None
        if entry is None:
            return info
        # (1) The archived atom: a ledger-snapshot commitment of the
        # pair's shared proposition. For C5B the archived subject is
        # the one the entry's trigger names, else any matching atom.
        if mv.kind == "C5B":
            trig = ((entry.get("trigger") or {}).get("concrete") or {})
            if trig.get("subject"):
                want_subj = norm_term(str(trig["subject"]))
        atom_subj = None
        for a in ((entry.get("ledger_snapshot") or {})
                  .get("committed_atoms") or []):
            if not isinstance(a, dict):
                continue
            a_s = norm_term(str(a.get("s", "")))
            if norm_term(str(a.get("p", ""))) != pred \
                    or a.get("polarity") != eff_pol:
                continue
            if want_subj is not None and a_s != want_subj:
                continue
            atom_subj = a_s
            break
        if atom_subj is None:
            return info
        info["s_pos"] = atom_subj
        info["triple"] = (atom_subj, s_neg, pred, eff_pol)
        # (2) Version continuity: the transcript's Defender version is
        # among the versions the entry troubled, OR the atom stands in
        # the Defender's turn-0 state — its first payload's snapshot
        # names both the archived subject and the predicate.
        continuity = transcript.get("defender_version") in \
            ((entry.get("provenance") or {})
             .get("defender_version_troubled") or [])
        if not continuity:
            for t0 in turns:
                if t0.get("role") != "defender":
                    continue
                pl0 = t0.get("defender_payload")
                if not isinstance(pl0, dict):
                    continue
                snap = pl0.get("state_snapshot") or {}
                joined = " ".join(
                    _archive_node_text(node)
                    for sec in ("definitions", "stances", "commitments")
                    for node in ((snap.get(sec) or {}).values())
                    if isinstance(node, dict))
                continuity = atom_subj in joined and pred in joined
                break
        if not continuity:
            return info
        # (3) No intervening revision: no earlier Defender payload in
        # this match defeats a node whose text names the pair (the
        # Defender has not already revised that stance away).
        for i0, t0 in enumerate(turns):
            if t0.get("turn", i0 + 1) >= turn_no \
                    or t0.get("role") != "defender":
                continue
            pl0 = t0.get("defender_payload")
            if not isinstance(pl0, dict):
                continue
            rev = pl0.get("state_revision")
            if not isinstance(rev, dict) or not rev.get("defeated_node"):
                continue
            snap = pl0.get("state_snapshot") or {}
            node = None
            for sec in ("definitions", "stances", "commitments"):
                cand = (snap.get(sec) or {}).get(rev.get("defeated_node"))
                if isinstance(cand, dict):
                    node = cand
                    break
            if node is not None:
                ntext = _archive_node_text(node)
                if atom_subj in ntext and pred in ntext:
                    return info
        info["valid"] = True
        info["arming"] = "ARCHIVE_TIER1"
        return info

    _SLOT_RE = re.compile(r"\[(\$[A-Za-z0-9_]+)\]")

    def _move_sig(m):
        """The archive-fidelity signature of a parsed Challenger move:
        kind, subject, (predicate, polarity), (reason, polarity)."""
        subj = getattr(m, "subject", None)
        pred = getattr(m, "predicate", None)
        reason = getattr(m, "reason", None)
        return (m.kind,
                norm_term(subj) if subj else None,
                (norm_term(pred), getattr(m, "pred_pol", None))
                if pred else None,
                (norm_term(reason), getattr(m, "reason_pol", None))
                if reason else None)

    def _check_archive_ref(t, mv):
        """v2.3: verify one Challenger turn's archive_ref against the
        bank (existence, step range, template fidelity under the
        substitution map, transferable-division discipline) and
        return its archive_use record. An invalid ref is never a
        violation — the turn has already been scored on its merits."""
        ref = t.get("archive_ref") or {}
        entry_id = ref.get("entry_id")
        rec = {"turn": turn_no, "entry_id": entry_id,
               "valid": False, "reason": None}
        bank = _debate_archive()
        if bank is None:
            rec["reason"] = "unverifiable: debate archive missing"
            return rec
        entry = bank.get(entry_id) if isinstance(entry_id, str) else None
        if entry is None:
            rec["reason"] = "entry not in debate archive"
            return rec
        seq = entry.get("sequence") or {}
        steps = seq.get("steps") or []
        slots = seq.get("slots") or {}
        smap = ref.get("substitution_map") or {}
        step = None
        if not steps:
            # A summary-only entry distils no playable steps: only a
            # confirm-anchor ref (step 1 by convention) is step-valid,
            # and there is no template to check fidelity against.
            if ref.get("mode") != "CONFIRM_POSITIVE_ANCHOR":
                rec["reason"] = ("summary-only entry admits only "
                                 "CONFIRM_POSITIVE_ANCHOR refs")
                return rec
        else:
            step_idx = ref.get("step_idx")
            if not (isinstance(step_idx, int)
                    and not isinstance(step_idx, bool)
                    and 1 <= step_idx <= len(steps)) \
                    or not isinstance(steps[step_idx - 1], dict):
                rec["reason"] = "step_idx out of range"
                return rec
            step = steps[step_idx - 1]
        # Division check: a subject slot replaced by a subject outside
        # the entry's transferable divisions breaks the replay licence
        # (Argon 012 adaptation invariants). Unmapped slots take their
        # bound values and are not substitutions; an entry listing no
        # divisions admits no subject substitution at all.
        divisions = {norm_term(x) for x in
                     ((entry.get("applicability") or {})
                      .get("transferable_divisions") or [])}
        for slot, sval in slots.items():
            if not isinstance(sval, dict):
                continue
            bound = sval.get("bound_value")
            if slot not in smap or bound is None:
                continue
            sub = smap[slot]
            if norm_term(str(sub)) == norm_term(str(bound)):
                continue
            is_subject_slot = "subject" in (sval.get("role") or "") \
                or slot == "$S" or slot.startswith("$S_")
            if not is_subject_slot:
                continue
            if not divisions \
                    or not (_ancestors(facts, str(sub)) & divisions):
                rec["reason"] = ("substituted subject outside the entry's "
                                 "transferable divisions: " + slot)
                return rec
        if step is not None:
            # Fidelity: instantiate the stored template under the
            # substitution map (unmapped slots fall back to their
            # bound values) and compare the parsed moves.
            inst = step.get("template") or ""
            for slot in _SLOT_RE.findall(inst):
                val = smap.get(slot)
                if val is None:
                    sv = slots.get(slot)
                    val = sv.get("bound_value") \
                        if isinstance(sv, dict) else None
                inst = inst.replace("[%s]" % slot,
                                    str(val) if val is not None else slot)
            imv, _iok, _ipr = parse_challenger(inst)
            if _move_sig(imv) != _move_sig(mv):
                rec["reason"] = ("move does not match the stored step "
                                 "under the substitution map")
                return rec
        rec["valid"] = True
        return rec

    def _verify_c5(mv, ref):
        """Trigger verification for an escape-challenge, from the
        match's treatment record alone. Returns the info the episode
        skeleton and the report's trigger_pair are built from."""
        s_neg = norm_term(mv.subject)
        pred, pol = mv.predicate, mv.pred_pol
        info = {"mode": None, "valid": False, "s_pos": None, "s_neg": s_neg,
                "predicate": pred, "t_pos": None, "t_neg": None,
                "triple": (None, s_neg, pred, pol), "arming": None}
        if isinstance(ref, dict) and ref.get("archive_entry") \
                and ref.get("t_pos") is None:
            # v2.3: the positive side is claimed from the archive.
            return _verify_c5_archive(mv, ref)
        if mv.kind == "C5B":
            denied_pol = not pol
            info["triple"] = (None, s_neg, pred, denied_pol)
            if not isinstance(ref, dict) or ref.get("kind") != "C5b":
                return info
            t_neg = ref.get("t_neg")
            if not (isinstance(t_neg, int) and not isinstance(t_neg, bool)):
                return info
            info["t_neg"] = t_neg
            info["valid"] = t_neg in denied_at.get((s_neg, pred, denied_pol), [])
            s_pos, best_turn = None, None
            for (s, p, pl), tlist in accepted_at.items():
                if p == pred and pl == denied_pol and s != s_neg and tlist:
                    if best_turn is None or min(tlist) < best_turn:
                        best_turn, s_pos = min(tlist), s
            info["s_pos"] = s_pos
            info["triple"] = (s_pos, s_neg, pred, denied_pol)
            return info
        # C5A
        s_pos = norm_term(mv.pos_subject)
        info["s_pos"] = s_pos
        info["triple"] = (s_pos, s_neg, pred, pol)
        if not isinstance(ref, dict) or ref.get("kind") != "C5a":
            return info
        t_pos, t_neg = ref.get("t_pos"), ref.get("t_neg")
        if not (isinstance(t_pos, int) and not isinstance(t_pos, bool)
                and isinstance(t_neg, int) and not isinstance(t_neg, bool)):
            return info
        info["t_pos"], info["t_neg"] = t_pos, t_neg
        prev_c_map, def_move_map = _history_maps(ledger.history)
        if t_pos == t_neg:
            # Mode 3: the referenced turn is itself the split — an RNE
            # response, or a payload sense ruling. The pair's subjects
            # and predicate are taken from the challenge text.
            info["mode"] = 3
            dmv = def_move_map.get(t_neg)
            sense = False
            pl = (turns_by_no.get(t_neg) or {}).get("defender_payload")
            if isinstance(pl, dict):
                sense = ((pl.get("derivation") or {}).get("gate_audit")
                         or {}).get("override") == "SENSE_RULING"
            info["valid"] = bool((dmv is not None and dmv.kind == "D_RNE") or sense)
            return info
        pc_pos, pc_neg = prev_c_map.get(t_pos), prev_c_map.get(t_neg)
        if pc_pos is not None and pc_neg is not None \
                and pc_pos.kind == "C2" and pc_neg.kind == "C2" \
                and pc_pos.reason and pc_pos.reason == pc_neg.reason:
            info["mode"] = 2
        else:
            info["mode"] = 1
        if s_pos == s_neg:
            return info
        if t_pos not in accepted_at.get((s_pos, pred, pol), []):
            return info
        if t_neg not in denied_at.get((s_neg, pred, pol), []):
            return info
        shared = _ancestors(facts, s_pos) & _ancestors(facts, s_neg)
        if not shared:
            canon = {norm_term(q) for q in facts.canonical_predicates}
            shared = {q for q in canon
                      if (s_pos, q, True) in accepted_at
                      and (s_neg, q, True) in accepted_at}
        info["valid"] = bool(shared)
        return info

    # ------------------------------------------------ v2.2 helpers
    def _c6_report_ep(ep, outcome, cascade, deflection_failed="absent"):
        d = {
            "episode_id": ep["episode_id"],
            "repair_target": ep["repair_target"],
            "target_turn": ep["target_turn"],
            "claim": {"subject": ep["claim"].get("subject"),
                      "predicate": ep["claim"].get("predicate"),
                      "reason": ep["claim"].get("reason")},
            "span": {"start": ep["span"][0], "end": ep["span"][1]},
            "substring_verified": ep["substring_verified"],
            "markers_ok": ep["markers_ok"],
            "term_match": ep["term_match"],
            "voice_status": ep["voice_status"],
            "registry_voice": ep["registry_voice"],
            "defender_response": ep["defender_response"],
            "context_gate": ep["context_gate"],
            "refute_grounded": ep["refute_grounded"],
            "outcome": outcome,
            "cascade_applied": cascade,
        }
        if deflection_failed != "absent":
            d["deflection_failed"] = deflection_failed
        quote_episodes.append(d)

    def _c6_cascade(ep):
        """The quotation stands in the ledger: inject the pervasion
        (tagged 'C6 text-established') and, for a pervasion repair,
        the cascaded thesis on the target consequence's subject."""
        claim = ep["claim"]
        ledger.add("perv", (claim.get("reason"), claim.get("predicate")),
                   True, ep["c6_turn"], False, "C6 text-established")
        if ep["repair_target"] == "PERVASION":
            ledger.add("atom", (claim.get("subject"), claim.get("predicate")),
                       True, ep["c6_turn"], False, "C6 text-established")
            ledger.explicit_atoms.add((norm_term(claim.get("subject") or ""),
                                       norm_term(claim.get("predicate") or ""),
                                       True))
        note_contradiction(ep["c6_turn"])

    def _c6_context_gate(ep, t):
        """The deterministic gate on a Defender deflection's passage
        evidence: a context_cite whose substring verifies AND which
        either lies inside the quotation's context window
        [start-400, end+300] or itself contains the Wylie stems of
        both the claimed reason and the claimed predicate."""
        cc = t.get("context_cite")
        if not isinstance(cc, dict) or not _verify_text_cite(cc):
            return "fail"
        s, e = cc.get("start"), cc.get("end")
        cs, ce = ep["span"]
        if isinstance(s, int) and isinstance(e, int) \
                and isinstance(cs, int) and isinstance(ce, int) \
                and cs - 400 <= s and e <= ce + 300:
            return "pass"
        stems_r = _glossary_stems(ep["claim"].get("reason"))
        stems_p = _glossary_stems(ep["claim"].get("predicate"))
        if stems_r and stems_p:
            w = " " + _wylie_norm(to_wylie(cc.get("quote") or "")) + " "
            if _stems_present(w, stems_r) and _stems_present(w, stems_p):
                return "pass"
        return "fail"

    def _c6_answer(ep, t, text, violate):
        """Score the Defender's response to a verified quotation.
        Exactly three forms are legal; anything else leaves the
        episode UNANSWERED with the cascade applied (the Defender
        failed to answer an authority move lawfully)."""
        nonlocal interp_count, c6_await
        claim = ep["claim"]
        if text.startswith("Accept. By the authority of the text,"):
            kind = "ACCEPT_QUOTE"
        elif text.startswith("That consequence does not establish the pervasion"):
            kind = "VOICE"
        elif text.startswith("I accept the passage, but it does not establish"):
            kind = "INTERPRET"
        else:
            kind = "OTHER"
        ep["defender_response"] = kind
        if kind == "OTHER":
            violate("c6_illegal_response: a verified quotation must be answered by accepting it, claiming an opponent's voice, or giving an interpretation")
            _c6_report_ep(ep, "UNANSWERED", True)
            _c6_cascade(ep)
            return
        if kind == "ACCEPT_QUOTE":
            if ep["repair_target"] == "PERVASION":
                v = facts.eval_pervasion(claim.get("reason"),
                                         claim.get("predicate"))
            else:
                v = facts.eval_atom(claim.get("subject"),
                                    claim.get("reason"))
            if ep["voice_status"] in ("KNOWN_OPPONENT", "WINDOW_DENIED") \
                    or v is False:
                # over-acceptance: an opponent's consequence or a
                # false pervasion swallowed whole corrupts the ledger.
                fid_item(0.0)
                _c6_report_ep(ep, "OVER_ACCEPTANCE", True)
            else:
                fid_item(1.0)
                _c6_report_ep(ep, "ACCEPTED", True)
            _c6_cascade(ep)
            return
        if kind == "VOICE":
            gate = _c6_context_gate(ep, t)
            ep["context_gate"] = gate
            if gate != "pass":
                violate("unsupported_voice_claim: an opponent-voice claim needs a verified passage marker inside the quotation's context window (or itself containing both terms)")
                _c6_report_ep(ep, "QUOTE_UPHELD", True, deflection_failed=True)
                _c6_cascade(ep)
                return
            vs = ep["voice_status"]
            if vs in ("VERIFIED_OWN", "WINDOW_OWN"):
                fid_item(0.0)
                _c6_report_ep(ep, "QUOTE_UPHELD", True, deflection_failed=True)
                _c6_cascade(ep)
                return
            if vs in ("KNOWN_OPPONENT", "WINDOW_DENIED"):
                fid_item(1.0)
                _c6_report_ep(ep, "VOICE_UPHELD", False, deflection_failed=False)
                return
            c6_await = {"ep": ep, "kind": "VOICE"}
            return
        # INTERPRET: rides the sense-ruling channel (cap 2 per match).
        interp_count += 1
        ep["context_gate"] = _c6_context_gate(ep, t)
        if interp_count > 2:
            violate("interp_cap: at most two interpretation/sense-ruling deflections per match")
            _c6_report_ep(ep, "QUOTE_UPHELD", True, deflection_failed=True)
            _c6_cascade(ep)
            return
        if interp_count == 2 and ep["context_gate"] != "pass":
            violate("interp_second_no_contrast: a second interpretation in a match needs a verified passage where Purchok himself contrasts the two senses")
            _c6_report_ep(ep, "QUOTE_UPHELD", True, deflection_failed=True)
            _c6_cascade(ep)
            return
        pl = t.get("defender_payload")
        deriv = (pl.get("derivation") or {}) if isinstance(pl, dict) else {}
        if deriv.get("interp_ground") == "TERM_SENSE_SHIFT":
            mod = deriv.get("claimed_modifier_tibetan")
            cite = (turns_by_no.get(ep["c6_turn"]) or {}).get("text_cite") or {}
            if mod and not _modifier_present(mod, cite.get("quote") or ""):
                _c6_report_ep(ep, "QUOTE_UPHELD", True, deflection_failed=True)
                _c6_cascade(ep)
                return
        c6_await = {"ep": ep, "kind": "INTERPRET"}
        return

    # v2.0: match type (absent/invalid = "A") and opening bookkeeping.
    match_type = transcript.get("match_type") or "A"
    if match_type not in ("B", "C"):
        match_type = "A"
    text_cites = []
    type_open = {}

    for idx, t in enumerate(turns):
        turn_no = t.get("turn", idx + 1)
        role, text = t["role"], t["text"]
        turn_ok = True
        def violate(msg):
            nonlocal turn_ok
            turn_ok = False
            violations.append({"turn": turn_no, "role": role, "violation": msg, "text": text[:120]})
        # v2.0: text_cite verification (all match types, either role).
        if t.get("text_cite") is not None:
            cite_ok = _verify_text_cite(t.get("text_cite"))
            text_cites.append({"turn": turn_no, "verified": cite_ok})
            if not cite_ok:
                violate("text_cite failed verification against sources/S06857E4_blo_rig.txt")
        # v2.0: Type B/C opening turns (indices 0-1) follow the opening
        # grammar, not C1-C4 / D-forms; the standard engine resumes at
        # index 2 with the opening commitments injected into the ledger.
        if match_type in ("B", "C") and idx == 0:
            mv, probs = parse_opening_demand(match_type, text)
            for p in probs:
                violate(p)
            type_open["demand_move"] = mv
            prev_c, prev_c_ok = mv, mv.kind != "INVALID"
            prev_c_illegal = not turn_ok
            ledger.history.append((turn_no, role, mv, text))
            if turn_ok:
                compliant_turns.add(idx)
            continue
        if match_type in ("B", "C") and idx == 1:
            mv, probs, data = parse_opening_statement(match_type, text, prev_c)
            for p in probs:
                violate(p)
            type_open.update(data)
            type_open["opening_turn"] = turn_no
            demand_mv = type_open.get("demand_move")
            if match_type == "B":
                S = getattr(demand_mv, "subject", None) or data.get("subject")
                P = getattr(demand_mv, "predicate", None) or data.get("predicate")
                R = data.get("reason")
                type_open.update({"subject": S, "predicate": P, "reason": R})
                if S and P and R:
                    # The reason statement concedes, in order: the
                    # minor premise, the pervasion, the thesis. These
                    # are explicit Defender acts (not implicit), tagged
                    # distinctly from in-play concessions.
                    ledger.add("atom", (S, R), True, turn_no, False,
                               "type B reason (minor premise)")
                    ledger.add("perv", (R, P), True, turn_no, False,
                               "type B reason (pervasion)")
                    ledger.add("atom", (S, P), True, turn_no, False,
                               "type B reason (thesis)")
                    ledger.explicit_atoms.add((norm_term(S), norm_term(P), True))
                    note_contradiction(turn_no)
            else:
                T = data.get("term")
                if T and data.get("illustration"):
                    # Illustration atom first, then one atom per
                    # stated division (same order as the justification
                    # concession counting).
                    ledger.add("atom", (data["illustration"], T), True, turn_no,
                               False, "type C meaning (illustration)")
                    ledger.explicit_atoms.add((norm_term(data["illustration"]),
                                               norm_term(T), True))
                    for div in data.get("divisions") or []:
                        ledger.add("atom", (div, T), True, turn_no, False,
                                   "type C meaning (division)")
                        ledger.explicit_atoms.add((norm_term(div), norm_term(T), True))
                    note_contradiction(turn_no)
            if mv.kind not in ("INVALID",):
                ledger.last_valid_d_text = text
                ledger.last_valid_d_move = mv
            prev_d, prev_d_text = mv, text
            ledger.history.append((turn_no, role, mv, text))
            if turn_ok:
                compliant_turns.add(idx)
            continue
        if role == "challenger":
            mv, ok, probs = parse_challenger(text)
            if not ok:
                violate("challenger syntax: " + "; ".join(probs))
            # v2.3: an archive_ref is verified against the bank and
            # recorded for the archive_use block; it never adds a
            # violation and never changes the turn's scoring.
            if isinstance(t.get("archive_ref"), dict):
                archive_refs.append(_check_archive_ref(t, mv))
            if mv.kind == "INVALID":
                prev_c, prev_c_ok = mv, False
            else:
                if mv.kind == "C3":
                    if not prev_d or prev_d.kind not in ("D_RNE", "D_NPV"):
                        violate("C3 not immediately after 'Reason not established' or 'No pervasion'")
                    else:
                        d_before_c3 = prev_d
                if mv.kind == "C4":
                    # evaluate against ledger: last defender move's commitments vs prior closure
                    res = evaluate_c4(mv.call, ledger, facts, root_key, prev_d)
                    c4_results.append({"turn": turn_no, "call": mv.call, "valid": res["valid"],
                                       "reason": res["reason"], "trap_complexity": res.get("trap_complexity", 0.0)})
                    if not res["valid"] and not mv.demonstration:
                        pass  # already noted at parse
                    prev_c4 = res
                    mv.c4_valid = res["valid"]
                if mv.kind in ("C1", "C2"):
                    # textual fidelity of the asserted propositions
                    fid(facts.eval_atom(mv.subject, mv.predicate, mv.pred_pol))
                    if mv.kind == "C2":
                        fid(facts.eval_atom(mv.subject, mv.reason, mv.reason_pol))
                        fid(perv_value_framed(mv.reason, mv.predicate, mv.reason_pol, mv.pred_pol))
                if mv.kind == "C2" and open_episode is not None and open_episode["answered"]:
                    # v2.1: a refutation consequence inside an open
                    # episode's window (the window closes after the
                    # Defender's reply to the second one).
                    open_episode["c2_count"] += 1
                if mv.kind == "C6_REFUTE" and c6_await is not None:
                    # v2.2: the refutation turn inside a quotation
                    # episode — its counter-citation is verified and
                    # recorded; it does not move deterministic outcomes.
                    cc = t.get("counter_cite")
                    c6_await["ep"]["refute_grounded"] = \
                        bool(_verify_text_cite(cc)) if isinstance(cc, dict) else None
                if mv.kind in ("C5A", "C5B"):
                    # v2.1 escape-challenge: a still-open episode's
                    # window is truncated by the new challenge.
                    if open_episode is not None:
                        _finalize_episode(open_episode, turn_no)
                    info = _verify_c5(mv, t.get("escape_ref"))
                    if c5_count - concede_first_count >= 2:
                        violate("c5_cap: the two-challenge budget for this match is already spent (a token is refunded only by an immediate concession)")
                    c5_count += 1
                    if info["triple"] in stood_triples:
                        violate("c5_rechallenge_locked: this (S_pos, S_neg, P) pair already stood against an escape-challenge in this match")
                    if not info["valid"]:
                        violate("unfounded_c5: the named accepted/denied pair is not in this match's ledger, or fails the proximity guard")
                    ep_seq += 1
                    open_episode = {
                        "episode_id": ep_seq,
                        "kind": "C5a" if mv.kind == "C5A" else "C5b",
                        "mode": info["mode"],
                        "trigger_valid": info["valid"],
                        "s_pos": info["s_pos"], "s_neg": info["s_neg"],
                        "predicate": info["predicate"],
                        "t_pos": info["t_pos"], "t_neg": info["t_neg"],
                        "triple": info["triple"],
                        "defender_response": "OTHER",
                        "answered": False, "awaiting_answer": True,
                        "answer_turn": None, "stated": None,
                        "canonical_resolved": None, "kb_verification": None,
                        "lock": None, "c2_count": 0,
                        "arming": info.get("arming"),
                    }
                    if info.get("arming") is not None:
                        archive_c5_log.append({
                            "episode_id": ep_seq,
                            "entry_id": (t.get("escape_ref") or {}).get("archive_entry"),
                            "tier1_pass": bool(info["valid"])})
                if mv.kind in ("C6_PERV", "C6_MINOR"):
                    # v2.2 quotation move: context legality first,
                    # then the deterministic citation layers; a
                    # verified episode waits for the Defender's answer.
                    if c6_pending is not None:
                        _c6_report_ep(c6_pending, "UNANSWERED", True)
                        _c6_cascade(c6_pending)
                        c6_pending = None
                    if c6_await is not None:
                        _c6_report_ep(c6_await["ep"], "PENDING_JUDGE", False,
                                      deflection_failed=None)
                        c6_await = None
                    c6_count += 1
                    if c6_count > 2:
                        violate("c6_cap: at most two quotation moves per match")
                    target = "PERVASION" if mv.kind == "C6_PERV" else "MINOR_PREMISE"
                    qc = t.get("quote_claim") or {}
                    cite = t.get("text_cite") or {}
                    claim = {"subject": qc.get("subject"),
                             "predicate": qc.get("predicate"),
                             "reason": qc.get("reason")}
                    qep_seq += 1
                    ep = {"episode_id": qep_seq, "c6_turn": turn_no,
                          "repair_target": target,
                          "target_turn": qc.get("target_turn"),
                          "claim": claim,
                          "span": (cite.get("start"), cite.get("end")),
                          "substring_verified": False, "markers_ok": False,
                          "term_match": None, "voice_status": "NOT_EVALUATED",
                          "registry_voice": None, "defender_response": None,
                          "context_gate": None, "refute_grounded": None}
                    # Context: the named target turn must be a C2
                    # whose parsed slots match the claim, answered by
                    # the matching denial on the turn right before
                    # this C6 — either the C2 directly precedes the
                    # denial, or the C2 is a refutation consequence
                    # inside an open escape episode.
                    target_ok = False
                    tt_no = qc.get("target_turn")
                    tt_idx = None
                    if isinstance(tt_no, int) and not isinstance(tt_no, bool):
                        for j, tj in enumerate(turns):
                            if tj.get("turn", j + 1) == tt_no:
                                tt_idx = j
                                break
                    if tt_idx is not None and idx >= 2 \
                            and turns[tt_idx].get("role") == "challenger":
                        tmv, _tok, _tpr = parse_challenger(
                            turns[tt_idx].get("text") or "")
                        dtn = turns[idx - 1]
                        dmv, _dok, _dpr = parse_defender(
                            dtn.get("text") or "",
                            {"prev_defender_text": None})
                        want = "D_NPV" if target == "PERVASION" else "D_RNE"
                        if tmv is not None and tmv.kind == "C2" \
                                and dtn.get("role") == "defender" \
                                and dmv is not None and dmv.kind == want \
                                and norm_term(tmv.subject or "") == norm_term(claim["subject"] or "") \
                                and norm_term(tmv.predicate or "") == norm_term(claim["predicate"] or "") \
                                and norm_term(tmv.reason or "") == norm_term(claim["reason"] or ""):
                            if tt_idx == idx - 2:
                                target_ok = True
                            elif open_episode is not None \
                                    and open_episode.get("answer_turn") is not None \
                                    and turns[tt_idx].get("turn", tt_idx + 1) > open_episode["answer_turn"]:
                                target_ok = True
                    if not target_ok:
                        violate("c6_context: a quotation move is legal only as a repair of the consequence it names, immediately after the matching denial")
                        _c6_report_ep(ep, "INVALID_CONTEXT", False)
                    else:
                        cs, ce = ep["span"]
                        for (s0, e0, r0, p0) in c6_spans:
                            if all(isinstance(x, int) and not isinstance(x, bool)
                                   for x in (cs, ce, s0, e0)):
                                ov = min(e0, ce) - max(s0, cs)
                                if ov > 0.5 * max(1, min(e0 - s0, ce - cs)) \
                                        and r0 == norm_term(claim["reason"] or "") \
                                        and p0 == norm_term(claim["predicate"] or ""):
                                    violate("c6_span_reuse: the same span may not be re-quoted for the same pervasion in one match")
                        c6_spans.append((cs, ce,
                                         norm_term(claim["reason"] or ""),
                                         norm_term(claim["predicate"] or "")))
                        ep["substring_verified"] = bool(
                            cite and _verify_text_cite(cite))
                        if not ep["substring_verified"]:
                            _c6_report_ep(ep, "MIS_CITATION", False)
                        else:
                            ep["markers_ok"] = _c6_markers_ok(
                                qc.get("inference_mode"),
                                cite.get("quote") or "")
                            ep["term_match"] = _c6_term_match(
                                claim, target, cite.get("quote") or "")
                            if not ep["markers_ok"] or ep["term_match"] is False:
                                _c6_report_ep(ep, "MIS_CITATION", False)
                            else:
                                ep["voice_status"], ep["registry_voice"] = \
                                    _c6_voice_status(cs, ce)
                                c6_pending = ep
                prev_c, prev_c_ok = mv, ok
            prev_c_illegal = not turn_ok
            ledger.history.append((turn_no, role, mv, text))
        else:  # defender
            # v2.2: the answer to a verified quotation — and the
            # closing turn after a deflection — follow their own
            # grammar, intercepted before everything else.
            if c6_pending is not None:
                ep = c6_pending
                c6_pending = None
                _c6_answer(ep, t, text, violate)
                mv, _ok, _pr = parse_defender(
                    text, {"prev_defender_text": ledger.last_valid_d_text})
                if mv.kind not in ("INVALID",):
                    ledger.last_valid_d_text = text
                    ledger.last_valid_d_move = mv
                prev_d, prev_d_text = mv, text
                ledger.history.append((turn_no, role, mv, text))
                if turn_ok:
                    compliant_turns.add(idx)
                continue
            if c6_await is not None:
                ep = c6_await["ep"]
                c6_await = None
                if text.startswith("Accept. By the authority of the text,"):
                    fid_item(1.0)
                    _c6_report_ep(ep, "UPHELD_AFTER_REFUTE", True,
                                  deflection_failed=True)
                    _c6_cascade(ep)
                else:
                    # A hold ("I hold the voice claim." / "I hold the
                    # interpretation.") — or anything else — leaves
                    # the contest to the judge undecided.
                    _c6_report_ep(ep, "PENDING_JUDGE", False,
                                  deflection_failed=None)
                mv, _ok, _pr = parse_defender(
                    text, {"prev_defender_text": ledger.last_valid_d_text})
                if mv.kind not in ("INVALID",):
                    ledger.last_valid_d_text = text
                    ledger.last_valid_d_move = mv
                prev_d, prev_d_text = mv, text
                ledger.history.append((turn_no, role, mv, text))
                if turn_ok:
                    compliant_turns.add(idx)
                continue
            # v2.1: the answer to an escape-challenge follows its own
            # grammar (D-Diff / D-Reason / D-Concede / D-Unfounded),
            # intercepted before the standard D-form machinery. An
            # answer matching none of the four forms is an OTHER
            # answer and falls through to the standard path.
            if prev_c is not None and prev_c.kind in ("C5A", "C5B") \
                    and open_episode is not None and open_episode["awaiting_answer"]:
                ans = _parse_c5_answer(text, prev_c.kind)
                if ans is None:
                    open_episode["defender_response"] = "OTHER"
                    open_episode["answered"] = True
                    open_episode["awaiting_answer"] = False
                    open_episode["answer_turn"] = turn_no
                else:
                    ep = open_episode
                    ep["answered"] = True
                    ep["awaiting_answer"] = False
                    ep["answer_turn"] = turn_no
                    if ans.kind == "D_DIFF":
                        ep["defender_response"] = "D_DIFF"
                        dres = _resolve_difference(ans.difference, canonical_norms)
                        ep["stated"] = ans.difference
                        ep["canonical_resolved"] = dres["resolved"]
                        payload = t.get("defender_payload")
                        route = (payload.get("derivation") or {}).get("relevance_route") \
                            if isinstance(payload, dict) else None
                        pos_v = _eval_difference(facts, ans.subject_pos, dres)
                        neg_v = _eval_difference(facts, ans.subject_neg, dres)
                        pos_c = _diff_contested(facts, ans.subject_pos, dres)
                        neg_c = _diff_contested(facts, ans.subject_neg, dres)
                        rel_v, rel_c = _eval_relevance(facts, route, dres,
                                                       ans.difference,
                                                       ans.predicate, ans.pred_pol)
                        neg_lacks = None if neg_v is None else (neg_v is False)
                        ep["kb_verification"] = {
                            "pos_holds": "contested" if pos_c else pos_v,
                            "neg_lacks": "contested" if neg_c else neg_lacks,
                            "is_relevant": "contested" if rel_c else rel_v}
                        ep["lock"] = {"kind": "diff",
                                      "s_pos": norm_term(ans.subject_pos),
                                      "s_neg": norm_term(ans.subject_neg),
                                      "parts": dres["parts"], "pol": dres["pol"]}
                        if not dres["resolved"]:
                            # a non-canonical D fails the turn's
                            # fidelity — no escape through jargon.
                            fid_item(0.0)
                        elif not (pos_c or neg_c or rel_c):
                            fields = [v for v in (pos_v, neg_lacks, rel_v)
                                      if v is not None]
                            if fields:
                                fid_item(sum(1 for v in fields if v) / len(fields))
                        # Locking: (S_pos is D) and (S_neg is not D)
                        # enter the ledger as Defender commitments.
                        if len(dres["parts"]) == 1:
                            ledger.add("atom", (ans.subject_pos, dres["parts"][0]),
                                       dres["pol"], turn_no, False, "D-Diff")
                            ledger.add("atom", (ans.subject_neg, dres["parts"][0]),
                                       not dres["pol"], turn_no, False, "D-Diff")
                        else:
                            for part in dres["parts"]:
                                ledger.add("atom", (ans.subject_pos, part),
                                           True, turn_no, False, "D-Diff")
                            # (S_neg is not D) for a conjunction D is
                            # a disjunction over the parts — not
                            # atom-representable in this ledger; the
                            # episode outcome check works on the
                            # recorded lock instead.
                        note_contradiction(turn_no)
                    elif ans.kind == "D_REASON":
                        ep["defender_response"] = "D_REASON"
                        ep["stated"] = ans.reason
                        s_neg_r = norm_term(ans.subject)
                        r_n = norm_term(ans.reason)
                        minor_v = facts.eval_atom_full(s_neg_r, r_n)
                        minor_c = facts.fault_line_atom(s_neg_r, r_n) is not None
                        perv_c = facts.fault_line_pervasion(
                            r_n, ans.predicate, True, ans.pred_pol) is not None
                        perv_v = facts.eval_pervasion_full(r_n, ans.predicate) \
                            if ans.pred_pol else \
                            facts.eval_pervasion(r_n, ans.predicate, True, False)
                        ep["kb_verification"] = {
                            "minor": "contested" if minor_c else minor_v,
                            "pervasion": "contested" if perv_c else perv_v}
                        ep["lock"] = {"kind": "reason", "s_neg": s_neg_r,
                                      "reason": r_n, "predicate": ans.predicate,
                                      "thesis_pol": ans.pred_pol}
                        if not (minor_c or perv_c):
                            fid_item(0.5 * (1 if minor_v is True else 0)
                                     + 0.5 * (1 if perv_v is True else 0))
                        # Locking, as a type B reason: minor premise,
                        # pervasion, thesis. A mixed-polarity pervasion
                        # (R -> not P) is recorded polarity-False —
                        # the not-closure-usable convention used for
                        # mixed Accept pervasions since v1.2.
                        ledger.add("atom", (s_neg_r, r_n), True, turn_no,
                                   False, "D-Reason")
                        ledger.add("perv", (r_n, ans.predicate), ans.pred_pol,
                                   turn_no, False, "D-Reason")
                        ledger.add("atom", (s_neg_r, ans.predicate), ans.pred_pol,
                                   turn_no, False, "D-Reason")
                        note_contradiction(turn_no)
                    elif ans.kind == "D_CONCEDE":
                        ep["defender_response"] = "D_CONCEDE"
                        concede_first_count += 1
                        # The denied thesis counts accepted from here.
                        ledger.add("atom", (ans.subject, ans.predicate),
                                   ans.pred_pol, turn_no, False, "D-Concede")
                        ledger.explicit_atoms.add(
                            (norm_term(ans.subject), ans.predicate, ans.pred_pol))
                        accepted_at.setdefault(
                            (norm_term(ans.subject), ans.predicate, ans.pred_pol),
                            []).append(turn_no)
                        note_contradiction(turn_no)
                        _finalize_episode(ep, turn_no)
                    elif ans.kind == "D_UNFOUNDED":
                        ep["defender_response"] = "D_UNFOUNDED"
                        if ep["trigger_valid"]:
                            violate("illegal_d_unfounded: the challenged pair stands in this match's ledger, so the unfounded-rejection is not available")
                        _finalize_episode(ep, turn_no)
                    ledger.last_valid_d_text = text
                    ledger.last_valid_d_move = ans
                    prev_d, prev_d_text = ans, text
                    ledger.history.append((turn_no, role, ans, text))
                    if turn_ok:
                        compliant_turns.add(idx)
                    continue
            ctx = {"prev_defender_text": ledger.last_valid_d_text}
            mv, ok, probs = parse_defender(text, ctx)
            if not ok and mv.kind != "D_REPEAT":
                violate("defender syntax: " + "; ".join(probs))
            # contextual legality
            if prev_c is not None and prev_c.kind == "INVALID":
                if mv.kind != "D_SYN":
                    violate("defender answered a malformed challenger move with something other than the D5 sentence")
            elif prev_c is not None:
                if prev_c_illegal and mv.kind == "D_SYN":
                    pass  # answering an illegal challenger move with the D5 sentence is tolerated
                elif prev_c.kind in ("C1", "C1_COND") and mv.kind not in ("D_ACC", "D_WHY"):
                    violate(f"illegal response family to C1: {mv.kind}")
                if prev_c.kind == "C2" and mv.kind not in ("D_ACC", "D_ALR", "D_RNE", "D_NPV"):
                    violate(f"illegal response family to C2: {mv.kind}")
                if prev_c.kind == "C3" and mv.kind not in ("D3A", "D3B"):
                    violate(f"illegal response family to C3: {mv.kind}")
                if prev_c.kind == "C4":
                    if getattr(prev_c, "c4_valid", False):
                        if mv.kind != "D_ACC":
                            violate("defender did not accept a demonstrated contradiction (C4 upheld)")
                    else:
                        if text.strip() != (ledger.last_valid_d_text or "").strip():
                            violate("defender failed to repeat its previous response verbatim after an unfounded C4")
                if mv.kind == "D_SYN" and prev_c.kind in ("C1", "C2", "C3", "C4") and not prev_c_illegal:
                    violate("defender used the D5 sentence against a well-formed challenger move")
            # v1.4 telemetry: derived here from PRIOR commitments only
            # (ledger at this point holds no commitment from this turn).
            # Positive contradiction only: facts.eval_atom(...) is False.
            if prev_c is not None and prev_c.kind in ("C1", "C2") and mv.kind in ("D_ACC", "D_WHY", "D_RNE", "D_NPV"):
                tx, ty = norm_term(prev_c.subject), norm_term(prev_c.predicate)
                tgt = (tx, ty, prev_c.pred_pol)
                kb_false = facts.eval_atom(prev_c.subject, prev_c.predicate, prev_c.pred_pol) is False
                prior = list(ledger.commitments)
                dag = minimal_dag(prior, tgt)
                prior_atoms, _, _ = closure(prior)
                entailed = dag is not None or tgt in prior_atoms
                if entailed and kb_false and dag is not None:
                    false_leaves = _false_leaves_of_dag(dag, facts)
                    has_nonroot = any(l[1] != "ROOT" for l in dag["leaves"])
                    if mv.kind == "D_ACC":
                        is_root_neg = (tx, ty) == root_key and prev_c.pred_pol is False
                        kind = "FORCED_ROOT_ACCEPT" if is_root_neg else "SOFT_KHOR_LO"
                        weight = 1.00 if is_root_neg else 0.75
                        # Guard B1: non-trivial inference, >=2 leaves,
                        # >=1 non-KB leaf. Guard B2: novel false leaves.
                        if dag["rules"] >= 1 and len(dag["leaves"]) >= 2 and has_nonroot:
                            if false_leaves and false_leaves <= consumed_false_leaves:
                                ev_score = 0.0
                            else:
                                ev_score = weight * (1.25 if dag["contrapositive_steps"] >= 1 else 1.0) * round(dag["leaf_weight_sum"], 6)
                                consumed_false_leaves |= false_leaves
                            telemetry_events.append({
                                "turn": turn_no, "thesis": "%s is %s%s" % (tx, "" if prev_c.pred_pol else "not ", ty),
                                "kind": kind, "weight": weight,
                                "dag_leaf_weight_sum": round(dag["leaf_weight_sum"], 6),
                                "dag_rules": dag["rules"], "dag_leaves": len(dag["leaves"]),
                                "contrapositive_steps": dag["contrapositive_steps"],
                                "dag_indirect_leaves": sum(1 for l in dag["leaves"] if l[1] in ("IMPLICIT", "C3")),
                                "dag_total_leaves": len(dag["leaves"]),
                                "event_score": round(ev_score, 3)})
                    else:
                        # GATE_BLEMISH: denial of an entailed KB-false
                        # thesis (v4 gate). No B1 depth gate — a 0-step
                        # denial of an explicit Accept is the shape.
                        # 004 bonuses: seed distance +0.05/turn (cap
                        # 0.50), assertion harvest +0.30, implicit
                        # harvest +0.35, contrapositive close +0.25.
                        min_turn = min(l[0] for l in dag["leaves"]) if dag["leaves"] else turn_no
                        bonuses = {}
                        bonuses["seed_distance"] = round(min(0.50, 0.05 * max(0, turn_no - min_turn)), 3)
                        bonuses["assertion_harvest"] = 0.30 if any((l[4].source or "") == "RNE" for l in dag["leaves"]) else 0.0
                        bonuses["implicit_harvest"] = 0.35 if any((l[4].source or "") == "NPV implicit concession" for l in dag["leaves"]) else 0.0
                        bonuses["contrapositive_close"] = 0.25 if dag["contrapositive_steps"] >= 1 else 0.0
                        if false_leaves and false_leaves <= consumed_false_leaves:
                            ev_score = 0.0
                        else:
                            ev_score = 0.85 + sum(bonuses.values())
                            consumed_false_leaves |= false_leaves
                        telemetry_events.append({
                            "turn": turn_no, "thesis": "%s is %s%s" % (tx, "" if prev_c.pred_pol else "not ", ty),
                            "kind": "GATE_BLEMISH", "weight": 0.85,
                            "dag_leaf_weight_sum": round(dag["leaf_weight_sum"], 6),
                            "dag_rules": dag["rules"], "dag_leaves": len(dag["leaves"]),
                            "contrapositive_steps": dag["contrapositive_steps"],
                            "dag_indirect_leaves": sum(1 for l in dag["leaves"] if l[1] in ("IMPLICIT", "C3")),
                            "dag_total_leaves": len(dag["leaves"]),
                            "bonuses": bonuses,
                            "event_score": round(ev_score, 3)})
            # move-specific checks + ledger updates + fidelity
            new_commits = []
            if mv.kind == "D_ACC" and prev_c is not None and prev_c.kind in ("C1", "C2"):
                x, y = norm_term(prev_c.subject), norm_term(prev_c.predicate)
                # v1.2: record the thesis with its TRUE polarity — a negated
                # Accept commits to (x, y, False), not (x, y, True).
                ledger.explicit_atoms.add((x, y, prev_c.pred_pol))
                all_accepts.append((turn_no, x, y, prev_c.pred_pol))
                new_commits.append(ledger.add("atom", (x, y), prev_c.pred_pol, turn_no, False, "Accept"))
                if prev_c.kind == "C2":
                    z = norm_term(prev_c.reason)
                    new_commits.append(ledger.add("atom", (x, z), prev_c.reason_pol, turn_no, True, "Accept C2 (minor conceded)"))
                    if prev_c.reason_pol and prev_c.pred_pol:
                        new_commits.append(ledger.add("perv", (z, y), True, turn_no, True, "Accept C2 (pervasion conceded)"))
                    elif (not prev_c.reason_pol) and (not prev_c.pred_pol):
                        # not-Z -> not-Y is exactly Y -> Z (contrapositive);
                        # the closure's modus tollens handles that form.
                        new_commits.append(ledger.add("perv", (y, z), True, turn_no, True, "Accept C2 (pervasion conceded, contrapositive form)"))
                    else:
                        # mixed polarity (e.g. Z -> not-Y): not representable
                        # as a positive pervasion; record it as denied-to-
                        # closure (polarity False) rather than a false
                        # positive pervasion.
                        new_commits.append(ledger.add("perv", (z, y), False, turn_no, True, "Accept C2 (mixed-polarity pervasion, not closure-usable)"))
                    fid_minor = facts.eval_atom(prev_c.subject, prev_c.reason, prev_c.reason_pol)
                    fid_thesis = facts.eval_atom(prev_c.subject, prev_c.predicate, prev_c.pred_pol)
                    if facts.fault_line_pervasion(prev_c.reason, prev_c.predicate, prev_c.reason_pol, prev_c.pred_pol) is not None:
                        # v1.6: Accept asserts the pervasion — on a
                        # contested pervasion this locks (or flips) the frame.
                        _pc = defender_perv_fid(prev_c.reason, prev_c.predicate, prev_c.reason_pol, prev_c.pred_pol, True)
                        fid(None if (fid_minor is None or fid_thesis is None)
                            else (fid_minor and _pc and fid_thesis))
                    else:
                        fid_perv = facts.eval_pervasion(prev_c.reason, prev_c.predicate, prev_c.reason_pol, prev_c.pred_pol)
                        fid(None if (fid_minor is None or fid_perv is None or fid_thesis is None)
                            else (fid_minor and fid_perv and fid_thesis))
                elif prev_c.kind == "C1":
                    fid(facts.eval_atom(prev_c.subject, prev_c.predicate, prev_c.pred_pol))
                elif prev_c.kind == "C4":
                    pass  # conceding a valid call: no new proposition scored
            elif mv.kind == "D_ACC" and prev_c is not None and prev_c.kind == "C1_COND":
                # v1.8: Accepting a conditional C1 concedes the pervasion
                # (polarity rules as for a C2 Accept, antecedent -> consequent).
                z, y = norm_term(prev_c.reason), norm_term(prev_c.predicate)
                if prev_c.reason_pol and prev_c.pred_pol:
                    new_commits.append(ledger.add("perv", (z, y), True, turn_no, True, "Accept C1_COND (pervasion conceded)"))
                elif (not prev_c.reason_pol) and (not prev_c.pred_pol):
                    new_commits.append(ledger.add("perv", (y, z), True, turn_no, True, "Accept C1_COND (pervasion conceded, contrapositive form)"))
                else:
                    new_commits.append(ledger.add("perv", (z, y), False, turn_no, True, "Accept C1_COND (mixed-polarity pervasion, not closure-usable)"))
                if facts.fault_line_pervasion(prev_c.reason, prev_c.predicate, prev_c.reason_pol, prev_c.pred_pol) is not None:
                    _pc = defender_perv_fid(prev_c.reason, prev_c.predicate, prev_c.reason_pol, prev_c.pred_pol, True)
                    fid(_pc)
                else:
                    fid(perv_value_framed(prev_c.reason, prev_c.predicate, prev_c.reason_pol, prev_c.pred_pol))
            elif mv.kind == "D_WHY" and prev_c is not None and prev_c.kind == "C1_COND":
                # v1.8: "Why" denies the conditional's pervasion.
                if facts.fault_line_pervasion(prev_c.reason, prev_c.predicate, prev_c.reason_pol, prev_c.pred_pol) is not None:
                    _pc = defender_perv_fid(prev_c.reason, prev_c.predicate, prev_c.reason_pol, prev_c.pred_pol, False)
                    fid(_pc)
                else:
                    v = perv_value_framed(prev_c.reason, prev_c.predicate, prev_c.reason_pol, prev_c.pred_pol)
                    fid(None if v is None else (not v))
            elif mv.kind == "D_WHY" and prev_c is not None and prev_c.kind == "C1":
                denied_at.setdefault((norm_term(prev_c.subject), norm_term(prev_c.predicate),
                                      prev_c.pred_pol), []).append(turn_no)
                # v1.2: denying "X is not Y" commits to (X, Y, True).
                new_commits.append(ledger.add("atom", (norm_term(prev_c.subject), norm_term(prev_c.predicate)), not prev_c.pred_pol, turn_no, False, "Why (denial)"))
                if (facts.fault_line_atom(prev_c.subject, prev_c.predicate) == "FL_03"
                        and prev_c.pred_pol):
                    # v1.6: 'Why' on a SILENT_DOCTRINAL atom is
                    # fidelity-correct (the text states neither side).
                    fid(True)
                else:
                    v = facts.eval_atom(prev_c.subject, prev_c.predicate, prev_c.pred_pol)
                    fid(None if v is None else (not v))
            elif mv.kind == "D_ALR" and prev_c is not None and prev_c.kind in ("C1", "C2"):
                key = (norm_term(prev_c.subject), norm_term(prev_c.predicate), prev_c.pred_pol)
                if key not in ledger.explicit_atoms:
                    violate("'Already accepted' claimed for a thesis never explicitly accepted")
                    mv.false_alr = True
            elif mv.kind == "D_RNE" and prev_c is not None and prev_c.kind == "C2":
                if norm_term(mv.subject) != norm_term(prev_c.subject) or mv.reason != norm_term(prev_c.reason):
                    violate("Reason-not-established slots do not bind to the preceding C2's subject and reason")
                denied_at.setdefault((norm_term(prev_c.subject), norm_term(prev_c.predicate),
                                      prev_c.pred_pol), []).append(turn_no)
                # v1.3: RNE denies the minor premise AS STATED — commit its
                # negation (not reason_pol), not always False. For a positive
                # reason this is identical to the old behaviour; for a negated
                # reason the old False commit manufactured a contradiction out
                # of a correct denial (iter007 match 2, turn 24).
                new_commits.append(ledger.add("atom", (norm_term(mv.subject), mv.reason), not prev_c.reason_pol, turn_no, False, "RNE"))
                ledger.explicit_atoms.discard((norm_term(mv.subject), mv.reason, prev_c.reason_pol))
                # v1.5: three-valued, mirroring D_NPV — a denial on an atom
                # the fact base cannot evaluate is UNSCORED, not incorrect
                # (Argon consultation 005). Only a provably-true minor
                # premise makes the denial a fidelity error.
                if (facts.fault_line_atom(prev_c.subject, prev_c.reason) == "FL_03"
                        and prev_c.reason_pol):
                    # v1.6: denying a positively-stated SILENT_DOCTRINAL
                    # minor premise is fidelity-correct.
                    fid(True)
                elif (facts.fault_line_atom(prev_c.subject, prev_c.reason) == "FL_03"
                        and not prev_c.reason_pol):
                    # v1.6: asserting a silent atom through a
                    # negated-reason denial is a voluntary ledger
                    # concession — unscored (Argon 007 denominator rule).
                    unscored_rne += 1
                    fid(None)
                else:
                    _minor_v = facts.eval_atom(prev_c.subject, prev_c.reason, prev_c.reason_pol)
                    if _minor_v is None:
                        unscored_rne += 1
                    fid(None if _minor_v is None else (_minor_v is False))
            elif mv.kind == "D_NPV" and prev_c is not None and prev_c.kind == "C2":
                if mv.reason != norm_term(prev_c.reason) or mv.predicate != norm_term(prev_c.predicate):
                    violate("No-pervasion slots do not bind to the preceding C2's reason and predicate")
                denied_at.setdefault((norm_term(prev_c.subject), norm_term(prev_c.predicate),
                                      prev_c.pred_pol), []).append(turn_no)
                # v1.2: the denied pervasion in canonical positive form
                # (not-Z -> not-Y denies Y -> Z); the implicit concession
                # carries the NPV text's own reason polarity.
                if (not mv.reason_pol) and (not mv.pred_pol):
                    new_commits.append(ledger.add("perv", (mv.predicate, mv.reason), False, turn_no, False, "NPV"))
                else:
                    new_commits.append(ledger.add("perv", (mv.reason, mv.predicate), False, turn_no, False, "NPV"))
                # implicit concession of the minor premise (Argon pt 2) — always enters the ledger
                new_commits.append(ledger.add("atom", (norm_term(prev_c.subject), norm_term(prev_c.reason)), mv.reason_pol, turn_no, True, "NPV implicit concession"))
                minor = facts.eval_atom(prev_c.subject, prev_c.reason, prev_c.reason_pol)
                if facts.fault_line_pervasion(prev_c.reason, prev_c.predicate, prev_c.reason_pol, prev_c.pred_pol) is not None:
                    # v1.6: NPV asserts the pervasion false — on a
                    # contested pervasion this locks (or flips) the
                    # frame. For precedence the asserted value False is
                    # the operative pervasion value.
                    _pc = defender_perv_fid(prev_c.reason, prev_c.predicate, prev_c.reason_pol, prev_c.pred_pol, False)
                    if minor is False:
                        violate("precedence error: minor premise false, so 'Reason not established' was mandatory; the implicit concession of the minor premise still enters the ledger")
                    fid(_pc)
                else:
                    perv = facts.eval_pervasion(prev_c.reason, prev_c.predicate, prev_c.reason_pol, prev_c.pred_pol)
                    if minor is False and perv is False:
                        violate("precedence error: minor premise false, so 'Reason not established' was mandatory; the implicit concession of the minor premise still enters the ledger")
                    fid(None if perv is None else (not perv))
            elif mv.kind in ("D3A", "D3B"):
                anchor_move = d_before_c3 or prev_d
                if mv.kind == "D3A":
                    new_commits.append(ledger.add("atom", (norm_term(mv.example), mv.reason), False, turn_no, False, "D3 example"))
                    v = facts.eval_atom(mv.example, mv.reason, True)
                    fid(None if v is None else (not v))
                else:
                    new_commits.append(ledger.add("atom", (norm_term(mv.example), mv.reason), True, turn_no, False, "D3 example"))
                    new_commits.append(ledger.add("atom", (norm_term(mv.example), mv.predicate), False, turn_no, False, "D3 example"))
                    v1 = facts.eval_atom(mv.example, mv.reason, True)
                    v2 = facts.eval_atom(mv.example, mv.predicate, True)
                    fid(None if (v1 is None or v2 is None) else (v1 and not v2))
            # forced-Accept detection (Argon/ledger): was this C2 already entailed by prior concessions?
            if prev_c is not None and prev_c.kind == "C2" and mv.kind in ("D_WHY", "D_RNE", "D_NPV"):
                prior_atoms, _, _ = closure([c for c in ledger.commitments if c.turn < turn_no])
                x, y, z = norm_term(prev_c.subject), norm_term(prev_c.predicate), norm_term(prev_c.reason)
                # v1.2: polarity-aware — the minor premise enters with its
                # own polarity, and a both-negated pervasion lives in the
                # closure in contrapositive form (y, z); mixed-polarity
                # pervasions are not closure-representable, so they cannot
                # force an Accept through this check.
                minor_in = (x, z, prev_c.reason_pol) in prior_atoms
                _, prior_pervs, _ = closure([c for c in ledger.commitments if c.turn < turn_no])
                if prev_c.reason_pol and prev_c.pred_pol:
                    perv_in = (z, y) in prior_pervs
                elif (not prev_c.reason_pol) and (not prev_c.pred_pol):
                    perv_in = (y, z) in prior_pervs
                else:
                    perv_in = False
                if minor_in and perv_in:
                    forced_events.append({"turn": turn_no, "thesis": f"{x} is {y}"})
                    violate("failed forced Accept: minor premise and pervasion were both already conceded")
            # v2.1: register this turn's treatments for escape-
            # challenge trigger verification — the propositions its
            # Accept / NPV-concession / RNE acts establish, and (for
            # an Accept) the negation of the accepted thesis, which
            # the Accept thereby denies.
            for c in new_commits:
                if c.kind == "atom" and c.source in ("Accept", "NPV implicit concession", "RNE"):
                    accepted_at.setdefault((c.key[0], c.key[1], c.polarity), []).append(turn_no)
                    if c.source == "Accept":
                        denied_at.setdefault((c.key[0], c.key[1], not c.polarity), []).append(turn_no)
            # ledger consistency: contradiction after this move?
            note_contradiction(turn_no)
            if mv.kind not in ("INVALID",):
                ledger.last_valid_d_text = text
                ledger.last_valid_d_move = mv
            prev_d, prev_d_text = mv, text
            ledger.history.append((turn_no, role, mv, text))
            # v2.1: an open episode's window closes with the reply to
            # its second refutation consequence.
            if open_episode is not None and open_episode["answered"] \
                    and open_episode["c2_count"] >= 2:
                _finalize_episode(open_episode, turn_no)
        if turn_ok:
            compliant_turns.add(idx)
    # v2.1: an episode still open at the last turn closes there.
    if open_episode is not None:
        _finalize_episode(open_episode, turns[-1].get("turn", n_turns) if turns else 0)
    # v2.2: quotation episodes left hanging at the last turn close
    # there — an unanswered verified quotation stands (UNANSWERED,
    # cascade); an unclosed deflection goes to the judge.
    if c6_pending is not None:
        _c6_report_ep(c6_pending, "UNANSWERED", True)
        _c6_cascade(c6_pending)
        c6_pending = None
    if c6_await is not None:
        _c6_report_ep(c6_await["ep"], "PENDING_JUDGE", False,
                      deflection_failed=None)
        c6_await = None
    rule_compliance = len(compliant_turns) / n_turns if n_turns else 0.0
    fidelity = (fid_correct / (fid_correct + fid_wrong)) if (fid_correct + fid_wrong) else None
    valid_c4 = [c for c in c4_results if c["valid"]]
    trap = max([c["trap_complexity"] for c in valid_c4], default=0.0)
    # longest concession chain: deepest derivation in the final closure
    final_atoms, _, _ = closure(ledger.commitments)
    longest_chain = max([v["steps"] for v in final_atoms.values()], default=0)
    # v1.9: justification scoring, only when the transcript carries
    # defender payloads (defender_v6). Never an input to the legacy
    # metrics above; payload-less transcripts keep their v1.8 values.
    if any(isinstance(t, dict) and t.get("defender_payload") for t in turns):
        justification_detail = justification.score_justification(transcript, facts)
        justification_det = justification_detail["justification_det"]
        hard_justification_failures = justification_detail["hard_justification_failures"]
        epistemic_forfeit = justification_detail["epistemic_forfeit"]
    else:
        justification_detail = None
        justification_det = None
        hard_justification_failures = 0
        epistemic_forfeit = False
    report = {
        "match_id": transcript.get("match_id"),
        "turns": n_turns,
        "scores": {
            "rule_compliance": round(rule_compliance, 3),
            "textual_fidelity": (round(fidelity, 3) if fidelity is not None else None),
            "ledger_consistency": round(max(0.0, 1.0 - len(contradictions) / max(1, n_turns // 2)), 3),
            "trap_complexity": round(trap, 3),
        },
        "fidelity_detail": {"correct": fid_correct, "incorrect": fid_wrong, "unevaluable": fid_unknown},
        "referee_version": "2.3",
        "justification_det": justification_det,
        "hard_justification_failures": hard_justification_failures,
        "epistemic_forfeit": epistemic_forfeit,
        "justification_detail": justification_detail,
        "fidelity_turns": fidelity_turns,
        "frame_locks": frame_locks,
        "frame_flips": frame_flips,
        "coverage": {
            "fidelity_coverage": (round((fid_correct + fid_wrong) / (fid_correct + fid_wrong + fid_unknown), 3)
                                  if (fid_correct + fid_wrong + fid_unknown) else None),
            "unscored_rne_atoms": unscored_rne,
        },
        "contradictions": contradictions,
        "forced_accept_failures": forced_events,
        "c4_calls": c4_results,
        "valid_khorlo_tsa_count": len(valid_c4),
        "longest_concession_chain": longest_chain,
        "violations": violations,
        "trap_telemetry": {
            "soft_khor_lo_count": sum(1 for e in telemetry_events if e["kind"] == "SOFT_KHOR_LO" and e["event_score"] > 0),
            "forced_root_accept_count": sum(1 for e in telemetry_events if e["kind"] == "FORCED_ROOT_ACCEPT" and e["event_score"] > 0),
            "gate_blemish_count": sum(1 for e in telemetry_events if e["kind"] == "GATE_BLEMISH" and e["event_score"] > 0),
            "indirect_lock_ratio": round(
                (sum(e["dag_indirect_leaves"] for e in telemetry_events if e["event_score"] > 0) /
                 max(1, sum(e["dag_total_leaves"] for e in telemetry_events if e["event_score"] > 0))), 3),
"max_event_score": round(max([e["event_score"] for e in telemetry_events], default=0.0), 3),
            "sum_event_scores": round(sum(e["event_score"] for e in telemetry_events), 3),
            "extended_trap_complexity": round(trap + sum(e["event_score"] for e in telemetry_events), 3),
            "forced_accept_events": telemetry_events,
        },
    }

    # ---------------------------------------------------------- v2.0
    # Type B/C report blocks (present only for those match types) and
    # the text_cites list (present only when a cite was carried).
    if text_cites:
        report["text_cites"] = text_cites
    if match_type == "B":
        S = type_open.get("subject"); P = type_open.get("predicate"); R = type_open.get("reason")
        minor_v = facts.eval_atom_full(S, R) if (S and R) else None
        perv_v = facts.eval_pervasion_full(R, P) if (R and P) else None
        vacuous = False
        if S and P and R:
            nR, nP, nS = norm_term(R), norm_term(P), norm_term(S)
            vacuous = (nR == nP or nR == nS
                       or nP in [part.strip() for part in nR.split(" and ")])
        turn1_fidelity = (0.5 * (1 if minor_v is True else 0)
                          + 0.5 * (1 if perv_v is True else 0))
        prep = transcript.get("challenger_prep") or {}
        ref = prep.get("reference_reason")
        prep_valid = bool(ref and S and P
                          and facts.eval_atom_full(S, ref) is True
                          and facts.eval_pervasion_full(ref, P) is True)
        # reason_defeated: computed from the final ledger's atom
        # commitments recorded AFTER the reason turn. LIMITATION: only
        # ledger-recorded atom propositions count — the Challenger's
        # win conditions as they can actually be forced in play (an
        # Accept of "S is not R", or Accepts of "[e] is R" and "[e] is
        # not P", or an RNE/assertion positing those atoms). A bare
        # pervasion denial (NPV commits a denied pervasion, not the
        # counterexample's atoms) does NOT register here unless the
        # pair itself entered the ledger as atoms.
        defeated = False
        if S and P and R:
            ns, np_, nr = norm_term(S), norm_term(P), norm_term(R)
            reason_turn = type_open.get("opening_turn", 2)
            pos, neg = set(), set()
            for c in ledger.commitments:
                if c.kind == "atom" and c.turn > reason_turn:
                    (pos if c.polarity else neg).add(c.key)
            defeated = (ns, nr) in neg or any(
                (e, nr) in pos and (e, np_) in neg for (e, _q) in list(pos))
        report["type_b"] = {
            "subject": S, "predicate": P, "reason": R,
            "vacuous": vacuous,
            "minor_value": minor_v, "perv_value": perv_v,
            "turn1_fidelity": turn1_fidelity,
            "prep_valid": prep_valid,
            "reason_defeated": defeated,
        }
    if match_type == "C":
        T = type_open.get("term")
        D = type_open.get("definiens")
        I = type_open.get("illustration")
        payload = turns[1].get("defender_payload") if len(turns) > 1 else None
        clauses_stated = None
        if isinstance(payload, dict):
            clauses_stated = (payload.get("derivation") or {}).get("clauses")
        if clauses_stated is None:
            if D:
                clauses_stated = [x.strip() for x in re.split(r",| and ", D) if x.strip()]
            else:
                clauses_stated = []
        clauses_stated = list(clauses_stated)
        entry = _canonical_def(T) if T else None
        canon_clauses = list((entry or {}).get("clauses") or [])
        term_unknown = not canon_clauses
        extra = sum(1 for sc in clauses_stated
                    if not any(_clause_match(sc, cc) for cc in canon_clauses))
        penalty = 0.25 * extra
        if term_unknown:
            recall = None
            definiens_score = None
        else:
            matched = sum(1 for cc in canon_clauses
                          if any(_clause_match(sc, cc) for sc in clauses_stated))
            recall = round(matched / len(canon_clauses), 3)
            definiens_score = round(max(0.0, min(1.0, recall - penalty)), 3)
        ill_value = facts.eval_atom(I, T) if (I and T) else None
        canon_def = (entry or {}).get("definiens") or ""
        dv = False
        if D:
            dv = (" or " in re.sub(r"\s+", " ", D.lower())
                  and " or " not in re.sub(r"\s+", " ", canon_def.lower()))
        report["type_c"] = {
            "term": T,
            "clauses_stated": clauses_stated,
            "recall": recall,
            "extra_clauses": extra,
            "precision_penalty": penalty,
            "definiens_score": definiens_score,
            "illustration_value": ill_value,
            "disjunction_violation": dv,
            "term_unknown": term_unknown,
        }
    # v2.1: the escape-challenges block exists only in matches where
    # a C5 move was issued (legacy identity for all others).
    if escape_episodes:
        report["escape_challenges"] = {
            "challenges_issued": c5_count,
            "valid_triggers": sum(1 for e in escape_episodes if e["trigger_valid"]),
            "episodes": escape_episodes,
        }
    # v2.2: the quote-episodes block exists only in matches where a
    # C6 move was attempted (legacy identity for all others).
    if quote_episodes:
        report["quote_episodes"] = {
            "c6_attempted": c6_count,
            "over_acceptances": sum(
                1 for e in quote_episodes if e["outcome"] == "OVER_ACCEPTANCE"),
            "episodes": quote_episodes,
        }
    # v2.3: the archive-use block exists only in matches that used
    # the archive (legacy identity for all others).
    if archive_refs or archive_c5_log:
        consults = transcript.get("archive_consultations")
        report["archive_use"] = {
            "refs_total": len(archive_refs),
            "refs_valid": sum(1 for r in archive_refs if r["valid"]),
            "refs": archive_refs,
            "cross_match_c5": archive_c5_log,
            "consultations_logged":
                len(consults) if isinstance(consults, list) else 0,
        }
    return report

def evaluate_c4(call, ledger, facts, root_key, prev_d):
    """Argon pt 4: Khor lo! valid iff the last Defender move contradicts the closure of the
    ledger prior to it (or was a false 'Already accepted'); Tsa! valid iff the last move
    entails the negation of the root thesis or directly contradicts Purchok's text."""
    d_turns = [h for h in ledger.history if h[1] == "defender"]
    if not d_turns:
        return {"valid": False, "reason": "no preceding defender move"}
    last_turn_no = d_turns[-1][0]
    prior = [c for c in ledger.commitments if c.turn < last_turn_no or c.turn == 0]
    last = [c for c in ledger.commitments if c.turn == last_turn_no]
    prior_atoms, prior_pervs, prior_contra = closure(prior)
    full_atoms, _, full_contra = closure(prior + last)
    if call == "Tsa!":
        neg_root = (root_key[0], root_key[1], False)
        if neg_root in full_atoms:
            return {"valid": True, "reason": "last move entails the negation of the root thesis",
                    "trap_complexity": _trap_score(full_atoms, neg_root, last)}
        for c in last:
            if c.kind == "atom":
                v = facts.eval_atom(c.key[0], c.key[1], True)
                if v is not None and v != c.polarity:
                    return {"valid": True, "reason": "last move directly contradicts Purchok's text",
                            "trap_complexity": _trap_score(full_atoms, (c.key[0], c.key[1], c.polarity), last)}
        return {"valid": False, "reason": "root thesis not contradicted and no direct contradiction of the text"}
    # Khor lo!
    if prev_d is not None and getattr(prev_d, "false_alr", False):
        return {"valid": True, "reason": "defender falsely claimed 'Already accepted'",
                "trap_complexity": 1.0}
    if full_contra and not prior_contra:
        s, p = full_contra
        info = full_atoms.get((s, p, True)) or full_atoms.get((s, p, False))
        return {"valid": True, "reason": f"last move contradicts prior concessions on '{s} / {p}'",
                "trap_complexity": _trap_score(full_atoms, (s, p, True), last)}
    for c in last:
        opp = (c.key[0], c.key[1], not c.polarity) if c.kind == "atom" else None
        if opp and opp in prior_atoms:
            return {"valid": True, "reason": "last move contradicts the closure of prior concessions",
                    "trap_complexity": _trap_score(prior_atoms, opp, last)}
    return {"valid": False, "reason": "no contradiction with prior concessions"}

def _trap_score(atoms, target_key, last_commits):
    info = atoms.get(target_key) or {"steps": 0, "mt_edges": 0, "subjects": set(), "implicit": False}
    subjects = set(info.get("subjects") or set())
    for c in last_commits:
        subjects.add(c.key[0])
    implicit = bool(info.get("implicit")) or any(c.implicit for c in last_commits) or \
        any(c.source in ("NPV implicit concession", "D3 example") for c in last_commits)
    return (1.0 * info.get("steps", 0)
            + 1.5 * info.get("mt_edges", 0)
            + 2.0 * max(0, len(subjects) - 1)
            + (1.5 if implicit else 0.0))

def main(argv):
    if len(argv) >= 3 and argv[1] == "score":
        tr = json.load(open(argv[2], encoding="utf-8"))
        rep = score_match(tr)
        print(json.dumps(rep, ensure_ascii=False, indent=1))
        s = rep["scores"]
        print(f"\n== {rep['match_id']}: compliance {s['rule_compliance']} | fidelity {s['textual_fidelity']} "
              f"| ledger {s['ledger_consistency']} | trap {s['trap_complexity']} | "
              f"contradictions {len(rep['contradictions'])} | valid C4 {rep['valid_khorlo_tsa_count']} "
              f"| longest chain {rep['longest_concession_chain']}")
        return 0
    print(__doc__)
    return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv))
