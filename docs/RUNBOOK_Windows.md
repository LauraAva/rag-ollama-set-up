\# Windows Runbook (Quick)



From repo root:



1\) Bootstrap

```powershell

.\\powershell\\00\_bootstrap.ps1



.\\powershell\\01\_setup\_db.ps1



. .\\powershell\\02\_env.ps1



$env:PGPASSWORD="<your postgres password>"



py .\\scripts\\ingest.py --path .\\sample\_docs --source pilot



py .\\scripts\\ask\_rag.py "What is dbt used for?"



.\\powershell\\03\_verify.ps1





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



