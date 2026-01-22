import random
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.core.database import get_db
from app.models import GameSession, Scene
from app.models.game import CharacterExpression
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


class SpecialImageResponse(BaseModel):
    image_url: str
    is_blurred: bool


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

    # 이전 씬 조회 (대화 맥락을 위해)
    previous_choice = None
    previous_dialogue = None
    if session.current_scene > 1:
        prev_scene_result = await db.execute(
            select(Scene)
            .where(
                Scene.session_id == session_id,
                Scene.scene_number == session.current_scene - 1
            )
        )
        prev_scene = prev_scene_result.scalar_one_or_none()
        if prev_scene:
            previous_dialogue = prev_scene.dialogue_text
            # 선택한 선택지 가져오기
            if prev_scene.selected_choice_index is not None and prev_scene.choices_offered:
                choices = prev_scene.choices_offered
                if 0 <= prev_scene.selected_choice_index < len(choices):
                    previous_choice = choices[prev_scene.selected_choice_index].get("text", "")

    # AI 콘텐츠 생성 (MBTI 및 캐릭터 설정 반영, 이전 대화 맥락 포함)
    content = await generate_scene_content(
        character_setting=session.character_setting,
        user_mbti=session.user.mbti if session.user else None,
        scene_number=session.current_scene,
        affection=session.affection,
        previous_choice=previous_choice,
        previous_dialogue=previous_dialogue,
    )

    # 캐릭터 표정 이미지 가져오기 (neutral 기본)
    image_url = content["image_url"]  # 기본 placeholder
    if session.character_setting:
        expr_result = await db.execute(
            select(CharacterExpression).where(
                CharacterExpression.setting_id == session.character_setting.id,
                CharacterExpression.expression_type == "neutral"
            )
        )
        neutral_expression = expr_result.scalar_one_or_none()
        if neutral_expression:
            image_url = neutral_expression.image_url

    # 씬 저장
    scene = Scene(
        session_id=session_id,
        scene_number=session.current_scene,
        image_url=image_url,
        dialogue_text=content["dialogue"],
        choices_offered=content["choices"],
    )
    db.add(scene)
    await db.commit()

    return SceneResponse(
        scene_number=session.current_scene,
        image_url=image_url,
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


@router.get("/{session_id}/special-image", response_model=SpecialImageResponse)
async def get_special_image(
    session_id: UUID,
    image_url: str,
    db: AsyncSession = Depends(get_db)
):
    """
    결제 상태에 따라 이미지 blur 처리 여부 결정

    Returns:
        image_url: 이미지 URL
        is_blurred: blur 처리 여부 (프리미엄 사용자는 False)
    """
    # 게임 세션 조회 (user 포함)
    result = await db.execute(
        select(GameSession)
        .options(selectinload(GameSession.user))
        .where(GameSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")

    # 프리미엄 사용자인 경우 blur 없음
    is_premium = session.user.is_premium if session.user else False

    return SpecialImageResponse(
        image_url=image_url,
        is_blurred=not is_premium
    )
