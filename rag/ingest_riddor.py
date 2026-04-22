from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
from rag.build_riddor import extract_regulations, build_chunks, build_schedule_chunks

VECTORSTORE_PATH = Path("vectorstore/riddor")
COLLECTION_NAME = "riddor"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
PDF_PATH = "data/documents/riddor.pdf"


def main():
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    print("Extracting regulations from main body (pages 0-12)")
    raw_regs = extract_regulations(PDF_PATH, 0, 12)
    reg_chunks = build_chunks(raw_regs)
    print(f"Regulation chunks ready: {len(reg_chunks)}")

    print("Extracting Schedule 2 categories (pages 15-17)")
    raw_cats = extract_regulations(PDF_PATH, 15, 17)
    schedule_chunks = build_schedule_chunks(raw_cats)
    print(f"Schedule chunks ready: {len(schedule_chunks)}")

    all_chunks = reg_chunks + schedule_chunks
    print(f"Total chunks to ingest: {len(all_chunks)}")

    print(f"Initialising Chroma at {VECTORSTORE_PATH}")
    VECTORSTORE_PATH.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(VECTORSTORE_PATH))

    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        print(f"Deleting existing collection: {COLLECTION_NAME}")
        client.delete_collection(COLLECTION_NAME)

    collection = client.create_collection(name=COLLECTION_NAME)

    print("Embedding chunk text and adding to collection")
    embeddings = model.encode(
        [c["text"] for c in all_chunks],
        show_progress_bar=True,
    ).tolist()

    collection.add(
        ids=[c["chunk_id"] for c in all_chunks],
        documents=[c["text"] for c in all_chunks],
        embeddings=embeddings,
        metadatas=[
            {
                "chunk_id": c["chunk_id"],
                "chunk_type": c["chunk_type"],
                "title": c["title"],
                "reporting_deadline": c.get("reporting_deadline") or "",
                "reporting_route": c.get("reporting_route") or "",
                "parent_regulation": c.get("parent_regulation") or "",
                "omission_note": c.get("omission_note") or "",
            }
            for c in all_chunks
        ],
    )

    print(f"\nIngestion complete: {collection.count()} chunks stored in {VECTORSTORE_PATH}")


if __name__ == "__main__":
    main()