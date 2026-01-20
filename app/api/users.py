from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import User
from app.schemas.user import UserResponse, MBTIUpdate, VALID_MBTI_TYPES

router = APIRouter()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """사용자 정보 조회"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.patch("/{user_id}/mbti", response_model=UserResponse)
async def update_user_mbti(
    user_id: UUID,
    mbti_data: MBTIUpdate,
    db: AsyncSession = Depends(get_db),
):
    """사용자 MBTI 업데이트"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.mbti = mbti_data.mbti
    await db.commit()
    await db.refresh(user)

    return user
