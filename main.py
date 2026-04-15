from fastapi import FastAPI, HTTPException
from app.config import get_settings
from app.models import IncidentRequest, TriageResponse

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Risk Event Classification and Regulatory Mapping System. "
        "Domain: Health and Social Care care home settings only. "
        "All outputs are decision-support tools only, not compliance determinations."
    ),
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "domain": settings.domain,
    }


@app.post("/triage", response_model=TriageResponse)
async def triage(request: IncidentRequest):
    raise HTTPException(
        status_code=501,
        detail="Pipeline not yet implemented. Models and API structure verified."
    )