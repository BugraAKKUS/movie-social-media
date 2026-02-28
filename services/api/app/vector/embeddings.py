"""
Sentence-transformer embedding service for the API layer.
Lazy-loads the model on first use.
"""
import numpy as np

from app.config import settings

_model = None


def get_embedding_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.embedding_model_name)
    return _model


def embed_text(text: str) -> list[float]:
    """Embed a single text string. Returns 384-dimensional vector."""
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def embed_movie(
    title: str,
    overview: str,
    genres: list[str],
    director: str | None = None,
    cast: list[str] | None = None,
    keywords: list[str] | None = None,
) -> list[float]:
    """Create a composite movie embedding."""
    parts = [title, overview or ""]
    if genres:
        parts.append(f"Genres: {', '.join(genres)}")
    if director:
        parts.append(f"Director: {director}")
    if cast:
        parts.append(f"Cast: {', '.join(cast[:5])}")
    if keywords:
        parts.append(f"Keywords: {', '.join(keywords)}")
    return embed_text(". ".join(parts))


def compute_user_preference_vector(
    movie_embeddings: list[list[float]], ratings: list[float]
) -> list[float]:
    """
    Compute weighted average of movie embeddings, weighted by normalized rating.
    u_vec = SUM(r_i/10 * emb_i) / N
    """
    if not movie_embeddings:
        return [0.0] * 384

    embeddings = np.array(movie_embeddings)
    weights = np.array(ratings) / 10.0
    weighted = embeddings * weights[:, np.newaxis]
    avg = weighted.mean(axis=0)

    norm = np.linalg.norm(avg)
    if norm > 0:
        avg = avg / norm

    return avg.tolist()
