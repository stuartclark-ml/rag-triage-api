from fastapi import FastAPI
from app.config import get_settings
from app.models import IncidentRequest, TriageResponse, SeverityPrediction, PatternAnalysis, ConfirmedFactsRequest, RiddorAdvisory, CausalAnalysis
from app.tools.predict_severity import predict_severity
from app.tools.analyse_causes import analyse_causes
from app.tools.map_riddor import extract_facts, map_riddor
from app.tools.find_patterns import find_patterns


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


@app.post("/extract-facts")
async def run_extract_facts(request: IncidentRequest):
    facts = extract_facts(request.narrative)
    return facts

@app.post("/predict-severity", response_model=SeverityPrediction)
async def run_predict_severity(request: IncidentRequest):
    result = predict_severity(request.narrative)
    return SeverityPrediction(**result)

@app.post("/map-riddor", response_model=RiddorAdvisory)
async def run_map_riddor(request: ConfirmedFactsRequest):
    facts = request.model_dump()
    result = map_riddor(facts)
    return RiddorAdvisory(**result)

@app.post("/analyse-causes", response_model=CausalAnalysis)
async def run_analyse_causes(request: IncidentRequest):
    result = analyse_causes(request.narrative)
    return CausalAnalysis(**result)

@app.post("/find-patterns", response_model=PatternAnalysis)
async def run_find_patterns(request: IncidentRequest):
    result = find_patterns(request.narrative)
    return PatternAnalysis(**result)

@app.post("/triage", response_model=TriageResponse)
async def triage(request: IncidentRequest):
    severity_result = predict_severity(request.narrative)
    severity_prediction = SeverityPrediction(**severity_result)

    facts = extract_facts(request.narrative)
    facts["predicted_incapacitation"] = severity_prediction.predicted_label
    riddor_result = map_riddor(facts)
    riddor_advisory = RiddorAdvisory(**riddor_result)

    causes_result = analyse_causes(request.narrative)
    causal_analysis = CausalAnalysis(**causes_result)

    patterns_result = find_patterns(request.narrative)
    pattern_analysis = PatternAnalysis(**patterns_result)

    return TriageResponse(
        severity_prediction=severity_prediction,
        riddor_advisory=riddor_advisory,
        causal_analysis=causal_analysis,
        pattern_analysis=pattern_analysis,
    )