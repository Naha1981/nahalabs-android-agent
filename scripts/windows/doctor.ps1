$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location (Join-Path $root "services\windows-agent")

Write-Host "NahaLabs AI Operator — Windows/ARTEMIS Doctor" -ForegroundColor Cyan
uv sync
uv run python doctor.py
