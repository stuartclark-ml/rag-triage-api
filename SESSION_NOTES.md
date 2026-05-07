# SESSION NOTES — Session 19
**Date:** 2026-05-07
**Branch:** feature/hitl-stepper
**Focus:** HITL stepper frontend — build, test, commit, push

---

## What was completed this session

### 1. Backend — /analyse-causes-amended endpoint
- Already committed at session start (carried over from Session 18 planning)
- Confirmed working via smoke test

### 2. vercel.json — endpoint path fixes
- Already committed at session start
- All six endpoints confirmed with hyphenated paths

### 3. stepper.html — complete HITL step-by-step frontend
Built and committed `vercel-frontend/stepper.html`. Full five-step analyst workflow:

**Step 1 — T1 Severity prediction**
- Displays probability distribution across all five classes
- Analyst severity override dropdown — pre-selected to model prediction
- Override feeds as `predicted_incapacitation` into /map-riddor
- Needlestick and boundary class alert banners

**Step 2 — Facts review**
- Four editable fields: injury_type, persons_involved, circumstances, known_severity
- persons_involved normalised from list to string on load
- Analyst corrections feed directly into /map-riddor body

**Step 3 — T2 RIDDOR advisory**
- Category checkboxes — analyst unchecks ruled-out categories
- Follow-up question answer fields (free text, recorded in final report)
- Ruled-out categories shown in final report with badge-ruled-out badge

**Step 4 — T3 Causal analysis**
- Remove buttons on each identified cause
- Add-cause form (cause_type dropdown + description input)
- If causes amended: amber "Rerun with amended causes" button POSTs to /analyse-causes-amended
- Rerun result shown in t3_rerun_review view (readonly, no further amendment)
- analyst-added cause descriptions tracked in analystAddedDescs Set for badge display

**Step 5 — T4 Pattern analysis**
- Cohort distribution and similar incidents (read-only)
- Analyst observations textarea — optional free text, appears in final report

**Complete view**
- Full assembled report with amendment badges throughout:
  - badge-override — severity class overridden by analyst
  - badge-amended — facts field amended
  - badge-analyst — cause added by analyst
  - badge-ruled-out — RIDDOR category ruled out
- Nav rail with scroll-to links
- Read-only — all fields locked

**ConfirmPanel**
- Fixed to viewport bottom (position: fixed)
- Primary confirm button + optional amber rerun button
- Page content has paddingBottom: 120px to prevent overlap

**State machine views:**
input → t1_loading → t1_review → facts_loading → facts_review → t2_loading → t2_review → t3_loading → t3_review → [t3_rerun_loading → t3_rerun_review] → t4_loading → t4_review → complete / error

**Key implementation notes:**
- `resolveClassId()` handles Pydantic enum serialising as `{value: N}` or plain integer
- `API_URL = ""` set before commit for Vercel proxy compatibility
- T3 rerun: `/analyse-causes-amended` skips extract_causes LLM call, runs HSG220 retrieval directly on provided cause list
- Error view has per-step retry buttons — retries the exact failed step

### 4. README — RIDDOR single-pass limitation documented
**Known limitation added:** Follow-up question answers are recorded but do not trigger a RIDDOR rerun. Future improvement: "Rerun RIDDOR with answers" step (same pattern as T3 rerun) where confirmed answers are passed into Gemini context to sharpen conditional categories into confirmed obligations. Current design is intentionally conservative — follow-up questions prompt analyst to pursue information; competent person makes final determination.

### 5. Git commits this session
```
fix(frontend): set API_URL to empty string for Vercel proxy
docs: add HITL RIDDOR limitation to README; feat(frontend): add stepper.html HITL stepper
feat(api): add /analyse-causes-amended endpoint for HITL cause rerun  [carried from S18]
```

### 6. Local smoke test
- Full pipeline tested locally against uvicorn dev server
- All five steps confirmed working
- Complete view renders with amendment badges

---

## What was NOT done (deferred)

- ECS Docker rebuild and redeploy — deferred. Original deployment running smoothly, backend working. Redeploy is low-risk and can be done in a single session when needed.
- Vercel frontend deploy — deferred pending ECS redeploy (IP may have changed on task restart)
- index.html redirect update (app.html → stepper.html) — deferred
- PR raise and merge — deferred
- LinkedIn post publish — deferred

---

## Repository state at session end
- Branch: feature/hitl-stepper — pushed to origin
- PR URL: https://github.com/stuartclark-ml/rag-triage-api/pull/new/feature/hitl-stepper
- ECS IP (last known): 13.212.184.68 — verify before redeploying (changes on task restart)
- Live Vercel URL: https://rag-triage.vercel.app (serving app.html — stepper not yet deployed)

---

## Next session checklist (when returning to this project)
1. Verify ECS task is still running and IP is unchanged
2. Rebuild Docker image with StaticFiles mount confirmed in main.py
3. Push image to ECR
4. Redeploy ECS task
5. Update vercel.json ECS IP if changed
6. Deploy to Vercel
7. Update index.html redirect to stepper.html
8. Raise PR — CI green — merge to main
9. Publish LinkedIn post

---

## Project 3
Moved to a separate Claude Project. Do not mix Project 3 context into this project's sessions.

## Session 18 — 2026-05-06
Session goal: Fix HF_TOKEN issue, resolve ECS crash loop, deploy Vercel frontend, finalise LinkedIn post.

