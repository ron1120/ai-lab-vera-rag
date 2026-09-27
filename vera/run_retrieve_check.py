"""
Run and check retrieval for the canonical T&E query. SYNTHETIC / FOR
TRAINING ONLY.
"""

from vera.retrieve import retrieve


def main():
    query = "Why was T&E over budget in Q3?"
    hits = retrieve(query, k=3)

    print(f"Query: {query!r}\n")
    for i, hit in enumerate(hits, 1):
        print(f"--- Hit {i} (score={hit['score']:.4f}) ---")
        print(f"doc_id:  {hit['doc_id']}")
        print(f"section: {hit['section']}")
        print(f"closed:  {hit['effective_or_closed_date']}")
        print(f"text:    {hit['text']}")
        print()

    print("=== Acceptance checklist ===")
    te_hit = next((h for h in hits if h["doc_id"] == "variance_report_q3_2026"), None)

    check1 = te_hit is not None
    print(f"[{'x' if check1 else ' '}] At least one hit has doc_id == 'variance_report_q3_2026': {check1}")

    check2 = bool(te_hit and "$401K" in te_hit["text"])
    print(f"[{'x' if check2 else ' '}] That chunk's text contains '$401K': {check2}")

    check3 = bool(te_hit and "$340K" in te_hit["text"])
    print(f"[{'x' if check3 else ' '}] That chunk's text contains '$340K': {check3}")

    section = (te_hit or {}).get("section", "") or ""
    check4 = "Travel & Entertainment" in section or "T&E" in section
    print(f"[{'x' if check4 else ' '}] Section mentions Travel & Entertainment / T&E: {check4}")

    check5 = bool(te_hit and te_hit["effective_or_closed_date"] == "2026-10-05")
    print(f"[{'x' if check5 else ' '}] Close date is 2026-10-05: {check5}")

    all_pass = all([check1, check2, check3, check4, check5])
    print(f"\nOVERALL: {'PASS' if all_pass else 'FAIL'}")


if __name__ == "__main__":
    main()
