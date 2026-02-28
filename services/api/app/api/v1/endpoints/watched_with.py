from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.watched_with import WatchedWith
from app.models.user import User

router = APIRouter()


@router.post("/{tag_id}/confirm")
async def confirm_watched_with(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Tagged user confirms the 'Watched With' tag."""
    result = await db.execute(select(WatchedWith).where(WatchedWith.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise NotFoundError("Tag not found")

    if tag.tagged_user_id != current_user.id:
        raise ForbiddenError("Only the tagged user can confirm")

    tag.confirmed = True
    tag.confirmed_at = datetime.now(timezone.utc)
    await db.flush()

    # TODO: Create Neo4j WATCHED_WITH edge between the two users
    return tag


@router.delete("/{tag_id}")
async def delete_watched_with(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(WatchedWith).where(WatchedWith.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise NotFoundError("Tag not found")

    if current_user.id not in (tag.user_id, tag.tagged_user_id):
        raise ForbiddenError("Not authorized to delete this tag")

    await db.delete(tag)
    return {"deleted": True}


@router.get("/user/{user_id}")
async def get_user_watched_with(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WatchedWith)
        .where(
            (WatchedWith.user_id == user_id) | (WatchedWith.tagged_user_id == user_id)
        )
        .order_by(WatchedWith.created_at.desc())
    )
    return result.scalars().all()
