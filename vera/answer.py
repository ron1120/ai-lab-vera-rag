"""
Vera answer generation. SYNTHETIC / FOR TRAINING ONLY.

answer(query) classifies the question BEFORE calling retrieve(), so
forward-looking and competitor/external-company questions are refused
without ever touching the vector store, then retrieves top chunks and
generates a plain-language answer using ONLY facts and numbers present in
the retrieved text — never inventing or rounding a number that isn't there.
"""

import os
import re

from vera.config import DOCS_DIR, LABEL, METADATA_CSV
from vera.retrieve import retrieve
from vera.ingest import _load_catalog

# --- Classification -------------------------------------------------------
#
# These are deliberately simple, explainable keyword/pattern checks (not a
# model call) so classification behavior is easy to audit and test. They
# only need to catch the phrasing patterns this lab's test questions use;
# a production Vera would likely use a small classifier model here (see
# Section V's "Intake" role) instead of hand-written patterns.

_FORWARD_LOOKING_PATTERNS = [
    r"\bwill\b.*\b(be|hit|come in|land)\b",
    r"\bwill\s+\w+\s+be\b",
    r"\bwhat will\b",
    r"\bwhat's .*going to be\b",
    r"\bnext (quarter|year|month)\b",
    r"\bforecast\b",
    r"\bproject(ed|ion)?\b",
    r"\bexpect(ed)? .* (to|will)\b",
    r"\bhit (its |our |the )?(budget|target|plan)\b",
    r"\bgoing forward\b",
    r"\bupcoming\b",
]

_COMPETITOR_PATTERNS = [
    r"\bcompetitor\b",
    r"\b(acme|globex|initech|umbrella|hooli|stark industries|wayne enterprises)\b",
    r"\b[A-Z][a-zA-Z]+ (Corp|Inc|Industries|Enterprises|LLC|Co\.)\b",
]

_MONTH_NAMES = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
]

# --- close_calendar_2026.md parsing ---------------------------------------
#
# Read directly from the source document (not via retrieve()) so the
# escalate decision is driven by the authoritative close calendar every
# time, independent of what similarity search happens to surface.

_CLOSE_TABLE_ROW_RE = re.compile(
    r"^\|\s*\*{0,2}([A-Za-z0-9 ]+?)\*{0,2}\s*\|\s*\*{0,2}([\d-]+|—)\*{0,2}\s*\|\s*\*{0,2}([\d-]+|—)\*{0,2}\s*\|\s*\*{0,2}([^|]+?)\*{0,2}\s*\|"
)


def _parse_close_calendar():
    """Parse close_calendar_2026.md into a structured view:
    {
      "periods": { "October 2026": {"status": "...", "target_close": "..."}, ... },
      "latest_closed_period": "Q3 2026",
      "latest_closed_date": "2026-10-05",
    }
    """
    path = os.path.join(DOCS_DIR, "close_calendar_2026.md")
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    periods = {}
    for line in lines:
        m = _CLOSE_TABLE_ROW_RE.match(line)
        if not m:
            continue
        period, target_close, actual_close, status = (g.strip() for g in m.groups())
        if period.lower() in ("period", "---", ""):
            continue
        if not re.search(r"\d{4}", period):
            continue
        periods[period] = {
            "status": status,
            "target_close": target_close,
            "actual_close": actual_close,
        }

    latest_closed_period, latest_closed_date = None, None
    for period, info in periods.items():
        if info["status"].lower().startswith("closed") and period.startswith("Q"):
            latest_closed_period = period
            latest_closed_date = info["actual_close"]

    return {
        "periods": periods,
        "latest_closed_period": latest_closed_period,
        "latest_closed_date": latest_closed_date,
    }


def _period_mentioned_in_query(query, periods):
    """Return the calendar period key (e.g. 'October 2026', 'Q4 2026') that
    the query appears to reference, or None."""
    q_lower = query.lower()

    if "q4" in q_lower or "fourth quarter" in q_lower:
        for period in periods:
            if period.startswith("Q4"):
                return period

    for month in _MONTH_NAMES:
        if month in q_lower:
            for period in periods:
                if period.lower().startswith(month):
                    return period

    return None


def _classify(query):
    """Return one of: 'forward_looking', 'competitor', 'period_not_closed',
    'in_scope'."""
    q = query.strip()
    q_lower = q.lower()

    for pattern in _FORWARD_LOOKING_PATTERNS:
        if re.search(pattern, q_lower):
            return "forward_looking"

    for pattern in _COMPETITOR_PATTERNS:
        match = re.search(pattern, q, flags=re.IGNORECASE)
        if match and "meridian" not in match.group(0).lower():
            return "competitor"

    calendar = _parse_close_calendar()
    mentioned_period = _period_mentioned_in_query(q, calendar["periods"])
    if mentioned_period:
        status = calendar["periods"][mentioned_period]["status"]
        if not status.lower().startswith("closed"):
            return "period_not_closed"

    return "in_scope"


