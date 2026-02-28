"""
Sentence-transformer wrapper for consistent embedding generation
across all CineSocial components.

Model: all-MiniLM-L6-v2 (384 dimensions, fast CPU inference)
"""
import numpy as np
from sentence_transformers import SentenceTransformer


class CineSocialEmbedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = 384

    def embed_movie(
        self,
        title: str,
        overview: str,
        genres: list[str],
        director: str | None = None,
        cast: list[str] | None = None,
        keywords: list[str] | None = None,
    ) -> np.ndarray:
        """Create a composite movie embedding from metadata."""
        parts = [title, overview or ""]
        if genres:
            parts.append(f"Genres: {', '.join(genres)}")
        if director:
            parts.append(f"Director: {director}")
        if cast:
            parts.append(f"Cast: {', '.join(cast[:5])}")
        if keywords:
            parts.append(f"Keywords: {', '.join(keywords)}")
        text = ". ".join(parts)
        return self.model.encode(text, normalize_embeddings=True)

    def embed_review(self, review_text: str) -> np.ndarray:
        return self.model.encode(review_text, normalize_embeddings=True)

    def embed_query(self, query: str) -> np.ndarray:
        return self.model.encode(query, normalize_embeddings=True)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True, batch_size=32)

    def compute_user_preference_vector(
        self, movie_embeddings: list[np.ndarray], ratings: list[float]
    ) -> np.ndarray:
        """
        User preference = weighted average of rated movie embeddings.
        u_vec = SUM(r_i/10 * emb_i) / N, then L2 normalized.
        """
        if not movie_embeddings:
            return np.zeros(self.dimension)

        weights = np.array(ratings) / 10.0
        embeddings = np.array(movie_embeddings)
        weighted = embeddings * weights[:, np.newaxis]
        avg = weighted.mean(axis=0)

        norm = np.linalg.norm(avg)
        return avg / norm if norm > 0 else avg
