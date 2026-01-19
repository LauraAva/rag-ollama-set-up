
---

## `docs/TROUBLESHOOTING.md`
```markdown
# Troubleshooting

## Connection refused on 5432
Postgres likely runs on another port (e.g., 5433).
This repo auto-detects port from postgresql.conf.

## SQL error: ï»¿CREATE
Your SQL file has a UTF-8 BOM.
This repo’s sql/rag_setup.sql is normal UTF-8 without BOM.
setup_rag.ps1 also rewrites it safely if needed.

## Operator does not exist: vector <=> double precision[]
Your query embedding must be cast to vector type.
ask_rag.py uses Vector(qvec) to fix this.

## Access denied when copying to Program Files
Run PowerShell as Administrator to copy pgvector files.
