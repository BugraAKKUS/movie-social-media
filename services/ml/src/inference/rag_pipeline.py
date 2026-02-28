"""
Multimodal RAG pipeline for the AI Film Companion chat.

Processes three data sources:
1. Movie Metadata (from Qdrant movie_embeddings)
2. User Rating History (from PostgreSQL + user_preferences collection)
3. Chat History (from Qdrant chat_embeddings)

Total context budget: ~2000 tokens
"""
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from services.ml.src.models.embedding_model import CineSocialEmbedder


class RAGPipeline:
    def __init__(
        self,
        embedder: CineSocialEmbedder,
        qdrant: AsyncQdrantClient,
    ):
        self.embedder = embedder
        self.qdrant = qdrant

    async def assemble_context(
        self,
        query: str,
        user_id: str,
        movie_id: str | None = None,
        conversation_id: str | None = None,
    ) -> str:
        """
        Assemble RAG context from multiple Qdrant collections.

        Returns a formatted context string ready for LLM prompting.
        """
        query_embedding = self.embedder.embed_query(query).tolist()

        # 1. Similar movies (~400 tokens)
        movie_results = await self.qdrant.search(
            collection_name="movie_embeddings",
            query_vector=query_embedding,
            limit=5,
        )

        # 2. Relevant reviews, excluding spoilers (~500 tokens)
        review_filter = Filter(
            must=[FieldCondition(key="is_spoiler", match=MatchValue(value=False))]
        )
        review_results = await self.qdrant.search(
            collection_name="review_embeddings",
            query_vector=query_embedding,
            query_filter=review_filter,
            limit=5,
        )

        # 3. Past chat context for this user (~600 tokens)
        chat_results = []
        if conversation_id:
            chat_filter = Filter(
                must=[
                    FieldCondition(
                        key="conversation_id",
                        match=MatchValue(value=conversation_id),
                    ),
                ]
            )
            chat_results = await self.qdrant.search(
                collection_name="chat_embeddings",
                query_vector=query_embedding,
                query_filter=chat_filter,
                limit=3,
            )

        # Assemble context string
        sections = []

        if movie_results:
            movie_context = "**Related Films:**\n"
            for hit in movie_results:
                payload = hit.payload or {}
                movie_context += (
                    f"- {payload.get('title', 'Unknown')} "
                    f"({', '.join(payload.get('genres', []))})"
                    f" — avg rating: {payload.get('avg_rating', 'N/A')}\n"
                )
            sections.append(movie_context)

        if review_results:
            review_context = "**Community Reviews:**\n"
            for hit in review_results[:3]:
                # Include a brief excerpt (first 200 chars of review)
                review_context += f"- (relevance: {hit.score:.2f}) [Review excerpt available]\n"
            sections.append(review_context)

        if chat_results:
            chat_context = "**Previous Conversation:**\n"
            for hit in chat_results:
                payload = hit.payload or {}
                role = payload.get("role", "unknown")
                chat_context += f"- [{role}]: [Previous message, relevance: {hit.score:.2f}]\n"
            sections.append(chat_context)

        return "\n".join(sections)

    def build_system_prompt(self, context: str, movie_title: str | None = None) -> str:
        """Build the system prompt for the AI Film Companion."""
        base = (
            "You are CineSocial's AI Film Companion — a knowledgeable, enthusiastic "
            "film discussion partner. You have deep knowledge of cinema history, "
            "filmmaking techniques, and storytelling. Be conversational and engaging. "
            "Reference specific films, directors, and movements when relevant. "
            "Use the provided context to ground your responses in real data.\n\n"
        )

        if movie_title:
            base += f"The user is discussing: **{movie_title}**\n\n"

        if context:
            base += f"Context from CineSocial database:\n{context}\n\n"

        base += (
            "Guidelines:\n"
            "- Be concise but insightful\n"
            "- Avoid spoilers unless the user explicitly asks\n"
            "- Reference community ratings and reviews when available\n"
            "- Suggest related films when appropriate\n"
        )

        return base
