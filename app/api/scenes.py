import random
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.core.database import get_db
from app.models import GameSession, Scene
from app.models.user import User
from app.schemas.game import SceneResponse, ChoiceResponse
from app.services.gemini_service import generate_scene_content

router = APIRouter()

# Special event probability threshold
SPECIAL_EVENT_PROBABILITY = 0.15


class SpecialEventResponse(BaseModel):
    is_special_event: bool
    special_image_url: str | None = None
    show_minigame: bool = False


@router.post("/{session_id}/generate", response_model=SceneResponse)
async def generate_scene(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """씬 생성 (이미지 + 대화 + 선택지) - MBTI 및 캐릭터 설정 반영"""
    # 게임 세션 조회 (character_setting, user 포함)
    result = await db.execute(
        select(GameSession)
        .options(
            selectinload(GameSession.character),
            selectinload(GameSession.character_setting),
            selectinload(GameSession.user),
        )
        .where(GameSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")

    if session.status != "playing":
        raise HTTPException(status_code=400, detail="Game already ended")

    # AI 콘텐츠 생성 (MBTI 및 캐릭터 설정 반영)
    content = await generate_scene_content(
        character_setting=session.character_setting,
        user_mbti=session.user.mbti if session.user else None,
        scene_number=session.current_scene,
        affection=session.affection,
    )

    # 씬 저장
    scene = Scene(
        session_id=session_id,
        scene_number=session.current_scene,
        image_url=content["image_url"],
        dialogue_text=content["dialogue"],
        choices_offered=content["choices"],
    )
    db.add(scene)
    await db.commit()

    return SceneResponse(
        scene_number=session.current_scene,
        image_url=content["image_url"],
        dialogue=content["dialogue"],
        choices=[
            ChoiceResponse(id=i, text=c["text"], delta=c["delta"])
            for i, c in enumerate(content["choices"])
        ],
        affection=session.affection,
        status=session.status,
    )


@router.post("/{session_id}/check-event", response_model=SpecialEventResponse)
async def check_special_event(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    특별 이벤트 발생 체크 (15% 확률)

    Returns:
        is_special_event: 이벤트 발생 여부
        special_image_url: 특별 이미지 URL (이벤트 발생 시)
        show_minigame: 미니게임 표시 여부
    """
    # 게임 세션 조회
    result = await db.execute(
        select(GameSession)
        .options(selectinload(GameSession.character_setting))
        .where(GameSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")

    if session.status != "playing":
        raise HTTPException(status_code=400, detail="Game already ended")

    # 15% 확률로 특별 이벤트 발생
    if random.random() < SPECIAL_EVENT_PROBABILITY:
        # TODO: 실제 Gemini API로 특별 이미지 생성
        special_image_url = f"https://placehold.co/1024x768/FF69B4/FFFFFF?text=Special+Event+Scene+{session.current_scene}"

        return SpecialEventResponse(
            is_special_event=True,
            special_image_url=special_image_url,
            show_minigame=True,
        )

    return SpecialEventResponse(is_special_event=False)
