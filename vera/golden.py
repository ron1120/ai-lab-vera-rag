"""
Parse the golden Q&A test set. SYNTHETIC / FOR TRAINING ONLY.

This is the EVAL HARNESS reading fpna_faq_golden.md as an answer key — not
Vera. Vera's own ingest (vera/ingest.py) only ever reads DOCS_DIR
(synthetic-data/documents/); the golden FAQ file is never embedded into
the vector store or retrievable by Vera, per the README's rule: "don't
let Vera read it as a source."
"""

import re

from vera.config import FAQ_DIR

_ROW_RE = re.compile(
    r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*\**(Answer|Refuse|Escalate)\**\s*\|\s*(.+?)\s*\|\s*$"
)

# Two golden questions use a placeholder ("[any named competitor]") —
# substitute a concrete fictional name so the eval can actually run them.
_PLACEHOLDER_SUBSTITUTIONS = {
    "What's [any named competitor]'s operating margin this quarter?": (
        "What's Acme Corp's operating margin this quarter?"
    ),
}


def load_golden_cases():
    """Return a list of dicts:
    {"id": int, "question": str, "expected_doc_ids": [str, ...],
     "expected_behavior": "Answer"|"Refuse"|"Escalate",
     "expected_must_include": str}
    """
    path = f"{FAQ_DIR}/fpna_faq_golden.md"
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    cases = []
    for line in lines:
        m = _ROW_RE.match(line)
        if not m:
            continue
        num, question, doc_ids_raw, behavior, must_include = m.groups()
        if num == "#":
            continue

        question = _PLACEHOLDER_SUBSTITUTIONS.get(question, question)

        doc_ids = re.findall(r"`([a-z0-9_]+)`", doc_ids_raw)

        cases.append(
            {
                "id": int(num),
                "question": question,
                "expected_doc_ids": doc_ids,
                "expected_behavior": behavior,
                "expected_must_include": must_include,
            }
        )
    return cases
