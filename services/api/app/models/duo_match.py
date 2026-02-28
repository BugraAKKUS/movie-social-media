import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DuoMatchSession(Base):
    """
    Duo-Match session with consent state machine.

    States: pending_partner_consent → both_consented → analyzing →
            recommendations_ready → viewed → expired
            Any state → declined | revoked (terminal)
    """
    __tablename__ = "duo_match_sessions"
    __table_args__ = (
        UniqueConstraint("initiator_id", "partner_id", name="uq_duo_match_pair"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    initiator_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    partner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    state: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending_partner_consent", index=True
    )

    # Consent timestamps
    initiator_consented_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    partner_consented_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Temporary data lifecycle
    temp_data_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    temp_data_deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    data_expiry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)

    # Results (cleared on revoke/expire)
    recommendations: Mapped[dict | list | None] = mapped_column(JSON)
    recommendations_generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class DuoMatchTempDMIndex(Base):
    """
    Temporary indexed preference signals extracted from DMs.
    Auto-deleted when session moves past 'analyzing' state.
    Raw messages are NEVER stored — only extracted signals.
    """
    __tablename__ = "duo_match_temp_dm_index"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("duo_match_sessions.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    # Extracted preference signals: {genres: {}, moods: {}, mentions: []}
    preference_signals: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
