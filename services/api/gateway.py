from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel, Field

from app.main import app, db, now


def init_gateway_db() -> None:
    with db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS office_tickets (
                id TEXT PRIMARY KEY,
                system TEXT NOT NULL,
                external_id TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                status TEXT NOT NULL,
                job_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE UNIQUE INDEX IF NOT EXISTS idx_office_ticket_external
                ON office_tickets(system, external_id);
            CREATE TABLE IF NOT EXISTS job_events (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                actor TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_job_events_job_created
                ON job_events(job_id, created_at);
            """
        )

        columns = {row[1] for row in conn.execute("PRAGMA table_info(jobs)").fetchall()}
        for name, ddl in {
            "office_system": "ALTER TABLE jobs ADD COLUMN office_system TEXT",
            "office_ticket_id": "ALTER TABLE jobs ADD COLUMN office_ticket_id TEXT",
            "field_status": "ALTER TABLE jobs ADD COLUMN field_status TEXT",
            "field_submission_json": "ALTER TABLE jobs ADD COLUMN field_submission_json TEXT",
            "office_sync_status": "ALTER TABLE jobs ADD COLUMN office_sync_status TEXT",
        }.items():
            if name not in columns:
                conn.execute(ddl)


init_gateway_db()


class OfficeTicket(BaseModel):
    system: str = Field(min_length=1, max_length=64)
    external_id: str = Field(min_length=1, max_length=128)
    customer: str = Field(min_length=1, max_length=200)
    location: str = Field(min_length=1, max_length=300)
    asset: str = Field(min_length=1, max_length=200)
    problem: str = Field(min_length=1, max_length=1000)
    priority: str = Field(default="NORMAL", max_length=32)
    sla_minutes: int = Field(default=240, ge=1, le=10080)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DispatchRequest(BaseModel):
    technician_id: str = Field(min_length=1, max_length=128)
    technician_name: str = Field(min_length=1, max_length=200)
    device_serial: str | None = None
    profile: str = Field(default="flash", pattern="^(flash|pro)$")


class FieldStatusUpdate(BaseModel):
    technician_id: str = Field(min_length=1, max_length=128)
    status: str = Field(pattern="^(accepted|en_route|arrived|inspecting|paused|awaiting_parts|repairing|ready_to_close|completed|needs_reinspection)$")
    note: str | None = Field(default=None, max_length=2000)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class FieldSubmission(BaseModel):
    technician_id: str = Field(min_length=1, max_length=128)
    gps_verified: bool = False
    technician_verified: bool = False
    checklist: list[dict[str, Any]] = Field(default_factory=list)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    notes: str | None = Field(default=None, max_length=5000)
    resolution: str | None = Field(default=None, max_length=2000)
    customer_signoff: bool = False
    submit_with_exception: bool = False


def record_event(job_id: str, actor: str, event_type: str, payload: dict[str, Any]) -> None:
    with db() as conn:
        conn.execute(
            "INSERT INTO job_events VALUES (?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), job_id, actor, event_type, json.dumps(payload, default=str), now()),
        )


def sync_office_ticket(job_id: str, status: str, payload: dict[str, Any]) -> None:
    with db() as conn:
        job = conn.execute("SELECT office_ticket_id FROM jobs WHERE id=?", (job_id,)).fetchone()
        if not job or not job["office_ticket_id"]:
            return
        ticket = conn.execute(
            "SELECT payload_json FROM office_tickets WHERE id=?", (job["office_ticket_id"],)
        ).fetchone()
        if not ticket:
            return
        current = json.loads(ticket["payload_json"])
        current.update({"nahalabs_status": status, "nahalabs_update": payload})
        conn.execute(
            "UPDATE office_tickets SET payload_json=?, status=?, updated_at=? WHERE id=?",
            (json.dumps(current, default=str), status, now(), job["office_ticket_id"]),
        )
        conn.execute(
            "UPDATE jobs SET office_sync_status='SYNCED', updated_at=? WHERE id=?",
            (now(), job_id),
        )


@app.get("/v1/gateway/integrations")
def list_gateway_integrations() -> dict[str, Any]:
    return {
        "gateway": "NahaLabs Office ↔ Field Gateway",
        "supported_system_contracts": ["generic-erp", "generic-crm", "generic-service-desk", "generic-claims"],
        "demo_adapter": "simulated-office-system",
        "direction": "bidirectional",
        "flow": [
            "office ticket import",
            "dispatch to technician",
            "phone status control",
            "field submission",
            "evidence + resolution recorded",
            "office ticket status sync",
        ],
    }


@app.post("/v1/office/tickets")
def create_office_ticket(payload: OfficeTicket) -> dict[str, Any]:
    ticket_id = str(uuid.uuid4())
    timestamp = now()
    ticket_payload = payload.model_dump()
    with db() as conn:
        existing = conn.execute(
            "SELECT * FROM office_tickets WHERE system=? AND external_id=?",
            (payload.system, payload.external_id),
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Office ticket already imported")
        conn.execute(
            "INSERT INTO office_tickets VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                ticket_id,
                payload.system,
                payload.external_id,
                json.dumps(ticket_payload, default=str),
                "IMPORTED",
                None,
                timestamp,
                timestamp,
            ),
        )
    return {"id": ticket_id, "status": "IMPORTED", "ticket": ticket_payload}


@app.get("/v1/office/tickets/{ticket_id}")
def get_office_ticket(ticket_id: str) -> dict[str, Any]:
    with db() as conn:
        row = conn.execute("SELECT * FROM office_tickets WHERE id=?", (ticket_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Office ticket not found")
    item = dict(row)
    item["payload"] = json.loads(item.pop("payload_json"))
    return item


@app.post("/v1/office/tickets/{ticket_id}/dispatch")
def dispatch_office_ticket(ticket_id: str, payload: DispatchRequest) -> dict[str, Any]:
    with db() as conn:
        ticket = conn.execute("SELECT * FROM office_tickets WHERE id=?", (ticket_id,)).fetchone()
        if not ticket:
            raise HTTPException(status_code=404, detail="Office ticket not found")
        if ticket["job_id"]:
            raise HTTPException(status_code=409, detail="Office ticket already dispatched")
        data = json.loads(ticket["payload_json"])

        job_id = str(uuid.uuid4())
        timestamp = now()
        instruction = (
            f"Field service job from {data['system']} ticket {data['external_id']}: "
            f"customer={data['customer']}; location={data['location']}; "
            f"asset={data['asset']}; problem={data['problem']}; priority={data['priority']}; "
            f"SLA={data['sla_minutes']} minutes. Technician={payload.technician_name}."
        )
        conn.execute(
            """
            INSERT INTO jobs (
                id, instruction, status, profile, device_serial, claimed_by,
                result_json, error, created_at, updated_at, source_file_id, context_json,
                office_system, office_ticket_id, field_status, field_submission_json, office_sync_status
            ) VALUES (?, ?, 'queued', ?, ?, NULL, NULL, NULL, ?, ?, NULL, ?, ?, ?, 'assigned', NULL, 'SYNCED')
            """,
            (
                job_id,
                instruction,
                payload.profile,
                payload.device_serial,
                timestamp,
                timestamp,
                None,
                payload.technician_id,
                ticket_id,
            ),
        )
        conn.execute(
            "UPDATE office_tickets SET job_id=?, status='DISPATCHED', updated_at=? WHERE id=?",
            (job_id, timestamp, ticket_id),
        )
        conn.execute(
            "UPDATE jobs SET office_system=?, office_ticket_id=? WHERE id=?",
            (data["system"], ticket_id, job_id),
        )

    record_event(job_id, "office", "DISPATCHED", {"ticket_id": ticket_id, "technician_id": payload.technician_id})
    return {"job_id": job_id, "status": "assigned", "office_ticket_id": ticket_id, "technician_id": payload.technician_id}


@app.get("/v1/field/jobs/{job_id}")
def get_field_job(job_id: str) -> dict[str, Any]:
    with db() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Field job not found")
        events = conn.execute(
            "SELECT id, actor, event_type, payload_json, created_at FROM job_events WHERE job_id=? ORDER BY created_at",
            (job_id,),
        ).fetchall()
    item = dict(row)
    if item.get("context_json"):
        item["office_context"] = json.loads(item.pop("context_json"))
    else:
        item.pop("context_json", None)
    if item.get("field_submission_json"):
        item["field_submission"] = json.loads(item.pop("field_submission_json"))
    else:
        item.pop("field_submission_json", None)
    item.pop("result_json", None)
    item["events"] = [
        {**dict(event), "payload": json.loads(event["payload_json"])} for event in events
    ]
    return item


@app.post("/v1/field/jobs/{job_id}/status")
def update_field_status(job_id: str, payload: FieldStatusUpdate) -> dict[str, Any]:
    with db() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Field job not found")
        if row["claimed_by"] and row["claimed_by"] != payload.technician_id:
            raise HTTPException(status_code=409, detail="Job is assigned to another technician")
        conn.execute(
            "UPDATE jobs SET claimed_by=?, status='running', field_status=?, updated_at=? WHERE id=?",
            (payload.technician_id, payload.status, now(), job_id),
        )
    event_payload = payload.model_dump(exclude_none=True)
    record_event(job_id, f"technician:{payload.technician_id}", payload.status.upper(), event_payload)
    sync_office_ticket(job_id, payload.status.upper(), event_payload)
    return {"job_id": job_id, "field_status": payload.status, "office_sync": "SYNCED"}


@app.post("/v1/field/jobs/{job_id}/submit")
def submit_field_job(job_id: str, payload: FieldSubmission) -> dict[str, Any]:
    with db() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Field job not found")
        if row["claimed_by"] and row["claimed_by"] != payload.technician_id:
            raise HTTPException(status_code=409, detail="Job is assigned to another technician")

        checklist_complete = bool(payload.checklist) and all(
            item.get("value") in {"pass", "issue"} for item in payload.checklist
        )
        evidence_present = len(payload.evidence) > 0
        trusted_completion = payload.gps_verified and payload.technician_verified and payload.customer_signoff
        if not payload.submit_with_exception and (not checklist_complete or not evidence_present or not trusted_completion):
            missing = []
            if not checklist_complete:
                missing.append("checklist")
            if not evidence_present:
                missing.append("evidence")
            if not payload.gps_verified:
                missing.append("gps_verification")
            if not payload.technician_verified:
                missing.append("technician_verification")
            if not payload.customer_signoff:
                missing.append("customer_signoff")
            raise HTTPException(status_code=422, detail={"message": "Submission is incomplete", "missing": missing})

        submission = payload.model_dump()
        timestamp = now()
        status = "succeeded" if trusted_completion else "needs_review"
        conn.execute(
            """
            UPDATE jobs
            SET claimed_by=?, status=?, field_status=?, field_submission_json=?, result_json=?, updated_at=?
            WHERE id=?
            """,
            (
                payload.technician_id,
                status,
                "completed" if status == "succeeded" else "needs_reinspection",
                json.dumps(submission, default=str),
                json.dumps({"submitted_from": "technician_phone", "submitted_at": timestamp}, default=str),
                timestamp,
                job_id,
            ),
        )

    record_event(job_id, f"technician:{payload.technician_id}", "FIELD_SUBMITTED", submission)
    sync_status = "CLOSED" if status == "succeeded" else "EXCEPTION"
    sync_office_ticket(job_id, sync_status, {"field_submission": submission})
    return {"job_id": job_id, "status": status, "office_sync": "SYNCED", "office_status": sync_status}


@app.get("/v1/field/jobs/{job_id}/events")
def list_field_events(job_id: str) -> list[dict[str, Any]]:
    with db() as conn:
        rows = conn.execute(
            "SELECT actor, event_type, payload_json, created_at FROM job_events WHERE job_id=? ORDER BY created_at",
            (job_id,),
        ).fetchall()
    if not rows:
        with db() as conn:
            exists = conn.execute("SELECT 1 FROM jobs WHERE id=?", (job_id,)).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Field job not found")
    return [
        {"actor": row["actor"], "event_type": row["event_type"], "payload": json.loads(row["payload_json"]), "created_at": row["created_at"]}
        for row in rows
    ]


# The gateway is an extension of the existing app. Run with:
# uv run uvicorn gateway:app --host 127.0.0.1 --port 8790
