from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.duo_match import (
    InitiateDuoMatchRequest,
    DuoMatchConsentRequest,
    DuoMatchSessionResponse,
)
from app.core.exceptions import NotFoundError, ForbiddenError, ConflictError
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.duo_match import DuoMatchSession, DuoMatchTempDMIndex
from app.models.user import User

router = APIRouter()

# Terminal states that cannot transition
TERMINAL_STATES = {"expired", "declined", "revoked"}


@router.post("/initiate", response_model=DuoMatchSessionResponse)
async def initiate_duo_match(
    body: InitiateDuoMatchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Initiate a Duo-Match session. Creates session in 'pending_partner_consent' state."""
    # Check for existing active session
    existing = await db.execute(
        select(DuoMatchSession).where(
            DuoMatchSession.initiator_id == current_user.id,
            DuoMatchSession.partner_id == body.partner_id,
            ~DuoMatchSession.state.in_(TERMINAL_STATES),
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError("Active Duo-Match session already exists with this user")

    session = DuoMatchSession(
        initiator_id=current_user.id,
        partner_id=body.partner_id,
        state="pending_partner_consent",
        initiator_consented_at=datetime.now(timezone.utc),
    )
    db.add(session)
    await db.flush()

    return _session_response(session)


@router.post("/{session_id}/consent", response_model=DuoMatchSessionResponse)
async def consent_duo_match(
    session_id: str,
    body: DuoMatchConsentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Partner consents or declines the Duo-Match."""
    session = await _get_session(session_id, db)

    if session.partner_id != current_user.id:
        raise ForbiddenError("Only the partner can consent to this session")

    if session.state != "pending_partner_consent":
        raise ConflictError(f"Cannot consent in state: {session.state}")

    if body.consent:
        session.state = "both_consented"
        session.partner_consented_at = datetime.now(timezone.utc)

        # TODO: Trigger ML pipeline to analyze DM history
        # Transition to 'analyzing' and start background task
        session.state = "analyzing"
        session.temp_data_created_at = datetime.now(timezone.utc)
    else:
        session.state = "declined"

    await db.flush()
    return _session_response(session)


@router.post("/{session_id}/revoke", response_model=DuoMatchSessionResponse)
async def revoke_duo_match(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Either party revokes consent. Triggers immediate data cleanup."""
    session = await _get_session(session_id, db)

    if current_user.id not in (session.initiator_id, session.partner_id):
        raise ForbiddenError("Not a participant in this session")

    if session.state in TERMINAL_STATES:
        raise ConflictError(f"Session already in terminal state: {session.state}")

    # Cleanup: delete all temporary data
    await _cleanup_session_data(session, db)

    session.state = "revoked"
    session.temp_data_deleted_at = datetime.now(timezone.utc)
    session.recommendations = None

    await db.flush()
    return _session_response(session)


@router.get("/{session_id}", response_model=DuoMatchSessionResponse)
async def get_duo_match(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await _get_session(session_id, db)

    if current_user.id not in (session.initiator_id, session.partner_id):
        raise ForbiddenError("Not a participant in this session")

    return _session_response(session)


@router.get("/{session_id}/recommendations")
async def get_recommendations(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await _get_session(session_id, db)

    if current_user.id not in (session.initiator_id, session.partner_id):
        raise ForbiddenError("Not a participant in this session")

    if session.state != "recommendations_ready":
        raise ConflictError("Recommendations not yet available")

    # Mark as viewed and start expiry timer
    if session.state == "recommendations_ready":
        session.state = "viewed"
        session.data_expiry_at = datetime.now(timezone.utc) + timedelta(hours=24)

    return session.recommendations or []


async def _get_session(session_id: str, db: AsyncSession) -> DuoMatchSession:
    result = await db.execute(
        select(DuoMatchSession).where(DuoMatchSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise NotFoundError("Duo-Match session not found")
    return session


async def _cleanup_session_data(session: DuoMatchSession, db: AsyncSession):
    """Delete all temporary DM index data for this session."""
    result = await db.execute(
        select(DuoMatchTempDMIndex).where(
            DuoMatchTempDMIndex.session_id == session.id
        )
    )
    for row in result.scalars().all():
        await db.delete(row)

    # TODO: Delete temporary Qdrant vectors tagged with this session_id


def _session_response(session: DuoMatchSession) -> DuoMatchSessionResponse:
    return DuoMatchSessionResponse(
        id=session.id,
        initiator_id=session.initiator_id,
        partner_id=session.partner_id,
        state=session.state,
        initiator_consented_at=session.initiator_consented_at.isoformat() if session.initiator_consented_at else None,
        partner_consented_at=session.partner_consented_at.isoformat() if session.partner_consented_at else None,
        data_expiry_at=session.data_expiry_at.isoformat() if session.data_expiry_at else None,
        recommendations_generated_at=session.recommendations_generated_at.isoformat() if session.recommendations_generated_at else None,
        created_at=session.created_at.isoformat(),
    )
