import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String, Text, Integer, Boolean, Numeric, DateTime, ForeignKey, JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    movie_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rating_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("ratings.id")
    )
    content_text: Mapped[str | None] = mapped_column(Text)
    video_url: Mapped[str | None] = mapped_column(Text)
    video_thumbnail: Mapped[str | None] = mapped_column(Text)

    # Spoiler detection results
    spoiler_score: Mapped[float] = mapped_column(Numeric(5, 4), default=0.0)
    is_spoiler: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    spoiler_spans: Mapped[dict | list] = mapped_column(JSON, default=list)

    # Source tracking
    published_from_chat: Mapped[bool] = mapped_column(Boolean, default=False)
    chat_message_id: Mapped[str | None] = mapped_column(String(36))

    # Engagement metrics
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    view_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="reviews")  # type: ignore[name-defined]
    movie: Mapped["Movie"] = relationship(back_populates="reviews")  # type: ignore[name-defined]
    watched_with_tags: Mapped[list["WatchedWith"]] = relationship(  # type: ignore[name-defined]
        back_populates="review", cascade="all, delete-orphan"
    )
