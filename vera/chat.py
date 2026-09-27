"""
Vera interactive CLI chat. SYNTHETIC / FOR TRAINING ONLY.

Runs the real multi-agent pipeline (vera/agents.py::orchestrate) live —
type a question, get a real answer, right in the terminal. Type
"trace" after any answer to see the agent trace for that last question,
"examples" to see the Definition of Done demo questions, or
"exit"/"quit" to leave.

Run with:  python -m vera.chat
"""

from vera.agents import orchestrate
from vera.config import LABEL

_BANNER = f"""
============================================================
 Vera — Meridian Industries FP&A Assistant  ({LABEL})
============================================================
Ask a budget / actual / variance question. Vera will answer only from
Meridian's own closed, published documents, refuse forward-looking or
competitor questions, and escalate if the period isn't closed yet.

Commands:
  examples   - show sample questions to try
  trace      - show the agent trace for the last question
  exit/quit  - leave

------------------------------------------------------------
""".strip("\n")

_EXAMPLES = [
    "Why was T&E over budget in Q3?",
    "Is T&E a COGS or SG&A account?",
    "What will Q4 revenue be?",
    "What's Acme Corp's margin?",
    "How is October tracking?",
]

_ROUTE_LABEL = {
    "answer": "ANSWER",
    "refuse_forward_looking": "REFUSED (forward-looking)",
    "refuse_competitor": "REFUSED (competitor/external)",
    "escalate_period_not_closed": "ESCALATED (period not closed)",
    "escalate_needs_human_review": "ESCALATED (needs human review)",
}


def _print_result(payload):
    route_label = _ROUTE_LABEL.get(payload["route"], payload["route"])
    print(f"\n[{route_label}]\n")
    print(payload["answer"])
    if payload["citations"]:
        print("\nCitations:")
        for c in payload["citations"]:
            print(f"  - {c['doc_id']} | {c['section']} | closed {c['effective_date']}")
    print()


def _print_trace(payload):
    if not payload:
        print("No question asked yet.\n")
        return
    print("\nAgent trace for the last question:")
    for t in payload["_trace"]:
        print(f"  - {t['agent']:<20} tier={t['model_tier']:<7} model={t['model_name']}")
    print(f"Final route: {payload['route']}\n")


def main():
    print(_BANNER)
    last_payload = None

    while True:
        try:
            question = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue

        cmd = question.lower()
        if cmd in ("exit", "quit"):
            print("Goodbye.")
            break
        if cmd == "examples":
            print("\nTry one of these:")
            for ex in _EXAMPLES:
                print(f"  - {ex}")
            print()
            continue
        if cmd == "trace":
            _print_trace(last_payload)
            continue

        last_payload = orchestrate(question)
        _print_result(last_payload)


if __name__ == "__main__":
    main()
