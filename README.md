# rag-ollama-set-up

Local RAG (Retrieval-Augmented Generation) setup using:
- **PostgreSQL + pgvector**
- **Ollama** for local embeddings & chat (bge-m3 + gemma3:4b)
- **Python** for ingestion, retrieval, and logging

---

## Setup Summary

1. **Install PostgreSQL (v16+)**
2. **Build pgvector** (see [docs/PGVECTOR_BUILD_Windows.md](docs/PGVECTOR_BUILD_Windows.md))
3. **Create RAG tables** (see `sql/rag_setup.sql`)
4. **Run scripts**
   - `ingest.py` → loads documents
   - `ask_rag.py` → queries with context
   - `promote_qa_to_chunks.py` → learns from previous Q&A

---

## Folder Layout

```text
rag-ollama-set-up/
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
├── docs/
│   ├── PGVECTOR_BUILD_Windows.md
│   ├── RUNBOOK_Windows.md
│   └── TROUBLESHOOTING.md
├── sql/
│   └── rag_setup.sql
├── scripts/
│   ├── ingest.py
│   ├── ask_rag.py
│   └── promote_qa_to_chunks.py
└── sample_docs/
    └── intro.txt
