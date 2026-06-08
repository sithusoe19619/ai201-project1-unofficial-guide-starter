"""
embed.py — Milestone 4: embed chunks into ChromaDB and retrieve.

Run once to build the index:
    python embed.py

Then import retrieve() in test_retrieval.py and Milestone 5.
"""

import json
from sentence_transformers import SentenceTransformer
import chromadb

CHUNKS_PATH = "documents/chunks.json"
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "unofficial_guide"
MODEL_NAME = "all-MiniLM-L6-v2"

_model = None       # lazy-loaded so imports don't trigger a download
_collection = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"Loading embedding model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def embed_and_store(chunks_path: str = CHUNKS_PATH) -> int:
    """
    Load chunks.json, embed all texts with all-MiniLM-L6-v2, store in ChromaDB.
    Returns the number of chunks stored.
    """
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    model = _get_model()
    texts = [c["text"] for c in chunks]

    print(f"Embedding {len(chunks)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True)

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Delete existing collection so re-runs start clean
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Deleted existing collection.")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    ids = [
        f"{c['metadata']['source_name']}_{c['metadata']['chunk_index']}"
        for c in chunks
    ]
    metadatas = [c["metadata"] for c in chunks]

    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=metadatas,
    )

    global _collection
    _collection = collection

    print(f"✓ Stored {len(chunks)} chunks in ChromaDB at '{CHROMA_PATH}/'")
    return len(chunks)


def retrieve(query: str, k: int = 5) -> list[dict]:
    """
    Embed query string, return the top-k most relevant chunks.

    Each result is a dict:
        {"text": str, "metadata": dict, "distance": float}

    Distance is cosine distance (0 = identical, 1 = unrelated).
    Results are ordered closest-first.
    """
    model = _get_model()
    collection = _get_collection()

    query_embedding = model.encode([query])

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=k,
    )

    # collection.query() returns list-of-lists because ChromaDB supports
    # batching multiple queries at once. We always send one query, so
    # index [0] gives the result list for our single query.
    output = []
    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        output.append({
            "text": text,
            "metadata": metadata,
            "distance": round(distance, 4),
        })
    return output


def main():
    embed_and_store()

    # Quick sanity check after embedding
    print("\nSanity check — 'Pell Grant maximum award amount':")
    for r in retrieve("Pell Grant maximum award amount", k=3):
        m = r["metadata"]
        print(
            f"  [{r['distance']}] {m['source_name']} "
            f"chunk {m['chunk_index'] + 1}/{m['total_chunks']} — "
            f"{r['text'][:120]}"
        )

    print("\n✓ Milestone 4 embedding complete. Run test_retrieval.py next.\n")


if __name__ == "__main__":
    main()
