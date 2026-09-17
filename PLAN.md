# NahaLabs Field Intelligence — Build Plan

## Phase 0 — Product contract
- [x] Lock product thesis.
- [x] Define Trade Link-style technician workflow.
- [x] Define three reusable screens.
- [x] Define generic operational data model.
- [x] Define AI trust boundaries.

## Phase 1 — Demonstrator shell
- [ ] Add Next.js 16.x App Router frontend under `services/web`.
- [ ] Add responsive enterprise UI shell.
- [ ] Add demo role switcher: Manager / Technician.
- [ ] Add synthetic scenario loader.

## Phase 2 — Technician flow
- [ ] Job summary and priority.
- [ ] Navigation CTA.
- [ ] Arrival/GPS verification state.
- [ ] Asset identity and serial scan simulation.
- [ ] Dynamic checklist.
- [ ] Photo evidence capture.
- [ ] Notes and document attachment simulation.
- [ ] Evidence completeness panel.
- [ ] Human-confirmed issue classification.
- [ ] Proof-of-work.
- [ ] Customer sign-off.
- [ ] Completion / exception submission.

## Phase 3 — Manager flow
- [ ] KPI cards.
- [ ] Live job status.
- [ ] SLA-risk queue.
- [ ] Critical issue queue.
- [ ] Reinspection queue.
- [ ] Map-like operational view.
- [ ] Issue detail panel.
- [ ] Timeline / audit evidence.
- [ ] Assign / Escalate / Reinspect actions.

## Phase 4 — Backend connection
- [ ] Add generic job/inspection/evidence API contracts.
- [ ] Connect frontend demo state to FastAPI.
- [ ] Persist synthetic data in the current SQLite prototype.
- [ ] Add evidence metadata.
- [ ] Add action/audit records.

## Phase 5 — Real execution bridge
- [ ] Map a desktop job to an Android task.
- [ ] Windows Agent claims task.
- [ ] ARTEMIS executes only the approved mobile action.
- [ ] Result/evidence returns to backend.
- [ ] Dashboard verifies completion.

## Phase 6 — Pilot readiness
- [ ] Role-based authentication.
- [ ] Organisation isolation.
- [ ] Policy engine.
- [ ] Human approval gates.
- [ ] External storage.
- [ ] Audit export.
- [ ] Integration adapters.

## Definition of done for first demonstrator

A manager can create/open a synthetic technician ticket, a technician can complete the entire mobile job flow using simulated GPS and photo evidence, the system can surface an AI evidence warning and require human confirmation, and management can see the result, evidence, SLA state and next action without phoning the technician.
