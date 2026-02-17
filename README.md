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

## Quickstart

### 1) Create venv + install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2) Ensure PostgreSQL and pgvector are installed

- PostgreSQL **16+** is required.
- Build/install pgvector (Windows instructions):
  - [docs/PGVECTOR_BUILD_Windows.md](docs/PGVECTOR_BUILD_Windows.md)

### 3) Create database and run schema

```bash
createdb ragdb
psql -d ragdb -f sql/rag_setup.sql
```

> If your environment uses connection variables, set `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, and `PGDATABASE=ragdb` before running scripts.

### 4) Pull required Ollama models

```bash
ollama pull bge-m3
ollama pull gemma3:4b
```

### 5) Ingest sample docs

```bash
python scripts/ingest.py --path sample_docs --collection public --source local
```

### 6) Ask questions with RAG

```bash
python scripts/ask_rag.py "What is this project about?" --collection public
```

### 7) Promote prior Q&A back into chunks

```bash
python scripts/promote_qa_to_chunks.py --collection public --only-verified --limit 50
```

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
```
