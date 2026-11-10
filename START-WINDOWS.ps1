$ErrorActionPreference = "Stop"
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
Write-Host "Starting Academic Petition Triage services..."
docker compose up --build
