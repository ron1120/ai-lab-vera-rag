"""
Vera corpus check. SYNTHETIC / FOR TRAINING ONLY.

Calls load_documents() and prints the doc_id and character count of each
document found, as a sanity check before building the real ingest pipeline.
"""

from vera.ingest import load_documents

EXPECTED_DOC_IDS = {
    "budget_2026",
    "variance_report_q3_2026",
    "chart_of_accounts",
    "close_calendar_2026",
    "expense_policy",
    "board_narrative_style_guide",
}


def main():
    docs = load_documents()
    print(f"Loaded {len(docs)} document(s):\n")
    found_doc_ids = set()
    for d in docs:
        print(f"  doc_id={d['doc_id']:<30} file={d['filename']:<35} chars={len(d['text'])}")
        found_doc_ids.add(d["doc_id"])

    print()
    missing = EXPECTED_DOC_IDS - found_doc_ids
    extra = found_doc_ids - EXPECTED_DOC_IDS
    if missing:
        print(f"MISSING expected doc_ids: {sorted(missing)}")
    if extra:
        print(f"UNEXPECTED extra doc_ids: {sorted(extra)}")
    if not missing and not extra and len(docs) == 6:
        print("OK: all 6 expected doc_ids present, matching document_catalog.csv.")


if __name__ == "__main__":
    main()
