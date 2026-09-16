$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$apiDir = Join-Path $repoRoot "services\api"
$agentDir = Join-Path $repoRoot "services\windows-agent"

Write-Host "Starting local NahaLabs API..." -ForegroundColor Cyan
$api = Start-Process -FilePath "uv" -ArgumentList @("run","uvicorn","app.main:app","--host","127.0.0.1","--port","8787") -WorkingDirectory $apiDir -PassThru

try {
    Start-Sleep -Seconds 2
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8787/health" -Method Get
    if ($health.status -ne "ok") { throw "NahaLabs API health check failed." }

    Write-Host "Creating harmless Android smoke-test job..." -ForegroundColor Cyan
    $body = @{
        instruction = "Open Android Settings. Verify that the Settings app is visible. Do not change any settings. Return a brief confirmation."
        profile = $env:ARTEMIS_PROFILE
        device_serial = $env:ARTEMIS_DEVICE_SERIAL
    } | ConvertTo-Json

    $job = Invoke-RestMethod -Uri "http://127.0.0.1:8787/v1/jobs" -Method Post -ContentType "application/json" -Body $body
    Write-Host "Queued job: $($job.id)" -ForegroundColor Green

    Write-Host "Running one Windows Agent cycle..." -ForegroundColor Cyan
    Set-Location $agentDir
    uv sync
    uv run python -m agent --once

    $result = Invoke-RestMethod -Uri "http://127.0.0.1:8787/v1/jobs/$($job.id)" -Method Get
    Write-Host "Final job status: $($result.status)" -ForegroundColor Green
    $result | ConvertTo-Json -Depth 10
}
finally {
    if ($api) { Stop-Process -Id $api.Id -Force -ErrorAction SilentlyContinue }
}
