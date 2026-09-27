# Travel & Entertainment and G&A Expense Policy — Meridian Industries

**SYNTHETIC / FOR TRAINING ONLY.** This document is fictional training data created for the Finance AI Academy "AI Solution Architect" course. It does not describe a real company, real financial results, or real financial advice.

| Field | Value |
|---|---|
| doc_id | `expense_policy` |
| Document title | T&E and G&A Expense Policy |
| Effective date | 2026-01-01 |
| Owner | Corporate Controller |
| Applies to | All Meridian Industries employees, all business units |

## 1. Approval thresholds

All expense reports require approval before reimbursement. Thresholds are based on the total dollar amount of the individual expense report (or, for a purchase requisition, the total committed spend):

| Amount | Required Approver |
|---|---|
| Under $500 | Direct manager |
| $500 – $5,000 | Department Director |
| Over $5,000 | Vice President (or CFO for spend over $25,000) |

Approval must be obtained **before** the expense is incurred whenever the spend is planned in advance (e.g. booking travel for a known event); expenses that could not reasonably be pre-approved (e.g. an unplanned same-day client meal) may be approved after the fact by the same approver tier, with a note explaining why pre-approval was not obtained.

## 2. What is reimbursable

Reimbursable under account 6100 (Travel & Entertainment — see `chart_of_accounts` for full account scope):

- Airfare, rail, rideshare/taxi, mileage (at the standard corporate mileage rate), parking, and tolls for business travel
- Hotel/lodging for business travel, at or below the standard corporate rate for the destination city
- Meals while traveling, within the per-diem limits in Section 3
- Client and prospect entertainment directly tied to a business purpose, with the business purpose and attendees documented on the expense report
- Registration, venue, and catering costs for a pre-approved department or company event

**Not reimbursable under this policy:**
- Relocation costs (handled separately under the Relocation Policy, booked to Salaries & Benefits, not T&E)
- Normal home-to-work commuting
- Personal travel extensions, upgrades beyond policy class of service, or entertainment with no business purpose
- Alcohol beyond a reasonable amount at a client meal (subject to manager judgment)

## 3. Per-diem notes

- Domestic travel: meals are reimbursed up to the standard domestic per-diem rate per day, receipts required for any single meal over $75.
- International travel: per-diem follows the destination-country rate published by Corporate Travel; receipts required for any single meal over $100.
- Per-diem is prorated for partial travel days (departure day and return day).
- Per-diem and actual-receipt reimbursement may not both be claimed for the same meal.

## 4. Large one-time events (company-wide kickoffs, conferences, offsites)

Company-wide or large department events — such as an annual sales kickoff, a company conference, or a multi-team offsite — are **not** treated as ordinary discretionary travel. They require:

1. A **pre-approved budget line** submitted by the sponsoring department (typically Sales or Marketing) during the annual budget cycle or, if planned mid-year, via a separate budget amendment approved by the CFO.
2. **VP-level sign-off** on the estimated total cost (venue, catering, attendee travel and lodging) before any vendor is contracted, regardless of whether the estimated total falls under the normal $5,000 report-level threshold in Section 1 — the event-level threshold applies to the full estimated event cost, not to any individual attendee's expense report.
3. A post-event reconciliation submitted by the event owner within 30 days of the event, comparing actual cost to the pre-approved budget line.

This is the process under which the FY2026 Global Sales Kickoff was budgeted as part of the Q3 2026 Travel & Entertainment line in `budget_2026`. When an event's actual cost exceeds its pre-approved budget line, the excess appears as an unfavorable T&E variance in the applicable quarter's variance report (see `variance_report_q3_2026` for an example) and should be called out by name in variance commentary, not folded silently into "general T&E overspend."

## 5. Submission and documentation

- Expense reports must be submitted within 30 days of the expense being incurred.
- Receipts are required for any expense over $25.
- Every expense report must state a business purpose; entertainment and event expenses must also list attendees.
