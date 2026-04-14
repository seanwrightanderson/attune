"""
RAG (Retrieval-Augmented Generation) service for Attune.

Uses ChromaDB locally in development. To swap for Pinecone in production,
replace the get_collection() function and the search() method.
"""

from typing import Optional, List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from services.embeddings import embed_text, embed_texts
from config import get_settings

settings = get_settings()

COLLECTION_NAME = "attune_music_theory"

_chroma_client = None


def get_chroma_client() -> chromadb.ClientAPI:
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _chroma_client


def get_collection() -> chromadb.Collection:
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


async def add_documents(
    documents: List[str],
    metadatas: List[dict],
    ids: List[str],
) -> None:
    """Embed and store documents in the vector store."""
    embeddings = await embed_texts(documents)
    collection = get_collection()
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )
    print(f"[RAG] Added {len(documents)} documents to collection.")


async def search(
    query: str,
    top_k: Optional[int] = None,
    where: Optional[dict] = None,
) -> List[dict]:
    """
    Semantic search over the knowledge base.
    Returns a list of dicts: {document, metadata, distance}
    """
    k = top_k or settings.rag_top_k
    query_embedding = await embed_text(query)
    collection = get_collection()

    kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": k,
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        kwargs["where"] = where

    results = collection.query(**kwargs)

    output = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        output.append({"document": doc, "metadata": meta, "distance": dist})

    return output


def collection_count() -> int:
    return get_collection().count()
