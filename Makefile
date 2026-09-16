api:
	cd services/api && uv run uvicorn app.main:app --host 127.0.0.1 --port 8787 --reload

agent:
	cd services/windows-agent && uv run python -m agent
