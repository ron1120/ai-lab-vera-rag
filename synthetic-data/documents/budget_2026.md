# FY2026 Approved Budget — Meridian Industries

**SYNTHETIC / FOR TRAINING ONLY.** This document is fictional training data created for the Finance AI Academy "AI Solution Architect" course. It does not describe a real company, real financial results, or real financial advice.

| Field | Value |
|---|---|
| doc_id | `budget_2026` |
| Document title | FY2026 Approved Budget |
| Status | Approved |
| Approval date | 2025-12-15 |
| Approved by | CFO, Meridian Industries |
| Owner | Corporate FP&A |
| Fiscal year | FY2026 (January – December 2026) |

## Company overview

Meridian Industries is a mid-size industrial and services company operating through three business units — **Manufacturing**, **Field Services**, and **Distribution**. The FY2026 budget presented below covers the consolidated corporate P&L accounts tracked by FP&A for quarterly budget-vs-actual reporting: revenue, cost of goods sold, SG&A (including Travel & Entertainment, Marketing, Salaries & Benefits, and Other G&A), R&D, and capital expenditures. This budget was built bottom-up by cost center and approved by the CFO on 2025-12-15.

## FY2026 quarterly budget by account

All figures in $ thousands (K) unless noted. Values reflect **budget**, not actuals.

| Account | Q1 2026 | Q2 2026 | Q3 2026 | Q4 2026 | FY2026 Total |
|---|---:|---:|---:|---:|---:|
| **Revenue** | 9,900 | 10,300 | 10,500 | 11,300 | **42,000** |
| **COGS** | 6,200 | 6,400 | 6,500 | 6,900 | **26,000** |
| **Gross Margin** | 3,700 | 3,900 | 4,000 | 4,400 | **16,000** |
| **SG&A (Total)** | 2,510 | 2,600 | 2,760 | 2,730 | **10,600** |
| — Travel & Entertainment (T&E) | 300 | 310 | 340 | 320 | 1,270 |
| — Marketing | 1,050 | 1,100 | 1,200 | 1,150 | 4,500 |
| — Salaries & Benefits (SG&A) | 870 | 890 | 910 | 930 | 3,600 |
| — Other G&A | 290 | 300 | 310 | 330 | 1,230 |
| **R&D** | 450 | 470 | 480 | 500 | **1,900** |
| **Capex** | 1,800 | 2,000 | 2,400 | 2,600 | **8,800** |

Note on Gross Margin %: FY2026 budgeted gross margin is 16,000 / 42,000 = 38.1% of revenue, broadly flat across quarters (37.4%–38.9%).

Note on the Q3 2026 T&E line: the budgeted Travel & Entertainment figure of **$340K** for Q3 2026 is the baseline against which Q3 actuals are compared in `variance_report_q3_2026`.

## Notes — budget methodology

- **Bottom-up by cost center.** Each department budget owner submits a bottom-up forecast for their cost center (headcount-driven Salaries & Benefits, planned campaigns for Marketing, planned trips and known company-wide events for T&E, capital project requests for Capex). FP&A business partners consolidate these into the business-unit and corporate rollups shown above.
- **Reviewed quarterly.** The FY2026 budget was approved once, on 2025-12-15, and is not re-baselined intra-year. FP&A reviews budget-vs-actual variance every quarter after books close (see `close_calendar_2026`) and publishes a variance report; the approved budget numbers themselves do not change mid-year except through a formal re-forecast, which would be issued as a separate, explicitly labeled document.
- **Large one-time events.** Company-wide events such as the FY2026 Global Sales Kickoff are expected to be pre-approved and budgeted as a distinct line within the relevant quarter's T&E allocation (see `expense_policy` for the approval process for large one-time events). Any spend on such an event that exceeds its pre-approved line shows up as a T&E variance in the applicable quarter's variance report.
- **Units.** All figures in this document are in $ thousands (K) unless a table cell explicitly states otherwise. FY totals are the sum of the four quarterly columns.
