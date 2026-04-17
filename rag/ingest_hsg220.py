from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
from rag.build_hsg220 import build_chapters, PDF_PATH

VECTORSTORE_PATH = Path("vectorstore/hsg220")
COLLECTION_NAME = "hsg220"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def ingest():
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    print(f"Building chapters from {PDF_PATH}")
    chapters = build_chapters(PDF_PATH)
    print(f"Chapters ready: {len(chapters)}")

    print(f"Initialising Chroma at {VECTORSTORE_PATH}")
    VECTORSTORE_PATH.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(VECTORSTORE_PATH))

    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        print(f"Deleting existing collection: {COLLECTION_NAME}")
        client.delete_collection(COLLECTION_NAME)

    collection = client.create_collection(name=COLLECTION_NAME)

    print("Embedding curated strings and adding to collection")
    embedding_strings = [ch["embedding_string"] for ch in chapters]
    embeddings = model.encode(embedding_strings, show_progress_bar=True).tolist()

    collection.add(
        ids=[ch["chapter_key"] for ch in chapters],
        documents=[ch["text"] for ch in chapters],
        embeddings=embeddings,
        metadatas=[{"chapter": ch["chapter_key"], "pages": ch["pages"]} for ch in chapters],
    )

    print(f"\nIngestion complete: {collection.count()} chunks stored in {VECTORSTORE_PATH}")


if __name__ == "__main__":
    ingest()