#!/usr/bin/env python3
"""Deterministic justification scoring for the Lorig debate arena
(referee v1.9, Part 1 of the 2026-10-28 redesign; Argon consultation
008, deterministic Stage A only — the LLM-judge stage is wired in with
Part 2, when the three debate types land).

Defender prompt v6 makes the Defender emit, per turn, a private JSON
payload (an EpistemicState snapshot plus a derivation blurb) alongside
its plain-text move. Transcripts carry it as turn["defender_payload"].
This module scores those payloads mechanically:

  DET_1 (15) referential/form integrity — every cited state id exists
             in THIS turn's snapshot and no cited stance/commitment is
             DEFEATED (definitions are IMMUTABLE, always citable);
             every cited ledger id is L_n with n within the count of
             concession-events up to and including this turn; every
             cited fact names an entry of the fact base; the prose
             summary is 35-75 words; cited_state_ids is non-empty.
  DET_2 (15) truth-table lock — the derivation's booleans must map to
             the derived move, and the formal move's surface form must
             match the derived move. Gate overrides (REVISION /
             SENSE_RULING) change the booleans' values, never the
             coupling; the C1 LEDGER_CLOSURE exception is the one
             sanctioned decoupling (ledger binds the answer, not the
             understanding). Not applicable to C3/C4 turns.
  DET_3 (10) term overlap — the consequence's canonical terms and the
             cited nodes' text must share at least one canonical term
             (blocks decorative citation). Vacuous pass when either
             side carries no canonical term.
  DET_4 (10) counterexample witness — an NPV derivation must name a
             concrete, non-placeholder counterexample (a canonical
             subject, a fact-base subject, or the consequence's own
             subject). Applicable only when derived_move == "NPV".

Plus the state-diff audit (illegal state mutations between consecutive
snapshots), revision accounting (3rd revision costs 0.10; a 4th is
epistemic collapse), and hard justification failures: a DET_2 failure,
a zombie citation (DET_1 failure caused by citing a DEFEATED node), or
an illegal state mutation zeroes the whole turn's earned weight; two
or more hard failures in a match are an epistemic forfeit.

Payload-less transcripts are never passed here by the referee — the
v1.9 referee calls this module only when a transcript carries at least
one defender_payload, so pre-v1.9 scoring is untouched.

v2.0 (Part 2 of the 2026-10-28 redesign; Argon consultation 009):
match types B and C. Two changes:
  - Concession-event counting learns the opening statements: a
    STATE_REASON move (the Type B reason statement) creates THREE
    concession events in the order minor premise, pervasion, thesis
    (matching the referee's ledger injection); a STATE_MEANING move
    (the three-line "Definiens: ..." statement) creates 1 + (number of
    stated divisions) events (illustration atom, then one per
    division; "none stated" = 0 divisions).
  - Constructive turn-1 payloads (derivation.constructive true — the
    Type B/C opening derivations of defender_v7): DET_2 and DET_4 are
    not applicable (there is no truth table to lock, and no NPV);
    DET_1 applies with the pervasion-form citation rule ("R-pervasion
    :: P" resolves against the pervasion table after stripping the
    suffix) and with cited_ledger_ids allowed empty at turn 1; DET_3
    is replaced by DET_3C (the cited nodes must actually contain the
    selected reason and predicate for B, or trace every stated clause
    for C). A constructive turn's applicable weight is DET_1 (15) +
    DET_3C (10) = 25, and it cannot hard-fail on DET_2; a zombie
    citation still hard-fails via DET_1.

v2.1 (Part 3 of the 2026-10-28 redesign; Argon consultation 010):
escape-challenge payloads (defender_v8). Concession-event counting
learns the new answers: a D-Diff move creates TWO events (the two
difference atoms), a D-Reason move creates THREE (it matches the
STATE_REASON shape — minor premise, pervasion, thesis), a D-Concede
creates ONE (the thesis that now counts accepted), a D-Unfounded
creates NONE. DET_3C gains the stated_difference subtype: on a D-Diff
payload the cited nodes must contain the stated difference D and the
denied predicate P as normalized substrings. D-Concede turns
(derived_move == "D_CONCEDE") have no truth table and no NPV witness,
so DET_2 / DET_4 are not applicable; DET_1 and the standard DET_3
term-overlap apply. The Challenger classifier learns C5A / C5B so
prev-move kinds stay truthful around the new answers.

v2.2 (Part 4 of the 2026-10-28 redesign; Argon consultation 011):
quotation moves. The Challenger classifier learns C6 / C6_REFUTE
(no form penalty — the referee checks the citation machinery).
Defender quote-response payloads are constructive turns with a
DET_3C 'quote' subtype: the cited nodes' combined text must contain
the quote claim's predicate and, for a pervasion repair, its reason.
An interpretation payload whose gate_audit override is not
SENSE_RULING fails DET_1 form integrity. Concession counting:
an accept-quote creates TWO events for a pervasion repair
(pervasion + cascaded thesis — the surface carries "therefore the
subject,") and ONE for a minor-premise repair; voice claims,
interpretations and holds create none.
"""
import json, os, re

