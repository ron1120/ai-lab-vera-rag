"""
Vera multi-agent pipeline. SYNTHETIC / FOR TRAINING ONLY.

Refactors the flat answer() function (vera/answer.py) into the four-agent
pipeline described in Section V of the booklet — Intake, FP&A Analyst,
Narrative Drafter, Controller Reviewer — plus the review-gated retry
(retrieve -> draft -> controller_review -> reply, with an escalate edge and
a clarify edge) described in Section U.

Every agent reads and adds to ONE shared payload dict (the handoff
contract from Section V):

    {
      "intent": "variance_question | policy_lookup | forward_looking | competitor_question",
      "entities": {"account": None, "department": None, "period": None},
      "citations": [{"doc_id": None, "section": None, "effective_date": None}],
      "compliance_flags": [],
      "escalate_to_human": False,
      "route": "answer | refuse_forward_looking | refuse_competitor | escalate_period_not_closed",
    }

plus two lab-only bookkeeping fields: "_question" (carries the original
question to agents that don't receive it as a parameter) and "_trace" (the
model-routing proof described below).
"""

import re

from vera.answer import (
    _classify,
    _compose_answer_text,
    _escalate_period_not_closed,
    _refuse_competitor,
    _refuse_forward_looking,
)
from vera.config import LABEL
from vera.retrieve import retrieve

# Controller Reviewer scans DRAFTED ANSWER TEXT (which, in this lab,
# largely echoes retrieved SOURCE DOCUMENT prose) for forward-looking
# leakage. This is a different job from classifying a short user
# QUESTION (vera.answer._FORWARD_LOOKING_PATTERNS) — reusing that list
# here produced false positives on legitimate historical/methodology
# language, e.g. "capital project requests" (project as a noun) and
# "submits a bottom-up forecast for their cost center" (forecast as a
# noun describing the budgeting process, not a prediction). These
# patterns instead target the actual shape of a leaked prediction, per
# the board_narrative_style_guide's own "Don't" examples ("we expect Q4
# to...", "this should normalize by...", "Q4 should come in around...").
_DRAFT_LEAKAGE_PATTERNS = [
    r"\bwe expect\b",
    r"\bwe forecast\b",
    r"\bshould (come in|normalize|land|hit|even out)\b",
    # Deliberately NOT "expected to be" — that also matches ordinary
    # normative/policy language ("large events are expected to be
    # pre-approved"), which isn't a financial forecast leak.
    r"\bexpected to (come in|land|hit|normalize)\b",
    r"\bwill (likely |probably )?(be|come in|land|hit)\b",
    r"\bgoing forward\b",
    r"\bnext (quarter|year|month)\b",
]

# ---------------------------------------------------------------------------
# Model routing (Section V — "Which model for which role")
# ---------------------------------------------------------------------------
#
# Intake and FP&A Analyst are narrow, high-volume, low-reasoning jobs
# (classification / retrieval) -> fast, cheap tier. Narrative Drafter and
# Controller Reviewer need the strongest reasoning -> strong tier. These
# model_name values are placeholders; no real model API is called for any
# of the four roles in this lab step. The point is to prove the ROUTING is
# wired correctly (see each agent's "_trace" entry below), not to make a
# live model call.

MODEL_ROUTING = {
    "intake": {"model_tier": "fast", "model_name": "claude-haiku-4-5"},
    "fpna_analyst": {"model_tier": "fast", "model_name": "claude-haiku-4-5"},
    "narrative_drafter": {"model_tier": "strong", "model_name": "claude-opus-5-5"},
    "controller_reviewer": {"model_tier": "strong", "model_name": "claude-opus-5-5"},
}

_MAX_CLARIFY_RETRIES = 1


def _new_payload(question):
    return {
        "intent": None,
        "entities": {"account": None, "department": None, "period": None},
        "citations": [],
        "compliance_flags": [],
        "escalate_to_human": False,
        "route": None,
        "answer": None,
        "_question": question,
        "_trace": [],
    }


def _trace(payload, role):
    payload["_trace"].append({"agent": role, **MODEL_ROUTING[role]})


# --- Entity extraction (Intake helper) -------------------------------------

_ACCOUNT_KEYWORDS = {
    "t&e": "Travel & Entertainment",
    "travel & entertainment": "Travel & Entertainment",
    "travel and entertainment": "Travel & Entertainment",
    "marketing": "Marketing",
    "cogs": "COGS",
    "sg&a": "SG&A",
    "capex": "Capex",
    "r&d": "R&D",
    "revenue": "Revenue",
}

_QUARTER_RE = re.compile(r"\bq[1-4]\s?2026\b", re.IGNORECASE)


def _extract_entities(query):
    q_lower = query.lower()
    account = None
    for kw, canonical in _ACCOUNT_KEYWORDS.items():
        if kw in q_lower:
            account = canonical
            break

    department = "SG&A" if account in (
        "Travel & Entertainment", "Marketing", "SG&A",
    ) else None

    period_match = _QUARTER_RE.search(query)
    period = period_match.group(0).upper().replace(" ", " ") if period_match else None

    return {"account": account, "department": department, "period": period}


# ---------------------------------------------------------------------------
# The four agents
# ---------------------------------------------------------------------------


