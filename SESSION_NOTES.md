# SESSION NOTES — rag-triage-api

## Project
Risk Event Classification and Regulatory Mapping System
Domain: Health and Social Care care home settings only
HuggingFace model: stuSterfc/ohs-severity-classifier

---

## Session Log

### Session 1 — 2026-04-08
**Status at end of session:**
Repository initialised locally. Folder structure created. Core config files in place. Not yet pushed to GitHub.

**Completed this session:**
- Ran prerequisite checklist against build brief
- Created GitHub repository at stuartclark-ml/rag-triage-api
- Initialised local Git repository at /home/stuart/rag-triage-api
- Created full folder structure
- Created .gitignore
- Created .env.example
- Created SESSION_NOTES.md
- Covered concepts: Git init, folder structure, here documents, .gitignore, .env vs .env.example, FastAPI, Pydantic

**Next session starts at:**
First commit and push to GitHub, then Python venv setup, then requirements.txt

**Blockers or open questions:**
- HSG220 is a priced HSE publication — confirm copy available before RAG build session
- H&C OSHA CSV location in WSL2 to be confirmed before Tool 5 build session

**Commands run this session:**
- cd /home/stuart/rag-triage-api
- git init -b main
- mkdir -p app/agent app/tools rag data vectorstore streamlit_app tests .github/workflows
- touch app/__init__.py app/agent/__init__.py app/tools/__init__.py rag/__init__.py streamlit_app/__init__.py tests/__init__.py
- cat > .gitignore
- cat > .env.example
- cat > SESSION_NOTES.md

---

## Architecture Decisions Log

| Decision | Choice | Reason | Session |
|---|---|---|---|
| Branch naming | main | Matches GitHub default, avoids mismatch | 1 |
| Folder structure | app/agent/tools/rag/data/vectorstore | Separation of concerns, one tool per file | 1 |
| Secrets management | .env never committed, .env.example committed | Production standard practice | 1 |

---

## Known Issues and Workarounds
| Issue | Workaround | Status |
|---|---|---|
| Needlestick blind spot in BERT model | Hard-coded flag in Tool 2 | Permanent by design |
| Org size prefix spurious correlation | Strip prefix before all embeddings | Permanent by design |
| OSHA data is US proxy for UK | Disclaimer on all RIDDOR output | Permanent by design |

---

## Environment
- OS: WSL2 Ubuntu
- Python: 3.11
- Working directory: /home/stuart/rag-triage-api
- Remote: https://github.com/stuartclark-ml/rag-triage-api.git

---

## Domain Constraint — Non-Negotiable
Model trained on H&C OSHA care home data only.
Not validated outside this domain.
This must be stated in all documentation, UI, and API responses.
