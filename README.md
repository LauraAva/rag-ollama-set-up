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
## 2) Bootstrap
.\powershell\00_bootstrap.ps1

## 3) create db + tables
.\powershell\01_setup_db.ps1

## 4) set env vars
. .\powershell\02_env.ps1

##avoid password prompts
$env:PGPASSWORD = "<your_postgres_password>"

## 5) ingest docs
py .\scripts\ingest.py --path .\sample_docs --source pilot

## 6) ask the RAG
py .\scripts\ask_rag.py "What is dbt used for?"

## 7) promote verified Q/A back into RAG
py .\scripts\promote_qa_to_chunks.py --only-verified --limit 50

## 8) verify tables/logs
.\powershell\03_verify.ps1
