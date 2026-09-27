# Chart of Accounts — Meridian Industries

**SYNTHETIC / FOR TRAINING ONLY.** This document is fictional training data created for the Finance AI Academy "AI Solution Architect" course. It does not describe a real company, real financial results, or real financial advice.

| Field | Value |
|---|---|
| doc_id | `chart_of_accounts` |
| Document title | Corporate Chart of Accounts |
| Effective date | 2026-01-01 |
| Owner | Corporate Controller |
| Scope | All Meridian Industries business units (Manufacturing, Field Services, Distribution) |

## Category definitions

- **Revenue** — Amounts billed to customers for products shipped or services performed, net of returns and allowances.
- **COGS (Cost of Goods Sold)** — Direct costs incurred to produce and deliver the goods or services sold: direct materials, direct labor, manufacturing overhead, freight-in, and field-service labor directly billable to a job. COGS scales with production/service volume.
- **SG&A (Selling, General & Administrative)** — Indirect costs of running the business that are not directly tied to producing a specific unit of product or service: sales and marketing costs, corporate and department administrative salaries, travel, office and facilities overhead not allocated to production, and general corporate support functions (Finance, HR, Legal, IT outside of production systems). **The dividing line: if a cost would still be incurred even with zero units produced that month, it is SG&A, not COGS. If a cost varies directly with production/service volume, it is COGS.**
- **R&D (Research & Development)** — Costs of developing new products, materials, or manufacturing processes, including engineering labor and prototyping, that are not yet part of a shipping product line.
- **Capex (Capital Expenditures)** — Cash spend on assets with a useful life beyond one year that are capitalized on the balance sheet and depreciated over time (equipment, machinery, facilities, major IT infrastructure), as opposed to expensed in the period incurred.

## Account table

| Code | Account Name | Category | Definition | Typical Owning Department |
|---|---|---|---|---|
| 4000 | Product Revenue | Revenue | Revenue from shipped manufactured goods | Manufacturing |
| 4010 | Service Revenue | Revenue | Revenue from billable field-service labor and contracts | Field Services |
| 4020 | Distribution Revenue | Revenue | Revenue from resale/distribution of third-party goods | Distribution |
| 5000 | Direct Materials | COGS | Raw materials and components consumed in production | Manufacturing |
| 5010 | Direct Labor | COGS | Production-line labor directly tied to units produced | Manufacturing |
| 5020 | Manufacturing Overhead | COGS | Plant utilities, equipment maintenance, production supervision allocated to units produced | Manufacturing |
| 5030 | Field Service Labor (Billable) | COGS | Technician labor directly billable to a customer job | Field Services |
| 5040 | Freight-In / Distribution COGS | COGS | Inbound freight and cost of goods resold through Distribution | Distribution |
| 6100 | Travel & Entertainment (T&E) | SG&A | See "Travel & Entertainment scope" below | All departments (booked to the traveling employee's cost center) |
| 6110 | Marketing | SG&A | Advertising, campaigns, trade shows, brand and demand-generation spend | Sales & Marketing |
| 6120 | Salaries & Benefits (SG&A) | SG&A | Base salary, payroll tax, and benefits cost for non-production (SG&A) headcount | Corporate / Department Admin |
| 6130 | Other G&A | SG&A | Office supplies, non-production facilities, professional/legal/audit fees, insurance, and other general administrative costs not elsewhere classified | Corporate |
| 6200 | IT & Corporate Systems (non-production) | SG&A | Software, licenses, and IT support for corporate (not shop-floor) systems | IT |
| 7000 | Engineering R&D Labor | R&D | Engineering and technical labor on new product/process development | Engineering / R&D |
| 7010 | Prototyping & Test | R&D | Materials and outside services for prototype builds and testing | Engineering / R&D |
| 8000 | Manufacturing Equipment | Capex | Capitalized production machinery and equipment (e.g. press lines) | Manufacturing |
| 8010 | Facilities & Leasehold Improvements | Capex | Capitalized building and facility improvements | Corporate Real Estate |
| 8020 | IT Infrastructure (Capitalized) | Capex | Capitalized servers, network hardware, and major system implementations | IT |

## Travel & Entertainment (Account 6100) — scope definition

**In scope (reimbursable under this account, subject to `expense_policy`):**
- Airfare and other transportation to/from a business destination (rail, rideshare, mileage, parking, tolls)
- Hotel / lodging while traveling on Meridian business
- Meals while traveling on Meridian business, within per-diem limits
- Client and prospect entertainment (meals, event tickets) directly tied to a business purpose
- Costs of company-wide or department events held away from a normal work location (e.g. sales kickoffs, offsites), including venue, catering, and attendee travel/lodging for that event

**Out of scope (booked elsewhere, not to account 6100):**
- **Relocation** — new-hire or transfer relocation costs are booked to HR/Salaries & Benefits (6120), not T&E
- **Commuting** — an employee's normal commute between home and their regular work location is never a reimbursable business expense and is not booked to any account
- Capital purchases made while traveling (e.g. equipment bought on a supplier visit) are booked to the relevant Capex account, not T&E
- Recurring local business meals with no travel component are booked to Other G&A (6130), not T&E, unless they are client entertainment tied to a specific deal

See `expense_policy` for approval thresholds and reimbursement process for T&E spend, and the pre-approval process required for large one-time company events.
