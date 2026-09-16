$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location (Join-Path $root "services\windows-agent")

Write-Host "NahaLabs AI Operator — Windows/ARTEMIS Doctor" -ForegroundColor Cyan
uv sync
uv run python doctor.py
