/* global React */

const { useState, useEffect, useRef } = React;

const D = window.RAG_DATA;

/* ---------- helpers ---------- */
const pct = (x) => `${Math.round(x * 100)}%`;
const sevById = (id) => D.severityClasses.find((c) => c.id === id);
const sevColor = (id) => `var(--sev-${id})`;
const sevTint = (id) => `var(--sev-${id}-tint)`;

/* ---------- Header / banners / footer ---------- */
function Header({ state }) {
  return (
    <header className="header">
      <div className="header-brand">
        <div className="header-mark">H&amp;C</div>
        <div>
          <div className="header-title">Incident Triage Console</div>
          <div className="header-sub">{D.meta.pipelineVersion} · phase 1</div>
        </div>
      </div>
      <div className="header-meta">
        <span><span className="dot"></span>pipeline online</span>
        <span>analyst · {D.meta.analyst}</span>
        <span>{state === "input" ? "draft" : D.meta.incidentRef}</span>
      </div>
    </header>
  );
}

function DomainBanner() {
  return (
    <div className="domain-banner">
      <span className="domain-banner-tag">DOMAIN · H&amp;C</span>
      <span className="domain-banner-text">
        This console is restricted to Health &amp; Social Care incident narratives. Domain confirmation is recorded at the input form before downstream tools run.
      </span>
    </div>
  );
}

function Footer() {
  return (
    <footer className="footer">
      <span>{D.meta.modelStack}</span>
      <span>phase 1 — display only · human confirmation gates deferred</span>
    </footer>
  );
}

/* ---------- Sections ---------- */
const SECTIONS = [
  { id: "t1", code: "T1", label: "Severity prediction" },
  { id: "t2", code: "T2", label: "RIDDOR mapping" },
  { id: "t3", code: "T3", label: "Causes & mitigation" },
  { id: "t4", code: "T4", label: "Population patterns" },
  { id: "rp", code: "RP", label: "Report" },
];

const TOOL_STEPS = [
  { code: "T1", label: "predict_severity" },
  { code: "T2", label: "map_riddor" },
  { code: "T3", label: "analyse_causes" },
  { code: "T4", label: "find_patterns" },
];

