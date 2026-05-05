# rag-triage-api

**Risk Event Classification and Regulatory Mapping System**

An agentic FastAPI service that takes a health and social care workplace incident narrative as input and returns a structured triage analysis. The system combines a live fine-tuned BERT classifier with retrieval-augmented generation (RAG) over three regulatory knowledge bases, run as a sequential four-tool pipeline.

Live endpoint: http://13.229.251.82/ui

---

## ⚠️ Domain Constraint — Read Before Use

This system is scoped exclusively to **health and social care care home settings**.

The BERT severity classifier (`stuSterfc/ohs-severity-classifier`) was trained on the OSHA Health and Social Care sector dataset. It has not been validated on any other industry or setting. All tools in this pipeline inherit that constraint.

- Every request must include `confirmed_hc_domain: true`. The API enforces this via a Pydantic field validator — requests where this is `false` are rejected before any processing begins.
- All outputs carry a domain disclaimer that predictions are decision-support tools only, not compliance determinations.
- The OSHA pattern analysis knowledge base uses the H&C sector subset only — not the full OSHA dataset.
- RIDDOR output is always a conditional advisory — never a definitive reportability determination.

This is not a weakness. It is honest engineering.

---

## What It Does

Submit a care home incident narrative. The `/triage` endpoint runs four tools in sequence and returns a structured report.

| Tool | Module | Purpose |
|---|---|---|
| `predict_severity` | `app/tools/predict_severity.py` | Predicts incident severity across five classes using a live HuggingFace BERT model |
| `extract_facts` + `map_riddor` | `app/tools/map_riddor.py` | Extracts structured facts from the narrative, then identifies which RIDDOR 2013 categories may potentially apply |
| `analyse_causes` | `app/tools/analyse_causes.py` | Extracts all contributing causes and retrieves relevant HSG220 mitigation directions for each |
| `find_patterns` | `app/tools/find_patterns.py` | Surfaces population-level severity benchmarks from similar H&C OSHA incidents |

### Severity Classes

| Class | Label |
|---|---|
| 0 | None (0 days) |
| 1 | Minor (1–2 days) |
| 2 | Moderate (3–7 days) |
| 3 | Severe (8–28 days) |
| 4 | Major (29+ days) |

---

## Architecture

The `/triage` endpoint is a plain sequential pipeline — no agent framework. Each tool is a Python function called in order. The output of one step informs the next.

```
POST /triage
      │
      ▼
IncidentRequest (Pydantic v2)
  narrative: str (min 50 chars)
  confirmed_hc_domain: bool
      │
      field_validator — rejects False before processing begins
      │
      ▼
1. predict_severity(narrative)
      └── HuggingFace Inference API → stuSterfc/ohs-severity-classifier
      └── Returns: probability distribution, predicted class, confidence,
                   needlestick_flag, middle_severity_flag
      │
      ▼
2. extract_facts(narrative) → map_riddor(facts + predicted_incapacitation)
      └── ChromaDB (RIDDOR 2013 PDF) + Gemini 2.5 Flash
      └── Returns: potentially applicable categories, information needed,
                   reporting deadlines, follow-up questions
      │
      ▼
3. analyse_causes(narrative)
      └── ChromaDB (HSG220 PDF) + Gemini 2.5 Flash
      └── Returns: all identified causes, HSG220 section references,
                   mitigation directions per cause
      │
      ▼
4. find_patterns(narrative)
      └── ChromaDB (OSHA H&C CSV)
      └── Returns: similar incidents, severity distribution,
                   injury mechanism base rates
      │
      ▼
TriageResponse (Pydantic v2)
  + domain_disclaimer on every response
```

### Domain Enforcement

Domain constraint is architectural, not a separate tool. `IncidentRequest` contains a `confirmed_hc_domain: bool` field with a Pydantic `field_validator` that raises a `ValueError` if the value is `False`. The request is rejected at validation before any tool runs.

### Safety Flags

Two flags are hardcoded on the severity prediction regardless of model output.

**`needlestick_flag`** — raised when needle-related terms appear in the narrative (`needle`, `needlestick`, `lancet`, `sharps`, `puncture`). 99.25% of needlestick injuries in the training data were labelled severity class 0. The model systematically underestimates needlestick severity. Mandatory human review is required when this flag is raised.

**`middle_severity_flag`** — raised when the predicted class is Moderate (2) or Severe (3). These classes have higher distributional uncertainty in the training data. Human review is recommended.

---

## RAG Knowledge Bases

| Knowledge Base | Source | Used By |
|---|---|---|
| RIDDOR 2013 | legislation.gov.uk | `map_riddor` |
| HSG220 — Health and safety in care homes | hse.gov.uk | `analyse_causes` |
| OSHA H&C sector subset | Dissertation dataset (CSV) | `find_patterns` |

All three vector stores are built at ingestion time using `sentence-transformers/all-MiniLM-L6-v2` and stored in ChromaDB. They are held in S3 and downloaded to the container at startup — they are not baked into the Docker image.

**Embedding decisions:**

