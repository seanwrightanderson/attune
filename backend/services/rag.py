"""
RAG (Retrieval-Augmented Generation) service for Attune.

Uses a lightweight numpy-based vector store so there's no dependency on
onnxruntime or libstdc++. All embeddings are produced by OpenAI.
"""

from typing import Optional, List
import json
import os
import numpy as np

from services.embeddings import embed_text, embed_texts
from config import get_settings

settings = get_settings()

STORE_FILE = os.path.join(settings.chroma_persist_dir, "store.json")

# In-memory cache: list of {id, document, metadata, embedding}
_store: Optional[List[dict]] = None


def _load_store() -> List[dict]:
    global _store
    if _store is not None:
        return _store
    os.makedirs(settings.chroma_persist_dir, exist_ok=True)
    if os.path.exists(STORE_FILE):
        with open(STORE_FILE, "r") as f:
            _store = json.load(f)
    else:
        _store = []
    return _store


def _save_store() -> None:
    os.makedirs(settings.chroma_persist_dir, exist_ok=True)
    with open(STORE_FILE, "w") as f:
        json.dump(_store, f)


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    norm_a = np.linalg.norm(va)
    norm_b = np.linalg.norm(vb)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))


async def add_documents(
    documents: List[str],
    metadatas: List[dict],
    ids: List[str],
) -> None:
    """Embed and store documents in the vector store."""
    store = _load_store()

    # Remove any existing entries with the same ids
    existing_ids = {entry["id"] for entry in store}
    new_docs = [
        (doc, meta, doc_id)
        for doc, meta, doc_id in zip(documents, metadatas, ids)
        if doc_id not in existing_ids
    ]

    if not new_docs:
        print("[RAG] All documents already in store, skipping.")
        return

    texts = [d[0] for d in new_docs]
    embeddings = await embed_texts(texts)

    for (doc, meta, doc_id), emb in zip(new_docs, embeddings):
        store.append({"id": doc_id, "document": doc, "metadata": meta, "embedding": emb})

    _save_store()
    print(f"[RAG] Added {len(new_docs)} documents to store (total: {len(store)}).")


async def search(
    query: str,
    top_k: Optional[int] = None,
    where: Optional[dict] = None,
) -> List[dict]:
    """
    Semantic search over the knowledge base.
    Returns a list of dicts: {document, metadata, distance}
    """
    store = _load_store()
    if not store:
        return []

    k = top_k or settings.rag_top_k
    query_embedding = await embed_text(query)

    # Filter by metadata if requested
    candidates = store
    if where:
        candidates = [
            entry for entry in store
            if all(entry["metadata"].get(key) == val for key, val in where.items())
        ]

    # Score all candidates
    scored = [
        (entry, _cosine_similarity(query_embedding, entry["embedding"]))
        for entry in candidates
    ]
    scored.sort(key=lambda x: x[1], reverse=True)

    return [
        {
            "document": entry["document"],
            "metadata": entry["metadata"],
            "distance": 1.0 - score,  # cosine distance
        }
        for entry, score in scored[:k]
    ]


def collection_count() -> int:
    return len(_load_store())