function ProgressRail({ activeId }) {
  const activeIdx = SECTIONS.findIndex((s) => s.id === activeId);
  return (
    <aside className="rail">
      <div className="rail-title">Sections</div>
      <ul className="rail-list">
        {SECTIONS.map((s, i) => (
          <li key={s.id}>
            <button
              className={
                "rail-item" +
                (s.id === activeId ? " active" : "") +
                (i < activeIdx ? " passed" : "")
              }
              onClick={() => {
                const el = document.getElementById(s.id);
                if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
              }}
            >
              <span className="rail-item-code">{s.code}</span>
              <span className="rail-item-label">{s.label}</span>
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}

function Section({ id, code, title, desc, children }) {
  return (
    <section id={id} className="section" data-screen-label={`${code} ${title}`}>
      <div className="section-head">
        <span className="section-code">{code}</span>
        <h2 className="section-title">{title}</h2>
      </div>
      {desc && <p className="section-desc">{desc}</p>}
      {children}
    </section>
  );
}

/* ---------- State 1: Input ---------- */
function InputState({ narrative, setNarrative, confirmed, setConfirmed, onRun, running, runStep }) {
  return (
    <div className="content" style={{ paddingTop: 56 }}>
      <div style={{ marginBottom: 28 }}>
        <div style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--ink-4)", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 8 }}>
          New incident · phase 1
        </div>
        <h1 style={{ fontSize: 28, fontWeight: 600, letterSpacing: "-0.025em", margin: "0 0 8px" }}>
          Triage a Health &amp; Social Care incident
        </h1>
        <p style={{ color: "var(--ink-3)", margin: 0, maxWidth: "60ch" }}>
          Paste or edit the raw incident narrative below. The pipeline runs four tools — severity prediction, RIDDOR mapping, cause analysis, and population patterns — and produces a single report.
        </p>
      </div>

      <div className="input-card">
        <label className="input-label" htmlFor="narrative">Narrative</label>
        <p className="input-help">Free-text description as captured by the reporter. Include people involved, setting, equipment, sequence of events, outcome, and any escalation.</p>
        <textarea
          id="narrative"
          className="input-textarea"
          value={narrative}
          onChange={(e) => setNarrative(e.target.value)}
          spellCheck={false}
        />

        <label className="input-checkbox">
          <input
            type="checkbox"
            checked={confirmed}
            onChange={(e) => setConfirmed(e.target.checked)}
          />
          <span className="input-checkbox-text">
            <strong>Confirm domain.</strong> I confirm this narrative concerns a Health &amp; Social Care incident and that all personal identifiers are pseudonymised in line with the local DPIA.
          </span>
        </label>

        <div className="input-actions">
          <span className="input-meta">
            {narrative.trim().split(/\s+/).filter(Boolean).length} words · {narrative.length} chars
          </span>
          <div style={{ display: "flex", gap: 8 }}>
            <button className="btn btn-ghost" onClick={() => setNarrative("")} disabled={running}>Clear</button>
            <button
              className="btn btn-primary"
              onClick={onRun}
              disabled={!confirmed || !narrative.trim() || running}
            >
              {running ? "Running…" : "Run triage analysis →"}
            </button>
          </div>
        </div>

        {running && (
          <div className="run-progress" style={{ marginTop: 24, padding: 0, border: 0 }}>
            <div className="run-progress-title">
              <span className="spinner"></span>
              Running pipeline
            </div>
            {TOOL_STEPS.map((s, i) => {
              const status = i < runStep ? "done" : i === runStep ? "active" : "";
              return (
                <div key={s.code} className={`run-step ${status}`}>
                  <div className="run-step-status"></div>
                  <div className="run-step-code">{s.code}</div>
                  <div className="run-step-label">{s.label}</div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

/* ---------- State 2: Results ---------- */
function ResultsState({ narrative, onReset }) {
  const [activeId, setActiveId] = useState("t1");

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]) setActiveId(visible[0].target.id);
      },
      {
        rootMargin: "-92px 0px -55% 0px",
        threshold: [0, 0.1, 0.5, 1],
      }
    );
    SECTIONS.forEach((s) => {
      const el = document.getElementById(s.id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, []);

  return (
    <div className="main">
      <ProgressRail activeId={activeId} />
      <div className="content">
        <InputSummary narrative={narrative} onReset={onReset} />
        <T1 />
        <T2 />
        <T3 />
        <T4 />
        <RP />
      </div>
      <aside className="meta-gutter">
        <MetaGutter activeId={activeId} />
      </aside>
    </div>
  );
}

function InputSummary({ narrative, onReset }) {
  return (
    <div className="input-summary">
      <div className="input-summary-text">{narrative}</div>
      <div className="input-summary-meta" style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
        <span>{narrative.split(/\s+/).filter(Boolean).length} words · domain confirmed</span>
        <button className="btn btn-ghost" onClick={onReset} style={{ padding: "4px 10px", fontSize: 12 }}>Edit narrative</button>
      </div>
    </div>
  );
}

function MetaGutter({ activeId }) {
  const map = {
    t1: { tool: "predict_severity", lat: "240 ms", model: "stuSterfc/ohs-severity-classifier (DistilBERT)" },
    t2: { tool: "map_riddor", lat: "60 ms", model: "rules + LLM extractor" },
    t3: { tool: "analyse_causes", lat: "420 ms", model: "vector + reranker (HSG220)" },
    t4: { tool: "find_patterns", lat: "310 ms", model: "k-NN over MiniLM-L6" },
    rp: { tool: "report-builder", lat: "—", model: "—" },
  };
  const m = map[activeId];
  return (
    <div>
      <div style={{ textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 8 }}>Active tool</div>
      <div style={{ color: "var(--ink-2)", fontSize: 12, marginBottom: 14 }}>{m.tool}</div>
      <div style={{ textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 6 }}>Model</div>
      <div style={{ color: "var(--ink-2)", fontSize: 12, marginBottom: 14 }}>{m.model}</div>
      <div style={{ textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 6 }}>Latency</div>
      <div style={{ color: "var(--ink-2)", fontSize: 12, marginBottom: 24 }}>{m.lat}</div>
      <div style={{ paddingTop: 14, borderTop: "1px solid var(--line)", fontSize: 10, lineHeight: 1.6 }}>
        Phase 1 is display-only. Human confirmation gates between tools are deferred to Phase 2.
      </div>
    </div>
  );
}

/* ---------- T1: predict_severity ---------- */
function T1() {
  const t = D.t1_predict_severity;
  const pred = sevById(t.predicted_class);

  return (
    <Section id="t1" code="T1" title="Severity prediction" desc="Five-class probability distribution over the C0–C4 lost-time taxonomy. Predicted class shown in bold; boundary-class cases are flagged for human review.">
      <div className="sev-row" style={{ borderColor: sevColor(t.predicted_class), background: sevTint(t.predicted_class) }}>
        <div className="sev-row-class" style={{ color: sevColor(t.predicted_class) }}>{pred.label}</div>
        <div className="sev-row-meta">
          <div className="sev-row-name">{pred.name} <span style={{ color: "var(--ink-4)", fontWeight: 400 }}>· {pred.band}</span></div>
          <div className="sev-row-conf">predicted · confidence {pct(t.confidence)}</div>
        </div>
        <div className="sev-row-tag" style={{ background: sevColor(t.predicted_class), color: "white" }}>
          predicted
        </div>
      </div>

      {t.needlestick_flag && (
        <div className="alert alert-danger">
          <div className="alert-icon">!</div>
          <div>
            <div className="alert-title">Needlestick / sharps exposure detected</div>
            <p className="alert-body">
              Trigger the immediate sharps-injury protocol: source-patient bloods, exposed-staff baseline bloods, and occupational health referral within 1 hour. Reportable as an incident regardless of severity prediction.
            </p>
          </div>
        </div>
      )}

      {t.middle_severity_flag && (
        <div className="alert alert-warn">
          <div className="alert-icon">⚠</div>
          <div>
            <div className="alert-title">Boundary class — human review recommended</div>
            <p className="alert-body">
              The predicted class falls in the C2–C4 band, where misclassification has reporting consequences (RIDDOR over-7-day vs. specified injury). A senior reviewer should confirm the lost-time band before any external notification.
            </p>
          </div>
        </div>
      )}

      <div className="card">
        <div className="card-title">
          <span>Class probabilities</span>
          <span className="card-title-sub">5-class softmax · C0 → C4</span>
        </div>
        {D.severityClasses.map((c) => {
          const p = t.probabilities[c.label] ?? 0;
          const isPred = c.id === t.predicted_class;
          return (
            <div key={c.label} className={"prob-row" + (isPred ? " predicted" : "")}>
              <div className="prob-row-label">
                <span className="index">{c.label}</span>
                <span>{c.name} <span style={{ color: "var(--ink-4)", fontWeight: 400, fontSize: 12 }}>· {c.band}</span></span>
              </div>
              <div className="prob-bar">
                <div
                  className="prob-bar-fill"
                  style={{
                    width: pct(p),
                    background: isPred ? sevColor(c.id) : sevTint(c.id),
                  }}
                ></div>
              </div>
              <div className="prob-row-value">{(p * 100).toFixed(1)}%</div>
            </div>
          );
        })}
      </div>

    </Section>
  );
}

/* ---------- T2: map_riddor ---------- */
function T2() {
  const t = D.t2_map_riddor;
  return (
    <Section id="t2" code="T2" title="RIDDOR mapping" desc="Rule-based RIDDOR 2013 mapping. Each candidate category names what's still needed to confirm or rule out, and the corresponding reporting deadline.">
      <div className={`riddor-banner ${t.overall_status}`}>
        <div>
          <div className="riddor-banner-status">{t.headline}</div>
          <div className="riddor-banner-rule">{t.statute}</div>
        </div>
        <span className="badge" style={{
          background: "white",
          borderColor: "rgba(0,0,0,0.08)",
          color: "var(--ink)",
          textTransform: "uppercase",
          letterSpacing: "0.06em",
        }}>{t.overall_status}</span>
      </div>

      <div className="card">
        <div className="card-title">
          <span>Candidate categories</span>
          <span className="card-title-sub">{t.categories.length} under consideration</span>
        </div>

        <div className="riddor-cat-list">
          {t.categories.map((c, i) => (
            <div key={i} className="riddor-cat">
              <h4 className="riddor-cat-name">{c.category}</h4>
              <p className="riddor-cat-desc">{c.description}</p>

              <div className="riddor-cat-needed">
                <div className="riddor-cat-needed-title">Information needed</div>
                <ul className="riddor-cat-needed-list">
                  {c.information_needed.map((info, j) => <li key={j}>{info}</li>)}
                </ul>
              </div>

              <div className="riddor-cat-deadline">
                <span className="riddor-cat-deadline-label">Deadline</span>
                <span>{c.reporting_deadline}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="card-title">
          <span>Follow-up questions</span>
          <span className="card-title-sub">advisory-level</span>
        </div>
        <div className="riddor-followup" style={{ background: "var(--surface-2)", border: "1px dashed var(--line-strong)" }}>
          <ul className="riddor-followup-list">
            {t.follow_up_questions.map((q, i) => (
              <li key={i}>
                <span className="num">Q{String(i + 1).padStart(2, "0")}</span>
                <span>{q}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Section>
  );
}

/* ---------- T3: analyse_causes ---------- */
function T3() {
  const t = D.t3_analyse_causes;
  return (
    <Section id="t3" code="T3" title="Contributing causes & mitigation directions" desc="Causal factors lifted from the narrative, each linked to an HSG220 (or related statutory) section and a list of mitigation actions.">
      <div className="card">
        <div className="card-title">
          <span>Causal factors → mitigations</span>
          <span className="card-title-sub">{t.factors.length} factors · HSG220-aligned</span>
        </div>
        <div className="mitigation">
          {t.factors.map((f, i) => (
            <div key={i} className="mit-item">
              <div className="mit-num">{String(i + 1).padStart(2, "0")}</div>
              <div className="mit-body">
                <div className="mit-cause">{f.cause_type}</div>
                <div className="mit-action">{f.description}</div>
                <div className="mit-ref">{f.hsg220_section}</div>
                <ul className="mit-actions-list">
                  {f.mitigation_actions.map((a, j) => <li key={j}>{a}</li>)}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
}

/* ---------- T4: find_patterns ---------- */
function DistChart({ dist }) {
  // dist is { "C0": 0.04, ... }
  const entries = D.severityClasses.map((c) => ({
    cls: c,
    value: dist[c.label] ?? 0,
  }));
  const max = Math.max(...entries.map((e) => e.value));
  return (
    <div className="dist-chart">
      {entries.map((e) => (
        <div key={e.cls.label} className={"dist-bar" + (e.value === max ? " highlight" : "")}>
          <div
            className="dist-bar-fill"
            style={{
              height: max > 0 ? `${(e.value / max) * 100}%` : "0%",
              background: e.value === max ? sevColor(e.cls.id) : sevTint(e.cls.id),
            }}
          ></div>
          <div className="dist-bar-value">{Math.round(e.value * 100)}%</div>
          <div className="dist-bar-label">{e.cls.label}</div>
        </div>
      ))}
    </div>
  );
}

function T4() {
  const t = D.t4_find_patterns;
  return (
    <Section id="t4" code="T4" title="Population-level pattern analysis" desc={`Compared against ${t.cohort_size.toLocaleString()} prior incidents. Top neighbours and the cohort severity distribution for the identified injury mechanism are shown.`}>
      <div className="card">
        <div className="card-title">
          <span>Injury mechanism</span>
          <span className="card-title-sub">classifier output</span>
        </div>
        <dl className="kv-grid">
          <dt>Mechanism</dt>
          <dd>{t.injury_mechanism}</dd>
          <dt>Cohort size</dt>
          <dd>{t.cohort_size.toLocaleString()} incidents</dd>
        </dl>
      </div>

      <div className="card">
        <div className="card-title">
          <span>Most similar incidents</span>
          <span className="card-title-sub">k-NN · MiniLM-L6 embedding</span>
        </div>
        {t.similar_incidents.map((s) => {
          const sev = sevById(s.severity_outcome);
          return (
            <div key={s.id} className="incident" style={{ gridTemplateColumns: "100px 1fr 110px" }}>
              <span className="incident-id">{s.id}</span>
              <span className="incident-summary">{s.narrative_excerpt}</span>
              <span className="incident-sev">
                <span className={`badge badge-sev-${sev.id}`}>{sev.label} · {sev.name}</span>
              </span>
            </div>
          );
        })}
      </div>

      <div className="card">
        <div className="card-title">
          <span>Severity distribution for this mechanism</span>
          <span className="card-title-sub">cohort split across C0–C4</span>
        </div>
        <DistChart dist={t.severity_distribution} />
      </div>
    </Section>
  );
}

/* ---------- RP ---------- */
function RP() {
  const m = D.meta;
  const fmt = (iso) => {
    const d = new Date(iso);
    return d.toLocaleString("en-GB", { dateStyle: "medium", timeStyle: "short" });
  };
  return (
    <Section id="rp" code="RP" title="Report" desc="Final report metadata and exports. Phase 1 produces a static bundle; Phase 2 will gate on human confirmation between tools.">
      <div className="report-header">
        <div className="report-header-grid">
          <div>
            <div className="report-field-label">Incident reference</div>
            <div className="report-field-value mono">{m.incidentRef}</div>
          </div>
          <div>
            <div className="report-field-label">Submitted</div>
            <div className="report-field-value mono">{fmt(m.submittedAt)}</div>
          </div>
          <div>
            <div className="report-field-label">Analyst</div>
            <div className="report-field-value">{m.analyst}</div>
            <div style={{ fontSize: 12, color: "rgba(255,255,255,0.6)", marginTop: 2 }}>{m.analystRole}</div>
          </div>
          <div>
            <div className="report-field-label">Pipeline</div>
            <div className="report-field-value mono">{m.pipelineVersion}</div>
            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.55)", marginTop: 2 }}>{m.modelStack}</div>
          </div>
        </div>
        <div className="report-actions">
          <button className="btn btn-onDark">Export PDF</button>
          <button className="btn btn-onDark">Export JSON</button>
          <button className="btn btn-onDark">Send to incident log</button>
          <button className="btn btn-onDark">Print</button>
        </div>
      </div>
    </Section>
  );
}

/* ---------- App root ---------- */
function App({ tweaks, initialState = "input" }) {
  const [state, setState] = useState(initialState);
  const [narrative, setNarrative] = useState(D.narrative);
  const [confirmed, setConfirmed] = useState(true);
  const [running, setRunning] = useState(false);
  const [runStep, setRunStep] = useState(0);

  useEffect(() => {
    const root = document.documentElement;
    if (tweaks) {
      root.style.setProperty("--accent", tweaks.accent);
      root.style.setProperty("--bg", tweaks.bg);
      root.style.fontSize = tweaks.density === "compact" ? "13px" : tweaks.density === "comfortable" ? "15px" : "14px";
    }
  }, [tweaks]);

  const handleRun = () => {
    // Skip the simulated pipeline entirely — go straight to results.
    setState("results");
    window.scrollTo({ top: 0 });
  };

  const handleReset = () => {
    setState("input");
    setRunStep(0);
    window.scrollTo({ top: 0 });
  };

  return (
    <div className="app">
      <Header state={state} />
      <DomainBanner />
      {state === "input" ? (
        <main className="main" style={{ gridTemplateColumns: "1fr" }}>
          <div style={{ maxWidth: 760, margin: "0 auto", width: "100%", padding: "0 24px" }}>
            <InputState
              narrative={narrative}
              setNarrative={setNarrative}
              confirmed={confirmed}
              setConfirmed={setConfirmed}
              onRun={handleRun}
              running={running}
              runStep={runStep}
            />
          </div>
        </main>
      ) : (
        <ResultsState narrative={narrative} onReset={handleReset} />
      )}
      <Footer />
    </div>
  );
}

window.App = App;

/* ---------- bootstrap ---------- */
const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "accent": "#2d3a8c",
  "bg": "#f6f6f3",
  "density": "default"
}/*EDITMODE-END*/;

function Root() {
  const [tweaks, setTweak] = useTweaks(TWEAK_DEFAULTS);
  return (
    <React.Fragment>
      <App tweaks={tweaks} />
      <TweaksPanel title="Tweaks">
        <TweakSection label="Theme">
          <TweakColor label="Accent" value={tweaks.accent} onChange={(v) => setTweak("accent", v)} />
          <TweakColor label="Background" value={tweaks.bg} onChange={(v) => setTweak("bg", v)} />
        </TweakSection>
        <TweakSection label="Density">
          <TweakRadio
            label="Type scale"
            value={tweaks.density}
            options={[
              { value: "compact", label: "Compact" },
              { value: "default", label: "Default" },
              { value: "comfortable", label: "Comfy" },
            ]}
            onChange={(v) => setTweak("density", v)}
          />
        </TweakSection>
      </TweaksPanel>
    </React.Fragment>
  );
}

function mount() {
  const el = document.getElementById("root");
  if (!el) { setTimeout(mount, 50); return; }
  ReactDOM.createRoot(el).render(<Root />);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", mount);
} else {
  mount();
}
