# NahaLabs Field Intelligence Demo

Trade Link-style technician workflow demonstrator.

## What it demonstrates

`ticket → technician → location → asset → checklist → evidence → AI quality check → repair → customer sign-off → SLA closure`

The current frontend uses synthetic demo state intentionally. It does not claim real GPS verification, real AI vision analysis or a live customer-system integration.

## Run locally

Requirements:
- Node.js 20.9+
- npm

```powershell
cd services/web
npm install
npm run dev
```

Open `http://localhost:3000`.

## Demo script

1. Open as **Manager**.
2. Review the active-job dashboard.
3. Switch to **Technician**.
4. Click **Start Job**.
5. Click **Verify Arrival**.
6. Begin inspection.
7. Mark Power and Screen as **PASS**.
8. Mark Network and Physical damage as **ISSUE**.
9. Capture a third evidence photo using the browser file/camera control.
10. Run **AI Evidence Check**.
11. Review the missing-evidence warning and add the environment photo when required.
12. Continue to repair.
13. Capture proof and request customer sign-off.
14. Capture the signature.
15. Switch back to **Manager** and inspect the timeline, SLA and proof-of-work.

## Architecture boundary

The page is deliberately isolated from model/provider and enterprise-system details.

Future integration points:
- `FastAPI job API`
- `NahaLabs policy / workflow service`
- `Gemini or other multimodal provider`
- `Supabase/Postgres`
- `object storage`
- `ARTEMIS / Windows Agent`
- customer ERP / CRM / ticketing adapters