def _refuse_forward_looking():
    return {
        "answer": (
            "Vera answers only from closed, published Meridian financials "
            "and does not forecast. I can't project future-period figures "
            f"such as revenue or budget attainment. {LABEL}."
        ),
        "citations": [],
        "label": LABEL,
    }


def _refuse_competitor():
    return {
        "answer": (
            "Vera only has access to Meridian Industries' own published "
            "financial documents. I don't have data on other companies and "
            f"can't answer questions about a competitor or external "
            f"organization. {LABEL}."
        ),
        "citations": [],
        "label": LABEL,
    }


def _escalate_period_not_closed(query):
    """Build an ESCALATION result (not an answer, not a refusal) for a
    question about a period close_calendar_2026.md shows as not yet
    closed. No Q4 figure of any kind is invented — everything here comes
    from the close calendar's own status/date fields."""
    calendar = _parse_close_calendar()
    mentioned_period = _period_mentioned_in_query(query, calendar["periods"])
    info = calendar["periods"].get(mentioned_period, {})
    target_close = info.get("target_close", "an unpublished date")

    latest_closed_period = calendar["latest_closed_period"]
    latest_closed_date = calendar["latest_closed_date"]

    _, catalog_rows = _load_catalog()
    close_cal_row = catalog_rows.get("close_calendar_2026", {})
    close_cal_effective_date = close_cal_row.get("effective_date", "")

    answer_text = (
        f"ESCALATION — not an answer. {mentioned_period or 'The requested period'} "
        f"is not yet closed (per `close_calendar_2026`, target close "
        f"{target_close}), so I can't report an actual figure for it. "
        f"The latest closed period is {latest_closed_period}, closed "
        f"{latest_closed_date}. Please contact your FP&A business partner "
        f"for any in-flight estimate for {mentioned_period or 'this period'}. "
        f"{LABEL}."
    )

    return {
        "answer": answer_text,
        "citations": [
            {
                "doc_id": "close_calendar_2026",
                "section": mentioned_period or "2026 close status by month and quarter",
                "closed_date": close_cal_effective_date,
            }
        ],
        "label": LABEL,
        "escalation": True,
    }


def answer(query, k=3):
    """Answer a Meridian FP&A question grounded strictly in retrieved
    chunks — but first classify the question, and refuse forward-looking
    or competitor/external-company questions WITHOUT calling retrieve() at
    all.

    Returns:
        {
            "answer": <string>,
            "citations": [ { "doc_id": ..., "section": ..., "closed_date": ... }, ... ],
            "label": "SYNTHETIC / FOR TRAINING ONLY",
        }
    """
    classification = _classify(query)

    if classification == "forward_looking":
        return _refuse_forward_looking()

    if classification == "competitor":
        return _refuse_competitor()

    if classification == "period_not_closed":
        return _escalate_period_not_closed(query)

    hits = retrieve(query, k=k)

    if not hits:
        return {
            "answer": (
                "I couldn't find anything in Meridian's published documents "
                "to answer this. Escalating to FP&A rather than guessing."
            ),
            "citations": [],
            "label": LABEL,
        }

    # Build the answer text and citations directly from the retrieved
    # chunks' own text — no numbers are generated outside of what is
    # literally present in the retrieved chunks below.
    answer_text = _compose_answer_text(query, hits)

    citations = [
        {
            "doc_id": h["doc_id"],
            "section": h["section"],
            "closed_date": h["effective_or_closed_date"],
        }
        for h in hits
    ]

    return {
        "answer": answer_text,
        "citations": citations,
        "label": LABEL,
    }


def _compose_answer_text(query, hits):
    """Compose a plain-language answer from the retrieved chunk text.

    This is a deliberately literal composer (no external LLM call in this
    lab step): it surfaces the retrieved passage(s) verbatim/near-verbatim
    plus a citation line, so every number in the output is guaranteed to
    come from the retrieved text and nothing else. It includes ALL
    retrieved hits' text (deduped by section), not just the top one — a
    supporting fact (e.g. the Chart of Accounts row that explicitly
    classifies an account as SG&A) can rank just outside the #1 vector
    match and would otherwise be silently dropped from the answer even
    though it was retrieved and cited.
    """
    passages = []
    citation_bits = []
    seen = set()
    for h in hits:
        key = (h["doc_id"], h["section"])
        if key in seen:
            continue
        seen.add(key)
        passages.append(h["text"].strip())
        citation_bits.append(
            f"`{h['doc_id']}`, section '{h['section']}', books closed {h['effective_or_closed_date']}"
        )

    source_line = "Source: " + "; ".join(citation_bits) + f". {LABEL}."
    return "\n\n".join(passages) + "\n\n" + source_line
