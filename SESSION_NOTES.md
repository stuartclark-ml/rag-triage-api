# SESSION NOTES — rag-triage-api

## Project
Risk Event Classification and Regulatory Mapping System
Domain: Health and Social Care care home settings only
HuggingFace model: stuSterfc/ohs-severity-classifier

---

## Session Log

### Session 2 — 2026-04-09
**Status at end of session:**
Repository pushed to GitHub. Virtual environment created and activated. Feature branch not yet created — stopped for AWS study.

**Completed this session:**
- Fixed .env.example placeholder to pass GitHub secret scanning
- Amended first commit and pushed successfully to GitHub
- Installed python3.12-venv
- Created and activated .venv virtual environment
- Covered concepts: git push protection, amend commit, virtual environments, branches and professional Git workflow

**Next session starts at:**
Create feature/project-setup branch, then requirements.txt, then config.py, then models.py

**Blockers or open questions:**
- HSG220 is a priced HSE publication — confirm copy available before RAG build session
- H&C OSHA CSV location in WSL2 to be confirmed before Tool 5 build session
- Python version is 3.12.3 not 3.11 — update all documentation to reflect this

**Commands run this session:**
- git push -u origin main
- sudo apt install python3.12-venv
- python3 -m venv .venv
- source .venv/bin/activate

---

## Architecture Decisions Log

| Decision | Choice | Reason | Session |
|---|---|---|---|
| Branch naming | main | Matches GitHub default, avoids mismatch | 1 |
| Folder structure | app/agent/tools/rag/data/vectorstore | Separation of concerns, one tool per file | 1 |
| Secrets management | .env never committed, .env.example committed | Production standard practice | 1 |
| Python version | 3.12.3 | System version available, all libraries support it | 2 |

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
- Python: 3.12.3
- Working directory: /home/stuart/rag-triage-api
- Remote: https://github.com/stuartclark-ml/rag-triage-api.git

---

## Domain Constraint — Non-Negotiable
Model trained on H&C OSHA care home data only.
Not validated outside this domain.
This must be stated in all documentation, UI, and API responses.
