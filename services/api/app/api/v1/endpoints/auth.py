from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.auth import (
    RegisterRequest, LoginRequest, AuthResponse, UserResponse,
)
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import get_password_hash, verify_password, create_access_token
from app.db.session import get_db
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=AuthResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check existing user
    existing = await db.execute(
        select(User).where((User.email == body.email) | (User.username == body.username))
    )
    if existing.scalar_one_or_none():
        raise ConflictError("User with this email or username already exists")

    user = User(
        username=body.username,
        email=body.email,
        password_hash=get_password_hash(body.password),
    )
    db.add(user)
    await db.flush()

    token = create_access_token(data={"sub": user.id})

    return AuthResponse(
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            created_at=user.created_at.isoformat(),
        ),
        access_token=token,
    )


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")

    token = create_access_token(data={"sub": user.id})

    return AuthResponse(
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            created_at=user.created_at.isoformat(),
        ),
        access_token=token,
    )
