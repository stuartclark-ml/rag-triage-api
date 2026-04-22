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