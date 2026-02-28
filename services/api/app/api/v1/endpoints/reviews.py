from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.review import CreateReviewRequest, ReviewResponse
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.review import Review
from app.models.watched_with import WatchedWith
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=ReviewResponse)
async def create_review(
    body: CreateReviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    review = Review(
        user_id=current_user.id,
        movie_id=body.movie_id,
        content_text=body.content_text,
        video_url=body.video_url,
    )
    db.add(review)
    await db.flush()

    # TODO: Run spoiler detection on review.content_text
    # result = await spoiler_service.detect(review.content_text, movie_title)
    # review.spoiler_score = result.overall_score
    # review.is_spoiler = result.is_spoiler
    # review.spoiler_spans = [s.model_dump() for s in result.spans]

    # Create "Watched With" tags
    if body.watched_with_user_ids:
        for tagged_id in body.watched_with_user_ids:
            tag = WatchedWith(
                review_id=review.id,
                user_id=current_user.id,
                tagged_user_id=tagged_id,
            )
            db.add(tag)

    await db.flush()

    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        movie_id=review.movie_id,
        content_text=review.content_text,
        video_url=review.video_url,
        spoiler_score=float(review.spoiler_score),
        is_spoiler=review.is_spoiler,
        spoiler_spans=review.spoiler_spans or [],
        published_from_chat=review.published_from_chat,
        like_count=review.like_count,
        comment_count=review.comment_count,
        view_count=review.view_count,
        created_at=review.created_at.isoformat(),
    )


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise NotFoundError("Review not found")

    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        movie_id=review.movie_id,
        content_text=review.content_text,
        video_url=review.video_url,
        spoiler_score=float(review.spoiler_score),
        is_spoiler=review.is_spoiler,
        spoiler_spans=review.spoiler_spans or [],
        published_from_chat=review.published_from_chat,
        like_count=review.like_count,
        comment_count=review.comment_count,
        view_count=review.view_count,
        created_at=review.created_at.isoformat(),
    )


@router.get("/movie/{movie_id}")
async def get_movie_reviews(movie_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Review)
        .where(Review.movie_id == movie_id)
        .order_by(Review.created_at.desc())
    )
    return result.scalars().all()
