from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gateway import app  # noqa: E402


client = TestClient(app)


def test_office_to_field_to_office_flow():
    external_id = "STD-ATM-18492"
    imported = client.post(
        "/v1/office/tickets",
        json={
            "system": "demo-service-desk",
            "external_id": external_id,
            "customer": "National Retail Group",
            "location": "Rosebank #184",
            "asset": "POS-1842",
            "problem": "Terminal offline",
            "priority": "HIGH",
            "sla_minutes": 240,
        },
    )
    assert imported.status_code == 200
    ticket_id = imported.json()["id"]

    dispatched = client.post(
        f"/v1/office/tickets/{ticket_id}/dispatch",
        json={
            "technician_id": "tech-184",
            "technician_name": "Sipho Mokoena",
        },
    )
    assert dispatched.status_code == 200
    job_id = dispatched.json()["job_id"]

    status = client.post(
        f"/v1/field/jobs/{job_id}/status",
        json={"technician_id": "tech-184", "status": "arrived", "latitude": -26.1076, "longitude": 28.0567},
    )
    assert status.status_code == 200
    assert status.json()["office_sync"] == "SYNCED"

    submitted = client.post(
        f"/v1/field/jobs/{job_id}/submit",
        json={
            "technician_id": "tech-184",
            "gps_verified": True,
            "technician_verified": True,
            "checklist": [
                {"id": "power", "value": "pass"},
                {"id": "network", "value": "issue"},
            ],
            "evidence": [{"type": "photo", "name": "proof.jpg"}],
            "notes": "Network fault confirmed.",
            "resolution": "Replaced network cable and retested.",
            "customer_signoff": True,
        },
    )
    assert submitted.status_code == 200
    assert submitted.json()["status"] == "succeeded"
    assert submitted.json()["office_sync"] == "SYNCED"

    office = client.get(f"/v1/office/tickets/{ticket_id}")
    assert office.status_code == 200
    assert office.json()["status"] == "CLOSED"
    assert office.json()["payload"]["nahalabs_status"] == "CLOSED"

    field = client.get(f"/v1/field/jobs/{job_id}")
    assert field.status_code == 200
    assert field.json()["field_status"] == "completed"
    assert field.json()["field_submission"]["customer_signoff"] is True


def test_phone_submission_blocks_incomplete_jobs_without_exception():
    imported = client.post(
        "/v1/office/tickets",
        json={
            "system": "demo-service-desk",
            "external_id": "STD-INCOMPLETE-1",
            "customer": "Example Customer",
            "location": "Johannesburg",
            "asset": "ASSET-1",
            "problem": "Fault",
        },
    )
    ticket_id = imported.json()["id"]
    dispatched = client.post(
        f"/v1/office/tickets/{ticket_id}/dispatch",
        json={"technician_id": "tech-2", "technician_name": "Test Technician"},
    )
    job_id = dispatched.json()["job_id"]

    response = client.post(
        f"/v1/field/jobs/{job_id}/submit",
        json={"technician_id": "tech-2"},
    )
    assert response.status_code == 422
    assert "checklist" in response.json()["detail"]["missing"]