FACTS_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "facts.json")

# Mirrors referee.ALIASES / referee.norm_term exactly (kept local so this
# module never imports the referee — the referee imports this module).
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

def norm_term(s):
    s = str(s).strip().lower().rstrip(".")
    s = re.sub(r"\s+", " ", s)
    for art in ("the ", "a ", "an "):
        if s.startswith(art):
            s = s[len(art):]
            break
    return ALIASES.get(s, s)

WEIGHTS = {"det1": 15, "det2": 15, "det3": 10, "det4": 10}
_PLACEHOLDERS = {"x", "example", "something", "a counterexample",
                 "counterexample", "tbd", "n/a"}
_LEDGER_RE = re.compile(r"^L_(\d+)$")
_D3A_RE = re.compile(r"^(.+) is not (.+)\.$")
_D3B_RE = re.compile(r"^(.+) is (.+) but not (.+)\.$")
_NODE_TEXT_FIELDS = ("term", "definiens", "text", "issue", "chosen_side")
_STATE_SECTIONS = ("definitions", "stances", "commitments")

_canonical_cache = None

def _canonical(facts):
    """(all canonical terms, canonical subjects), normalized. Taken
    from the Facts object when it carries them, else read once from
    the fact base the referee itself loads."""
    global _canonical_cache
    subs = getattr(facts, "canonical_subjects", None)
    preds = getattr(facts, "canonical_predicates", None)
    if subs is None or preds is None:
        if _canonical_cache is None:
            d = json.load(open(FACTS_PATH, encoding="utf-8"))
            _canonical_cache = (d["canonical_subjects"], d["canonical_predicates"])
        subs, preds = _canonical_cache
    subjects = {norm_term(s) for s in subs}
    return subjects | {norm_term(p) for p in preds}, subjects

