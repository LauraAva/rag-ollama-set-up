# Troubleshooting

## 1) `psql` not found / `Get-Command psql` fails
**Cause:** PostgreSQL `bin` folder isn’t on PATH.  
**Fix:** call it with the full path (recommended), e.g.
```powershell
$PGROOT = "C:\Program Files\PostgreSQL\16"
& "$PGROOT\bin\psql.exe" --version

Select-String -Path "C:\Program Files\PostgreSQL\16\data\postgresql.conf" -Pattern "^\s*port\s*="

$PORT = 5433
$PGROOT = "C:\Program Files\PostgreSQL\16"
& "$PGROOT\bin\psql.exe" -h 127.0.0.1 -p $PORT -U postgres -d postgres -c "SELECT version();"

$env:PGPASSWORD = "<your_password>"

& "$PGROOT\bin\psql.exe" -h 127.0.0.1 -p 5433 -U postgres -d postgres -c "\dx"
```

##SQL error: Syntaxfehler bei »ï»¿CREATE«
**Cause:** The SQL file was saved with UTF-8 BOM (Byte Order Mark).
**Fix:** rewrite the file as UTF-8 without BOM:
```
$sqlPath = "$HOME\Desktop\rag_setup.sql"
$sql = Get-Content $sqlPath -Raw
[System.IO.File]::WriteAllText($sqlPath, $sql, (New-Object System.Text.UTF8Encoding($false)))

& "$PGROOT\bin\psql.exe" -h 127.0.0.1 -p $PORT -U postgres -d ragdb -f $sqlPath
```
##Operator does not exist: vector <=> double precision[]

**Cause:*** You passed a plain Python list/array instead of a pgvector value.
**Fix:** wrap the embedding with Vector(...) in Python:
```

from pgvector.psycopg import Vector
cur.execute(
  "SELECT id, content FROM rag_chunks ORDER BY embedding <=> %s LIMIT %s",
  (Vector(qvec), k)
)

```
##Copying files into C:\Program Files\... says “Access denied”
**Cause:** Windows requires Admin rights to write into Program Files.
**Fix:** open PowerShell as Administrator and run the copy again:
```

$PGROOT = "C:\Program Files\PostgreSQL\16"
Copy-Item ".\pgvector-0.5.1\vector.dll" "$PGROOT\lib\" -Force
Copy-Item ".\pgvector-0.5.1\vector.control" "$PGROOT\share\extension\" -Force
Copy-Item ".\pgvector-0.5.1\sql\vector--0.5.1.sql" "$PGROOT\share\extension\" -Force

```
##CREATE EXTENSION vector; fails / vector type does not exist

**Cause:** pgvector files are not installed into the Postgres directories, or you are connected to the wrong database/server.
**Fix:** Confirm files exist/right port
```

Test-Path "$PGROOT\lib\vector.dll"
Test-Path "$PGROOT\share\extension\vector.control"
Test-Path "$PGROOT\share\extension\vector--0.5.1.sql"

& "$PGROOT\bin\psql.exe" -h 127.0.0.1 -p $PORT -U postgres -d postgres -c "SELECT version();"

& "$PGROOT\bin\psql.exe" -h 127.0.0.1 -p $PORT -U postgres -d ragdb -c "CREATE EXTENSION IF NOT EXISTS vector;"

```
##nmake not found / pgvector won’t compile

**Cause:** Visual Studio Build Tools aren’t installed or you didn’t open the correct dev prompt.
**Fix:** Install Visual Studio Build Tools with Desktop development with C++
**Open x64 Native Tools Command Prompt for VS**
**Then build:**
```

set PGROOT=C:\Program Files\PostgreSQL\16
cd %USERPROFILE%\Desktop\pgvector-0.5.1
nmake /f Makefile.win clean
nmake /f Makefile.win

```
##“It runs, but RAG returns irrelevant answers”
**Likely causes:** Not enough documents ingested
**Chunks are too large/small**
**Wrong embedding model or dimension mismatch**
```

& "$PGROOT\bin\psql.exe" -h 127.0.0.1 -p $PORT -U postgres -d ragdb -c "SELECT count(*) FROM rag_chunks;"
