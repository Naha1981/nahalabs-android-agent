$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$apiDir = Join-Path $repoRoot "services\api"
$agentDir = Join-Path $repoRoot "services\windows-agent"
$profile = if ($env:ARTEMIS_PROFILE) { $env:ARTEMIS_PROFILE } else { "flash" }

Write-Host "Starting local NahaLabs API..." -ForegroundColor Cyan
Set-Location $apiDir
uv sync
$api = Start-Process -FilePath "uv" -ArgumentList @("run","uvicorn","app.main:app","--host","127.0.0.1","--port","8787") -WorkingDirectory $apiDir -PassThru

try {
    $ready = $false
    for ($i = 0; $i -lt 15; $i++) {
        try {
            $health = Invoke-RestMethod -Uri "http://127.0.0.1:8787/health" -Method Get
            if ($health.status -eq "ok") { $ready = $true; break }
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    if (-not $ready) { throw "NahaLabs API did not become ready." }

    Write-Host "Creating harmless Android smoke-test job..." -ForegroundColor Cyan
    $body = @{
        instruction = "Open Android Settings. Verify that the Settings app is visible. Do not change any settings. Return a brief confirmation."
        profile = $profile
    }
    if ($env:ARTEMIS_DEVICE_SERIAL) { $body.device_serial = $env:ARTEMIS_DEVICE_SERIAL }

    $json = $body | ConvertTo-Json
    $job = Invoke-RestMethod -Uri "http://127.0.0.1:8787/v1/jobs" -Method Post -ContentType "application/json" -Body $json
    Write-Host "Queued job: $($job.id)" -ForegroundColor Green

    Write-Host "Running one Windows Agent cycle..." -ForegroundColor Cyan
    Set-Location $agentDir
    uv sync
    $env:NAHALABS_API_URL = "http://127.0.0.1:8787"
    uv run python -m agent --once

    $result = Invoke-RestMethod -Uri "http://127.0.0.1:8787/v1/jobs/$($job.id)" -Method Get
    Write-Host "Final job status: $($result.status)" -ForegroundColor Green
    $result | ConvertTo-Json -Depth 10

    if ($result.status -ne "succeeded") {
        throw "Smoke test did not succeed. See the job result above."
    }
}
finally {
    if ($api) { Stop-Process -Id $api.Id -Force -ErrorAction SilentlyContinue }
}
