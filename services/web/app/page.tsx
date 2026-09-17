"use client";

import { useMemo, useRef, useState } from "react";

type Role = "manager" | "technician";
type Step = "assigned" | "en_route" | "arrived" | "inspecting" | "evidence_review" | "repair" | "customer_signoff" | "completed";
type Severity = "LOW" | "MEDIUM" | "HIGH";

type ChecklistItem = {
  id: string;
  label: string;
  value: "pending" | "pass" | "issue";
};

type Evidence = {
  id: string;
  name: string;
  kind: "photo" | "document";
  createdAt: string;
  size?: number;
};

const INITIAL_CHECKLIST: ChecklistItem[] = [
  { id: "power", label: "Power connection", value: "pending" },
  { id: "screen", label: "Screen condition", value: "pending" },
  { id: "network", label: "Network connectivity", value: "pending" },
  { id: "damage", label: "Physical damage", value: "pending" },
];

const INITIAL_JOB = {
  id: "JOB-18492",
  customer: "National Retail Group",
  store: "Rosebank #184",
  asset: "POS-1842",
  problem: "Terminal offline",
  technician: "Sipho Mokoena",
  priority: "HIGH",
  slaMinutes: 118,
};

function Icon({ name }: { name: "pin" | "check" | "camera" | "alert" | "arrow" | "clock" | "shield" | "phone" | "map" | "spark" }) {
  const common = { width: 18, height: 18, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
  const paths: Record<string, React.ReactNode> = {
    pin: <><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></>,
    check: <path d="m5 12 4 4L19 6"/>,
    camera: <><path d="M4 7h4l1.5-2h5L16 7h4v12H4Z"/><circle cx="12" cy="13" r="3.5"/></>,
    alert: <><path d="M12 3 2.5 20h19L12 3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></>,
    arrow: <><path d="M5 12h13"/><path d="m13 6 6 6-6 6"/></>,
    clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
    shield: <path d="M12 3 19 6v5c0 5-3.5 8-7 10-3.5-2-7-5-7-10V6l7-3Z"/>,
    phone: <><path d="M7 3h3l1.3 4-2 1.5c.9 2 2.2 3.3 4.2 4.2L15 11l4 1v3c0 1.1-.9 2-2 2C10.4 17 7 13.6 7 7c0-1.1 0-3 0-4Z"/></>,
    map: <><path d="m9 18-6 3V6l6-3 6 3 6-3v15l-6 3-6-3Z"/><path d="M9 3v15"/><path d="M15 6v15"/></>,
    spark: <><path d="m12 3 1.3 5.7L19 10l-5.7 1.3L12 17l-1.3-5.7L5 10l5.7-1.3L12 3Z"/><path d="m19 16 .7 2.3L22 19l-2.3.7L19 22l-.7-2.3L16 19l2.3-.7L19 16Z"/></>,
  };
  return <svg {...common}>{paths[name]}</svg>;
}

function StatusPill({ children, tone = "neutral" }: { children: React.ReactNode; tone?: "neutral" | "success" | "warning" | "danger" | "blue" }) {
  return <span className={`pill pill-${tone}`}>{children}</span>;
}

function ProgressLine({ step, current }: { step: Step; current: Step }) {
  const order: Step[] = ["assigned", "en_route", "arrived", "inspecting", "evidence_review", "repair", "customer_signoff", "completed"];
  return <div className="stepper">{order.map((item, index) => {
    const currentIndex = order.indexOf(current);
    const itemIndex = order.indexOf(item);
    const done = itemIndex < currentIndex;
    const active = item === step;
    return <div className="stepper-item" key={item}><span className={`step-dot ${done ? "done" : ""} ${active ? "active" : ""}`}>{done ? <Icon name="check" /> : index + 1}</span>{index < order.length - 1 && <span className={`step-connector ${done ? "done" : ""}`} />}</div>;
  })}</div>;
}

export default function HomePage() {
  const [role, setRole] = useState<Role>("manager");
  const [step, setStep] = useState<Step>("assigned");
  const [checklist, setChecklist] = useState<ChecklistItem[]>(INITIAL_CHECKLIST);
  const [evidence, setEvidence] = useState<Evidence[]>([
    { id: "e1", name: "terminal-front.jpg", kind: "photo", createdAt: "09:51" },
    { id: "e2", name: "fault-close-up.jpg", kind: "photo", createdAt: "09:53" },
  ]);
  const [aiConfirmed, setAiConfirmed] = useState(false);
  const [customerSigned, setCustomerSigned] = useState(false);
  const [note, setNote] = useState("");
  const [slaMinutes, setSlaMinutes] = useState(INITIAL_JOB.slaMinutes);
  const fileRef = useRef<HTMLInputElement>(null);

  const issues = useMemo(() => checklist.filter((item) => item.value === "issue"), [checklist]);
  const allChecked = checklist.every((item) => item.value !== "pending");
  const missingEnvironmentPhoto = evidence.length < 3;
  const canSubmitInspection = allChecked && !missingEnvironmentPhoto;

  const setItem = (id: string, value: ChecklistItem["value"]) => {
    setChecklist((items) => items.map((item) => item.id === id ? { ...item, value } : item));
  };

  const advance = (next: Step) => {
    setStep(next);
  };

  const addEvidence = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const newEvidence: Evidence = {
      id: crypto.randomUUID(),
      name: file.name,
      kind: "photo",
      createdAt: new Date().toLocaleTimeString("en-ZA", { hour: "2-digit", minute: "2-digit" }),
      size: file.size,
    };
    setEvidence((current) => [...current, newEvidence]);
    event.target.value = "";
  };

  const runAiReview = () => {
    setAiConfirmed(false);
    advance("evidence_review");
  };

  const resetDemo = () => {
    setRole("manager");
    setStep("assigned");
    setChecklist(INITIAL_CHECKLIST);
    setEvidence([
      { id: "e1", name: "terminal-front.jpg", kind: "photo", createdAt: "09:51" },
      { id: "e2", name: "fault-close-up.jpg", kind: "photo", createdAt: "09:53" },
    ]);
    setAiConfirmed(false);
    setCustomerSigned(false);
    setNote("");
    setSlaMinutes(INITIAL_JOB.slaMinutes);
  };

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark"><Icon name="spark" /></div>
          <div>
            <div className="brand-name">NahaLabs</div>
            <div className="brand-sub">FIELD INTELLIGENCE</div>
          </div>
        </div>
        <div className="topbar-center">
          <StatusPill tone="success">● SYSTEM ONLINE</StatusPill>
          <span className="demo-label">TRADE LINK-STYLE TECHNICIAN DEMO</span>
        </div>
        <div className="topbar-actions">
          <button className={`role-toggle ${role === "manager" ? "selected" : ""}`} onClick={() => setRole("manager")}>Manager</button>
          <button className={`role-toggle ${role === "technician" ? "selected" : ""}`} onClick={() => setRole("technician")}>Technician</button>
          <button className="reset-button" onClick={resetDemo}>Reset</button>
        </div>
      </header>

      <section className="hero-strip">
        <div>
          <span className="eyebrow">FIELD → INTELLIGENCE → ACTION</span>
          <h1>Connect physical work to the systems running the business.</h1>
          <p>One operational layer for dispatch, field evidence, AI-assisted verification, exceptions and SLA closure.</p>
        </div>
        <div className="hero-metrics">
          <div><span>ACTIVE JOBS</span><strong>142</strong></div>
          <div><span>COMPLETED TODAY</span><strong>918</strong></div>
          <div><span>SLA AT RISK</span><strong className="orange">17</strong></div>
          <div><span>CRITICAL</span><strong className="red">8</strong></div>
        </div>
      </section>

      {role === "manager" ? (
        <ManagerView step={step} evidence={evidence} issues={issues.length} customerSigned={customerSigned} slaMinutes={slaMinutes} />
      ) : (
        <TechnicianView
          step={step}
          checklist={checklist}
          evidence={evidence}
          issues={issues.length}
          note={note}
          setNote={setNote}
          setItem={setItem}
          setStep={advance}
          addEvidence={addEvidence}
          fileRef={fileRef}
          runAiReview={runAiReview}
          aiConfirmed={aiConfirmed}
          setAiConfirmed={setAiConfirmed}
          customerSigned={customerSigned}
          setCustomerSigned={setCustomerSigned}
          canSubmitInspection={canSubmitInspection}
          missingEnvironmentPhoto={missingEnvironmentPhoto}
          slaMinutes={slaMinutes}
          setSlaMinutes={setSlaMinutes}
        />
      )}
    </main>
  );
}

