"""
Vera ingest pipeline. SYNTHETIC / FOR TRAINING ONLY.

Stage 1 (CC-02): load_documents() — read every .md file in DOCS_DIR and map
filename -> doc_id using document_catalog.csv.

Stage 2 (CC-03): chunk_documents() + embed_and_load() — split documents into
retrievable chunks (never splitting a markdown table row across chunks),
attach metadata, and load them into a persistent ChromaDB collection.
"""

import csv
import os
import re

import chromadb

from vera.config import CHROMA_DIR, COLLECTION_NAME, DOCS_DIR, METADATA_CSV


def _load_catalog():
    """Read document_catalog.csv and return {file_path: doc_id} plus
    {doc_id: full_row_dict}."""
    file_to_doc_id = {}
    catalog_rows = {}
    with open(METADATA_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # file_path in the CSV is relative to the synthetic-data/ folder,
            # e.g. "documents/budget_2026.md" -> match on basename.
            filename = os.path.basename(row["file_path"])
            file_to_doc_id[filename] = row["doc_id"]
            catalog_rows[row["doc_id"]] = row
    return file_to_doc_id, catalog_rows


def load_documents():
    """Read every .md file in DOCS_DIR and return a list of
    {doc_id, filename, text} dicts, using document_catalog.csv to map
    filename -> doc_id. Raises if a file on disk has no catalog entry."""
    file_to_doc_id, _ = _load_catalog()

    docs = []
    for filename in sorted(os.listdir(DOCS_DIR)):
        if not filename.endswith(".md"):
            continue
        if filename not in file_to_doc_id:
            raise ValueError(
                f"No doc_id found in {METADATA_CSV} for file '{filename}'. "
                "Refusing to guess a doc_id — fix the catalog or the file."
            )
        doc_id = file_to_doc_id[filename]
        path = os.path.join(DOCS_DIR, filename)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        docs.append({"doc_id": doc_id, "filename": filename, "text": text})
    return docs


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")

# Target chunk size in characters for non-table prose. Table blocks are kept
# whole regardless of this target (the hard rule below).
_TARGET_CHUNK_CHARS = 900


def _split_into_blocks(text):
    """Split a document's markdown text into an ordered list of blocks:
    {"type": "heading"|"para"|"table", "text": str, "heading": <nearest
    heading text above this block>}.

    HARD RULE: a markdown table (a contiguous run of lines starting with
    "|") is always kept as ONE block — every row of the table stays
    together, including its header/separator row — so a table can never be
    split across two chunks downstream.
    """
    lines = text.split("\n")
    blocks = []
    current_heading = None
    i = 0
    para_buf = []

    def flush_para():
        if para_buf:
            joined = "\n".join(para_buf).strip("\n")
            if joined.strip():
                blocks.append(
                    {"type": "para", "text": joined, "heading": current_heading}
                )
            para_buf.clear()

    while i < len(lines):
        line = lines[i]

        heading_match = _HEADING_RE.match(line)
        if heading_match:
            flush_para()
            current_heading = heading_match.group(2).strip()
            blocks.append(
                {"type": "heading", "text": line, "heading": current_heading}
            )
            i += 1
            continue

        if _TABLE_ROW_RE.match(line):
            # Start of a table block: consume every contiguous table-row
            # line (including the "|---|---|" separator row) as ONE
            # indivisible block. This is what guarantees a budget/variance
            # table row's actual and budget figures always land in the same
            # chunk.
            flush_para()
            table_lines = []
            while i < len(lines) and _TABLE_ROW_RE.match(lines[i]):
                table_lines.append(lines[i])
                i += 1
            blocks.append(
                {
                    "type": "table",
                    "text": "\n".join(table_lines),
                    "heading": current_heading,
                }
            )
            continue

        para_buf.append(line)
        i += 1

    flush_para()
    return blocks


def chunk_documents(docs):
    """Split each document's text into retrievable chunks.

    HARD RULE: never split a markdown table row across two chunks — a
    contiguous markdown table is always kept fully intact within a single
    chunk (see _split_into_blocks), even if that makes some chunks larger
    than the target size.

    Non-table content is grouped under its nearest heading and packed up to
    ~_TARGET_CHUNK_CHARS per chunk, only ever breaking between blocks
    (never inside a table).

    Returns a list of {doc_id, section, text, chunk_index} dicts (dates are
    attached separately in embed_and_load, from document_catalog.csv).
    """
    all_chunks = []

    for doc in docs:
        blocks = _split_into_blocks(doc["text"])

        current_text_parts = []
        current_heading = None
        current_len = 0
        chunk_index = 0

        def flush_chunk():
            nonlocal current_text_parts, current_len, chunk_index
            if current_text_parts:
                text = "\n".join(current_text_parts).strip("\n")
                if text.strip():
                    all_chunks.append(
                        {
                            "doc_id": doc["doc_id"],
                            "section": current_heading or doc["doc_id"],
                            "text": text,
                            "chunk_index": chunk_index,
                        }
                    )
                    chunk_index += 1
                current_text_parts = []
                current_len = 0

        for block in blocks:
            if block["type"] == "heading":
                # Flush whatever we were accumulating under the OLD heading
                # first, then start a fresh chunk under the new heading —
                # a heading must never get appended to the tail of the
                # previous section's chunk (that would mislabel it).
                flush_chunk()
                current_heading = block["heading"]
                current_text_parts.append(block["text"])
                current_len += len(block["text"])
                continue

            if block["type"] == "table":
                # Tables are never split. If adding this whole table would
                # blow the target size AND we already have content in the
                # current chunk, flush first so the table starts its own
                # chunk (still keeping the table itself intact either way).
                if current_len > 0 and current_len + len(block["text"]) > _TARGET_CHUNK_CHARS:
                    flush_chunk()
                    current_heading = block["heading"]
                current_text_parts.append(block["text"])
                current_len += len(block["text"])
                continue

            # Plain paragraph block.
            if current_len > 0 and current_len + len(block["text"]) > _TARGET_CHUNK_CHARS:
                flush_chunk()
                current_heading = block["heading"]
            current_text_parts.append(block["text"])
            current_len += len(block["text"])

        flush_chunk()

    return all_chunks


# ---------------------------------------------------------------------------
# Embed + load
# ---------------------------------------------------------------------------


def embed_and_load(chunks):
    """Create (or reset) a persistent Chroma collection named 'vera_docs',
    persisted to CHROMA_DIR, and load all chunks with their metadata
    (doc_id, section, effective_or_closed_date).

    Uses Chroma's bundled default embedding function (a local ONNX
    MiniLM-L6-v2 model via onnxruntime) — chosen because it ships with
    chromadb itself, runs fully offline/local, and needs zero extra API
    keys or accounts, which is the least setup for a local prototype like
    this one. A hosted embeddings API (OpenAI/Anthropic/etc.) would work
    too, but would add a network dependency and an API key requirement
    that this lab doesn't need.
    """
    _, catalog_rows = _load_catalog()

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Reset the collection each run so re-running ingest doesn't duplicate
    # or stale-out chunks.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    ids, documents, metadatas = [], [], []
    for chunk in chunks:
        row = catalog_rows.get(chunk["doc_id"], {})
        closed_date = row.get("effective_date", "")
        chunk_id = f"{chunk['doc_id']}__{chunk['chunk_index']}"
        ids.append(chunk_id)
        documents.append(chunk["text"])
        metadatas.append(
            {
                "doc_id": chunk["doc_id"],
                "section": chunk["section"],
                "effective_or_closed_date": closed_date,
            }
        )

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    return collection
