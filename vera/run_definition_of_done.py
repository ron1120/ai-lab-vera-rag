"""
Run the full Section Y Definition of Done demo script — all 5 questions,
in order. SYNTHETIC / FOR TRAINING ONLY.
"""

import json

from vera.answer import answer

QUESTIONS = [
    "Why was T&E over budget in Q3?",
    "What will Q4 revenue be?",
    "What's Acme Corp's margin?",
    "How is October tracking?",
    "Is T&E a COGS or SG&A account?",
]


def main():
    for i, q in enumerate(QUESTIONS, 1):
        result = answer(q)
        print(f"--- #{i}: {q} ---")
        print(json.dumps(result, indent=2))
        print()


if __name__ == "__main__":
    main()
