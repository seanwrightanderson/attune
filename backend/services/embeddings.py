from typing import List
from openai import AsyncOpenAI
from config import get_settings

settings = get_settings()
_client = None


def get_openai_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def embed_text(text: str) -> List[float]:
    """Embed a single string using OpenAI text-embedding-3-small."""
    client = get_openai_client()
    response = await client.embeddings.create(
        model=settings.embedding_model,
        input=text.replace("\n", " "),
    )
    return response.data[0].embedding


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed multiple strings in one API call."""
    client = get_openai_client()
    cleaned = [t.replace("\n", " ") for t in texts]
    response = await client.embeddings.create(
        model=settings.embedding_model,
        input=cleaned,
    )
    return [item.embedding for item in response.data]
