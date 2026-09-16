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
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    async def run(self, goal):
        return SimpleNamespace(
            succeeded=True,
            status="completed",
            error=None,
            device_serial="test-device",
            trace_id="task-123",
        )


def test_execute_uses_artemis_contract(monkeypatch):
    monkeypatch.setattr(agent, "ArtemisClient", FakeClient)
    monkeypatch.setattr(agent, "ARTEMIS_URL", "http://127.0.0.1:8000")
    monkeypatch.setattr(agent, "DEVICE_SERIAL", "test-device")
    monkeypatch.setattr(agent, "PROFILE", "flash")

    result = asyncio.run(agent.execute({"instruction": "Open the test app and report the title"}))

    assert result == {
        "succeeded": True,
        "status": "completed",
        "error": None,
        "device_serial": "test-device",
        "trace_id": "task-123",
    }
