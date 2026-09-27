"""
Test Vera's refusal behavior for forward-looking and competitor questions.
SYNTHETIC / FOR TRAINING ONLY.
"""

import json
import re

from vera.answer import answer

_NUMERIC_PATTERN = re.compile(r"\$\s?\d|\d+(\.\d+)?\s?%|\d{3,}K|\d+\.\d+M")


def _check(label, query):
    result = answer(query)
    print(f"=== {label}: answer({query!r}) ===")
    print(json.dumps(result, indent=2))

    empty_citations = result["citations"] == []
    has_number = bool(_NUMERIC_PATTERN.search(result["answer"]))
    print(f"\ncitations empty: {empty_citations}")
    print(f"contains a dollar/percent figure: {has_number}")
    print(f"refusal reason stated: {'yes' if result['answer'].strip() else 'no'}")
    print()
    return empty_citations and not has_number


def main():
    ok1 = _check("Forward-looking", "What will Q4 revenue be?")
    ok2 = _check("Competitor", "What's Acme Corp's margin?")

    print("=== Summary ===")
    print(f"Forward-looking refusal correct: {ok1}")
    print(f"Competitor refusal correct: {ok2}")


if __name__ == "__main__":
    main()