def _classify_challenger(text):
    """Minimal Challenger-move classifier + slot extraction, mirroring
    referee.parse_challenger's forms (kept local: no referee import).
    Returns (kind, {subject, predicate, reason})."""
    t = (text or "").strip()
    if t == "Posit an example.":
        return "C3", {}
    if t.startswith("Khor lo!") or t.startswith("Tsa!"):
        return "C4", {}
    if "because Purchok states in his own voice:" in t:
        # v2.2 quotation move — pervasion form opens "If something
        # is", minor-premise form "The subject,"; the machine data
        # rides in the turn's quote_claim, checked by the referee.
        return "C6", {}
    if t.startswith("The passage stands in Purchok's own voice:"):
        return "C6_REFUTE", {}
    if t.startswith("If it is "):
        for marker in (", it follows it is ", ", it follows that it is "):
            i = t.find(marker)
            if i >= 0:
                return "C1_COND", {"subject": None,
                                   "reason": t[len("If it is "):i].strip(),
                                   "predicate": t[i + len(marker):].strip().rstrip(".")}
        return "C1_COND", {}
    m = _C5A_RE.match(t)
    if m:
        # v2.1: difference-demand — subject is the DENIED case; the
        # positive case rides in the because-clause.
        return "C5A", {"subject": m.group(1).strip(),
                       "predicate": ((m.group(2) or "") + m.group(3)).strip(),
                       "reason": None}
    m = _C5B_RE.match(t)
    if m:
        return "C5B", {"subject": m.group(1).strip(),
                       "predicate": ((m.group(2) or "") + m.group(3)).strip(),
                       "reason": None}
    if t.startswith("The subject, "):
        marker = ", it follows that it is "
        i = t.find(marker)
        if i < 0:
            return "INVALID", {}
        subj = t[len("The subject, "):i].strip()
        rest = t[i + len(marker):]
        for bm in (", because of not being ", ", because of being "):
            j = rest.find(bm)
            if j >= 0:
                return "C2", {"subject": subj, "predicate": rest[:j].strip(),
                              "reason": rest[j + len(bm):].strip().rstrip(".")}
        return "C1", {"subject": subj, "predicate": rest.strip().rstrip("."),
                      "reason": None}
    return "INVALID", {}

def _is_concession_event(text, prev_kind):
    """A Defender turn that creates a ledger commitment (Argon 008:
    every concession is tagged L_01, L_02, ... in the order commitments
    arise): an Accept to C1/C2, an NPV, an RNE, a C3 posit, or a C4
    Accept."""
    t = (text or "").strip()
    if t == "Accept" and prev_kind in ("C1", "C2", "C4"):
        return True
    if t.startswith("No pervasion."):
        return True
    if t.startswith("Reason not established."):
        return True
    if prev_kind == "C3" and (_D3B_RE.match(t) or _D3A_RE.match(t)):
        return True
    return False

# v2.0: the Type B reason statement — one move, three commitments.
_B_REASON_RE = re.compile(r"^The subject, (.+), is (.+), because of being (.+)\.$")

# v2.1: escape-challenge forms (mirrors referee C5A_RE / C5B_RE).
_C5A_RE = re.compile(r"^The subject, (.+?), it follows that it is (not )?(.+?), because (.+?) is (not )?(.+?) and the reasoning is the same\. State the difference\.$")
_C5B_RE = re.compile(r"^The subject, (.+?), it follows that it is (not )?(.+?), because\? State the reason\.$")

def _concession_event_count(text, prev_kind):
    """How many ledger concession events a Defender turn creates
    (v2.0: the Type B/C opening statements are multi-event moves; the
    referee's ledger injection creates them in the same counts and
    order, so L_n bounds stay comparable across both modules)."""
    t = (text or "").strip()
    if t.startswith("Accept. By the authority of the text,"):
        # v2.2 accept-quote: a pervasion repair concedes the
        # pervasion AND the cascaded thesis; a minor-premise repair
        # concedes the atom only.
        return 2 if "therefore the subject," in t else 1
    if t.startswith("That consequence does not establish the pervasion") \
            or t.startswith("I accept the passage, but it does not establish") \
            or t in ("I hold the voice claim.", "I hold the interpretation."):
        return 0  # v2.2 deflections and holds concede nothing
    if _B_REASON_RE.match(t):
        # STATE_REASON: minor premise, pervasion, thesis.
        return 3
    if t.startswith("Definiens:"):
        # STATE_MEANING: illustration atom, then one per stated
        # division ("Divisions: none stated" = 0 divisions).
        divisions = 0
        for line in t.splitlines():
            line = line.strip()
            if line.startswith("Divisions:"):
                rest = line[len("Divisions:"):].strip()
                if rest and rest.lower() != "none stated":
                    divisions = len([x for x in rest.split(";") if x.strip()])
        return 1 + divisions
    # v2.1 escape-challenge answers. (A D-Reason move needs no branch:
    # it matches _B_REASON_RE above — minor premise, pervasion, thesis,
    # exactly as a STATE_REASON.) D-Diff locks its two difference
    # atoms; D-Concede locks the one thesis that now counts accepted;
    # D-Unfounded asserts nothing and creates no event.
    if t.startswith("There is a difference:"):
        return 2
    if t.startswith("I concede the distinction:"):
        return 1
    if t.startswith("Distinction challenge unfounded:") \
            or t.startswith("Reason demand unfounded:"):
        return 0
    return 1 if _is_concession_event(text, prev_kind) else 0

