from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.movie import Movie

router = APIRouter()


@router.get("/")
async def list_movies(
    q: str | None = Query(None, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(Movie)
    if q:
        query = query.where(Movie.title.ilike(f"%{q}%"))
    query = query.order_by(Movie.avg_rating.desc()).offset(offset).limit(limit)

    result = await db.execute(query)
    movies = result.scalars().all()
    return movies


@router.get("/{movie_id}")
async def get_movie(movie_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Movie).where(Movie.id == movie_id))
    movie = result.scalar_one_or_none()
    if not movie:
        raise NotFoundError("Movie not found")
    return movie
