# NahaLabs Field Intelligence — Trade Link Technician Demonstrator PRD

## Product thesis

NahaLabs is building a reusable field-to-action operational layer that connects office work orders to physical field execution, evidence, verification and management action.

The first demonstrator is a technician workflow inspired by the common field-service pattern: **ticket → technician → location → asset → inspection → evidence → resolution → SLA**.

This is a synthetic demo. It does not impersonate or use Trade Link branding, customer data, or proprietary systems.

## Problem

Field-service organisations often have work orders in desktop/web systems while the actual work happens at customer sites. Technicians may use paper, WhatsApp, photos or disconnected mobile forms, then return to the office before work can be reviewed, reconciled or closed.

Operational consequences:
- delayed visibility
- incomplete evidence
- duplicate administrative capture
- weak SLA control
- managers calling technicians for status
- avoidable rework and reinspection

## Demo outcome

A prospect should understand within two minutes:

> **NahaLabs turns a technician visit into verified, structured operational data without replacing the customer's existing enterprise system.**

## Primary user roles

### Technician
Receives a job, navigates to site, verifies arrival, identifies the asset, completes the checklist, captures evidence, records work performed and obtains customer confirmation.

### Supervisor
Reviews active jobs, SLA risk, evidence completeness and exceptions; assigns, escalates or requests reinspection.

### Manager
Sees operational KPIs, map-level activity, critical issues and the complete job timeline.

## Core screens

1. **Operations Dashboard** — active jobs, completed jobs, SLA risk, critical issues, reinspection queue, map and issue detail.
2. **Technician Job** — job summary, location, asset, navigation, arrival verification and checklist.
3. **Inspection / Work** — dynamic checklist, evidence capture, AI evidence check, issue classification, proof-of-work, customer sign-off and completion.

## Core entities

Organisation, Worker, Job, Location, Asset, Inspection, Evidence, Issue and Action.

## Demo workflow

1. Manager opens a synthetic service ticket.
2. Job is assigned to technician Sipho Mokoena.
3. Technician sees a HIGH-priority job for Rosebank Retail Centre / POS-1842.
4. Technician starts navigation.
5. Arrival is verified using simulated GPS.
6. Technician checks power and screen, finds network and physical-damage issues.
7. Technician captures photos and adds notes.
8. AI checks evidence completeness and identifies missing/weak evidence.
9. Human confirms issue classification.
10. Technician completes repair/replacement workflow.
11. Customer signs off.
12. SLA status changes to closed / resolved.
13. Management view updates with evidence, timeline and outcome.

## AI behaviour

AI must remain assistive, not authoritative.

### Evidence validation
- Check whether required evidence exists.
- Distinguish complete / incomplete / ambiguous.
- Ask for missing evidence.

### Issue classification
- Suggest category, severity and description.
- Show confidence.
- Require human confirmation for consequential classifications.

### Report generation
- Turn structured job data into a concise management summary.

### Missing-information detection
- Block normal completion where mandatory evidence is missing, unless the user explicitly chooses **Submit with exception**.

## Safety / trust boundaries

- No real financial transactions.
- No destructive actions.
- No external customer systems in the demo.
- Synthetic South African data only.
- AI never claims to see evidence that is not present.
- AI suggestions remain visibly different from human-confirmed facts.

## Success criteria

The demonstrator is successful when a prospect can see:

- who is doing the work
- where they are
- what asset they are servicing
- what they found
- what proof exists
- what the AI detected or checked
- what action is required
- whether the SLA is at risk
- whether the customer confirmed completion

## Technical target

- Next.js 16.x App Router frontend
- FastAPI backend already present in the repository
- Demo-first local state in the first UI milestone
- API integration behind a small service boundary
- Model/provider agnostic AI interface
- Responsive mobile technician experience
- Desktop management experience

Next.js 16.x is the current Active LTS line as of September 2026. citeturn226015search4turn226015search2
