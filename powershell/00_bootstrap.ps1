Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "== Bootstrap: Python deps + Ollama models =="

# 1) Verify Python
try { & py --version } catch { throw "Python 'py' not found. Install Python first and re-open PowerShell." }

# 2) Verify Ollama
try { & ollama --version } catch { throw "Ollama not found. Install Ollama first." }

# 3) Install Python deps from repo root
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$req = Join-Path $repoRoot "requirements.txt"
if (!(Test-Path $req)) { throw "requirements.txt not found at $req" }

Write-Host "Installing Python deps from requirements.txt..."
& py -m pip install -r $req

# 4) Pull models
Write-Host "Pulling Ollama models..."
& ollama pull bge-m3
& ollama pull gemma3:4b

Write-Host "Bootstrap done."
Write-Host "Next: run .\powershell\01_setup_db.ps1"
