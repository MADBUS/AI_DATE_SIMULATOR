import random
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import GameSession, Character, ChoiceTemplate, CharacterExpression
from app.schemas.game import (
    GameSessionCreate,
    GameSessionResponse,
    GameSessionWithSettingsResponse,
    ChoiceSelect,
    ChoiceResponse,
    SelectChoiceResponse,
)
from app.schemas.character import CharacterSettingResponse

router = APIRouter()


@router.get("", response_model=list[GameSessionResponse])
async def get_games(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """사용자의 게임 목록 조회"""
    result = await db.execute(
        select(GameSession)
        .options(
            selectinload(GameSession.character),
            selectinload(GameSession.character_setting),
        )
        .where(GameSession.user_id == user_id)
        .order_by(GameSession.updated_at.desc())
    )
    sessions = result.scalars().all()

    return [
        GameSessionResponse(
            id=s.id,
            character_id=s.character_id,
            character_name=s.character.name if s.character else None,
            character_type=s.character.type if s.character else None,
            affection=s.affection,
            current_scene=s.current_scene,
            status=s.status,
            save_slot=s.save_slot,
            created_at=s.created_at,
            updated_at=s.updated_at,
            character_settings=CharacterSettingResponse(
                id=s.character_setting.id,
                gender=s.character_setting.gender,
                style=s.character_setting.style,
                mbti=s.character_setting.mbti,
                art_style=s.character_setting.art_style,
            ) if s.character_setting else None,
        )
        for s in sessions
    ]


@router.post("/new", response_model=GameSessionResponse)
async def create_game(
    user_id: UUID,
    game_data: GameSessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """새 게임 생성"""
    # 캐릭터 조회
    result = await db.execute(
        select(Character).where(Character.id == game_data.character_id)
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # 호감도 랜덤 초기화
    initial_affection = random.randint(
        character.base_affection_min, character.base_affection_max
    )

    # 게임 세션 생성
    session = GameSession(
        user_id=user_id,
        character_id=game_data.character_id,
        affection=initial_affection,
        save_slot=game_data.save_slot,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return GameSessionResponse(
        id=session.id,
        character_id=session.character_id,
        character_name=character.name,
        character_type=character.type,
        affection=session.affection,
        current_scene=session.current_scene,
        status=session.status,
        save_slot=session.save_slot,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.get("/{session_id}", response_model=GameSessionWithSettingsResponse)
async def get_game(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """게임 세션 조회 (캐릭터 설정 포함)"""
    result = await db.execute(
        select(GameSession)
        .options(
            selectinload(GameSession.character),
            selectinload(GameSession.character_setting),
        )
        .where(GameSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")

    # Build character_settings response if exists
    character_settings = None
    if session.character_setting:
        character_settings = CharacterSettingResponse(
            id=session.character_setting.id,
            gender=session.character_setting.gender,
            style=session.character_setting.style,
            mbti=session.character_setting.mbti,
            art_style=session.character_setting.art_style,
        )

    return GameSessionWithSettingsResponse(
        id=session.id,
        user_id=session.user_id,
        affection=session.affection,
        current_scene=session.current_scene,
        status=session.status,
        save_slot=session.save_slot,
        character_settings=character_settings,
    )


@router.get("/{session_id}/choices", response_model=list[ChoiceResponse])
async def get_choices(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """현재 씬의 선택지 조회"""
    # 게임 세션 조회
    result = await db.execute(
        select(GameSession).where(GameSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")

    # 호감도 범위에 맞는 선택지 조회
    result = await db.execute(
        select(ChoiceTemplate).where(
            ChoiceTemplate.character_id == session.character_id,
            ChoiceTemplate.affection_min <= session.affection,
            ChoiceTemplate.affection_max >= session.affection,
        )
    )
    templates = result.scalars().all()

    # 긍정/중립/부정 선택지 분류 및 랜덤 선택
    positive = [t for t in templates if t.affection_delta > 3]
    neutral = [t for t in templates if -3 <= t.affection_delta <= 3]
    negative = [t for t in templates if t.affection_delta < -3]

    choices = []
    if positive:
        choices.append(random.choice(positive))
    if neutral:
        choices.append(random.choice(neutral))
    if negative:
        choices.append(random.choice(negative))

    random.shuffle(choices)

    return [
        ChoiceResponse(id=c.id, text=c.choice_text, delta=c.affection_delta)
        for c in choices
    ]


@router.post("/{session_id}/select", response_model=SelectChoiceResponse)
async def select_choice(
    session_id: UUID,
    choice: ChoiceSelect,
    db: AsyncSession = Depends(get_db),
):
    """선택지 선택 및 게임 진행 - 감정 이미지 반환"""
    # 게임 세션 조회 (character_setting 포함)
    result = await db.execute(
        select(GameSession)
        .options(selectinload(GameSession.character_setting))
        .where(GameSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")

    # 호감도 계산
    new_affection = max(0, min(100, session.affection + choice.affection_delta))
    session.affection = new_affection
    session.current_scene += 1

    # 엔딩 체크
    if new_affection <= 10:
        session.status = "sad_ending"
    elif session.current_scene >= 10:
        session.status = "happy_ending" if new_affection >= 70 else "sad_ending"

    await db.commit()

    # 감정 타입 결정 (없으면 neutral)
    expression_type = choice.expression_type or "neutral"

    # 해당 감정의 이미지 조회
    expression_image_url = None
    if session.character_setting:
        expr_result = await db.execute(
            select(CharacterExpression).where(
                CharacterExpression.setting_id == session.character_setting.id,
                CharacterExpression.expression_type == expression_type
            )
        )
        expression = expr_result.scalar_one_or_none()
        if expression:
            expression_image_url = expression.image_url

    return SelectChoiceResponse(
        new_affection=new_affection,
        next_scene=session.current_scene,
        status=session.status,
        expression_type=expression_type,
        expression_image_url=expression_image_url,
    )


@router.delete("/{session_id}")
async def delete_game(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """게임 삭제"""
    result = await db.execute(
        select(GameSession).where(GameSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")

    await db.delete(session)
    await db.commit()
    return {"success": True}