Completed this session:

HF_TOKEN warning diagnosed — root cause was variable name mismatch. ECS task definition had HUGGINGFACE_API_TOKEN but the huggingface_hub library reads HF_TOKEN specifically. Fixed by adding HF_TOKEN as a second environment variable in the task definition pointing to the same Secrets Manager ARN
Pydantic crash loop — caused by accidentally deleting HUGGINGFACE_API_TOKEN when adding HF_TOKEN. ECS task crash-looped across multiple task IDs. Fixed by restoring both environment variables in a new task definition revision. Clean startup confirmed in CloudWatch logs
ECS IP changed — from 54.169.243.25 to 13.212.184.68. vercel.json updated accordingly
Vercel account connected to stuartclark-ml GitHub organisation — required installing the Vercel GitHub App on the organisation separately from the personal account
vercel-frontend/ folder added to repo containing three files: index.html, app.html, vercel.json
vercel.json proxy rewrites configured for six endpoints: /health, /triage, /predict_severity, /map_riddor, /analyse_causes, /find_patterns — all proxied to ECS. Proxy is server-side so browser never touches HTTP directly, resolving the mixed content problem
Status/fallback page (index.html) built — on load runs health check against /health, auto-redirects to /app.html after 500ms if ECS is online, shows offline panel with reasons and LinkedIn contact button if ECS is unreachable
app.html — existing triage frontend HTML deployed to Vercel unchanged. API_URL = "" means all fetch calls are relative paths, intercepted and proxied by Vercel
Vercel deployment live at https://rag-triage.vercel.app
Auto-redirect confirmed working — status page checks health, forwards to app automatically
LinkedIn post finalised — evidence-based opener (HSE 30% RIDDOR miscoding statistic), 3 hashtags, corrected stack (LangGraph removed, sequential pipeline documented), URL updated to Vercel

Open items for next session:

HITL stepper frontend — calls individual endpoints sequentially with confirmation between each step (backend already complete, proxy rewrites already configured)
SHAP offline notebook in shap_analysis/ — genuine v2 addition
Transient 500 errors observed on Vercel — caused by intermittent failures in external dependencies (Gemini API, HuggingFace Inference). Not systemic but worth documenting in README as known limitation
LinkedIn post — publish and begin network expansion into operational risk and insurance verticals

Key decisions made this session:

Both HUGGINGFACE_API_TOKEN and HF_TOKEN must exist in ECS task definition — former for Pydantic Settings, latter for huggingface_hub library
Vercel proxy rewrite timeout for rewrites is 120 seconds — not subject to the 10 second serverless function limit
vercel-frontend/ kept as a subfolder in the existing repo — Vercel Root Directory set to vercel-frontend/ in project config
Status page auto-redirects rather than requiring manual button click — better user experience from LinkedIn
vercel.json proxy routes include all individual tool endpoints for future HITL stepper, not just /triage
ECS HTML and Vercel HTML are separate — ECS continues to serve the original frontend at /ui, Vercel serves app.html independently

Live endpoints:

Vercel frontend: https://rag-triage.vercel.app
ECS API health: http://13.212.184.68:8000/health
ECS frontend (backup): http://13.212.184.68:8000/ui
Note: ECS public IP changes on every task restart — update vercel.json when this happens

## Session 17 — 2026-05-05

**Session goal:** README, mobile frontend fix, session housekeeping.

**Completed this session:**
- Confirmed docs/session-notes-s16 PR merged to main
- README written from scratch — accurate architecture, honest limitations, AWS deployment documented
- README corrected after code review — LangGraph removed (never implemented), plain sequential pipeline documented, individual endpoints table added, sev-hero flags panel documented
- Interview prep MD updated — all unanswered Pydantic, API Design, Architecture, and SHAP questions answered; AWS Deployment section added (14 questions)
- Mobile responsive layout — media queries added for max-width 640px covering: layout collapse, nav rail hidden, header meta hidden, sev-hero vertical stack, prob/dist row label columns reduced, RIDDOR deadline stacked, modal padding reduced, footer stacked
- sev-hero flags panel inline style converted to CSS class to allow media query targeting
- New triage button added to bottom of ResultsView for mobile users without nav rail
- Docker image rebuilt and pushed to ECR as :v4
- ECS task definition updated, force new deployment
- Live IP updated: 54.169.243.25
- Frontend confirmed working on mobile
- SHAP reference removed from README — shap_analysis/ directory does not exist
- HITL discussion — individual endpoints already exist as backend building blocks; decided to post LinkedIn now and add HITL stepper frontend as v2

**Open items for next session:**
- LinkedIn post
- HITL stepper frontend — calls individual endpoints sequentially with confirmation between each step (backend already complete)
- SHAP offline notebook in shap_analysis/ — genuine v2 addition
- HF_TOKEN warning in logs — unauthenticated HuggingFace requests

**Key decisions made this session:**
- LangGraph was never implemented — sequential pipeline is four direct function calls in main.py
- HITL deferred to v2 — project is deployable and differentiated now; post LinkedIn first
- :latest is an anti-pattern in ECS — explicit version tags enforced

**Live endpoint:**
- API health: http://54.169.243.25:8000/health
- Frontend: http://54.169.243.25:8000/ui
- Note: public IP changes on every ECS task restart

