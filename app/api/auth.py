from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import User
from app.schemas.user import UserCreate, UserResponse, Token, GoogleAuthRequest
from app.services.auth_service import create_access_token, verify_google_token

router = APIRouter()


@router.post("/google", response_model=Token)
async def google_auth(
    request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    """Google OAuth 로그인/회원가입"""
    # Google 토큰 검증
    google_user = await verify_google_token(request.id_token)
    if not google_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )

    # 기존 사용자 확인
    result = await db.execute(
        select(User).where(User.google_id == google_user["sub"])
    )
    user = result.scalar_one_or_none()

    # 신규 사용자 생성
    if not user:
        user = User(
            google_id=google_user["sub"],
            email=google_user["email"],
            name=google_user.get("name", "User"),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # JWT 토큰 발급
    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """사용자 생성 (테스트용)"""
    # 기존 사용자 확인
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return existing_user

    user = User(**user_data.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
