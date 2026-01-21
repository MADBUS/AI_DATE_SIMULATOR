from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import User, UserGallery
from app.schemas.user import UserResponse, MBTIUpdate, VALID_MBTI_TYPES


class GalleryImageResponse(BaseModel):
    id: UUID
    image_url: str
    image_type: str
    expression_type: str | None = None
    is_blurred: bool


class GalleryResponse(BaseModel):
    images: list[GalleryImageResponse]


class GalleryImageCreate(BaseModel):
    image_url: str
    image_type: str  # 'expression', 'special', 'ending'
    expression_type: str | None = None

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


@router.get("/{user_id}/gallery", response_model=GalleryResponse)
async def get_user_gallery(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    사용자 갤러리 조회

    - 프리미엄 사용자: 모든 이미지 blur 없음
    - 비프리미엄 사용자: expression은 blur 없음, special/ending은 blur 처리
    """
    result = await db.execute(
        select(User)
        .options(selectinload(User.gallery_images))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    images = []
    for gallery_item in user.gallery_images:
        # 프리미엄 사용자는 모든 이미지 blur 없음
        # 비프리미엄 사용자는 expression만 blur 없음
        if user.is_premium:
            is_blurred = False
        else:
            is_blurred = gallery_item.image_type in ["special", "ending"]

        images.append(GalleryImageResponse(
            id=gallery_item.id,
            image_url=gallery_item.image_url,
            image_type=gallery_item.image_type,
            expression_type=gallery_item.expression_type,
            is_blurred=is_blurred,
        ))

    return GalleryResponse(images=images)


@router.post("/{user_id}/gallery", response_model=GalleryImageResponse, status_code=status.HTTP_201_CREATED)
async def save_to_gallery(
    user_id: UUID,
    image_data: GalleryImageCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    이미지를 사용자 갤러리에 저장
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    gallery_item = UserGallery(
        user_id=user_id,
        image_url=image_data.image_url,
        image_type=image_data.image_type,
        expression_type=image_data.expression_type,
    )
    db.add(gallery_item)
    await db.commit()
    await db.refresh(gallery_item)

    # 프리미엄 여부에 따라 blur 결정
    if user.is_premium:
        is_blurred = False
    else:
        is_blurred = gallery_item.image_type in ["special", "ending"]

    return GalleryImageResponse(
        id=gallery_item.id,
        image_url=gallery_item.image_url,
        image_type=gallery_item.image_type,
        expression_type=gallery_item.expression_type,
        is_blurred=is_blurred,
    )
