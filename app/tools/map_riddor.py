import json
import chromadb
from sentence_transformers import SentenceTransformer
from google import genai
from app.config import get_settings

DISCLAIMER = (
    "This is a conditional advisory only. A competent person must make "
    "the final RIDDOR determination when full information is available."
)

_embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

_chroma_client = chromadb.PersistentClient(path="vectorstore/riddor")
_riddor_collection = _chroma_client.get_collection("riddor")


def extract_facts(narrative: str) -> dict:
    settings = get_settings()
    client = genai.Client(api_key=settings.gemini_api_key)

    prompt = f"""You are a health and safety incident analyst.

Extract the following facts from the incident narrative below.
Return a JSON object only — no prose, no markdown, no explanation.

Fields:
- injury_type: what physical injury or harm occurred
- persons_involved: who was involved (employee, resident, contractor, member of public)
- circumstances: what activity was taking place and what environmental factors were present
- known_severity: what is currently known about severity and medical treatment (if nothing is known, return "unknown")

Narrative:
{narrative}

Return only valid JSON."""

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


def retrieve_riddor_sections(facts: dict) -> list:
    embedding_string = (
        f"Injury: {facts.get('injury_type', '')}. "
        f"Persons involved: {facts.get('persons_involved', '')}. "
        f"Circumstances: {facts.get('circumstances', '')}. "
        f"Known severity: {facts.get('known_severity', '')}."
        f"Predicted incapacitation: {facts.get('predicted_incapacitation', 'unknown')}."

    )

    embedding = _embedder.encode(embedding_string).tolist()

    results = _riddor_collection.query(
        query_embeddings=[embedding],
        n_results=5,
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


def generate_advisory(facts: dict, chunks: list) -> dict:
    settings = get_settings()
    client = genai.Client(api_key=settings.gemini_api_key)

    chunks_text = "\n\n".join(
        f"[{c['metadata'].get('regulation', 'Unknown')}]\n{c['text']}"
        for c in chunks
    )

    prompt = f"""You are a health and safety regulatory adviser specialising in RIDDOR 2013.

You have been given extracted facts from a health and social care incident and relevant sections from RIDDOR 2013.

Your task is to produce a conditional advisory — not a determination. The reporter may not yet have complete information.

The predicted incapacitation period is derived from a machine learning model and has been confirmed by the user. Use it as a signal only — it is not a clinical determination. It is particularly relevant to Regulation 4 (over-7-day incapacitation) and Regulation 5 (specified injuries).

Return a JSON object only — no prose, no markdown, no explanation.

Fields:
- potentially_applicable: list of objects, each with:
  - category: RIDDOR category name
  - description: what this category covers and why it may apply
  - information_needed: list of strings — what is still required to confirm or rule out this category
  - reporting_deadline: statutory deadline if this category applies
- follow_up_questions: list of specific questions the reporter should pursue
- disclaimer: always return exactly "This output is advisory only. A competent person must make the final RIDDOR determination when full information is available."

Extracted facts:
{json.dumps(facts, indent=2)}

Relevant RIDDOR sections:
{chunks_text}

Return only valid JSON."""

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


def map_riddor(facts: dict) -> dict:
    chunks = retrieve_riddor_sections(facts)
    advisory = generate_advisory(facts, chunks)

    return {
        "potentially_applicable": advisory.get("potentially_applicable", []),
        "follow_up_questions": advisory.get("follow_up_questions", []),
        "disclaimer": DISCLAIMER,
    }