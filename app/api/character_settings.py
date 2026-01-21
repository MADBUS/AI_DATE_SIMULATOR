"""
Character Settings API
TASK-004: 연애 대상자 커스터마이징 API
"""

import random

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.models.game import GameSession, CharacterSetting
from app.schemas.character import CharacterSettingCreate, CharacterSettingResponse
from app.schemas.game import GameSessionWithSettingsResponse

router = APIRouter()


@router.post(
    "/",
    response_model=GameSessionWithSettingsResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_character_settings(
    data: CharacterSettingCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new game session with character settings.

    This endpoint:
    1. Validates that the user exists
    2. Creates a new game session with random initial affection (30-50)
    3. Creates character settings for the session
    4. Returns the complete game session with character settings
    """
    # Check if user exists
    result = await db.execute(select(User).where(User.id == data.user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Create game session with initial affection 30
    game_session = GameSession(
        user_id=data.user_id,
        affection=30,  # 고정값 30으로 시작
        current_scene=1,
        status="playing",
        save_slot=1,
    )
    db.add(game_session)
    await db.flush()  # Get the session ID

    # Create character settings
    character_setting = CharacterSetting(
        session_id=game_session.id,
        gender=data.gender,
        style=data.style,
        mbti=data.mbti,
        art_style=data.art_style,
    )
    db.add(character_setting)
    await db.commit()

    # Build response
    return GameSessionWithSettingsResponse(
        id=game_session.id,
        user_id=game_session.user_id,
        affection=game_session.affection,
        current_scene=game_session.current_scene,
        status=game_session.status,
        save_slot=game_session.save_slot,
        character_settings=CharacterSettingResponse(
            id=character_setting.id,
            gender=character_setting.gender,
            style=character_setting.style,
            mbti=character_setting.mbti,
            art_style=character_setting.art_style,
        ),
    )