function ManagerView({ step, evidence, issues, customerSigned, slaMinutes }: { step: Step; evidence: Evidence[]; issues: number; customerSigned: boolean; slaMinutes: number }) {
  const status = step === "completed" ? "COMPLETED" : step === "evidence_review" ? "EXCEPTION" : "IN FIELD";
  return <div className="page-grid manager-grid">
    <section className="panel map-panel">
      <div className="panel-head">
        <div><span className="eyebrow">OPERATIONS CONTROL</span><h2>Field activity</h2></div>
        <StatusPill tone={status === "EXCEPTION" ? "warning" : status === "COMPLETED" ? "success" : "blue"}>{status}</StatusPill>
      </div>
      <div className="map-canvas">
        <div className="map-grid-lines" />
        <div className="map-route route-a" />
        <div className="map-route route-b" />
        <span className="map-dot dot-a" /><span className="map-dot dot-b" /><span className="map-dot dot-c" />
        <span className="map-dot dot-d danger-dot" />
        <div className="map-card"><span className="tiny-label">HIGH PRIORITY</span><strong>JOB-18492</strong><span>Rosebank #184 · POS-1842</span></div>
        <div className="map-legend"><span><i className="legend-dot live" /> Active</span><span><i className="legend-dot warn" /> SLA risk</span><span><i className="legend-dot critical" /> Critical</span></div>
      </div>
    </section>

    <section className="panel issue-panel">
      <div className="panel-head"><div><span className="eyebrow">JOB DETAIL</span><h2>JOB-18492</h2></div><StatusPill tone={step === "completed" ? "success" : "warning"}>{status}</StatusPill></div>
      <div className="job-summary">
        <div><span>Customer</span><strong>National Retail Group</strong></div>
        <div><span>Location</span><strong>Rosebank #184</strong></div>
        <div><span>Asset</span><strong>POS-1842</strong></div>
        <div><span>Technician</span><strong>Sipho Mokoena</strong></div>
      </div>
      <div className="issue-callout">
        <div className="issue-icon"><Icon name="alert" /></div>
        <div><span className="tiny-label">DETECTED ISSUE</span><strong>{issues ? "Physical damage + network fault" : "Terminal offline"}</strong><p>{issues ? `${issues} checklist exceptions confirmed.` : "Awaiting field diagnosis."}</p></div>
      </div>
      <div className="sla-block"><div><span>SLA REMAINING</span><strong>{Math.floor(slaMinutes / 60)}h {slaMinutes % 60}m</strong></div><div className="sla-bar"><span style={{ width: `${Math.max(7, Math.min(100, (slaMinutes / 240) * 100))}%` }} /></div><small>{slaMinutes < 90 ? "At risk — intervention recommended" : "Within target"}</small></div>
      <div className="button-row"><button className="primary-button">ASSIGN</button><button className="secondary-button">ESCALATE</button><button className="secondary-button">REINSPECT</button></div>
    </section>

    <section className="panel timeline-panel">
      <div className="panel-head"><div><span className="eyebrow">AUDIT TRAIL</span><h2>What happened</h2></div><StatusPill tone="neutral">LIVE</StatusPill></div>
      <div className="timeline">
        {[
          ["09:42", "GPS arrival verified", "Location matched Rosebank #184"],
          ["09:49", "Asset identified", "POS-1842 / serial verified"],
          ["09:53", "Evidence captured", `${evidence.length} evidence files`],
          ["10:02", "AI evidence review", "Missing environment photograph flagged"],
          ["10:06", customerSigned ? "Customer sign-off" : "Awaiting customer sign-off", customerSigned ? "Completion confirmed" : "Signature required before closure"],
        ].map(([time, title, meta], index) => <div className="timeline-item" key={title}><div className={`timeline-node ${index < 4 ? "complete" : ""}`}>{index < 4 ? <Icon name="check" /> : <Icon name="clock" />}</div><div><span>{time}</span><strong>{title}</strong><p>{meta}</p></div></div>)}
      </div>
    </section>

    <section className="panel outcome-panel">
      <div className="panel-head"><div><span className="eyebrow">FIELD OUTCOME</span><h2>Proof of work</h2></div></div>
      <div className="outcome-stats"><div><span>EVIDENCE</span><strong>{evidence.length}</strong></div><div><span>GPS</span><strong className="green">VERIFIED</strong></div><div><span>CUSTOMER</span><strong className={customerSigned ? "green" : "orange"}>{customerSigned ? "SIGNED" : "PENDING"}</strong></div></div>
      <div className="report-card"><span className="tiny-label">MANAGEMENT SUMMARY</span><p>Technician inspected POS-1842 at Rosebank #184. Network fault and physical damage were observed and supported by on-site evidence. Job status is <strong>{step === "completed" ? "closed" : "in progress"}</strong>.</p><div className="report-meta"><span><Icon name="shield" /> Evidence-backed</span><span><Icon name="clock" /> SLA tracked</span></div></div>
    </section>
  </div>;
}

