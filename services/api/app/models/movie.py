import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Integer, Numeric, Date, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tmdb_id: Mapped[int | None] = mapped_column(Integer, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    original_title: Mapped[str | None] = mapped_column(String(500))
    overview: Mapped[str | None] = mapped_column(Text)
    release_date: Mapped[datetime | None] = mapped_column(Date)
    runtime_minutes: Mapped[int | None] = mapped_column(Integer)
    poster_url: Mapped[str | None] = mapped_column(Text)
    backdrop_url: Mapped[str | None] = mapped_column(Text)
    genres: Mapped[dict | list] = mapped_column(JSON, default=list)
    keywords: Mapped[dict | list] = mapped_column(JSON, default=list)
    cast_list: Mapped[dict | list] = mapped_column(JSON, default=list)
    director: Mapped[str | None] = mapped_column(String(255))
    avg_rating: Mapped[float] = mapped_column(Numeric(4, 2), default=0.0)
    rating_count: Mapped[int] = mapped_column(Integer, default=0)
    content_vector_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    ratings: Mapped[list["Rating"]] = relationship(back_populates="movie", cascade="all, delete-orphan")  # type: ignore[name-defined]
    reviews: Mapped[list["Review"]] = relationship(back_populates="movie", cascade="all, delete-orphan")  # type: ignore[name-defined]
