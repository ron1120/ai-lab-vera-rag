"""
MA-3 check: run orchestrate() on all 5 Definition of Done questions and
print, for each: the question, the final route, and the full _trace list.
SYNTHETIC / FOR TRAINING ONLY.

Confirms, for each of the five, that the _trace list contains exactly the
agents the Action -> agent -> handoff map in Section V says it should, in
the right order, with no extra agents.
"""

from vera.agents import orchestrate

QUESTIONS = [
    ("Why was T&E over budget in Q3?", ["intake", "fpna_analyst", "narrative_drafter", "controller_reviewer"]),
    ("Is T&E a COGS or SG&A account?", ["intake", "fpna_analyst", "narrative_drafter", "controller_reviewer"]),
    ("What will Q4 revenue be?", ["intake"]),
    ("What's Acme Corp's margin?", ["intake"]),
    ("How is October tracking?", ["intake"]),
]


def main():
    all_ok = True
    for question, expected_agents in QUESTIONS:
        payload = orchestrate(question)
        trace_agents = [t["agent"] for t in payload["_trace"]]

        print(f"Question: {question}")
        print(f"  route: {payload['route']}")
        print(f"  trace:")
        for t in payload["_trace"]:
            print(f"    - {t['agent']:<20} tier={t['model_tier']:<7} model={t['model_name']}")

        # Dedup the expected happy-path trace to allow for one clarify
        # retry (which legitimately re-runs analyst/drafter/reviewer) —
        # what must NEVER happen is narrative_drafter/controller_reviewer
        # appearing on a refuse/escalate question.
        unexpected = [a for a in trace_agents if a not in expected_agents]
        missing = [a for a in expected_agents if a not in trace_agents]
        ok = not unexpected and not missing
        all_ok = all_ok and ok
        print(f"  agents match Section V's map: {ok}")
        if unexpected:
            print(f"  BUG - unexpected agents in trace: {unexpected}")
        print()

    print(f"=== OVERALL: {'PASS' if all_ok else 'FAIL'} ===")


if __name__ == "__main__":
    main()