For HSG220, curated keyword-dense embedding strings are vectorised separately from the full chapter text stored for LLM reasoning. This is motivated by the 256-token limit of `all-MiniLM-L6-v2` — embedding truncated prose degrades retrieval quality.

For the OSHA knowledge base, the organisation size prefix (everything before and including the first `[SEP]` token) is stripped before embedding. This removes a spurious correlation identified during dissertation model training.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check — returns app name, version, environment, domain |
| POST | `/extract-facts` | Extract structured facts from a narrative |
| POST | `/predict-severity` | Run severity prediction only |
| POST | `/map-riddor` | Run RIDDOR advisory only, given confirmed facts |
| POST | `/analyse-causes` | Run causal analysis only |
| POST | `/find-patterns` | Run pattern analysis only |
| POST | `/triage` | Full sequential pipeline — all four tools |

Individual tool endpoints allow each component to be tested in isolation. The frontend uses `/triage`.

Interactive API docs: `http://13.229.251.82/docs`

---

## AWS Deployment

```
ECR  →  ECS Fargate  ←  S3 (vector stores)
                ↑
         Secrets Manager
      (GEMINI_API_KEY, HF_TOKEN)
```

| Service | Purpose |
|---|---|
| ECR | Stores the Docker container image |
| ECS Fargate | Runs the FastAPI container — serverless, no EC2 management |
| S3 | Stores ChromaDB vector stores — decoupled from the application image |
| Secrets Manager | Stores API keys — never in environment variables or baked into the image |
| IAM | Task role (S3 read) + execution role (ECR pull, Secrets Manager read) |

The frontend is a single-page HTML file served by FastAPI via `StaticFiles`. No separate hosting is required.

**Image tagging:** Docker images are tagged with explicit version numbers (`:v1`, `:v2`, ...) rather than `:latest`. ECS task definitions pin to a specific tag. This avoids the caching behaviour where ECS continues running a stale image digest even after a new image is pushed.

---

## Tech Stack

| Component | Technology |
|---|---|
| API framework | FastAPI |
| Validation | Pydantic v2 |
| Vector store | ChromaDB |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Severity classifier | DistilBERT fine-tuned — stuSterfc/ohs-severity-classifier |
| LLM | Gemini 2.5 Flash (Google PAYG) |
| PDF ingestion | PyMuPDF (fitz) |
| Containerisation | Docker |
| Deployment | AWS ECS Fargate |
| CI | GitHub Actions — ruff, mypy (pydantic plugin), pytest |
| Python | 3.12.3, WSL2 Ubuntu |


## Running Locally

**Prerequisites:** Python 3.12, a Google PAYG API key for Gemini 2.5 Flash, a HuggingFace API token.

```bash
git clone https://github.com/stuartclark-ml/rag-triage-api
cd rag-triage-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Set environment variables:

```bash
export GEMINI_API_KEY=your_key
export HUGGINGFACE_API_TOKEN=your_token
```

Build vector stores (first run only):

```bash
python -m rag.ingest_hsg220
python -m rag.ingest_riddor
python -m rag.ingest_osha
```

Run the API:

```bash
uvicorn main:app --reload
```

Frontend: `http://localhost:8000/ui`
API docs: `http://localhost:8000/docs`

---

## Honest Limitations

**Model scope**
- The BERT classifier was trained on H&C OSHA data only. Not validated outside care home settings.
- Known needlestick blind spot — 99.25% of needlestick training examples were labelled severity class 0. The `needlestick_flag` exists to mitigate this, not eliminate it.
- Organisation size was a spurious correlate in training data. Size prefix is stripped before all embeddings.

**Data**
- OSHA data is a US proxy for UK H&C settings. Regulatory differences exist. RIDDOR advisory always requires verification by a competent person familiar with UK law.
- The OSHA dataset has no timestamp at record level. No time-based analysis is possible. All pattern output describes static severity distributions only.
- Pattern analysis is population-level only. No equipment, location, or individual-level metrics are available.

**Output scope**
- RIDDOR output is always a conditional advisory. The system identifies what information is needed and what categories may apply — it never produces a definitive reportability determination.
- Causal analysis surfaces mitigation directions for investigation. It does not identify root causes. Root cause determination requires a full investigation by a competent person.
- The system has not been evaluated against a labelled ground truth for RIDDOR mapping or causal extraction accuracy.

---

## Portfolio Context

This is Project 2 of a three-project ML engineering portfolio.

| Project | Description |
|---|---|
| Dissertation | DistilBERT/ModernBERT + SHAP to predict workplace incident severity from OSHA narratives. Model live at `stuSterfc/ohs-severity-classifier` |
| Project 1 | OHS certificate intelligence parser — FastAPI, PyMuPDF, Tesseract OCR, Gemini 2.5 Flash, Streamlit, Railway |
| **Project 2** | **This project — RAG triage API for H&C care home incidents** |


Positioning: safety-critical document intelligence engineering targeting ML Engineering roles in Insurance and Operational Risk.

---

## CI

GitHub Actions runs on every PR to main: `ruff`, `mypy` (with pydantic plugin), `pytest`. All three must pass before merge.

---

## Licence

MIT