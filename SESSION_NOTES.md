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