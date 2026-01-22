"""
Character Expressions API
TASK-007: 표정 이미지 7종 사전 생성
Phase 2: 표정별 애니메이션 비디오 생성 추가
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.game import GameSession, CharacterSetting, CharacterExpression
from app.schemas.character import CharacterExpressionResponse, ExpressionsGeneratedResponse
from app.services.gemini_service import (
    generate_character_image,
    generate_character_video,
    get_character_design,
)

router = APIRouter()

# Expression types to generate (7가지)
EXPRESSION_TYPES = ["neutral", "happy", "sad", "jealous", "shy", "excited", "disgusted"]


@router.post(
    "/{session_id}/generate-expressions",
    response_model=ExpressionsGeneratedResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_expressions(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate 7 expression images and videos for a game session's character.

    This endpoint:
    1. Validates that the game session exists
    2. Validates that the session has character settings
    3. Generates 7 expression images (neutral, happy, sad, jealous, shy, excited, disgusted)
    4. Generates 7 expression animation videos using Veo model
    5. Saves them to the database
    6. Returns the generated expressions
    """
    # Check if game session exists
    result = await db.execute(
        select(GameSession)
        .options(selectinload(GameSession.character_setting))
        .where(GameSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found"
        )

    # Check if character settings exist
    if not session.character_setting:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Character settings not found for this session"
        )

    character_setting = session.character_setting
    expressions = []

    # 캐릭터 디자인을 한 번만 생성 (모든 표정에서 동일한 캐릭터 유지)
    character_design = get_character_design(
        gender=character_setting.gender,
        style=character_setting.style,
    )

    # Generate expression images and videos using Gemini API (동일 캐릭터 디자인 사용)
    for expression_type in EXPRESSION_TYPES:
        # 이미지 생성 (Imagen 4.0)
        image_url = await generate_character_image(
            gender=character_setting.gender,
            style=character_setting.style,
            art_style=character_setting.art_style or "anime",
            expression=expression_type,
            character_design=character_design,
        )

        # 비디오 생성 (Veo 2.0)
        video_url = await generate_character_video(
            gender=character_setting.gender,
            style=character_setting.style,
            art_style=character_setting.art_style or "anime",
            expression=expression_type,
            character_design=character_design,
        )

        expression = CharacterExpression(
            setting_id=character_setting.id,
            expression_type=expression_type,
            image_url=image_url,
            video_url=video_url,
        )
        db.add(expression)
        expressions.append(expression)

    await db.commit()

    # Refresh to get IDs
    for expr in expressions:
        await db.refresh(expr)

    return ExpressionsGeneratedResponse(
        expressions=[
            CharacterExpressionResponse(
                id=expr.id,
                expression_type=expr.expression_type,
                image_url=expr.image_url,
                video_url=expr.video_url,
            )
            for expr in expressions
        ]
    )


@router.get(
    "/{session_id}/expressions",
    response_model=ExpressionsGeneratedResponse,
)
async def get_expressions(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all expression images and videos for a game session's character.
    """
    # Check if game session exists
    result = await db.execute(
        select(GameSession)
        .options(selectinload(GameSession.character_setting))
        .where(GameSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found"
        )

    # Check if character settings exist
    if not session.character_setting:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Character settings not found for this session"
        )

    # Get existing expressions
    result = await db.execute(
        select(CharacterExpression)
        .where(CharacterExpression.setting_id == session.character_setting.id)
    )
    expressions = result.scalars().all()

    return ExpressionsGeneratedResponse(
        expressions=[
            CharacterExpressionResponse(
                id=expr.id,
                expression_type=expr.expression_type,
                image_url=expr.image_url,
                video_url=expr.video_url,
            )
            for expr in expressions
        ]
    )
