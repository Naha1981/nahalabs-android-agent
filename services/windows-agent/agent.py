from __future__ import annotations

import argparse
import asyncio
import os
import platform
import socket
import traceback

import httpx

try:
    from artemis_client import ArtemisClient
except ImportError:  # pragma: no cover - allows API-only development
    ArtemisClient = None  # type: ignore[assignment,misc]

API_URL = os.getenv("NAHALABS_API_URL", "http://127.0.0.1:8787").rstrip("/")
ARTEMIS_URL = os.getenv("ARTEMIS_URL", "http://127.0.0.1:8000").rstrip("/")
PROFILE = os.getenv("ARTEMIS_PROFILE", "flash")
DEVICE_SERIAL = os.getenv("ARTEMIS_DEVICE_SERIAL") or None
WORKER_ID = os.getenv("NAHALABS_WORKER_ID", f"windows-{socket.gethostname()}")
POLL_SECONDS = float(os.getenv("NAHALABS_POLL_SECONDS", "2"))


def build_client() -> ArtemisClient:
    if ArtemisClient is None:
        raise RuntimeError(
            "artemis-client is not installed. Run `uv sync` in services/windows-agent."
        )
    return ArtemisClient(
        ARTEMIS_URL,
        device_serial=DEVICE_SERIAL,
        default_profile=PROFILE,  # type: ignore[arg-type]
    )


async def execute(job: dict) -> dict:
    client = build_client()
    result = await client.run(
        job["instruction"],
        profile=job.get("profile") or PROFILE,
        device_serial=job.get("device_serial") or DEVICE_SERIAL,
        timeout=float(os.getenv("ARTEMIS_TASK_TIMEOUT", "900")),
    )
    return {
        "succeeded": bool(result.succeeded),
        "status": result.status,
        "goal": result.goal,
        "error": result.error,
        "device_serial": result.device_serial,
        "trace_id": result.trace_id,
        "output": result.output,
        "turns": result.turns,
    }


async def process_one(http: httpx.AsyncClient) -> bool:
    response = await http.post(
        f"{API_URL}/v1/jobs/claim",
        json={"worker_id": WORKER_ID},
    )
    response.raise_for_status()
    job = response.json()
    if not job:
        return False

    print(f"Executing job {job['id']}: {job['instruction']}")
    try:
        result = await execute(job)
        completion = await http.post(
            f"{API_URL}/v1/jobs/{job['id']}/complete",
            json={
                "worker_id": WORKER_ID,
                "result": result,
                "error": result.get("error") if not result.get("succeeded") else None,
            },
        )
        completion.raise_for_status()
        print(f"Completed {job['id']}: {result}")
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        print(error)
        traceback.print_exc()
        completion = await http.post(
            f"{API_URL}/v1/jobs/{job['id']}/complete",
            json={"worker_id": WORKER_ID, "result": {}, "error": error},
        )
        completion.raise_for_status()
    return True


async def loop(once: bool = False) -> None:
    print(f"NahaLabs Windows Agent: {WORKER_ID}")
    print(f"API: {API_URL}")
    print(f"ARTEMIS: {ARTEMIS_URL}")
    print(f"Profile: {PROFILE}")
    print(f"Device: {DEVICE_SERIAL or 'auto'}")
    print(f"Host: {platform.platform()}")

    async with httpx.AsyncClient(timeout=30) as http:
        if once:
            await process_one(http)
            return

        while True:
            try:
                processed = await process_one(http)
                if not processed:
                    await asyncio.sleep(POLL_SECONDS)
            except Exception as exc:
                print(f"Agent loop error: {type(exc).__name__}: {exc}")
                await asyncio.sleep(max(POLL_SECONDS, 3))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NahaLabs Windows Agent")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Claim and execute at most one queued job, then exit.",
    )
    args = parser.parse_args()
    asyncio.run(loop(once=args.once))
