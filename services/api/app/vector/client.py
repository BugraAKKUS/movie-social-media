from qdrant_client import AsyncQdrantClient

from app.config import settings

_client = None


async def get_qdrant_client() -> AsyncQdrantClient:
    global _client
    if _client is None:
        _client = AsyncQdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
    return _client


async def close_qdrant_client():
    global _client
    if _client:
        await _client.close()
        _client = None
