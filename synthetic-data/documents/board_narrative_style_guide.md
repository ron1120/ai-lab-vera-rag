# Board Narrative Style Guide — Variance Commentary — Meridian Industries

**SYNTHETIC / FOR TRAINING ONLY.** This document is fictional training data created for the Finance AI Academy "AI Solution Architect" course. It does not describe a real company, real financial results, or real financial advice.

| Field | Value |
|---|---|
| doc_id | `board_narrative_style_guide` |
| Document title | Board Narrative Style Guide — Variance Commentary |
| Effective date | 2025-11-01 |
| Owner | CFO, Meridian Industries |
| Purpose | How FP&A and the Controller's team should write variance commentary that goes to the Board — used later in this course as a fine-tuning teaching example (consistent tone at scale) |

## Why this exists

Meridian produces hundreds of variance commentary lines a year across business units and cost centers. The CFO wants every one of them to read like it came from the same disciplined analyst, regardless of who drafted it. Prompting a model with these rules works for a handful of examples; holding this exact tone consistently across hundreds of commentaries per year, per department, is the kind of scale problem fine-tuning is better suited for than prompting alone.

## Rules

1. **Lead with the number and direction.** The first clause states the actual, the budget (or the variance $/%), and whether it's favorable or unfavorable. Do not bury the number in the third sentence.
2. **Name the driver.** Every material variance must name the specific, identifiable cause (an event, a customer, a vendor, a timing shift) — never a vague category like "higher costs" or "market conditions" on its own.
3. **Avoid hedging language.** Do not write "seems to," "may have been," "it's possible that," or "roughly." State the number precisely and the driver plainly. If a number is genuinely uncertain or unclosed, say so explicitly and route to escalation — do not hedge around it.
4. **Avoid forward-looking statements.** Board variance commentary reports what happened in a closed period. Never add "we expect Q4 to...", "this should normalize by...", or any projection. Forward guidance belongs in a separate, explicitly labeled forecast document, not in variance commentary.
5. **Always cite the source document and the books-closed date.** Every commentary line must be traceable to a `doc_id` and the close date of the period it describes — never "as of today."
6. **Be concise.** One to three sentences per variance line. The Board reads dozens of these; brevity is a feature.

## Examples — correct style

> Q3 2026 Travel & Entertainment came in at $401K against a $340K budget, a $61K (+18.0%) unfavorable variance, driven primarily by the $122K Global Sales Kickoff held in September 2026. Source: `variance_report_q3_2026`, books closed 2026-10-05.

> Q3 2026 Capex was $1.9M against a $2.4M budget, a $500K (-20.8%) favorable variance due to delayed delivery of press-line equipment for Manufacturing; the purchase order has not yet been received. Source: `variance_report_q3_2026`, books closed 2026-10-05.

> Q3 2026 Revenue was $10.8M against a $10.5M budget, a $300K (+2.9%) favorable variance, driven by stronger order volume in Manufacturing and Field Services. Source: `variance_report_q3_2026`, books closed 2026-10-05.

## Examples — wrong style ("Don't")

> **Don't:** "T&E was a bit high this quarter, mostly due to some travel and a few events — nothing too concerning, and it should probably even out by year end."
> *Why it's wrong: no precise number, no named driver, hedging language ("a bit," "should probably"), and a forward-looking statement ("even out by year end") that does not belong in closed-period variance commentary.*

> **Don't:** "Given the kickoff overspend, we expect Q4 T&E to come in around $310K as the team tightens travel discipline."
> *Why it's wrong: this sneaks in a forecast for an unclosed period (Q4 2026). Variance commentary reports what already happened in a closed period; it never projects a future number, even when the projection sounds reasonable.*

## Checklist before publishing a commentary line

- [ ] States the actual and budget (or $ and % variance) in the first sentence
- [ ] Names a specific driver, not a vague category
- [ ] Contains no hedging words ("roughly," "seems," "may have")
- [ ] Contains no forward-looking statement about a future/unclosed period
- [ ] Cites `doc_id` and the books-closed date
- [ ] Is three sentences or fewer