def _tokens(s):
    """Word tokens with punctuation stripped (DET_3C / clause matching)."""
    return set(re.findall(r"[a-z0-9]+", (s or "").lower()))

def _clause_traced(clause, cited_tokens):
    """DET_3C clause test: token overlap with the combined cited-node
    text — Jaccard >= 0.3, or either token set a subset of the other."""
    ctoks = _tokens(clause)
    if not ctoks or not cited_tokens:
        return False
    if ctoks <= cited_tokens or cited_tokens <= ctoks:
        return True
    return len(ctoks & cited_tokens) / len(ctoks | cited_tokens) >= 0.3

def _formal_consistent(derived, formal):
    """Surface-form lock between derived_move and the emitted move."""
    formal = (formal or "").strip()
    if derived == "ACCEPT":
        return formal == "Accept"
    if derived == "ALREADY_ACCEPTED":
        return formal == "Already accepted"
    if derived == "RNE":
        return formal.startswith("Reason not established.")
    if derived == "NPV":
        return formal.startswith("No pervasion.")
    if derived == "WHY":
        return formal == "Why"
    return True  # POSIT / C4_* derived moves carry no fixed surface form here

def _node_text(node):
    return " ".join(str(node[f]) for f in _NODE_TEXT_FIELDS if node.get(f))

def _text_norm(s):
    return re.sub(r"\s+", " ", (s or "").lower())

