# Start the FastAPI backend with reload scoped to source folders only.
# Avoids watching .venv, frontend/.next, node_modules, and other noisy paths
# that can trigger excessive reloads and orphan worker processes on Windows.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Uvicorn = Join-Path $Root "backend\.venv\Scripts\uvicorn.exe"
if (-not (Test-Path $Uvicorn)) {
    throw "Backend venv not found. Run: python -m venv backend\.venv; backend\.venv\Scripts\pip install -r backend\requirements.txt -r database\requirements.txt"
}

& $Uvicorn backend.app.main:app `
    --reload `
    --reload-dir backend `
    --reload-dir database `
    --port 8000
