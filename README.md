# NahaLabs AI Operator

Windows business data → NahaLabs job API → Windows Agent → ARTEMIS → Android → result/evidence → NahaLabs API.

## Architecture

```text
┌──────────────────────┐
│ Windows business     │
│ CSV / XLSX / desktop │
└──────────┬───────────┘
           │ upload + context
           ▼
┌──────────────────────┐
│ NahaLabs API         │
│ files + jobs + audit │
│ :8787                │
└──────────┬───────────┘
           │ polling
           ▼
┌──────────────────────┐
│ Windows Agent        │
│ local execution edge │
└──────────┬───────────┘
           │ ArtemisClient
           ▼
┌──────────────────────┐
│ ARTEMIS              │
│ :8000                │
└──────────┬───────────┘
           │ ADB
           ▼
┌──────────────────────┐
│ Android phone        │
└──────────────────────┘
```

## Current milestone

The local proof-of-concept now supports:

1. Upload a CSV/XLSX business file.
2. Store the parsed rows in SQLite.
3. Attach selected desktop-file context to a natural-language mobile job.
4. Queue the job for the Windows Agent.
5. Have the Windows Agent submit the job to ARTEMIS.
6. Capture structured ARTEMIS output, status, device serial and trace ID.
7. Display job state from the dashboard/API.
8. Run a controlled one-shot smoke test instead of leaving a worker running.

Supabase/Cloudflare are deliberately kept behind interfaces so the local proof-of-concept stays free and portable.

## Requirements

- Windows 10/11
- Python 3.12+
- `uv`
- Android phone with USB debugging
- Google ARTEMIS installed separately from https://github.com/google/artemis
- One configured ARTEMIS model provider

ARTEMIS provides a Python client (`artemis-client`) and remote HTTP API. The NahaLabs Windows Agent uses that client rather than shelling out to arbitrary commands.

## Run API

```powershell
cd services/api
uv sync
uv run uvicorn app.main:app --host 127.0.0.1 --port 8787 --reload
```

Open `http://127.0.0.1:8787` for the local operator dashboard.

## Check the Android/ARTEMIS connection

From the repository root:

```powershell
.\scripts\windows\doctor.ps1
```

The doctor checks ARTEMIS health, readiness, and visible Android devices.

## Run the Windows Agent

```powershell
cd services/windows-agent
uv sync
uv run python -m agent
```

For a single queued job:

```powershell
uv run python -m agent --once
```

Set these environment variables when needed:

```powershell
$env:NAHALABS_API_URL="http://127.0.0.1:8787"
$env:ARTEMIS_URL="http://127.0.0.1:8000"
$env:ARTEMIS_PROFILE="flash"
$env:ARTEMIS_DEVICE_SERIAL=""
```

## Controlled smoke test

After ARTEMIS is running and your phone is connected:

```powershell
.\scripts\windows\smoke-test.ps1
```

The smoke test tells ARTEMIS to open Android Settings and verify that the Settings app is visible. It does not intentionally change device settings.

## Desktop-file workflow

The dashboard now supports:

**Upload Excel/CSV → select file → write natural-language instruction → dispatch job → Windows Agent → ARTEMIS → Android.**

The uploaded rows are attached to the job as context so the Android operator receives the relevant desktop business data together with the instruction.

## Safety

The Windows Agent never executes arbitrary shell commands from a business job. The first version only submits a natural-language task to ARTEMIS and records the result. ARTEMIS should initially be pointed at a dedicated test device until authentication, approvals, device policy, audit retention and enterprise isolation are hardened.
