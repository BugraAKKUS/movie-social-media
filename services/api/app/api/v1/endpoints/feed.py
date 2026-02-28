from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.review import Review

router = APIRouter()


@router.get("/")
async def get_feed(
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=50),
    type: str = Query("algorithmic", pattern="^(algorithmic|chronological)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the discovery feed.

    For MVP, returns reviews sorted by recency.
    TODO: Implement full feed ranking algorithm:
      feed_score = 0.30*relevance + 0.25*engagement_velocity
                 + 0.20*social_proximity + 0.15*freshness
                 + 0.10*diversity_bonus
    """
    query = select(Review).order_by(Review.created_at.desc())

    if cursor:
        # Cursor-based pagination: cursor is a created_at timestamp
        query = query.where(Review.created_at < cursor)

    query = query.limit(limit + 1)  # Fetch one extra to check for next page
    result = await db.execute(query)
    reviews = list(result.scalars().all())

    has_next = len(reviews) > limit
    if has_next:
        reviews = reviews[:limit]

    next_cursor = reviews[-1].created_at.isoformat() if reviews and has_next else None

    return {
        "items": reviews,
        "next_cursor": next_cursor,
    }
