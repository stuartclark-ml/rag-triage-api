import json
import chromadb
from sentence_transformers import SentenceTransformer
from app.models import SeverityClass

DISTRIBUTION_PATH = "data/osha_severity_distribution.json"

_embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

_chroma_client = chromadb.PersistentClient(path="vectorstore/osha")
_osha_collection = _chroma_client.get_collection("osha_hc_incidents")


def search_similar_incidents(narrative: str) -> tuple[list[dict], list[dict]]:
    embedding = _embedder.encode(narrative).tolist()

    results = _osha_collection.query(
        query_embeddings=[embedding],
        n_results=50,
        include=["documents", "metadatas", "distances"],
    )

    docs = results["documents"] or []
    metas = results["metadatas"] or []
    dists = results["distances"] or []

    all_incidents = []
    for doc, meta, dist in zip(docs[0], metas[0], dists[0]):
        all_incidents.append({
            "narrative_excerpt": doc,
            "severity_outcome": SeverityClass(int(str(meta["severity_bin"]))),
            "distance": round(dist, 4),
        })

    top_10 = all_incidents[:10]
    return all_incidents, top_10

def compute_query_distribution(incidents: list[dict]) -> dict[str, float]:
    counts: dict[int, int] = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    for incident in incidents:
        cls = incident["severity_outcome"].value
        counts[cls] += 1
    total = len(incidents)
    return {
        str(k): round((v / total) * 100, 2)
        for k, v in counts.items()
    }

def load_base_rate_distribution() -> dict[str, float]:
    with open(DISTRIBUTION_PATH, "r") as f:
        raw = json.load(f)
    return {
        k: v["percentage"]
        for k, v in raw["severity_distribution"].items()
    }

def find_patterns(narrative: str) -> dict:
    all_incidents, top_10 = search_similar_incidents(narrative)
    severity_distribution = compute_query_distribution(all_incidents)

    return {
        "similar_incidents": top_10,
        "severity_distribution": severity_distribution,
        "injury_mechanism": "Not extractable from current dataset — OSHA H&C records contain narrative text and severity labels only. Activity patterns are visible in the similar incidents above.",
    }