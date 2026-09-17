# NahaLabs Field Intelligence — Execution Plan

## Engineering sequence

### 1. Establish the frontend runtime

Create `services/web` as a standalone Next.js 16.x App Router application. Keep it independent from the existing FastAPI service so the UI can evolve without coupling business logic to rendering.

### 2. Build one deterministic synthetic job

Use one scenario:
- Customer: National Retail Group (synthetic)
- Store: Rosebank #184 (synthetic)
- Asset: POS-1842 (synthetic)
- Fault: terminal offline
- Technician: Sipho Mokoena (synthetic)
- SLA: 4 hours
- Priority: HIGH

The scenario is deliberately fixed before adding scenario generators.

### 3. Implement the technician state machine

`assigned → en_route → arrived → inspecting → evidence_review → repair → customer_signoff → completed`

Exception path:

`evidence_review → blocked_missing_evidence → evidence_added → inspecting`

Escalation path:

`inspecting → critical_issue → escalated`

### 4. Implement manager state model

Dashboard derives operational state from the same demo job state. No second source of truth is allowed.

### 5. Build AI as a replaceable service boundary

Frontend receives deterministic demo AI results first. The boundary should later accept real multimodal output from Gemini or another model without redesigning the UI.

### 6. Add real media capture

Use browser camera/file APIs where supported. If a device denies camera access, fall back to file upload and make the state visible.

### 7. Connect to FastAPI

Add a typed API client and map the demonstrator states onto the existing jobs endpoint. Avoid leaking SQLite details into the frontend.

### 8. Add ARTEMIS execution

Only after the human-visible workflow is stable, connect the job action to the Windows Agent and ARTEMIS. The first real action remains harmless and reversible.

### 9. Test the critical path

Required verification:
- mobile layout
- desktop layout
- job state transitions
- missing evidence gate
- photo upload
- customer sign-off
- SLA transition
- manager/technician shared state
- API error state
- accessibility keyboard navigation
- CI build and lint

### 10. Demo script

1. Manager sees 142 active jobs.
2. Open high-priority Rosebank job.
3. Switch to technician view.
4. Start job.
5. Verify arrival.
6. Run checklist.
7. Find network + physical damage.
8. Capture evidence.
9. AI flags missing environment photo.
10. Capture missing evidence.
11. Confirm HIGH severity.
12. Complete work.
13. Capture customer sign-off.
14. Submit.
15. Switch back to manager.
16. Show completed timeline, evidence and SLA closure.

## Release discipline

- Do not claim real AI analysis when running demo fixtures.
- Do not claim real GPS verification when using simulated GPS.
- Do not claim enterprise integration until an actual adapter is connected.
- Every major milestone must pass CI before the next layer is added.
