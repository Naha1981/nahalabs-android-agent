# NahaLabs AI Operator

Windows business data → NahaLabs job API → Windows Agent → ARTEMIS → Android → result/evidence → NahaLabs API.

## Architecture

```text
┌──────────────────────┐
│ Windows business     │
│ files: CSV/XLSX      │
└──────────┬───────────┘
           │ ingest
           ▼
┌──────────────────────┐
│ NahaLabs API         │
│ jobs + audit + data  │
│ :8787                │
└──────────┬───────────┘
           │ polling
           ▼
┌──────────────────────┐
│ Windows Agent        │
│ local bridge         │
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

This repo implements the local vertical slice with SQLite:

1. Upload/ingest a CSV or XLSX file into the API.
2. Create a natural-language mobile job.
3. Windows Agent claims the job.
4. Agent sends the instruction to ARTEMIS.
5. Agent posts the structured result back.
6. Dashboard/API exposes job state.

Supabase/Cloudflare are deliberately kept behind interfaces so the local proof-of-concept stays free and portable.

## Requirements

- Windows 10/11
- Python 3.12+
- `uv`
- Android phone with USB debugging
- Google ARTEMIS installed separately from https://github.com/google/artemis
- One configured ARTEMIS model provider

ARTEMIS currently documents a Python SDK package (`artemis-client`) and an HTTP server at `http://localhost:8000`. See the upstream project for current setup requirements.

## Run API

```powershell
cd services/api
uv run uvicorn app.main:app --host 127.0.0.1 --port 8787 --reload
```

## Run Windows Agent

```powershell
cd services/windows-agent
uv run python -m agent
```

Set these environment variables when needed:

```powershell
$env:NAHALABS_API_URL="http://127.0.0.1:8787"
$env:ARTEMIS_URL="http://127.0.0.1:8000"
$env:ARTEMIS_PROFILE="flash"
$env:ARTEMIS_DEVICE_SERIAL=""
```

## Safety

The agent never executes arbitrary shell commands from a business job. The first version only submits a natural-language task to ARTEMIS and records the result. ARTEMIS itself should only be pointed at a dedicated test device until the security model is hardened.
