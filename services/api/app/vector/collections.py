"""
Qdrant collection definitions and management.
All collections use 384-dimensional vectors (all-MiniLM-L6-v2).
"""
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

from app.vector.client import get_qdrant_client

VECTOR_SIZE = 384

COLLECTIONS = {
    "movie_embeddings": {
        "vectors": VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        "payload_schema": {
            "movie_id": PayloadSchemaType.KEYWORD,
            "tmdb_id": PayloadSchemaType.INTEGER,
            "title": PayloadSchemaType.TEXT,
            "genres": PayloadSchemaType.KEYWORD,
            "release_year": PayloadSchemaType.INTEGER,
            "avg_rating": PayloadSchemaType.FLOAT,
        },
    },
    "user_preferences": {
        "vectors": VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        "payload_schema": {
            "user_id": PayloadSchemaType.KEYWORD,
            "top_genres": PayloadSchemaType.KEYWORD,
            "avg_rating_given": PayloadSchemaType.FLOAT,
            "rating_count": PayloadSchemaType.INTEGER,
        },
    },
    "review_embeddings": {
        "vectors": VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        "payload_schema": {
            "review_id": PayloadSchemaType.KEYWORD,
            "user_id": PayloadSchemaType.KEYWORD,
            "movie_id": PayloadSchemaType.KEYWORD,
            "is_spoiler": PayloadSchemaType.BOOL,
            "rating_score": PayloadSchemaType.FLOAT,
        },
    },
    "chat_embeddings": {
        "vectors": VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        "payload_schema": {
            "message_id": PayloadSchemaType.KEYWORD,
            "conversation_id": PayloadSchemaType.KEYWORD,
            "user_id": PayloadSchemaType.KEYWORD,
            "movie_id": PayloadSchemaType.KEYWORD,
            "role": PayloadSchemaType.KEYWORD,
        },
    },
}


async def ensure_collections():
    """Create all Qdrant collections if they don't exist."""
    client = await get_qdrant_client()
    existing = await client.get_collections()
    existing_names = {c.name for c in existing.collections}

    for name, config in COLLECTIONS.items():
        if name not in existing_names:
            await client.create_collection(
                collection_name=name,
                vectors_config=config["vectors"],
            )