def intake(question, payload):
    """Classify the question and, for refuse/escalate cases, is the ONLY
    agent allowed to short-circuit straight to a reply — no other agent
    ever runs for those cases."""
    classification = _classify(question)

    if classification == "forward_looking":
        payload["intent"] = "forward_looking"
        payload["route"] = "refuse_forward_looking"
        payload["citations"] = []
        payload["answer"] = _refuse_forward_looking()["answer"]

    elif classification == "competitor":
        payload["intent"] = "competitor_question"
        payload["route"] = "refuse_competitor"
        payload["citations"] = []
        payload["answer"] = _refuse_competitor()["answer"]

    elif classification == "period_not_closed":
        result = _escalate_period_not_closed(question)
        payload["intent"] = "variance_question"
        payload["route"] = "escalate_period_not_closed"
        # _escalate_period_not_closed() (vera/answer.py) uses the
        # "closed_date" key to match the flat answer() schema; the
        # multi-agent handoff schema (Section V) uses "effective_date" —
        # remap here so every agent in this pipeline sees one consistent
        # citation shape.
        payload["citations"] = [
            {
                "doc_id": c["doc_id"],
                "section": c["section"],
                "effective_date": c["closed_date"],
            }
            for c in result["citations"]
        ]
        payload["compliance_flags"] = ["period_not_closed"]
        payload["escalate_to_human"] = True
        payload["answer"] = result["answer"]
        entities = _extract_entities(question)
        entities["period"] = None  # unclosed period has no confirmed entity
        payload["entities"] = entities

    else:
        entities = _extract_entities(question)
        payload["entities"] = entities
        payload["intent"] = (
            "variance_question" if entities["account"] else "policy_lookup"
        )
        payload["route"] = "answer"

    _trace(payload, "intake")
    return payload


def fpna_analyst(payload):
    """Runs RAG over the financial docs, pulls the exact figures. Never
    invents or rounds a number — everything comes from retrieve()."""
    hits = retrieve(payload["_question"], k=3)
    payload["_retrieved_hits"] = hits
    payload["citations"] = [
        {
            "doc_id": h["doc_id"],
            "section": h["section"],
            "effective_date": h["effective_or_closed_date"],
        }
        for h in hits
    ]
    _trace(payload, "fpna_analyst")
    return payload


def narrative_drafter(payload):
    """Writes the answer from the Analyst's figures only — reads the
    handoff payload's retrieved hits, adds no commentary of its own."""
    hits = payload.get("_retrieved_hits", [])
    if hits:
        payload["answer"] = _compose_answer_text(payload["_question"], hits)
    else:
        payload["answer"] = (
            "I couldn't find anything in Meridian's published documents to "
            f"answer this. Escalating to FP&A rather than guessing. {LABEL}."
        )
    _trace(payload, "narrative_drafter")
    return payload


def controller_reviewer(payload):
    """Blocks unapproved forward guidance, verifies citation accuracy,
    catches unclosed-period leaks, clears the draft to send. Never
    rewrites the numbers — only flags and (once) sends the question back
    for a redo via the Section U 'clarify' edge."""
    draft = payload.get("answer") or ""
    issues = []

    if not payload.get("citations"):
        issues.append("missing_citation")

    if not any(c.get("effective_date") for c in payload.get("citations", [])):
        issues.append("missing_close_date")

    for pattern in _DRAFT_LEAKAGE_PATTERNS:
        if re.search(pattern, draft.lower()):
            issues.append("forward_looking_language_in_draft")
            break

    if issues:
        payload["compliance_flags"] = list(
            dict.fromkeys(payload.get("compliance_flags", []) + issues)
        )
        payload["route"] = "clarify"
    else:
        payload["route"] = "answer"

    _trace(payload, "controller_reviewer")
    return payload


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def orchestrate(question):
    """Run the full Vera multi-agent pipeline for one question.

    - Always calls intake() first.
    - If intake sets route "answer", calls fpna_analyst() -> narrative_drafter()
      -> controller_reviewer() in order.
    - If controller_reviewer routes to "clarify" (Section U's review-gate
      retry edge), sends the question back through fpna_analyst() ->
      narrative_drafter() -> controller_reviewer() ONCE more before giving
      up and shipping the best draft, flagging that it was not fully
      cleared.
    - If intake sets any other route (refuse_forward_looking,
      refuse_competitor, escalate_period_not_closed), returns immediately
      after intake — fpna_analyst, narrative_drafter, and
      controller_reviewer never run, by design (see Section V's
      action -> agent -> handoff map).

    Returns the final payload, including the full "_trace" list.
    """
    payload = _new_payload(question)
    intake(question, payload)

    if payload["route"] != "answer":
        return payload

    fpna_analyst(payload)
    narrative_drafter(payload)
    controller_reviewer(payload)

    retries = 0
    while payload["route"] == "clarify" and retries < _MAX_CLARIFY_RETRIES:
        retries += 1
        fpna_analyst(payload)
        narrative_drafter(payload)
        controller_reviewer(payload)

    if payload["route"] == "clarify":
        # Exhausted retries and still not clean — escalate to a human
        # rather than ship an uncleared draft, per Vera's "never guess"
        # rule. "clarify" is an internal in-flight state, never a valid
        # final route, so it must not leak out of orchestrate().
        payload["escalate_to_human"] = True
        payload["route"] = "escalate_needs_human_review"
        payload["answer"] = (
            "ESCALATION — not an answer. Vera's Controller Reviewer could "
            "not clear a compliant draft for this question after "
            f"{_MAX_CLARIFY_RETRIES + 1} attempt(s) (flags: "
            f"{payload['compliance_flags']}). Routing to a human FP&A "
            f"reviewer rather than shipping an unverified draft. {LABEL}."
        )

    return payload