function TechnicianView({ step, checklist, evidence, issues, note, setNote, setItem, setStep, addEvidence, fileRef, runAiReview, aiConfirmed, setAiConfirmed, customerSigned, setCustomerSigned, canSubmitInspection, missingEnvironmentPhoto, slaMinutes, setSlaMinutes }: {
  step: Step;
  checklist: ChecklistItem[];
  evidence: Evidence[];
  issues: number;
  note: string;
  setNote: (value: string) => void;
  setItem: (id: string, value: ChecklistItem["value"]) => void;
  setStep: (step: Step) => void;
  addEvidence: (event: React.ChangeEvent<HTMLInputElement>) => void;
  fileRef: React.RefObject<HTMLInputElement | null>;
  runAiReview: () => void;
  aiConfirmed: boolean;
  setAiConfirmed: (value: boolean) => void;
  customerSigned: boolean;
  setCustomerSigned: (value: boolean) => void;
  canSubmitInspection: boolean;
  missingEnvironmentPhoto: boolean;
  slaMinutes: number;
  setSlaMinutes: (value: number) => void;
}) {
  const [cameraOpen, setCameraOpen] = useState(false);
  return <div className="page-grid tech-grid">
    <section className="panel job-card tech-job">
      <div className="mobile-topline"><StatusPill tone="success">● ONLINE</StatusPill><span>JOB #{INITIAL_JOB.id.replace("JOB-", "")}</span></div>
      <div className="job-head"><div><span className="eyebrow">PRIORITY {INITIAL_JOB.priority}</span><h2>{INITIAL_JOB.problem}</h2><p>{INITIAL_JOB.customer}</p></div><div className="priority-badge">HIGH</div></div>
      <div className="location-card"><div className="location-icon"><Icon name="pin" /></div><div><span className="tiny-label">ASSIGNED LOCATION</span><strong>{INITIAL_JOB.store}</strong><p>0.3 km · Johannesburg</p></div><button className="icon-button" aria-label="Open map"><Icon name="map" /></button></div>
      <div className="asset-row"><div><span>ASSET</span><strong>{INITIAL_JOB.asset}</strong></div><div><span>TECHNICIAN</span><strong>{INITIAL_JOB.technician}</strong></div><div><span>SLA</span><strong className="orange">{Math.floor(slaMinutes / 60)}h {slaMinutes % 60}m</strong></div></div>
      <ProgressLine step={step} current={step} />
      {step === "assigned" && <div className="cta-stack"><button className="primary-button full" onClick={() => setStep("en_route")}><Icon name="arrow" /> START JOB</button></div>}
      {step === "en_route" && <div className="cta-stack"><button className="primary-button full" onClick={() => setStep("arrived")}><Icon name="pin" /> VERIFY ARRIVAL</button><p className="helper">GPS verification is simulated for this demo.</p></div>}
      {step === "arrived" && <div className="arrival-banner"><Icon name="check" /><div><strong>GPS VERIFIED</strong><span>Rosebank #184 · 09:42</span></div><button onClick={() => setStep("inspecting")}>BEGIN INSPECTION <Icon name="arrow" /></button></div>}
    </section>

    <section className="panel work-panel">
      <div className="panel-head"><div><span className="eyebrow">INSPECTION / WORK</span><h2>POS-1842</h2></div><StatusPill tone={issues ? "warning" : "blue"}>{issues ? `${issues} ISSUES` : "DIAGNOSING"}</StatusPill></div>
      <div className="work-layout">
        <div className="checklist-card">
          <div className="subhead"><strong>DEVICE CONDITION</strong><span>{checklist.filter((x) => x.value !== "pending").length}/{checklist.length}</span></div>
          {checklist.map((item) => <div className="check-row" key={item.id}><div className={`check-state ${item.value}`}>{item.value === "pass" ? <Icon name="check" /> : item.value === "issue" ? <Icon name="alert" /> : "•"}</div><div><strong>{item.label}</strong><span>{item.value === "pass" ? "PASS" : item.value === "issue" ? "ISSUE" : "Pending"}</span></div><div className="check-actions"><button onClick={() => setItem(item.id, "pass")} className={item.value === "pass" ? "active-pass" : ""}>PASS</button><button onClick={() => setItem(item.id, "issue")} className={item.value === "issue" ? "active-issue" : ""}>ISSUE</button></div></div>)}
        </div>
        <div className="evidence-card">
          <div className="subhead"><strong>EVIDENCE</strong><span>{evidence.length} captured</span></div>
          <div className="evidence-grid">{evidence.map((item) => <div className="evidence-thumb" key={item.id}><div className="fake-photo"><div className="fake-object" /></div><span>{item.name}</span></div>)}</div>
          <input ref={fileRef} type="file" accept="image/*" capture="environment" className="hidden-input" onChange={addEvidence} />
          <div className="button-row"><button className="secondary-button" onClick={() => fileRef.current?.click()}><Icon name="camera" /> TAKE PHOTO</button><button className={`secondary-button ${cameraOpen ? "selected" : ""}`} onClick={() => setCameraOpen((v) => !v)}><Icon name="phone" /> LIVE VIEW</button></div>
          {cameraOpen && <div className="camera-sim"><div className="camera-corner top-left" /><div className="camera-corner top-right" /><div className="camera-corner bottom-left" /><div className="camera-corner bottom-right" /><span>CAMERA VIEW · DEMO</span><strong>Point the camera at the asset</strong></div>}
        </div>
      </div>
      <div className="note-area"><label htmlFor="note">FIELD NOTE</label><textarea id="note" value={note} onChange={(e) => setNote(e.target.value)} placeholder="Describe what you observed..." /></div>
      {step === "inspecting" && <div className="action-bar"><button className="secondary-button" onClick={runAiReview}><Icon name="spark" /> RUN EVIDENCE CHECK</button><button className="primary-button" disabled={!canSubmitInspection} onClick={() => setStep("repair")}>CONTINUE <Icon name="arrow" /></button></div>}
      {step === "evidence_review" && <div className="ai-review"><div className="ai-head"><div className="ai-chip"><Icon name="spark" /></div><div><span className="eyebrow">AI EVIDENCE CHECK</span><strong>Pre-submission quality control</strong></div></div><div className="ai-items"><div className="ai-item good"><Icon name="check" /><span>Required front view</span><strong>PASS</strong></div><div className="ai-item good"><Icon name="check" /><span>Fault close-up</span><strong>PASS</strong></div><div className={`ai-item ${missingEnvironmentPhoto ? "warn" : "good"}`}><Icon name={missingEnvironmentPhoto ? "alert" : "check"} /><span>Environment photograph</span><strong>{missingEnvironmentPhoto ? "MISSING" : "PASS"}</strong></div></div>{missingEnvironmentPhoto && <p className="ai-explain">One additional environment photograph is required to show the fault in context. Capture it before closure.</p>}<div className="action-bar"><button className="secondary-button" onClick={() => { setAiConfirmed(true); if (missingEnvironmentPhoto) fileRef.current?.click(); }}><Icon name="camera" /> {missingEnvironmentPhoto ? "ADD MISSING PHOTO" : "CONFIRM EVIDENCE"}</button><button className="primary-button" disabled={!aiConfirmed && missingEnvironmentPhoto} onClick={() => setStep("repair")}>PROCEED <Icon name="arrow" /></button></div></div>}
      {step === "repair" && <div className="repair-card"><div><span className="eyebrow">WORK COMPLETED</span><h3>Terminal restored and network tested.</h3><p>Record the final proof-of-work, then request customer confirmation.</p></div><div className="button-row"><button className="secondary-button" onClick={() => { setSlaMinutes(Math.max(38, slaMinutes - 6)); setStep("customer_signoff"); }}>CAPTURE PROOF</button><button className="primary-button" onClick={() => setStep("customer_signoff")}>REQUEST SIGN-OFF <Icon name="arrow" /></button></div></div>}
      {step === "customer_signoff" && <div className="signoff-card"><div className="signoff-icon"><Icon name="shield" /></div><div><span className="eyebrow">CUSTOMER CONFIRMATION</span><h3>{customerSigned ? "Customer sign-off captured" : "Get customer sign-off"}</h3><p>{customerSigned ? "Completion confirmed. The job can now be closed." : "Customer confirms the technician completed the work described."}</p></div><button className="primary-button" onClick={() => { setCustomerSigned(true); setSlaMinutes(Math.max(0, slaMinutes - 12)); setStep("completed"); }}>{customerSigned ? "CLOSE JOB" : "CAPTURE SIGNATURE"}</button></div>}
      {step === "completed" && <div className="complete-card"><div className="complete-icon"><Icon name="check" /></div><div><span className="eyebrow">JOB COMPLETE</span><h3>JOB-18492 closed</h3><p>Evidence, technician notes, customer confirmation and SLA outcome have been recorded.</p></div><div className="complete-facts"><span><Icon name="pin" /> GPS verified</span><span><Icon name="camera" /> {evidence.length} evidence files</span><span><Icon name="shield" /> customer signed</span></div></div>}
    </section>
  </div>;
}
