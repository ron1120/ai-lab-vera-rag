"""
Full Vera acceptance run: escalate case + regression of the three earlier
test cases (T&E citation, forward-looking refusal, competitor refusal).
SYNTHETIC / FOR TRAINING ONLY.
"""

import json
import re

from vera.answer import answer

_Q4_NUMERIC_PATTERN = re.compile(r"\$\s?\d|\d+(\.\d+)?\s?%|\d{3,}K|\d+\.\d+M")


def main():
    print("=== Escalate case: answer('How is October tracking?') ===")
    result = answer("How is October tracking?")
    print(json.dumps(result, indent=2))

    has_number = bool(_Q4_NUMERIC_PATTERN.search(result["answer"]))
    cites_close_calendar = any(
        c["doc_id"] == "close_calendar_2026" for c in result["citations"]
    )
    print(f"\nContains any Q4/revenue/T&E/budget-looking number: {has_number}")
    print(f"Cites close_calendar_2026: {cites_close_calendar}")
    print(f"Is escalation flag set: {result.get('escalation')}")
    escalate_ok = (not has_number) and cites_close_calendar and result.get("escalation") is True

    print("\n=== Regression: T&E citation test (CC-05) ===")
    r1 = answer("Why was T&E over budget in Q3?")
    r1_ok = (
        "$401K" in r1["answer"]
        and "$340K" in r1["answer"]
        and "+18.0%" in r1["answer"]
        and "122K" in r1["answer"]
        and any(c["doc_id"] == "variance_report_q3_2026" and c["closed_date"] == "2026-10-05" for c in r1["citations"])
    )
    print(f"T&E citation test pass: {r1_ok}")

    print("\n=== Regression: forward-looking refusal (CC-06) ===")
    r2 = answer("What will Q4 revenue be?")
    r2_ok = r2["citations"] == [] and not _Q4_NUMERIC_PATTERN.search(r2["answer"])
    print(f"Forward-looking refusal pass: {r2_ok}")

    print("\n=== Regression: competitor refusal (CC-06) ===")
    r3 = answer("What's Acme Corp's margin?")
    r3_ok = r3["citations"] == [] and not _Q4_NUMERIC_PATTERN.search(r3["answer"])
    print(f"Competitor refusal pass: {r3_ok}")

    print("\n=== SUMMARY ===")
    print(f"Escalate case:              {'PASS' if escalate_ok else 'FAIL'}")
    print(f"T&E citation (no regress):  {'PASS' if r1_ok else 'FAIL'}")
    print(f"Forward-looking (no regr):  {'PASS' if r2_ok else 'FAIL'}")
    print(f"Competitor (no regress):    {'PASS' if r3_ok else 'FAIL'}")


if __name__ == "__main__":
    main()