## Session 16 — 2026-05-05

**Session goal:** Complete AWS deployment — add StaticFiles mount, rebuild and push Docker image, deploy frontend via ECS Fargate.

**Completed this session:**
- Added StaticFiles import and mount to main.py — frontend now served at /ui
- Diagnosed ECS caching issue — task definition was pinned to old image digest, not a tag
- Switched image tagging strategy from :latest to explicit version tags (:v2, :v3)
- Fixed hardcoded localhost:8000 API URL in frontend/index.html — replaced with relative URL
- Rebuilt and pushed :v2 (StaticFiles fix) and :v3 (relative URL fix) to ECR
- Created task definition revisions :4 and :5 in ECS console
- Frontend live and pipeline confirmed working end-to-end on AWS
- feature/aws-deployment merged to main

**Open items for next session:**
- Mobile responsiveness — modal too large on phone screens, main screen scrolls accidentally
- README update — document AWS architecture, honest limitations, remove any Streamlit refs
- SHAP offline notebook in shap_analysis/
- HF_TOKEN warning in logs — unauthenticated HuggingFace requests

**Key decisions made this session:**
- :latest tag is an anti-pattern in ECS — use explicit version tags for all future builds
- Relative API URL (/triage not http://host/triage) is the correct pattern for same-origin deployments
- Mobile UI fix deferred — to be addressed before LinkedIn post

**Live endpoint:**
- API health: http://13.250.9.126:8000/health
- Frontend: http://13.250.9.126:8000/ui
- Note: public IP changes on every ECS task restart

### Session 15 — 2026-05-04
**Branch at session end:** feature/aws-deployment — open, not yet merged

**Completed this session:**
- Branch housekeeping — all stale merged branches deleted locally
- Dockerfile created with python:3.12-slim base image
- .dockerignore created — excludes venv, vectorstore, data, rag, tests
- entrypoint.sh created — downloads vector stores from S3 at container startup
- S3 bucket created — rag-triage-api-vectorstore in ap-southeast-1
- Vector stores uploaded to S3 — hsg220 (1.3MB), osha (228MB), riddor (588KB)
- ECR repository created — rag-triage-api
- Docker image built locally and pushed to ECR
- IAM roles created — rag-triage-api-ecs-task-role (S3 read) and ecsTaskExecutionRole (ECR pull)
- Secrets Manager — GEMINI_API_KEY and HUGGINGFACE_API_TOKEN stored at rag-triage-api/prod
- ECS cluster created — rag-triage-api-cluster
- Task definition created — rag-triage-api-task:3 with both IAM roles and Secrets Manager references
- ECS service created — rag-triage-api-task-service, 1/1 tasks running
- API live and healthy — http://47.129.55.82:8000/health confirmed

**Next session starts at:**
- Add StaticFiles mount to main.py — two lines, explained in Session 15
- Rebuild Docker image locally
- Push new image to ECR
- Force ECS service to redeploy using new image
- Verify frontend accessible at http://<new-public-ip>:8000/ui
- Then raise PR for feature/aws-deployment and merge to main
- README update — document AWS architecture, honest limitations, remove Streamlit refs

**Open items carried forward:**
- Frontend not accessible — main.py missing StaticFiles mount
- feature/tool-find-patterns branch preserved — contains Phase 2 stepper frontend (app.jsx, 654 lines)
- SHAP offline notebook in shap_analysis/
- T4 cohort distribution reframing
- Consider reordering T4 before T1
- HF_TOKEN warning in logs — unauthenticated HuggingFace requests

**Architectural decisions confirmed this session:**
- API keys stored in Secrets Manager, not plain text environment variables
- Vector stores in S3, not baked into Docker image — correct separation of concerns
- ECS Fargate over EC2 — no server management required for portfolio project
- Public IP assigned to task — sufficient for portfolio demo, load balancer deferred

### Session 14 — 2026-05-01
**Branch at session end:** main — all work merged

**Completed this session:**
- Merged feature/frontend-wiring to main — live API wiring, input form, Session 13 notes confirmed landed
- Fixed typo in index.html — committed via fix/frontend-typo PR

**Next session starts at:**
- feature/readme-update — remove Streamlit refs, document frontend architecture and honest limitations
- Then Dockerfile, S3, ECR, ECS Fargate deployment

**Open items carried forward:**
- README update (Streamlit removal, frontend architecture, honest limitations)
- PDF printout / consolidated actionable plan
- T4 cohort distribution reframing
- Consider reordering T4 before T1
- SHAP offline notebook in shap_analysis/
- HF_TOKEN in Dockerfile

**Architectural decisions confirmed this session:**
- AWS deployment is next priority — single-page frontend is stable enough to deploy
- HITL stepper deferred until after AWS deployment
- UI wording polish deferred — lowest return against portfolio goals
- Vector stores (hsg220, osha, riddor) exist locally — need S3 upload before deployment
- No Dockerfile exists yet — build from scratch in Session 15

## Session 13 — 30 April 2026

### Branch
feature/frontend-wiring

### Completed
- Added CORSMiddleware to main.py — allows browser fetch from file:// origin
- Replaced static data.js frontend with live API-wired index.html
- Built InputForm component — narrative textarea, domain checkbox, character counter, validation
- Built LoadingView component — spinner, pipeline step cycling, 30–60s wait messaging
- Built ResultsView component — passes live API response as props to T1–T4
- Added DEMO_MODE flag for local UI testing without hitting API
- Added client-side meta generation — incidentRef, submittedAt, analyst
- Implemented cross-block mitigation deduplication in T3 with fallback message
- Fixed riddor-deadline CSS — white-space: normal, max-width: 200px
- Smoke tested end-to-end — narrative in, four tool outputs rendered correctly
- Smoke tested needlestick narrative — flag triggered correctly, caution wording refined

### Key decisions
- data.js removed entirely — all data from live API
- meta fields generated client-side — not in TriageResponse
- T3 deduplication: cross-block, normalised lowercase comparison, empty block fallback
- Needlestick caution wording updated to reference 99% training data blind spot explicitly

### Open items for Session 14
- PDF printout / consolidated actionable plan (options documented)
- T4 cohort distribution — reframe description, link to T1 prediction (options documented)
- T3 RAG retrieval quality — cause embedding too broad for some incident types (tool-level fix, future session)
- Consider reordering T4 before T1 (options documented)

### Known issues
- Two Plant causes with identical mitigation lists — second block renders fallback message correctly but underlying RAG retrieval needs tightening at tool level
- Needlestick Practices/People mitigations include moving and handling content — assessed as domain-appropriate given resident movement as contributing factor

## Session 12 — 30 April 2026

### Branch
feature/triage-endpoint, feature/frontend-phase1-demo

### Completed
- Recovered unmerged frontend Phase 1 branch and SESSION_NOTES S11 — committed via PR #4 and #5
- Wired /triage endpoint — sequential pipeline: predict_severity → extract_facts → map_riddor → analyse_causes → find_patterns → TriageResponse
- Fixed middle_severity_flag range: corrected to classes 1–3 (Minor, Moderate, Severe)
- Fixed persons_involved: changed type to str | list[str] in ConfirmedFactsRequest
- Fixed retrieve_riddor_sections: list-safe persons_involved formatting in embedding string
- Removed unused HTTPException import caught by CI ruff check
- Documented injury_mechanism as honest data limitation
- Rebuilt frontend from scratch: single index.html + data.js, ISO 7010 safety colour palette, consent/disclaimer modal, no C# labels visible to user
- Removed redundant frontend files: app.jsx, styles.css, tweaks-panel.jsx

### Key decisions
- Frontend stays as HTML/React — not Streamlit. Stuart has HTML/CSS experience and design quality matters for demo
- All data in data.js separate from index.html — cleaner for Phase 2 API wiring
- ISO 7010 colour palette: blue mandatory, amber hazard, red danger, green safe — defensible in OHS context

### Known issues
- Frontend not yet wired to live API — Phase 2 work
- Input form for narrative not yet built — required before API wiring
- OSHA severity_distribution keys are "0"–"4" strings — frontend handles correctly

### Session 13 starting point
- Design and build narrative input form
- Wire frontend to /triage endpoint replacing static data.js
- Test full end-to-end flow in browser

### Session 11 — 2026-04-28
**Branch at session end:** `main` — all work merged

**Completed this session:**

Act 1 — Frontend design review
- Reviewed Claude design project output (7-screen stepper UI)
- Decision: Phase 2 stepper design kept as-is for future wiring
- Decision: Build Phase 1 single-page view first — all tool outputs on one 
  scrollable page, no confirmation gates, static demo data only
- Decision: Streamlit removed entirely — replaced by static HTML frontend 
  served via FastAPI StaticFiles at deployment time

Act 2 — Frontend corrections
- Claude design single-page output reviewed against actual API models
- Corrected severity taxonomy: S1–S5 replaced with C0–C4 throughout
  (None/Minor/Moderate/Severe/Major with lost-time bands)
- Corrected pipeline to four tools — domain validation is input form only,
  not a tool output section
- Restored correct field names: CausalFactor, information_needed, 
  reporting_deadline with two-stage deadline strings
- Removed invented rationale card from T1 — SeverityPrediction has no 
  rationale field, model returns probabilities only
- Fixed analyst name to S. Clark
- Fixed model label to stuSterfc/ohs-severity-classifier (DistilBERT)
- Added integration point comment in data.js flagging probabilities key 
  divergence from live API CLASS_LABELS

Act 3 — Repo housekeeping
- frontend/ directory created under repo root
- Five files placed: index.html, app.jsx, data.js, styles.css, 
  tweaks-panel.jsx
- streamlit_app/__init__.py deleted
- Accidental edits to main.py and map_riddor.py identified and reverted 
  via git restore before committing
- Committed on feature/frontend-phase1, PR raised, CI green, merged to main
- Cherry-pick used to recover frontend commit after it was made on 
  feature/tool-find-patterns post-merge

**Architectural decisions made this session:**
- Streamlit removed — static HTML frontend is the UI layer
- Frontend served via FastAPI StaticFiles in production (not yet wired —
  deferred until AWS deployment)
- Phase 1 is display-only static demo — no API calls from frontend yet
- Phase 2 stepper wiring deferred until after /triage endpoint is complete

**Open items for Session 12:**
- Wire /triage endpoint — sequential pipeline calling all four tools
- Reconcile probabilities key format between data.js (C0–C4) and live 
  API CLASS_LABELS (full label strings)
- Update README — remove Streamlit references, document frontend architecture
- SESSION_NOTES.md commit at session start

**Known integration points flagged:**
- data.js probabilities keyed as "C0"–"C4"; live API uses full label strings 
  e.g. "None (0 days)" — reconcile when wiring real endpoint
- T2, T3, T4 demo data is approximate — will self-correct through integration

### Session 10 — 2026-04-28
**Branch at session end:** `feature/tool-find-patterns` — merged to main

**Completed this session:**

Act 1 — CI fixes
- Fixed mypy errors in predict_severity.py: stray curses import removed, 
  duplicate pipeline import removed, Any annotation added for transformers 
  pipeline output
- Fixed mypy errors in map_riddor.py: response.text or "" guard added in 
  two places, ChromaDB Optional fields guarded with or []
- All 12 mypy errors resolved, CI green

Act 2 — Endpoint wiring
- main.py updated with /predict-severity, /extract-facts, /map-riddor, 
  /analyse-causes, /find-patterns endpoints
- ConfirmedFactsRequest added to models.py for /map-riddor request body
- predicted_label added to SeverityPrediction — human-readable label with 
  absence duration retained in API response
- All endpoints verified working end-to-end with test narrative

Act 3 — analyse_causes
- Built app/tools/analyse_causes.py
- 4Ps causal framework (Plant, Premises, Practices, People) — UK-aligned, 
  HSE-recognised
- Option B — only return categories where a contributing factor was identified
- extract_causes — Gemini call, returns list of cause dicts
- retrieve_hsg220_for_cause — one embedding per cause, top 3 HSG220 chunks
- extract_mitigations — single batched Gemini call across all causes and 
  chunks, returns concise action lists per cause
- section_refs includes chapter name and page range for citation
- Smoke test passed — Premises and Practices identified for wet floor slip

Act 4 — find_patterns
- Built app/tools/find_patterns.py
- OSHA collection name confirmed as osha_hc_incidents (not osha_hc)
- Retrieves 50 similar incidents, returns top 10 narratives to API
- Query-specific severity distribution computed from all 50 retrieved incidents
- Population-level distribution dropped — query-specific is more meaningful
- Smoke test: 42% Class 4 for wet floor slip — significantly above population 
  baseline of 18.56%
- Honest tension documented: BERT predicts Moderate (confidence 0.29, 
  middle_severity_flag True), OSHA distribution shows 42% Major outcomes 
  for similar incidents — system working as designed, surfaces ambiguity 
  for human review

**Architectural decisions confirmed this session:**
- One branch per tool going forward — corrected from Session 10 onwards
- Query-specific distribution from 50 retrieved incidents preferred over 
  population-level figures for Tool 5 output
- extract_mitigations batched into single Gemini call to avoid per-cause 
  latency

**Next session starts at:**
- All four tools complete and verified
- Build the static HTML frontend — Phase 1 single screen output
- Raise PR for feature/tool-find-patterns before starting

**Open items carried forward:**
- SHAP — POST /explain endpoint still deferred
- RAG evaluation — after frontend complete
- HF_TOKEN environment variable still to be set
- README not yet updated with architectural decisions
- Token cost of verbose RIDDOR output to be monitored
- Chapter 1 HSG220 retrieval for broad queries — known limitation, 
  document in README

### Session 9 — 2026-04-24
**Branch at session end:** `feature/tool-predict-severity`

**Completed this session:**

Act 1 — Housekeeping
- Confirmed architecture before writing any code
- Confirmed four-tool linear pipeline
- Confirmed LangGraph removed — replaced by session-based FastAPI endpoints
- Confirmed Streamlit removed — replaced by static HTML frontend calling FastAPI directly
- Confirmed HITL enforced structurally between every endpoint via confirmation POST
- Confirmed RAG evaluation deferred until all four tools are built and pipeline is end-to-end functional
- Confirmed SHAP deferred until all four tools are built — to be added as separate POST /explain endpoint

Act 2 — predict_severity
- Built app/tools/predict_severity.py
- detect_needlestick — keyword set, strips punctuation before matching
- detect_ambiguous_severity — flags classes 2, 3, 4 based on dissertation finding of poor learned correlation
- predict_severity — loads stuSterfc/ohs-severity-classifier locally via transformers pipeline
- Confirmed HuggingFace Inference API not available for this model — switched to local inference
- Model weights cached at ~/.cache/huggingface/ after first download
- Smoke test passed — wet floor slip narrative returned Severe (8-28 days), confidence 0.2885, ambiguous_severity_flag True
- Committed: feat(tools): add predict_severity with needlestick and ambiguous severity detection

Act 3 — map_riddor
- Built app/tools/map_riddor.py
- extract_facts — Gemini call, returns four structured fields as JSON
- retrieve_riddor_sections — embeds confirmed facts, queries RIDDOR ChromaDB collection, returns top 5 chunks
- generate_advisory — Gemini call with retrieved chunks and confirmed facts, returns conditional advisory
- map_riddor — orchestrates retrieve and generate, appends hardcoded disclaimer
- Confirmed predicted_incapacitation from confirmed severity passed into facts dict at endpoint level, not inside tool
- Confirmed extract_facts is called by /extract-facts endpoint, map_riddor is called by /map-riddor endpoint — two separate endpoints with HITL confirmation between them
- Import check passed
- Committed: feat(tools): add map_riddor with fact extraction, RAG retrieval and conditional RIDDOR advisory

**Architectural decisions confirmed this session:**
- google.generativeai deprecated — switched to google.genai 1.72.0
- Local model inference via transformers pipeline — HuggingFace Inference API not available for this model
- Model weights baked into Docker image at build time — no runtime download in deployed container
- Railway hosts HTML frontend only — FastAPI backend with model runs on AWS ECS Fargate
- SHAP added as POST /explain endpoint after all four tools complete — local inference removes original barrier
- RAG evaluation uses industry-standard methodology — designed after pipeline is end-to-end functional
- User override available at every HITL confirmation step

**Next session starts at:**
- Build app/tools/analyse_causes.py
- Raise PR for feature/tool-predict-severity before starting

**Open items carried forward:**
- SHAP — POST /explain endpoint after all four tools complete
- RAG evaluation — after pipeline is end-to-end functional
- HF_TOKEN environment variable to be set in Dockerfile to suppress unauthenticated warning
- embeddings.position_ids UNEXPECTED warning from sentence-transformers — confirmed harmless, can be ignored
- README to document all architectural decisions including LangGraph removal rationale and SHAP deferral

## Session 8 — 2026-04-23

### What was built
- `rag/ingest_osha.py` — full OSHA H&C ingestion pipeline
  - `clean_narrative(text)` — strips organisation size prefix and `[SEP]`
    tokens from raw BERT training narratives
  - `load_and_clean(csv_path)` — reads all 181,374 records from CSV,
    cleans each narrative, returns flat list of dicts with `severity_bin`
    and `narrative` fields
  - `compute_distribution(records)` — counts records per severity class
    from full dataset, calculates percentages, returns distribution dict
  - `ingest(records, chroma_path)` — embeds all records using
    `all-MiniLM-L6-v2` in batches of 256, stores in ChromaDB with
    `severity_bin` as metadata
  - `main()` — orchestrates load, distribute, ingest in correct order
- `data/osha_severity_distribution.json` — precomputed severity
  distribution across all 181,374 records. Used by Tool 5 for
  population-level statistics. Computed before sampling to ensure
  accuracy against full dataset.

### Key decisions made this session
- Full corpus ingestion (181,374 records) chosen over stratified sample
  (5,000). Timing test confirmed 5.1 minutes build time — acceptable
  one-time cost. Full corpus improves query-specific severity
  distributions, which are more meaningful than population-level
  figures for Tool 5 output.
- Stratified sampling approach was designed and then deliberately
  discarded when Stuart correctly identified that query-specific
  distributions derived from similar incidents require the full corpus
  to be statistically reliable.
- `data/*` used in `.gitignore` instead of `data/` to allow `!`
  exception rules to take effect for `osha_severity_distribution.json`.
  Directory-level ignore blocks Git from entering the directory,
  preventing exceptions from working.
- Distribution JSON committed to version control as a computed output
  file. Raw CSV remains gitignored.

### Dataset characteristics
- Total records: 181,374 (181,375 lines including header)
- Class 0 (None, 0 days): 97,863 — 53.96%
- Class 1 (Minor, 1-2 days): 8,939 — 4.93%
- Class 2 (Moderate, 3-7 days): 17,483 — 9.64%
- Class 3 (Severe, 8-28 days): 23,427 — 12.92%
- Class 4 (Major, 29+ days): 33,663 — 18.56%

### Smoke test results
- Query: "employee slipped on wet floor while assisting resident"
- Result 1: Class 2, Distance 0.1647 — slip on wet floor in resident room
- Result 2: Class 4, Distance 0.2202 — slip on wet floor in resident room
- Result 3: Class 4, Distance 0.2444 — slip on wet floor in bathroom
- Result 4: Class 2, Distance 0.2478 — slip on wet floor in hallway
- Result 5: Class 3, Distance 0.2673 — slip on wet floor assisting care
- All five results correctly identified wet floor slip in care setting.
  Distance scores improved significantly versus 5,000 record sample test.

### Branch and commit
- Branch: `feature/osha-ingestion`
- Commit: `feat(osha): add OSHA H&C ingestion script and severity distribution`
- 3 files changed: `rag/ingest_osha.py`, `data/osha_severity_distribution.json`,
  `.gitignore`

### Branch protection configured this session
- GitHub branch ruleset `protect-main` applied to `main`
- Rules enabled: restrict deletions, require pull request before merging,
  block force pushes, require status checks to pass (job: `test`)
- Bypass list empty — rule applies to all contributors including owner
- Stale `feature/project-setup` branch deleted locally and remotely

### Open items carried forward
- `feature/osha-ingestion` branch open — raise PR and merge to main
  before Session 9 begins
- All three RAG knowledge bases now complete:
  - HSG220: 14 chunks in `vectorstore/hsg220/`
  - RIDDOR: 31 chunks in `vectorstore/riddor/`
  - OSHA: 181,374 records in `vectorstore/osha/`
- Vector stores are gitignored — regenerate with:
  - `python3 -m rag.build_hsg220` then `python3 -m rag.ingest_hsg220`
  - `python3 -m rag.ingest_riddor`
  - `python3 -m rag.ingest_osha`
- Session 9 starting point: raise PR for `feature/osha-ingestion`,
  merge to main, then begin Tool 2 — `predict_severity` implementation

### Notes
- NER-based injury mechanism extraction considered and rejected.
  OSHA data is US proxy for UK settings. Project demonstrates RAG,
  LangGraph, and FastAPI — mechanism-level taxonomy adds complexity
  without proportionate portfolio value.
- Total records figure of 181,375 in distribution JSON includes header
  row. Minor inaccuracy, does not affect percentages or ingestion.
  Document honestly in README limitations.

## Session 7 — 2026-04-22

### What was built
- `rag/build_riddor.py` — RIDDOR 2013 extraction and chunking
  - `extract_regulations(pdf_path, start_page, end_page)` — page-scoped
    extraction using line-pair boundary detection (title line followed by
    number pattern `^\d{1,2}\.[\s\—]`)
  - `build_chunks(regulations)` — applies hardcoded metadata lookup dict,
    skips regulations 1 and 2, splits regulation 4 into two chunks
    (specified injuries / over-seven-day incapacitation), splits regulation
    11 into two chunks (gas incidents / gas installation faults)
  - `build_schedule_chunks(categories)` — filters Schedule 2 to 11 retained
    H&C-relevant categories, attaches parent_regulation, deadline and route
    inherited from Regulation 7, applies title override for category 22
- `rag/ingest_riddor.py` — ChromaDB ingestion
  - Embeds regulation and schedule chunk text directly (no curated embedding
    string required — RIDDOR text is short enough for MiniLM 256-token limit)
  - 31 chunks stored: 20 regulation chunks, 11 schedule chunks
  - Collection name: `riddor`
  - Vectorstore path: `vectorstore/riddor/`

### Key design decisions made this session
- Regulation 4 split on phrase `"more than seven consecutive"` to separate
  specified injury (10-day) and over-seven-day incapacitation (15-day)
  reporting pathways
- Regulation 11 split on phrase `"approved person"` to separate gas incident
  notification (without delay) from gas installation fault report (14 days)
- Deadline strings carry full obligation — `"Notify without delay, then report
  within 10 days"` rather than just `"10 days"` — to correctly represent the
  dual notification and report obligation
- Schedule 2 omitted categories hardcoded and documented in
  `OMITTED_SCHEDULE2_NOTE` — explosives block (5–9), diving operations
  (13–17), train collisions (19)
- Schedule 1 Part 1 (reporting procedure prose) treated as reference material
  for building the metadata lookup dict — not stored as a retrievable chunk
- `vectorstore/riddor/` gitignored by design — build artifact, regenerate
  with `python3 -m rag.ingest_riddor`
- `OMITTED_SCHEDULE2` removed as dead code — omission documented in
  `OMITTED_SCHEDULE2_NOTE` and README instead

### Smoke tests
- Injury query (`worker fractured wrist after fall from ladder`) — `reg_4a`
  surfaced at rank 2, `reg_4b` at rank 3. Correct.
- Dangerous occurrence query (`hoist collapsed while lifting resident in care
  home`) — `sch2_1` Lifting equipment surfaced at rank 1. Correct.
  `parent_regulation: "7"` in chunk metadata means `reg_7` does not need to
  appear in retrieval for Tool 3 to know Regulation 7 applies.

### Commits
- `feat(riddor): add RIDDOR 2013 extraction, chunking and ChromaDB ingestion`
  — 2 files, 272 insertions

### Open items carried forward
- OSHA CSV ingestion not started — next session starting point
- HSG220 Chapter 2 ranking high for generic queries — revisit after Tool 4
  integration (carried from Session 6)
- Retrieval smoke tests used matching sentence-transformer model via
  `query_embeddings` — consistent with ingestion, correct approach confirmed
- README not yet updated with RIDDOR omission decisions and Schedule 2
  scoping rationale — add before final portfolio review
- `feature/riddor-ingestion` branch open — do not merge until OSHA CSV
  ingestion is also complete and tested, or cut a PR now and open a new
  branch for OSHA. Decision deferred to Session 8.

### Session 7 — 2026-04-17

**Status at end of session:**
HSG220 ingestion complete. Vector store built and retrieval verified. 14 chunks stored in `vectorstore/hsg220/`.

**Completed this session:**
- Walked through `rag/build_hsg220.py` in detail — imports, constants, extraction function, build function, main, scope resolution
- Confirmed Python scope rules (LEGB) and why `CHAPTER_EMBEDDINGS` does not need to be a parameter
- Confirmed `chromadb==1.5.7` and `sentence-transformers==5.4.0` installed in venv
- Reviewed `rag/ingest_hsg220.py` line by line — `PersistentClient`, collection lifecycle, manual embedding, `add()` call
- Extended `build_chapters` to include page ranges per chapter
- Extended ingestion metadata to include chapter and pages for downstream citation
- Ran `python -m rag.ingest_hsg220` successfully — 14 chunks stored
- Verified retrieval with ad-hoc query — store is queryable
- Added interview prep entries for scope and RAG patterns to external repo

**Next session starts at:**
RIDDOR ingestion script — parallel structure to HSG220 but different chunking strategy (per-regulation rather than per-chapter). Open a new feature branch `feature/riddor-ingestion` before starting.

**Open items:**
- RIDDOR ingestion script not yet started
- OSHA CSV ingestion script not yet started
- `hsg220_clean.txt` is a temporary inspection file — not part of final build (now in `.gitignore`)
- HSG220 retrieval test: Chapter 2 ranks high for generic incident queries — embedding string may be too broad. Revisit after Tool 4 integration when queries are LLM-extracted cause phrases rather than raw narratives.
- Retrieval test used Chroma's default ONNX embedding function rather than the sentence-transformer used for ingestion. Acceptable for smoke test. Real Tool 4 must use `query_embeddings` with matching model to guarantee vector-space consistency.

**Commands run this session:**
- `pip list | grep -E "^(chromadb|sentence-transformers)"`
- `python -c "from rag.build_hsg220 import build_chapters, PDF_PATH; ..."` (page range sanity check)
- `python -m rag.ingest_hsg220`
- `ls -la vectorstore/hsg220/`
- Ad-hoc Chroma query test

### Session 6 — 2026-04-17

**Status at end of session:**
Ingestion script for HSG220 not yet written. `build_hsg220.py` reviewed line by line and understood. Concept walkthrough complete.

**Completed this session:**
- Walked through `rag/build_hsg220.py` in detail — imports, constants, extraction function, build function, main, scope resolution
- Confirmed Python scope rules (LEGB) and why `CHAPTER_EMBEDDINGS` does not need to be a parameter
- Confirmed `chromadb==1.5.7` and `sentence-transformers==5.4.0` installed in venv
- Decided ingestion approach: import `build_chapters` from `build_hsg220.py`, embed curated strings manually, store full chapter text as documents, use separate Chroma collection per document
- Decided on persistent Chroma client with collection-per-document pattern (`hsg220`, `riddor`, `osha_hc`)

**Next session starts at:**
Write `rag/ingest_hsg220.py` — embed curated strings with sentence-transformers, store full chapter text in persistent ChromaDB collection at `vectorstore/hsg220/`

**Open items:**
- RIDDOR ingestion script not yet started
- OSHA CSV ingestion script not yet started
- `hsg220_clean.txt` is a temporary inspection file — not part of final build
- First run of sentence-transformer will download ~90MB model to `~/.cache/huggingface/`

**Commands run this session:**
- `pip list | grep -E "^(chromadb|sentence-transformers)"`

### Session 5 — 2026-04-16
**Status at end of session:**
HSG220 extraction and chapter splitting complete. ChromaDB ingestion not yet written.

**Completed this session:**
- Reviewed chunking strategies per document type
- Decided on page-index based chapter extraction for HSG220
- Created rag/hsg220_embeddings.py with 14 curated embedding strings
- Built rag/build_hsg220.py — extracts and splits HSG220 into 14 clean chapters
- Verified chapter character counts — all 14 chapters credible
- hsg220_clean.txt written as inspection output

**Next session starts at:**
ChromaDB ingestion — embedding each HSG220 chapter and storing in vector store

**Open items:**
- RIDDOR ingestion script not yet started
- OSHA CSV ingestion script not yet started
- hsg220_clean.txt is a temporary inspection file — not part of final build

**Commands run this session:**
- python -m rag.build_hsg220
### Session 4 — 2026-04-15
**Status at end of session:**
Foundation complete. API skeleton running and verified. All source documents in place.

**Completed this session:**
- app/models.py — all Pydantic request and response schemas
- main.py — FastAPI skeleton with health check and triage endpoint
- API verified running at localhost:8000/docs
- Domain constraint validated — rejects confirmed_hc_domain: false correctly
- SHAP decision made — offline notebook in shap_analysis/, not in live API
- validate_domain tool removed — domain constraint handled architecturally
- Source documents cleaned and organised in data/
- Org size prefix strip strategy confirmed for RAG ingestion

**Next session starts at:**
RAG build scripts — ingesting RIDDOR 2013, HSG220, and OSHA CSV into ChromaDB

**Open items resolved:**
- HSG220 confirmed — data/documents/hsg220.pdf
- OSHA CSV confirmed — data/csv/osha_hc_incidents.csv

**Blockers or open questions:**
- None — all documents confirmed, ready for RAG build

### Session 3 — 2026-04-10
**Status at end of session:**
CI pipeline live on GitHub Actions. config.py working and committed. pytest placeholder in place.

**Completed this session:**
- Debugged venv activation issue
- Switched from Python 3.11 to 3.12.3
- Installed pip-tools and chose it over pip freeze for professional dependency management
- Created requirements.in with direct dependencies only
- Generated requirements.txt via pip-compile
- Replaced CUDA torch with CPU-only build
- Verified torch installation
- Created app/config.py with pydantic-settings
- Tested config.py loads correctly from .env
- Created .github/workflows/ci.yml
- Fixed mypy errors with mypy.ini and pydantic plugin
- Added pytest.ini and placeholder test
- Created ml-engineering-interview-prep repository with INTERVIEW_PREP.md

**Next session starts at:**
models.py — Pydantic request and response schemas

**Blockers or open questions:**
- HSG220 PDF availability still unconfirmed
- H&C OSHA CSV location in WSL2 still unconfirmed
- pytest placeholder test should be replaced when real tests are written

**Commands run this session:**
- python3 -m venv venv
- source venv/bin/activate
- pip install pip-tools
- pip-compile requirements.in
- pip config set global.timeout 300
- pip-sync requirements.txt
- python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
- python -c "from app.config import get_settings; ..."
- mkdir -p .github/workflows