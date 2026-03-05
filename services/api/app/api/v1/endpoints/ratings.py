from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.rating import (
    CreateRatingRequest, UpdateRatingRequest, RatingResponse, MovieRatingAggregateResponse,
)
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.rating import Rating
from app.models.movie import Movie
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=RatingResponse)
async def create_rating(
    body: CreateRatingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Upsert: update if exists, create if not
    result = await db.execute(
        select(Rating).where(
            Rating.user_id == current_user.id,
            Rating.movie_id == body.movie_id,
        )
    )
    rating = result.scalar_one_or_none()

    if rating:
        rating.score = body.score
    else:
        rating = Rating(
            user_id=current_user.id,
            movie_id=body.movie_id,
            score=body.score,
        )
        db.add(rating)

    await db.flush()

    # Update movie aggregate
    agg = await db.execute(
        select(
            func.avg(Rating.score).label("avg"),
            func.count(Rating.id).label("count"),
        ).where(Rating.movie_id == body.movie_id)
    )
    row = agg.one()
    movie_result = await db.execute(select(Movie).where(Movie.id == body.movie_id))
    movie = movie_result.scalar_one_or_none()
    if movie:
        movie.avg_rating = round(float(row.avg or 0), 2)
        movie.rating_count = row.count

    return RatingResponse(
        id=rating.id,
        user_id=rating.user_id,
        movie_id=rating.movie_id,
        score=float(rating.score),
        created_at=rating.created_at.isoformat(),
        updated_at=rating.updated_at.isoformat(),
    )


@router.get("/movie/{movie_id}", response_model=MovieRatingAggregateResponse)
async def get_movie_ratings(
    movie_id: str,
    db: AsyncSession = Depends(get_db),
):
    agg = await db.execute(
        select(
            func.avg(Rating.score).label("avg"),
            func.count(Rating.id).label("count"),
        ).where(Rating.movie_id == movie_id)
    )
    row = agg.one()

    return MovieRatingAggregateResponse(
        avg_score=round(float(row.avg or 0), 2),
        count=row.count,
        user_rating=None,
    )


@router.get("/user/{user_id}")
async def get_user_ratings(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Rating)
        .where(Rating.user_id == user_id)
        .order_by(Rating.updated_at.desc())
    )
    return result.scalars().all()
