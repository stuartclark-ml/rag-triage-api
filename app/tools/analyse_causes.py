import json
import chromadb
from sentence_transformers import SentenceTransformer
from google import genai
from app.config import get_settings

DISCLAIMER = (
    "These are directions for investigation only. Determination of root cause "
    "requires full investigation by a competent person."
)

_embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

_chroma_client = chromadb.PersistentClient(path="vectorstore/hsg220")
_hsg220_collection = _chroma_client.get_collection("hsg220")


def extract_causes(narrative: str) -> list[dict]:
    settings = get_settings()
    client = genai.Client(api_key=settings.gemini_api_key)

    prompt = f"""You are a health and safety incident analyst specialising in UK care home settings.

Analyse the incident narrative below using the 4Ps causal framework used in UK health and safety investigation:
- Plant: any equipment, tools, or devices involved, bed rails, needlesticks, sharps, chemicals, gas and air, latex, ill health
- Premises: any environmental or physical conditions present, falls from heigh, slips, trips, confined spaces, temperature
- Practices: any work methods, procedures, or systems of work involved, moving and handling,scalding burning, disease, drugs
- People: any human factors such as training, supervision, fatigue, violence, or staffing

Return only the categories where a contributing factor was identified. Do not return a category if nothing relevant was found.

Return a JSON array only — no prose, no markdown, no explanation.

Each item in the array must have:
- cause_type: one of "Plant", "Premises", "Practices", "People"
- description: a maximum 20 words concise description of the specific contributing factor identified

Narrative:
{narrative}

Return only a valid JSON array."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    raw = (response.text or "").strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def retrieve_hsg220_for_cause(cause_description: str) -> list[dict]:
    embedding = _embedder.encode(cause_description).tolist()

    results = _hsg220_collection.query(
        query_embeddings=[embedding],
        n_results=3,
        include=["documents", "metadatas", "distances"],
    )

    docs = results["documents"] or []
    metas = results["metadatas"] or []
    dists = results["distances"] or []

    chunks = []
    for doc, meta, dist in zip(docs[0], metas[0], dists[0]):
        chunks.append({
            "text": doc,
            "metadata": meta,
            "distance": round(dist, 4),
        })

    return chunks

def extract_mitigations(causes_with_chunks: list[dict]) -> list[dict]:
    settings = get_settings()
    client = genai.Client(api_key=settings.gemini_api_key)

    causes_text = ""
    for item in causes_with_chunks:
        causes_text += f"\nCause type: {item['cause_type']}\n"
        causes_text += f"Description: {item['description']}\n"
        causes_text += "Relevant HSG220 guidance:\n"
        for chunk in item["chunks"]:
            causes_text += f"  [{chunk['metadata'].get('chapter', 'Unknown')}] {chunk['text']}\n"

    prompt = f"""You are a health and safety adviser specialising in UK care home settings.

For each cause below, extract a concise list of specific mitigation actions to investigate.
Base your response strictly on the HSG220 guidance provided for each cause.
Do not invent actions not supported by the guidance.
Each action must be a single sentence of maximum 20 words.

Return a JSON array only — no prose, no markdown, no explanation.

Each item in the array must have:
- cause_type: matching the cause_type provided
- mitigation_actions: list of concise action strings to investigate

Causes and guidance:
{causes_text}

Return only a valid JSON array."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    raw = (response.text or "").strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def analyse_causes(narrative: str) -> dict:
    causes = extract_causes(narrative)

    causes_with_chunks = []
    for cause in causes:
        chunks = retrieve_hsg220_for_cause(cause["description"])
        causes_with_chunks.append({
            "cause_type": cause["cause_type"],
            "description": cause["description"],
            "chunks": chunks,
        })

    mitigations = extract_mitigations(causes_with_chunks)

    mitigation_map = {
        item["cause_type"]: item.get("mitigation_actions", [])
        for item in mitigations
    }

    identified_causes = []
    for item in causes_with_chunks:
        section_refs = ", ".join(
            f"{c['metadata'].get('chapter', 'Unknown')} (pp.{c['metadata'].get('pages', '')})"
            for c in item["chunks"]
        )
        identified_causes.append({
            "cause_type": item["cause_type"],
            "description": item["description"],
            "hsg220_section": section_refs,
            "mitigation_actions": mitigation_map.get(item["cause_type"], []),
        })

    return {
        "identified_causes": identified_causes,
        "disclaimer": DISCLAIMER,
    }