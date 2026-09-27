"""
Run the full Vera ingest pipeline. SYNTHETIC / FOR TRAINING ONLY.

Loads documents, chunks them (never splitting a table row across chunks),
embeds + loads into a persistent Chroma collection, and prints a summary
including the T&E variance chunk to confirm $401K and $340K landed together.
"""

from collections import Counter

from vera.ingest import chunk_documents, embed_and_load, load_documents


def main():
    docs = load_documents()
    chunks = chunk_documents(docs)

    print(f"Total chunks created: {len(chunks)}\n")
    counts = Counter(c["doc_id"] for c in chunks)
    for doc_id in sorted(counts):
        print(f"  {doc_id:<30} {counts[doc_id]} chunk(s)")

    collection = embed_and_load(chunks)
    count_in_db = collection.count()
    print(f"\nChroma collection 'vera_docs' now contains {count_in_db} chunk(s), "
          f"persisted to ./chroma_db")

    print("\n--- T&E variance chunk check ---")
    te_doc_chunks = [c for c in chunks if c["doc_id"] == "variance_report_q3_2026"]
    winning_chunk = None
    for c in te_doc_chunks:
        has_actual = "$401K" in c["text"]
        has_budget = "$340K" in c["text"]
        if has_actual and has_budget:
            winning_chunk = c
            break

    if winning_chunk:
        print(f"\nChunk (section: {winning_chunk['section']}):")
        print("-" * 60)
        print(winning_chunk["text"])
        print("-" * 60)
        print("Contains $401K (actual): True")
        print("Contains $340K (budget): True")
        print("\nPASS: $401K and $340K appear together in the same chunk.")
    else:
        print("FAIL: no single chunk contains both $401K and $340K together.")
        for c in te_doc_chunks:
            print(f"  - section={c['section']!r} "
                  f"has_401K={'$401K' in c['text']} has_340K={'$340K' in c['text']}")


if __name__ == "__main__":
    main()
