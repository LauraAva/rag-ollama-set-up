# Dot-source this file:
#   . .\powershell\env.ps1

# Update if your install differs:
$env:PGHOST="127.0.0.1"
$env:PGUSER="postgres"
$env:PGDATABASE="ragdb"

# Let setup_rag.ps1 discover port automatically and export it here
# If you want to hardcode, set $env:PGPORT="5433"
try {
    $svc = "postgresql-x64-16"
    $pathName = (Get-CimInstance Win32_Service -Filter "Name='$svc'").PathName
    if ($pathName -match '-D\s+"([^"]+)"') {
        $dataDir = $Matches[1]
        $conf = Join-Path $dataDir "postgresql.conf"
        $line = (Select-String -Path $conf -Pattern '^\s*port\s*=\s*\d+').Line
        if ($line -match '(\d+)') { $env:PGPORT = $Matches[1] }
    }
} catch {}

# Models
$env:EMBED_MODEL="bge-m3"
$env:CHAT_MODEL="gemma3:4b"

Write-Host "Env set:"
Write-Host "  PGHOST=$env:PGHOST"
Write-Host "  PGPORT=$env:PGPORT"
Write-Host "  PGUSER=$env:PGUSER"
Write-Host "  PGDATABASE=$env:PGDATABASE"
Write-Host "  EMBED_MODEL=$env:EMBED_MODEL"
Write-Host "  CHAT_MODEL=$env:CHAT_MODEL"
Write-Host ""
Write-Host "Optional (do NOT commit):"
Write-Host '  $env:PGPASSWORD="<your_password>"'
