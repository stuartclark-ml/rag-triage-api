import csv
import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

CSV_PATH = Path("data/csv/osha_hc_incidents.csv")
DISTRIBUTION_PATH = Path("data/osha_severity_distribution.json")
CHROMA_PATH = Path("vectorstore/osha")
COLLECTION_NAME = "osha_hc_incidents"
BATCH_SIZE = 256


def clean_narrative(text: str) -> str:
    if "[SEP]" in text:
        parts = text.split("[SEP]")
        parts = [p.strip() for p in parts]
        if parts[0].startswith("Organisation size:"):
            parts = parts[1:]
        return " ".join(parts).strip()
    return text.strip()


def load_and_clean(csv_path: Path) -> list[dict]:
    records = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            narrative = clean_narrative(row["final_narrative_size"])
            if narrative:
                records.append({
                    "severity_bin": row["severity_bin"].strip(),
                    "narrative": narrative,
                })
    return records


def compute_distribution(records: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for record in records:
        severity = record["severity_bin"]
        counts[severity] = counts.get(severity, 0) + 1
    total = len(records)
    distribution = {}
    for severity in sorted(counts.keys()):
        count = counts[severity]
        distribution[severity] = {
            "count": count,
            "percentage": round((count / total) * 100, 2),
        }
    return {"total_records": total, "severity_distribution": distribution}


def ingest(records: list[dict], chroma_path: Path) -> None:
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(
        path=str(chroma_path),
        settings=Settings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(COLLECTION_NAME)

    narratives = [r["narrative"] for r in records]
    severities = [r["severity_bin"] for r in records]
    total = len(narratives)

    for batch_start in range(0, total, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total)
        batch_narratives = narratives[batch_start:batch_end]
        batch_severities = severities[batch_start:batch_end]

        embeddings = model.encode(
            batch_narratives,
            show_progress_bar=False,
        ).tolist()

        ids = [f"osha_{batch_start + i}" for i in range(len(batch_narratives))]
        metadatas = [{"severity_bin": s} for s in batch_severities]

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=batch_narratives,
            metadatas=metadatas,  # type: ignore[arg-type]
        )


def main() -> None:
    print("Loading and cleaning CSV...")
    records = load_and_clean(CSV_PATH)
    print(f"Loaded {len(records)} records")

    print("\nComputing severity distribution...")
    distribution = compute_distribution(records)
    DISTRIBUTION_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DISTRIBUTION_PATH, "w", encoding="utf-8") as f:
        json.dump(distribution, f, indent=2)
    print(f"Distribution saved to {DISTRIBUTION_PATH}")
    for severity, stats in distribution["severity_distribution"].items():
        print(f"  Class {severity}: {stats['count']} records ({stats['percentage']}%)")

    print(f"\nEmbedding and ingesting {len(records)} records to ChromaDB...")
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    ingest(records, CHROMA_PATH)
    print("\nOSHA ingestion complete.")


if __name__ == "__main__":
    main()