def score_justification(transcript, facts):
    """Score every Defender payload in the transcript. Returns the
    justification_detail dict the referee merges into its report."""
    turns = transcript.get("turns", [])
    is_a = getattr(facts, "is_a", {}) or {}
    perv = getattr(facts, "perv", {}) or {}
    fact_entries = set(is_a) | set(perv)
    is_a_subjects = {s for (s, _p) in is_a}
    canonical_terms, canonical_subjects = _canonical(facts)

    detail_turns = []
    illegal = []
    prev_kind, prev_slots = None, {}
    last_c6_claim = None   # v2.2: quote_claim of the latest C6 turn
    concession_count = 0
    prev_snapshot = None
    revision_count = 0
    hard_failures = 0
    earned_total = 0.0
    applicable_total = 0.0

    for idx, t in enumerate(turns):
        turn_no = t.get("turn", idx + 1)
        role = t.get("role")
        if role == "challenger":
            prev_kind, prev_slots = _classify_challenger(t.get("text", ""))
            if prev_kind == "C6":
                last_c6_claim = t.get("quote_claim")
            continue
        if role != "defender":
            continue
        # concession-events are counted up to AND INCLUDING this turn
        # before its payload is judged (the turn's own concession is
        # already on the ledger when its blurb cites it). v2.0: a turn
        # can create several events (the Type B/C opening statements).
        concession_count += _concession_event_count(t.get("text", ""), prev_kind)
        payload = t.get("defender_payload")
        if not payload:
            continue

        snap = payload.get("state_snapshot") or {}
        deriv = payload.get("derivation") or {}
        revision = payload.get("state_revision")
        if revision:
            revision_count += 1
        sections = {}
        nodes = {}
        for name in _STATE_SECTIONS:
            sec = snap.get(name)
            sec = sec if isinstance(sec, dict) else {}
            sections[name] = sec
            for nid, node in sec.items():
                nodes[nid] = (name, node if isinstance(node, dict) else {})

        cited_ids = deriv.get("cited_state_ids") or []
        cited_ledger = deriv.get("cited_ledger_ids") or []
        cited_facts = deriv.get("cited_facts") or []
        gate_audit = deriv.get("gate_audit") or {}
        # v2.0: turn-1 payloads of Type B/C matches carry a constructive
        # derivation (defender_v7) instead of the truth-table fields.
        # v2.2: quote-response payloads (derivation carries
        # quote_response, or the turn answers a C6 / closes after a
        # C6 refute) are constructive too.
        quote_turn = bool(deriv.get("quote_response")) \
            or prev_kind in ("C6", "C6_REFUTE")
        constructive = deriv.get("constructive") is True or quote_turn

        # ---------------- DET_1: referential / form integrity
        det1 = True
        zombie = False
        if not cited_ids:
            det1 = False
        for nid in cited_ids:
            if nid not in nodes:
                det1 = False
                continue
            name, node = nodes[nid]
            # definitions are IMMUTABLE and always citable; a cited
            # DEFEATED stance/commitment is a zombie citation.
            if name in ("stances", "commitments") and node.get("status") == "DEFEATED":
                det1 = False
                zombie = True
        for lid in cited_ledger:
            m = _LEDGER_RE.match(lid) if isinstance(lid, str) else None
            if not m or not (1 <= int(m.group(1)) <= concession_count):
                det1 = False
        for cf in cited_facts:
            if not isinstance(cf, str) or "::" not in cf:
                det1 = False
                continue
            s_part, p_part = cf.split("::", 1)
            ns, np_ = norm_term(s_part), norm_term(p_part)
            if (ns, np_) in fact_entries:
                continue
            if constructive:
                # v2.0 DET_1(i): a fact citation names an is_a entry
                # ("S :: R") or a pervasion ("R-pervasion :: P" — the
                # "-pervasion" suffix on the subject side marks the
                # pervasion form; strip it before the lookup). Plain
                # (R, P) pervasion membership is already covered by
                # fact_entries above.
                base = ns[:-len("-pervasion")] if ns.endswith("-pervasion") else ns
                if (base, np_) in perv or (base, np_) in is_a:
                    continue
            det1 = False
        prose = deriv.get("prose_summary")
        word_count = len(prose.split()) if isinstance(prose, str) else 0
        if not (35 <= word_count <= 75):
            det1 = False
        # v2.2: an interpretation answer must ride the sense-ruling
        # channel; without the SENSE_RULING override it fails DET_1
        # form integrity.
        if (t.get("text") or "").startswith(
                "I accept the passage, but it does not establish") \
                and gate_audit.get("override") != "SENSE_RULING":
            det1 = False

        # ---------------- DET_2: truth-table lock
        # v2.0: not applicable to constructive turns (no truth table).
        parsed = payload.get("parsed") or {}
        kinds = {k for k in (prev_kind, parsed.get("challenger_move")) if k}
        derived = deriv.get("derived_move")
        formal = payload.get("formal_move") or ""
        det2 = None
        if constructive or derived == "D_CONCEDE":
            # v2.1: a D-Concede has no truth table to lock (the
            # withdrawal is recorded in its DISTINCTION_WITHDRAWAL
            # revision, audited by the state-diff check), whether or
            # not the payload flags the turn constructive.
            det2 = None
        elif "C2" in kinds:
            a, b = deriv.get("step_a_holds"), deriv.get("step_b_holds")
            if a is None or b is None:
                det2 = False
            else:
                if a is False:
                    expected = {"RNE"}
                elif b is False:
                    expected = {"NPV"}
                else:
                    expected = {"ACCEPT", "ALREADY_ACCEPTED"}
                # Overrides (REVISION / SENSE_RULING) change the
                # booleans' values, never the coupling: the payload's
                # booleans are the post-ruling ones and the same
                # mapping judges them.
                det2 = derived in expected and _formal_consistent(derived, formal)
        elif kinds & {"C1", "C1_COND"}:
            th = deriv.get("thesis_holds")
            if th is True:
                det2 = derived == "ACCEPT" and _formal_consistent(derived, formal)
            elif th is False:
                if derived == "WHY":
                    det2 = _formal_consistent(derived, formal)
                elif derived == "ACCEPT" and gate_audit.get("override") == "LEDGER_CLOSURE":
                    # the one sanctioned decoupling: the ledger binds
                    # the answer, not the understanding.
                    det2 = _formal_consistent(derived, formal)
                else:
                    det2 = False
            else:
                det2 = False
        # C3/C4 turns: DET_2 not applicable (stays None).

        # ---------------- DET_3: term overlap
        subj = parsed.get("subject") or prev_slots.get("subject") or ""
        pred = parsed.get("predicate") or prev_slots.get("predicate") or ""
        reason = parsed.get("reason") or prev_slots.get("reason") or ""
        cons_text = _text_norm(" ".join(x for x in (subj, pred, reason) if x))
        cons_terms = {x for x in canonical_terms if x and x in cons_text}
        cited_text = _text_norm(" ".join(_node_text(nodes[nid][1])
                                         for nid in cited_ids if nid in nodes))
        cited_terms = {x for x in canonical_terms if x and x in cited_text}
        det3c = None
        if constructive and derived != "D_CONCEDE":
            # v2.0 DET_3C replaces DET_3 on constructive turns: the
            # cited nodes must actually ground the construction — for
            # Type B both the selected reason and the predicate must
            # appear (normalized) in the combined cited-node text; for
            # Type C every stated clause must trace to it.
            # v2.1: a D-Concede turn keeps the standard DET_3 (else
            # branch) even when flagged constructive — it states no
            # difference / reason / clause set to trace.
            if deriv.get("quote_response") or prev_kind in ("C6", "C6_REFUTE"):
                # v2.2 DET_3C-quote: the cited nodes must contain the
                # quotation claim's predicate and (for a pervasion
                # repair) its reason, as normalized substrings.
                qc = last_c6_claim or {}
                qp = norm_term(qc.get("predicate") or "")
                qr = norm_term(qc.get("reason") or "")
                det3c = bool(qp and qp in cited_text)
                if qc.get("repair_target") == "PERVASION":
                    det3c = bool(det3c and qr and qr in cited_text)
            elif "stated_difference" in deriv:
                # v2.1 D-Diff: the cited nodes must contain the stated
                # difference D and the denied predicate P.
                d_norm = norm_term(deriv.get("stated_difference") or "")
                p_norm = norm_term(parsed.get("predicate") or "")
                det3c = bool(d_norm and p_norm
                             and d_norm in cited_text and p_norm in cited_text)
            elif "selected_reason" in deriv:
                r_norm = norm_term(deriv.get("selected_reason") or "")
                p_norm = norm_term(parsed.get("predicate") or "")
                det3c = bool(r_norm and p_norm
                             and r_norm in cited_text and p_norm in cited_text)
            elif "clauses" in deriv:
                cited_tokens = _tokens(cited_text)
                clauses = deriv.get("clauses") or []
                det3c = bool(clauses) and all(
                    _clause_traced(c, cited_tokens) for c in clauses)
            else:
                det3c = False
            det3 = det3c
        else:
            det3 = not (cons_terms and cited_terms and not (cons_terms & cited_terms))

        # ---------------- DET_4: counterexample witness (NPV only)
        # v2.0: not applicable to constructive turns.
        det4 = None
        if derived == "NPV" and not constructive:
            det4 = False
            ce = deriv.get("counterexample")
            if isinstance(ce, str):
                s = ce.strip()
                if len(s) >= 3 and s.lower() not in _PLACEHOLDERS \
                        and norm_term(s) not in _PLACEHOLDERS:
                    nce = norm_term(s)
                    if nce in canonical_subjects or nce in is_a_subjects \
                            or (subj and nce == norm_term(subj)):
                        det4 = True

        # ---------------- state-diff audit (illegal mutations)
        turn_illegal = []
        if prev_snapshot is not None:
            for name in _STATE_SECTIONS:
                prev_sec = prev_snapshot.get(name)
                prev_sec = prev_sec if isinstance(prev_sec, dict) else {}
                cur_sec = sections[name]
                for nid, pnode in prev_sec.items():
                    if nid not in cur_sec:
                        turn_illegal.append({"turn": turn_no, "node": nid,
                                             "detail": f"node disappeared from {name}"})
                        continue
                    pnode = pnode if isinstance(pnode, dict) else {}
                    cnode = cur_sec[nid] if isinstance(cur_sec[nid], dict) else {}
                    changed = sorted(k for k in (set(pnode) | set(cnode)) - {"status", "ledger_links"}
                                     if pnode.get(k) != cnode.get(k))
                    if changed:
                        turn_illegal.append({"turn": turn_no, "node": nid,
                                             "detail": "fields changed without revision: " + ", ".join(changed)})
                    ps, cs = pnode.get("status"), cnode.get("status")
                    if ps != cs:
                        if ps == "ACTIVE" and cs == "DEFEATED":
                            if not revision or revision.get("defeated_node") != nid:
                                turn_illegal.append({"turn": turn_no, "node": nid,
                                                     "detail": "status ACTIVE->DEFEATED without a matching state_revision"})
                        elif ps == "DEFEATED" and cs == "ACTIVE":
                            turn_illegal.append({"turn": turn_no, "node": nid,
                                                 "detail": "status DEFEATED->ACTIVE (resurrection)"})
                        else:
                            turn_illegal.append({"turn": turn_no, "node": nid,
                                                 "detail": f"status changed {ps} -> {cs}"})
                for nid in cur_sec:
                    if nid not in prev_sec and not (revision and revision.get("new_node_id") == nid):
                        turn_illegal.append({"turn": turn_no, "node": nid,
                                             "detail": f"new node in {name} without a state_revision naming it"})
        illegal.extend(turn_illegal)
        prev_snapshot = snap

        # ---------------- weights / hard failures
        # A constructive turn cannot hard-fail on DET_2 (det2 is None);
        # a zombie citation still hard-fails via DET_1.
        hard = bool(det2 is False or zombie or turn_illegal)
        if constructive:
            # applicable weight is DET_1 + DET_3C only (25).
            applicable = WEIGHTS["det1"] + WEIGHTS["det3"]
            earned = (WEIGHTS["det1"] if det1 else 0) + (WEIGHTS["det3"] if det3 else 0)
        else:
            applicable = WEIGHTS["det1"] + WEIGHTS["det3"]
            earned = (WEIGHTS["det1"] if det1 else 0) + (WEIGHTS["det3"] if det3 else 0)
            if det2 is not None:
                applicable += WEIGHTS["det2"]
                earned += WEIGHTS["det2"] if det2 else 0
            if det4 is not None:
                applicable += WEIGHTS["det4"]
                earned += WEIGHTS["det4"] if det4 else 0
        if hard:
            earned = 0
            hard_failures += 1
        earned_total += earned
        applicable_total += applicable
        detail_turns.append({"turn": turn_no, "det1": det1, "det2": det2,
                             "det3": det3, "det4": det4, "hard_failure": hard,
                             "constructive": constructive, "det3c": det3c})

    if detail_turns and applicable_total:
        det = earned_total / applicable_total
        if revision_count >= 3:
            det = max(0.0, det - 0.10)  # the 3rd revision costs 0.10, once
        det = round(det, 3)
    else:
        det = None
    return {
        "justification_det": det,
        "hard_justification_failures": hard_failures,
        "epistemic_forfeit": bool(revision_count >= 4 or hard_failures >= 2),
        "revision_count": revision_count,
        "scored_turns": len(detail_turns),
        "turns": detail_turns,
        "illegal_state_mutations": illegal,
    }
