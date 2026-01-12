Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---- CONFIG ----
$PGROOT = "C:\Program Files\PostgreSQL\16"
$ServiceName = "postgresql-x64-16"
$DbName = "ragdb"
$SqlFile = Join-Path $PSScriptRoot "..\sql\rag_setup.sql"

function Get-PostgresPort {
    param([string]$svc)

    $pathName = (Get-CimInstance Win32_Service -Filter "Name='$svc'").PathName
    if ($pathName -notmatch '-D\s+"([^"]+)"') { throw "Could not parse data dir from service PathName: $pathName" }
    $dataDir = $Matches[1]
    $conf = Join-Path $dataDir "postgresql.conf"
    if (!(Test-Path $conf)) { throw "postgresql.conf not found at: $conf" }

    $line = (Select-String -Path $conf -Pattern '^\s*port\s*=\s*\d+').Line
    if (!$line) { throw "Could not find port= in $conf" }
    if ($line -notmatch '(\d+)') { throw "Could not parse port from line: $line" }
    return [int]$Matches[1]
}

function Invoke-PSQL {
    param(
        [string]$Db,
        [string]$Sql,
        [int]$Port
    )
    & "$PGROOT\bin\psql.exe" -h 127.0.0.1 -p $Port -U postgres -d $Db -c $Sql
}

# Ensure service running
$svc = Get-Service -Name $ServiceName -ErrorAction Stop
if ($svc.Status -ne "Running") { Start-Service $ServiceName }

# Detect port
$PORT = Get-PostgresPort -svc $ServiceName
Write-Host "PGROOT=$PGROOT"
Write-Host "PORT=$PORT"

# Test
Invoke-PSQL -Db "postgres" -Sql "SELECT version();" -Port $PORT

# Create DB (ignore errors if exists)
try {
    Invoke-PSQL -Db "postgres" -Sql "CREATE DATABASE $DbName;" -Port $PORT
} catch {
    Write-Host "CREATE DATABASE $DbName failed (likely already exists). Continuing..."
}

# Apply SQL file
# If BOM sneaks in, rewrite as UTF-8 without BOM and retry.
try {
    & "$PGROOT\bin\psql.exe" -h 127.0.0.1 -p $PORT -U postgres -d $DbName -f $SqlFile
} catch {
    Write-Host "SQL apply failed. Attempting BOM-safe rewrite and retry..."
    $raw = Get-Content $SqlFile -Raw
    [System.IO.File]::WriteAllText($SqlFile, $raw, (New-Object System.Text.UTF8Encoding($false)))
    & "$PGROOT\bin\psql.exe" -h 127.0.0.1 -p $PORT -U postgres -d $DbName -f $SqlFile
}

Write-Host "`nVerifying extension + tables..."
& "$PGROOT\bin\psql.exe" -h 127.0.0.1 -p $PORT -U postgres -d $DbName -c "\dx"
& "$PGROOT\bin\psql.exe" -h 127.0.0.1 -p $PORT -U postgres -d $DbName -c "\dt"

Write-Host "`nDone. Next:"
Write-Host "  . .\powershell\env.ps1"
Write-Host "  py .\scripts\ingest.py --path .\sample_docs --source pilot"
Write-Host "  py .\scripts\ask_rag.py `"What is dbt used for?`""
