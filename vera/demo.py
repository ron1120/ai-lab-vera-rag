"""
Vera CLI demo. SYNTHETIC / FOR TRAINING ONLY.

Calls answer("Why was T&E over budget in Q3?") and pretty-prints the result.
"""

import json

from vera.answer import answer


def main():
    query = "Why was T&E over budget in Q3?"
    result = answer(query)

    print(f"Query: {query}\n")
    print("Answer:")
    print(result["answer"])
    print()
    print("Citations:")
    print(json.dumps(result["citations"], indent=2))
    print()
    print(f"Label: {result['label']}")


if __name__ == "__main__":
    main()
