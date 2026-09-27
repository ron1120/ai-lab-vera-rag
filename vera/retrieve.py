"""
Vera retrieval. SYNTHETIC / FOR TRAINING ONLY.

retrieve(query, k=3) queries the persistent "vera_docs" Chroma collection
and returns the top-k chunks with their metadata and similarity scores.
"""

import re

import chromadb

from vera.config import CHROMA_DIR, COLLECTION_NAME

# Pull back a wider pool from the vector store, then lexically rerank down
# to k. This is a small hybrid-retrieval step: pure embedding similarity on
# a short MiniLM model can under-rank a dense reference table (e.g. the
# Chart of Accounts account table) against a query that shares few
# embedding-salient words with it but shares exact keywords/codes.
_CANDIDATE_POOL_MULTIPLIER = 4
_STOPWORDS = {
    "a", "an", "the", "is", "was", "were", "be", "been", "or", "and",
    "to", "of", "in", "on", "for", "at", "it", "what", "why", "how",
    "does", "do", "did", "this", "that", "as", "vs", "vs.",
}


def _keywords(text):
    words = re.findall(r"[a-z0-9&]+", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 1}


def retrieve(query, k=3):
    """Query the persistent 'vera_docs' Chroma collection for the top-k
    chunks most relevant to `query`.

    Retrieves a wider candidate pool by embedding similarity, then
    reranks that pool by lexical keyword overlap with the query (falling
    back to embedding distance as a tie-breaker), and returns the top-k
    after reranking.

    Returns a list of dicts:
        {"text": str, "doc_id": str, "section": str,
         "effective_or_closed_date": str, "score": float}
    where `score` is the original embedding distance (lower = more
    similar; Chroma's default embedding function uses cosine/L2 distance
    depending on config) — kept for transparency even after reranking.
    """
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(COLLECTION_NAME)

    pool_size = max(k * _CANDIDATE_POOL_MULTIPLIER, k)
    results = collection.query(query_texts=[query], n_results=pool_size)

    candidates = []
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]
    for text, meta, dist in zip(docs, metas, dists):
        candidates.append(
            {
                "text": text,
                "doc_id": meta.get("doc_id"),
                "section": meta.get("section"),
                "effective_or_closed_date": meta.get("effective_or_closed_date"),
                "score": dist,
            }
        )

    query_kw = _keywords(query)

    def rerank_key(hit):
        overlap = len(query_kw & _keywords(hit["text"]))
        # More keyword overlap first (negated for ascending sort), then
        # lower embedding distance (already "lower is better").
        return (-overlap, hit["score"])

    candidates.sort(key=rerank_key)
    return candidates[:k]
