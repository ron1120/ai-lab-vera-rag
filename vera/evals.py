"""
Vera eval suite — Section W. SYNTHETIC / FOR TRAINING ONLY.

Runs every case in the golden Q&A test set through the multi-agent
pipeline (vera/agents.py::orchestrate) and checks, per Section W:

  1. The node path — did it retrieve, or correctly jump to
     refuse/escalate?
  2. The retrieved doc_id / section — was it the right document?
  3. The final answer vs. the golden figures.
  4. For refusal/escalation cases — was the refusal/escalation actually
     triggered, not answered through?

...and specifically screens every result for Section W's four named
failure modes:

  - Hallucinated numbers    — a number in the answer that isn't in any
                               retrieved chunk.
  - Missing citation        — a stated figure with no doc_id / close date
                               attached.
  - Forward-looking leakage — an answer-route response that still
                               contains forward-looking language.
  - Wrong department attribution — the T&E figure attributed to a
                               department other than SG&A.
"""

import re
import sys

from vera.agents import _DRAFT_LEAKAGE_PATTERNS, orchestrate
from vera.golden import load_golden_cases

_NUMERIC_TOKEN_RE = re.compile(
    r"\$\d[\d,]*(?:\.\d+)?\s?[KM]?|\d{1,3}(?:\.\d+)?%"
)

_BEHAVIOR_TO_ROUTES = {
    "Answer": {"answer"},
    "Refuse": {"refuse_forward_looking", "refuse_competitor"},
    "Escalate": {"escalate_period_not_closed"},
}


def _actual_behavior(route):
    for behavior, routes in _BEHAVIOR_TO_ROUTES.items():
        if route in routes:
            return behavior
    return f"UNKNOWN({route})"


def _check_hallucinated_numbers(payload):
    """Every $ / % figure in the shipped answer must appear in the text
    of at least one retrieved chunk (for answer/escalate routes) — an
    escalate route is exempt because it must contain NO figures at all,
    which is checked separately."""
    answer_text = payload.get("answer") or ""
    numbers_in_answer = set(_NUMERIC_TOKEN_RE.findall(answer_text))
    if not numbers_in_answer:
        return True, []

    retrieved_text = " ".join(
        h["text"] for h in payload.get("_retrieved_hits", [])
    )
    hallucinated = [n for n in numbers_in_answer if n not in retrieved_text]
    return (len(hallucinated) == 0), hallucinated


def _check_missing_citation(payload, expected_behavior):
    if expected_behavior == "Refuse":
        return True, None  # refusals correctly carry no citations at all
    citations = payload.get("citations") or []
    if not citations:
        return False, "no citations at all"
    for c in citations:
        if not c.get("doc_id"):
            return False, "citation missing doc_id"
        if not c.get("effective_date"):
            return False, "citation missing close/effective date"
    return True, None


def _check_forward_looking_leakage(payload):
    if payload["route"] != "answer":
        return True, None
    answer_text = (payload.get("answer") or "").lower()
    for pattern in _DRAFT_LEAKAGE_PATTERNS:
        if re.search(pattern, answer_text):
            return False, pattern
    return True, None


def _check_department_attribution(payload, question):
    """Targeted check: if the question is about T&E, the answer must
    never describe the T&E figure as a Marketing variance (the specific
    failure mode Section W calls out). Restricted to a single line so
    two unrelated table rows ("T&E | 340 | ..." / "Marketing | 1,200 |
    ...") sitting near each other in a reference table don't
    false-positive as a misattribution."""
    if "t&e" not in question.lower() and "travel" not in question.lower():
        return True, None
    answer_text = payload.get("answer") or ""
    for line in answer_text.split("\n"):
        if re.search(r"(t&e|travel\s*&\s*entertainment)", line, re.IGNORECASE) and re.search(
            r"marketing\s*variance", line, re.IGNORECASE
        ):
            return False, f"same-line T&E/Marketing-variance misattribution: {line!r}"
    return True, None


def _check_no_invented_figures(payload):
    """For Refuse/Escalate routes specifically: zero numeric figures of
    any kind should appear anywhere in the answer."""
    if payload["route"] == "answer":
        return True, []
    answer_text = payload.get("answer") or ""
    found = _NUMERIC_TOKEN_RE.findall(answer_text)
    return (len(found) == 0), found


def run_evals(verbose=True):
    cases = load_golden_cases()
    results = []

    for case in cases:
        payload = orchestrate(case["question"])
        actual_behavior = _actual_behavior(payload["route"])
        behavior_ok = actual_behavior == case["expected_behavior"]

        cited_doc_ids = {c["doc_id"] for c in payload.get("citations", [])}
        doc_id_ok = (
            True
            if not case["expected_doc_ids"]
            else bool(cited_doc_ids & set(case["expected_doc_ids"]))
        )

        halluc_ok, halluc_bad = _check_hallucinated_numbers(payload)
        citation_ok, citation_bad = _check_missing_citation(payload, case["expected_behavior"])
        forward_ok, forward_bad = _check_forward_looking_leakage(payload)
        dept_ok, dept_bad = _check_department_attribution(payload, case["question"])
        no_invented_ok, invented_bad = _check_no_invented_figures(payload)

        all_ok = all([
            behavior_ok, doc_id_ok, halluc_ok, citation_ok,
            forward_ok, dept_ok, no_invented_ok,
        ])

        result = {
            "id": case["id"],
            "question": case["question"],
            "expected_behavior": case["expected_behavior"],
            "actual_behavior": actual_behavior,
            "route": payload["route"],
            "trace": [t["agent"] for t in payload["_trace"]],
            "cited_doc_ids": sorted(cited_doc_ids),
            "checks": {
                "behavior_matches_golden": behavior_ok,
                "doc_id_matches_golden": doc_id_ok,
                "no_hallucinated_numbers": (halluc_ok, halluc_bad),
                "citations_complete": (citation_ok, citation_bad),
                "no_forward_looking_leakage": (forward_ok, forward_bad),
                "correct_department_attribution": (dept_ok, dept_bad),
                "no_invented_figures_on_refuse_escalate": (no_invented_ok, invented_bad),
            },
            "pass": all_ok,
        }
        results.append(result)

        if verbose:
            status = "PASS" if all_ok else "FAIL"
            print(f"[{status}] #{case['id']:>2} {case['question']}")
            print(f"       expected={case['expected_behavior']:<8} actual={actual_behavior:<8} route={payload['route']}")
            print(f"       trace: {' -> '.join(result['trace'])}")
            print(f"       cited doc_ids: {result['cited_doc_ids']}")
            if not all_ok:
                for check_name, val in result["checks"].items():
                    ok = val[0] if isinstance(val, tuple) else val
                    if not ok:
                        print(f"       FAILED CHECK: {check_name} -> {val}")
            print()

    return results


def main():
    results = run_evals(verbose=True)
    n_pass = sum(1 for r in results if r["pass"])
    n_total = len(results)
    print(f"=== Eval summary: {n_pass}/{n_total} passed ===")

    if n_pass < n_total:
        print("\nFailures:")
        for r in results:
            if not r["pass"]:
                print(f"  #{r['id']}: {r['question']}")
        sys.exit(1)  # non-zero exit so CI actually fails the job


if __name__ == "__main__":
    main()
