from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import app  # noqa: E402


client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_job_lifecycle():
    created = client.post('/v1/jobs', json={
        'instruction': 'Open the test app and report its title',
        'profile': 'flash',
    })
    assert created.status_code == 200
    job_id = created.json()['id']

    claimed = client.post('/v1/jobs/claim', json={'worker_id': 'test-worker'})
    assert claimed.status_code == 200
    assert claimed.json()['id'] == job_id
    assert claimed.json()['status'] == 'running'

    completed = client.post(
        f'/v1/jobs/{job_id}/complete',
        json={
            'worker_id': 'test-worker',
            'result': {'succeeded': True, 'trace_id': 'test-trace'},
        },
    )
    assert completed.status_code == 200
    assert completed.json()['status'] == 'succeeded'

    detail = client.get(f'/v1/jobs/{job_id}')
    assert detail.status_code == 200
    assert detail.json()['result']['succeeded'] is True


def test_desktop_file_context_can_be_attached_to_job():
    upload = client.post(
        '/v1/files/ingest',
        files={'file': ('stores.csv', 'store,task\n184,opening checklist\n185,refrigeration', 'text/csv')},
    )
    assert upload.status_code == 200
    file_id = upload.json()['id']
    assert upload.json()['rows'] == 2

    created = client.post('/v1/jobs', json={
        'instruction': 'Handle the store tasks listed in the attached business file.',
        'profile': 'flash',
        'source_file_id': file_id,
        'row_limit': 2,
    })
    assert created.status_code == 200
    assert created.json()['source_file_id'] == file_id
    assert created.json()['context_rows'] == 2

    job = client.get(f"/v1/jobs/{created.json()['id']}")
    assert job.status_code == 200
    assert len(job.json()['context']) == 2
    assert 'stores.csv' in job.json()['instruction']
