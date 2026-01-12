# rag-ollama-set-up
# rag-ollama-set-up

Windows local RAG setup using:
- Ollama (LLM + embeddings)
- PostgreSQL 16
- pgvector extension
- Python scripts for ingestion + retrieval + Q/A logging + promotion

## Quickstart (Windows)

### 0) Prereqs
- Ollama installed and running
- Python installed (`py --version`)
- PostgreSQL 16 installed (server + psql)
- pgvector installed into PostgreSQL (see docs/PGVECTOR_BUILD_Windows.md)

### 1) Pull models
```powershell
ollama pull bge-m3
ollama pull gemma3:4b
