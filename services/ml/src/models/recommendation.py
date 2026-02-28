"""
Neural Collaborative Filtering model for CineSocial.

Used for:
1. Single-user movie recommendations (predict rating)
2. Duo-Match joint recommendations (combine two user vectors)

Mathematical Formulation for Duo-Match Joint Score:
    J(u1, u2, m) = 0.35 * min(r̂(u1,m), r̂(u2,m))     # Pareto fairness
                 + 0.30 * avg(r̂(u1,m), r̂(u2,m))       # Average enjoyment
                 + 0.15 * novelty(u1, u2, m)             # Unseen bonus
                 + 0.20 * dm_signal(u1, u2, m)           # DM preference signal
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class UserMovieEncoder(nn.Module):
    """
    Encodes user and movie features into a shared embedding space.

    User features -> FC(input, 128) -> ReLU -> Dropout -> FC(128, 64)
    Movie features -> FC(input, 128) -> ReLU -> Dropout -> FC(128, 64)
    Rating = sigmoid(MLP(concat(user_emb, movie_emb))) * 10
    """

    def __init__(
        self,
        user_feature_dim: int,
        movie_feature_dim: int,
        embedding_dim: int = 64,
    ):
        super().__init__()
        self.embedding_dim = embedding_dim

        self.user_encoder = nn.Sequential(
            nn.Linear(user_feature_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, embedding_dim),
        )

        self.movie_encoder = nn.Sequential(
            nn.Linear(movie_feature_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, embedding_dim),
        )

        # Rating prediction head: concat(user, movie) -> predicted rating [0, 10]
        self.rating_head = nn.Sequential(
            nn.Linear(embedding_dim * 2, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid(),  # Output in [0, 1], scaled to [0, 10]
        )

    def encode_user(self, user_features: torch.Tensor) -> torch.Tensor:
        return F.normalize(self.user_encoder(user_features), dim=-1)

    def encode_movie(self, movie_features: torch.Tensor) -> torch.Tensor:
        return F.normalize(self.movie_encoder(movie_features), dim=-1)

    def predict_rating(
        self, user_emb: torch.Tensor, movie_emb: torch.Tensor
    ) -> torch.Tensor:
        """Predict rating on 0-10 scale."""
        combined = torch.cat([user_emb, movie_emb], dim=-1)
        return self.rating_head(combined) * 10.0

    def forward(
        self,
        user_features: torch.Tensor,
        movie_features: torch.Tensor,
        target_ratings: torch.Tensor | None = None,
    ) -> dict:
        user_emb = self.encode_user(user_features)
        movie_emb = self.encode_movie(movie_features)
        predicted_ratings = self.predict_rating(user_emb, movie_emb)

        loss = None
        if target_ratings is not None:
            loss = F.mse_loss(predicted_ratings.squeeze(), target_ratings)

        return {
            "loss": loss,
            "predicted_ratings": predicted_ratings,
            "user_embeddings": user_emb,
            "movie_embeddings": movie_emb,
        }


def compute_joint_score(
    r_hat_u1: float,
    r_hat_u2: float,
    novelty: float,
    dm_signal: float,
    w_min: float = 0.35,
    w_avg: float = 0.30,
    w_novel: float = 0.15,
    w_dm: float = 0.20,
) -> float:
    """
    Compute Duo-Match joint utility score for a movie.

    Args:
        r_hat_u1: Predicted rating for user 1 (0-10)
        r_hat_u2: Predicted rating for user 2 (0-10)
        novelty: Novelty score (0-1)
        dm_signal: DM-derived preference signal (0-1)
        w_min: Weight for Pareto fairness (min of two ratings)
        w_avg: Weight for average enjoyment
        w_novel: Weight for novelty bonus
        w_dm: Weight for DM preference signal

    Returns:
        Joint score in [0, 10] range
    """
    pareto = min(r_hat_u1, r_hat_u2)
    avg = (r_hat_u1 + r_hat_u2) / 2.0

    return w_min * pareto + w_avg * avg + w_novel * novelty * 10 + w_dm * dm_signal * 10


def compute_novelty(
    u1_rated: set[str], u2_rated: set[str], movie_id: str
) -> float:
    """
    Compute novelty score for a movie given two users' rating histories.

    Returns:
        1.0 if neither has rated, 0.3 if exactly one rated it highly, 0.0 if both rated
    """
    u1_seen = movie_id in u1_rated
    u2_seen = movie_id in u2_rated

    if not u1_seen and not u2_seen:
        return 1.0
    if u1_seen and u2_seen:
        return 0.0
    return 0.3


def rank_duo_match_candidates(
    model: UserMovieEncoder,
    user1_features: torch.Tensor,
    user2_features: torch.Tensor,
    candidate_features: torch.Tensor,
    candidate_ids: list[str],
    u1_rated: set[str],
    u2_rated: set[str],
    dm_signals: dict[str, float] | None = None,
    top_k: int = 10,
    min_score_threshold: float = 5.0,
) -> list[dict]:
    """
    Rank candidate movies for Duo-Match using joint-utility scoring.

    Returns top-K recommendations sorted by joint score.
    """
    model.eval()
    with torch.no_grad():
        u1_emb = model.encode_user(user1_features.unsqueeze(0))
        u2_emb = model.encode_user(user2_features.unsqueeze(0))

        movie_embs = model.encode_movie(candidate_features)

        u1_ratings = model.predict_rating(
            u1_emb.expand(len(candidate_ids), -1), movie_embs
        ).squeeze()
        u2_ratings = model.predict_rating(
            u2_emb.expand(len(candidate_ids), -1), movie_embs
        ).squeeze()

    results = []
    for i, movie_id in enumerate(candidate_ids):
        r1 = u1_ratings[i].item()
        r2 = u2_ratings[i].item()

        # Filter: neither user should be predicted to dislike
        if min(r1, r2) < min_score_threshold:
            continue

        novelty = compute_novelty(u1_rated, u2_rated, movie_id)
        dm_sig = (dm_signals or {}).get(movie_id, 0.0)

        joint = compute_joint_score(r1, r2, novelty, dm_sig)
        results.append({
            "movie_id": movie_id,
            "joint_score": round(joint, 2),
            "user1_predicted_rating": round(r1, 1),
            "user2_predicted_rating": round(r2, 1),
            "novelty": novelty,
        })

    results.sort(key=lambda x: x["joint_score"], reverse=True)
    return results[:top_k]
