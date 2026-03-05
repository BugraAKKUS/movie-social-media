# CineSocial — Duo-Match System Design

## Overview

Duo-Match is a privacy-preserving feature that analyzes preference signals from two users' DM conversation to recommend movies both would enjoy. It uses a joint-utility scoring function with Pareto fairness constraints.

## Consent State Machine

```
                    ┌──────────┐
     User A         │ pending  │          User B
     initiates ──── │ partner  │ ◄─── receives invite
                    │ consent  │
                    └────┬─────┘
                         │ User B consents
                    ┌────▼─────┐
                    │  both    │
                    │consented │
                    └────┬─────┘
                         │ system starts analysis
                    ┌────▼─────┐
                    │analyzing │
                    └────┬─────┘
                         │ ML pipeline completes
              ┌──────────▼──────────┐
              │ recommendations     │
              │ ready               │
              └──────────┬──────────┘
                         │ both users view
                    ┌────▼─────┐
                    │  viewed  │
                    └────┬─────┘
                         │ 24h TTL
                    ┌────▼─────┐
                    │ expired  │
                    └──────────┘

  Any state ──────► declined (partner rejects)
  Any state ──────► revoked  (either party revokes)
```

## Privacy Design

### What We Store
- **Extracted preference signals** only: genre mentions, mood keywords, entity references (actor/director names)
- Example: `{"genres": ["horror", "thriller"], "moods": ["scary", "intense"], "entities": ["Jordan Peele"]}`
- Stored in `duo_match_temp_dm_index` table

### What We Never Store
- Raw DM message content
- Message timestamps or metadata
- Conversation structure or flow

### Data Lifecycle
1. **Extraction**: DM text → NLP keyword extraction → preference signals JSON
2. **Storage**: Temporary table with session foreign key
3. **Deletion triggers**:
   - Both users view results → 24h countdown → auto-delete
   - Either user revokes → immediate deletion
   - Session expires → background cleanup (Celery task every 15 min)

## Joint-Utility Scoring

```
J(u1, u2, m) = 0.35 × min(r̂(u1,m), r̂(u2,m))    # Pareto fairness
             + 0.30 × avg(r̂(u1,m), r̂(u2,m))      # Average enjoyment
             + 0.15 × novelty(u1, u2, m)            # Unseen bonus
             + 0.20 × dm_signal(u1, u2, m)           # DM preference alignment
```

### Component Breakdown

**Pareto Fairness (0.35)**
- Uses `min()` of both predicted ratings
- Ensures neither user gets a movie they'd dislike
- Hard constraint: `min(r̂(u1,m), r̂(u2,m)) >= 5.0`

**Average Enjoyment (0.30)**
- Mean of both predicted ratings
- Maximizes total group satisfaction

**Novelty (0.15)**
- Bonus for movies neither user has seen
- `novelty(u1, u2, m) = (1 - seen(u1,m)) × (1 - seen(u2,m)) × 10`
- Returns 10 if both haven't seen it, 0 otherwise

**DM Signal (0.20)**
- Cosine similarity between DM-extracted preference vector and movie content vector
- Captures specific preferences expressed in conversation
- `dm_signal = cosine_sim(dm_preference_vector, movie_embedding) × 10`

## Recommendation Pipeline

```
Both consent
    │
    ▼
Extract DM preference signals (NLP keyword matching)
    │
    ▼
Build dm_preference_vector (embed extracted signals)
    │
    ▼
Get candidate movies from Qdrant (top-100 by combined user similarity)
    │
    ▼
For each candidate:
    ├── Predict r̂(u1, m) via UserMovieEncoder
    ├── Predict r̂(u2, m) via UserMovieEncoder
    ├── Check min >= 5.0 constraint
    ├── Compute novelty score
    └── Compute dm_signal score
    │
    ▼
Rank by J(u1, u2, m)
    │
    ▼
Return top-10 recommendations with explanations
```

## Neural Collaborative Filtering Model

```
User features ──► UserEncoder ──► 64d user embedding (L2 normalized)
                  FC(in,128)→ReLU→FC(128,64)

Movie features ─► MovieEncoder ─► 64d movie embedding (L2 normalized)
                  FC(in,128)→ReLU→FC(128,64)

Concatenate(user_emb, movie_emb) ──► RatingHead ──► predicted score
                                     FC(128,64)→ReLU→FC(64,1)→Sigmoid×10
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | /duo-match/initiate | Start session, partner receives invite |
| POST | /duo-match/{id}/consent | Partner gives consent |
| POST | /duo-match/{id}/revoke | Either party revokes (triggers cleanup) |
| GET | /duo-match/{id} | Get session state |
| GET | /duo-match/{id}/recommendations | Get results (only if ready) |
