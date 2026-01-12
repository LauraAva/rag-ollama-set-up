$PGROOT = "C:\Program Files\PostgreSQL\16"
. "$PSScriptRoot\env.ps1"

& "$PGROOT\bin\psql.exe" -h 127.0.0.1 -p $env:PGPORT -U postgres -d $env:PGDATABASE -c "\dx"
& "$PGROOT\bin\psql.exe" -h 127.0.0.1 -p $env:PGPORT -U postgres -d $env:PGDATABASE -c "\dt"
& "$PGROOT\bin\psql.exe" -h 127.0.0.1 -p $env:PGPORT -U postgres -d $env:PGDATABASE -c "SELECT count(*) AS chunks FROM rag_chunks;"
& "$PGROOT\bin\psql.exe" -h 127.0.0.1 -p $env:PGPORT -U postgres -d $env:PGDATABASE -c "SELECT count(*) AS qa_rows FROM qa_log;"
