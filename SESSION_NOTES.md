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