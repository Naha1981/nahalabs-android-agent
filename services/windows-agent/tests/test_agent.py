import asyncio
import importlib.util
from pathlib import Path
from types import SimpleNamespace


MODULE_PATH = Path(__file__).resolve().parents[1] / "agent.py"
spec = importlib.util.spec_from_file_location("nahalabs_windows_agent", MODULE_PATH)
agent = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(agent)


class FakeClient:
    instances = []

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.instances.append(self)

    async def run(self, goal, **kwargs):
        return SimpleNamespace(
            succeeded=True,
            status="completed",
            goal=goal,
            error=None,
            device_serial=kwargs.get("device_serial") or self.kwargs.get("device_serial"),
            trace_id="task-123",
            output="verified",
            turns=2,
        )


def test_execute_uses_job_profile_and_device(monkeypatch):
    FakeClient.instances.clear()
    monkeypatch.setattr(agent, "ArtemisClient", FakeClient)
    monkeypatch.setattr(agent, "ARTEMIS_URL", "http://127.0.0.1:8000")
    monkeypatch.setattr(agent, "DEVICE_SERIAL", "default-device")
    monkeypatch.setattr(agent, "PROFILE", "flash")

    result = asyncio.run(
        agent.execute(
            {
                "instruction": "Open the approved test app and report the title",
                "profile": "pro",
                "device_serial": "job-device",
            }
        )
    )

    assert FakeClient.instances[0].kwargs["default_profile"] == "pro"
    assert FakeClient.instances[0].kwargs["device_serial"] == "job-device"
    assert result["succeeded"] is True
    assert result["profile"] == "pro"
    assert result["device_serial"] == "job-device"
    assert result["trace_id"] == "task-123"
    assert result["output"] == "verified"


def test_execute_falls_back_to_worker_defaults(monkeypatch):
    FakeClient.instances.clear()
    monkeypatch.setattr(agent, "ArtemisClient", FakeClient)
    monkeypatch.setattr(agent, "ARTEMIS_URL", "http://127.0.0.1:8000")
    monkeypatch.setattr(agent, "DEVICE_SERIAL", "default-device")
    monkeypatch.setattr(agent, "PROFILE", "flash")

    result = asyncio.run(agent.execute({"instruction": "Open the test app"}))

    assert FakeClient.instances[0].kwargs["default_profile"] == "flash"
    assert FakeClient.instances[0].kwargs["device_serial"] == "default-device"
    assert result["profile"] == "flash"
    assert result["device_serial"] == "default-device"
