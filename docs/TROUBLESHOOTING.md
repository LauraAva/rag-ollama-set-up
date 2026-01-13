

\### `docs\\TROUBLESHOOTING.md`

Paste:

```markdown

\# Troubleshooting



\## Connection refused on 5432

Postgres may run on another port (often 5433). Scripts auto-detect.



\## SQL error: ï»¿CREATE

Your SQL file was saved with UTF-8 BOM. The setup script rewrites without BOM.



\## Operator does not exist: vector <=> double precision\[]

Fix is to pass query embeddings as pgvector type: `Vector(qvec)` (already in ask\_rag.py).



\## Access denied copying to Program Files

Copying `vector.dll` etc. into Postgres install requires Admin rights.



