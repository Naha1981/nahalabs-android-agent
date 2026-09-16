from __future__ import annotations

import asyncio
import os
import platform

from artemis_client import ArtemisClient

ARTEMIS_URL = os.getenv("ARTEMIS_URL", "http://127.0.0.1:8000").rstrip("/")
DEVICE_SERIAL = os.getenv("ARTEMIS_DEVICE_SERIAL") or None
PROFILE = os.getenv("ARTEMIS_PROFILE", "flash")


def status(ok: bool) -> str:
    return "OK" if ok else "NOT READY"


async def main() -> int:
    print("NahaLabs AI Operator — Windows/ARTEMIS Doctor")
    print(f"Windows: {platform.platform()}")
    print(f"ARTEMIS: {ARTEMIS_URL}")
    print(f"Profile: {PROFILE}")
    print()

    client = ArtemisClient(
        ARTEMIS_URL,
        device_serial=DEVICE_SERIAL,
        default_profile=PROFILE,
        request_timeout=15,
    )

    try:
        health = await client.health()
        print(f"ARTEMIS health: {status(True)} {health}")
    except Exception as exc:
        print(f"ARTEMIS health: NOT READY — {type(exc).__name__}: {exc}")
        return 1

    try:
        readiness = await client.readiness()
        print(f"ARTEMIS readiness: {status(True)}")
        print(readiness)
    except Exception as exc:
        print(f"ARTEMIS readiness: WARNING — {type(exc).__name__}: {exc}")

    try:
        devices = await client.list_devices()
    except Exception as exc:
        print(f"Android devices: NOT READY — {type(exc).__name__}: {exc}")
        return 1

    if not devices:
        print("Android devices: NOT READY — no devices reported by ARTEMIS")
        return 1

    print("Android devices:")
    for device in devices:
        marker = " <- configured" if DEVICE_SERIAL and device.serial == DEVICE_SERIAL else ""
        print(
            f"  {device.serial} | state={device.state} | busy={device.busy}"
            f" | model={device.model or 'unknown'}{marker}"
        )

    if DEVICE_SERIAL and all(device.serial != DEVICE_SERIAL for device in devices):
        print(f"Configured device {DEVICE_SERIAL!r} was not found.")
        return 1

    print("\nSystem is ready for a controlled smoke test.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
