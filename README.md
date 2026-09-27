# ai-lab-vera-rag

**SYNTHETIC / FOR TRAINING ONLY.** Meridian Industries, Vera, and every document, number, and person in this repo are fictional. Not real financial data or advice.

A working RAG + multi-agent prototype of **Vera**, the FP&A assistant for the fictional Meridian Industries, built as part of the AI Solution Architect program's Meeting 6 lab ("RAG & Multi-Agent Systems").

Vera answers budget/actual/variance questions strictly from Meridian's own closed, published documents, always cites her source, and refuses or escalates rather than ever guessing a number.

![Vera CLI chat demo: a cited T&E variance answer, a forward-looking refusal, and an unclosed-period escalation](vera_chat_demo.gif)

*Live terminal session — a cited answer (`$401K actual / $340K budget / +18.0%`), a forward-looking refusal, and an unclosed-period escalation, each with its real citation.*

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r vera/requirements.txt

# Build the vector store (persists to ./chroma_db)
python -m vera.run_ingest

# Chat with Vera live
python -m vera.chat

# Or run the full golden-set eval suite
python -m vera.evals
```

## What's here

| Path | What it does |
|---|---|
| `synthetic-data/` | The RAG corpus: 6 Meridian finance documents, a golden Q&A test set, and a doc catalog |
| `vera/ingest.py` | Loads + table-safe-chunks the corpus, embeds into a persistent ChromaDB collection |
| `vera/retrieve.py` | Vector search + a lexical rerank pass (hybrid retrieval) |
| `vera/answer.py` | Flat `answer()` pipeline: classifies the question, refuses/escalates before ever retrieving, or answers grounded strictly in retrieved text |
| `vera/agents.py` | Multi-agent refactor: `intake → fpna_analyst → narrative_drafter → controller_reviewer`, with model-tier routing and a review-gated "clarify" retry loop |
| `vera/golden.py` + `vera/evals.py` | Parses the golden Q&A set (16 cases) and screens every run for hallucinated numbers, missing citations, forward-looking leakage, and wrong department attribution |
| `vera/chat.py` | Live interactive CLI chat against the real pipeline |

## Definition of Done

- [x] Ingest runs; retrieval index contains chunks from `variance_report_q3_2026`
- [x] *"Why was T&E over budget in Q3?"* → $401K actual / $340K budget / +18.0%, cited to `variance_report_q3_2026`, closed 2026-10-05
- [x] *"What will Q4 revenue be?"* → refused (forward-looking)
- [x] *"What's [any competitor]'s margin?"* → refused (external company)
- [x] *"How is October tracking?"* → escalated (period not yet closed)
- [x] Full golden set (16 cases): 16/16 pass

## Architecture, in short

Every question hits `intake()` first. Forward-looking, competitor, and
unclosed-period questions get refused/escalated immediately — the vector
store is never even queried on those paths. Only genuinely in-scope
questions proceed through `fpna_analyst` (retrieval) → `narrative_drafter`
(compose from retrieved text only) → `controller_reviewer` (catches
missing citations or forward-looking leakage, and can bounce a flawed
draft back for one retry before shipping it).

The point: the *architecture*, not just the prompt, is what enforces
"never guess."
