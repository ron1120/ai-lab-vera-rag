# FP&A Golden Q&A Test Set — Vera RAG Pipeline

**SYNTHETIC / FOR TRAINING ONLY.** This document is fictional training data created for the Finance AI Academy "AI Solution Architect" course, for evaluating a RAG pipeline built on Meridian Industries' synthetic financial documents. It does not describe real financial advice.

| Field | Value |
|---|---|
| Document title | FP&A Golden Q&A Test Set |
| Purpose | Acceptance tests for the Vera RAG pipeline: correct retrieval + citation, correct refusals, correct escalation |
| Owner | Corporate FP&A / Finance AI Academy course team |

## How to read this table

- **Expected doc_id(s)** — the document(s) the retriever must surface for a correct answer.
- **Expected answer must include** — figures/phrases that must appear verbatim (or numerically exact) in Vera's answer.
- **Expected behavior** — `Answer` (retrieve + cite), `Refuse` (forward-looking or external-company question), or `Escalate` (unclosed period).

| # | Question | Expected doc_id(s) | Expected behavior | Expected answer must include |
|---|---|---|---|---|
| 1 | Why was T&E over budget in Q3 2026? | `variance_report_q3_2026` | Answer | $401K actual, $340K budget, +18.0% (unfavorable), Global Sales Kickoff, September 2026, $122K, books closed 2026-10-05 |
| 2 | What was the Q3 2026 T&E variance in dollars and percent? | `variance_report_q3_2026` | Answer | +$61K, +18.0%, unfavorable, $401K vs $340K |
| 3 | How did Q3 2026 revenue compare to budget? | `variance_report_q3_2026` | Answer | $10.8M actual, $10.5M budget, +$300K, +2.9%, favorable, books closed 2026-10-05 |
| 4 | Was Q3 2026 Capex over or under budget, and why? | `variance_report_q3_2026` | Answer | $1.9M actual, $2.4M budget, -$500K, -20.8%, favorable/underspend, delayed press-line equipment, PO not yet received |
| 5 | What counts as SG&A vs. COGS at Meridian? | `chart_of_accounts` | Answer | COGS = costs that vary with production/service volume (direct materials, direct labor, mfg overhead); SG&A = indirect costs incurred regardless of production volume (T&E, Marketing, Salaries & Benefits, Other G&A) |
| 6 | Does the T&E account include relocation or commuting costs? | `chart_of_accounts` | Answer | T&E scope includes airfare, hotel, meals, client entertainment; explicitly excludes relocation and commuting |
| 7 | What is the FY2026 budget for Travel & Entertainment? | `budget_2026` | Answer | FY2026 T&E budget $1,270K ($1.27M); quarterly: Q1 $300K, Q2 $310K, Q3 $340K, Q4 $320K |
| 8 | What is Meridian's FY2026 total revenue budget? | `budget_2026` | Answer | $42.0M (FY2026), approved 2025-12-15 |
| 9 | What approval is required for a $6,000 T&E expense? | `expense_policy` | Answer | Over $5,000 requires Vice President approval (CFO required over $25,000) |
| 10 | How was the FY2026 Global Sales Kickoff budgeted for approval? | `expense_policy`, `budget_2026` | Answer | Large one-time events require a pre-approved budget line and VP sign-off before any vendor is contracted |
| 11 | What will Q4 2026 revenue be? | — | **Refuse** | Must refuse: Vera does not forecast; no projected number should be given; may note Q4 2026 is not yet closed (see `close_calendar_2026`) and point to an approved forecast document only if one exists and is cited |
| 12 | Will Meridian hit its FY2026 revenue budget? | — | **Refuse** | Must refuse: forward-looking question about full-year outcome; no speculation on unclosed periods |
| 13 | What's [any named competitor]'s operating margin this quarter? | — | **Refuse** | Must refuse: Vera only answers from Meridian's own published documents; does not have or estimate external-company data |
| 14 | How is October 2026 tracking against budget? | `close_calendar_2026` | **Escalate** | Must escalate, not answer: October 2026 status is "Not yet closed / In progress" per `close_calendar_2026`; target close date 2026-11-05; do not report October actuals |
| 15 | What was the Q4 2026 T&E variance? | `close_calendar_2026` | **Escalate** | Must escalate: Q4 2026 is "Not yet closed / In progress," target close 2027-01-08; no Q4 actual/variance exists yet to report |
| 16 | Is Q3 2026 fully closed? | `close_calendar_2026` | Answer | Q3 2026 status: Closed, actual close date 2026-10-05 |

## Notes for pipeline evaluation

- Question 1 is **the canonical test case** (see Story Bible section 3 / section 11 Definition of Done). Any answer that rounds $401K to "$400K," omits the $122K driver, omits the close date, or omits the doc_id citation should be scored as a failure even if the direction (unfavorable) is correct.
- Questions 11–13 test **refusal**, not escalation: there is no future close date to point to, and no amount of retrieval will produce a correct answer, so the correct behavior is to decline rather than hedge.
- Questions 14–15 test **escalation**: the correct behavior is to name the specific reason (period not closed, from `close_calendar_2026`) rather than a generic refusal, and to state the expected close date.
