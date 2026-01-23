import random
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.core.database import get_db
from app.models import GameSession, Scene
from app.models.game import CharacterExpression, SpecialEventImage, CharacterSetting
from app.models.user import User
from app.schemas.game import SceneResponse, ChoiceResponse
from app.services.gemini_service import (
    generate_scene_content,
    generate_special_event_image,
    get_character_design,
)

router = APIRouter()

# 특별 이벤트 발생 주기 (5턴마다)
SPECIAL_EVENT_INTERVAL = 5


class SpecialEventResponse(BaseModel):
    is_special_event: bool
    special_image_url: str | None = None
    event_description: str | None = None
    show_minigame: bool = False


class MinigameResultRequest(BaseModel):
    success: bool
    is_pvp: bool = False  # PvP 게임 여부
    bet_amount: int = 0   # PvP 베팅 금액
    opponent_session_id: str | None = None  # PvP 상대방 세션 ID (캐릭터 뺏기용)


class MinigameResultResponse(BaseModel):
    affection_change: int
    new_affection: int
    message: str
    show_event_scene: bool  # True only when minigame success
    # 엔딩 관련
    game_ended: bool = False
    ending_type: str | None = None  # "happy_ending" or "sad_ending"
    # 캐릭터 뺏김 관련 (PvP)
    character_stolen: bool = False
    stolen_character_id: str | None = None


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

    # 이미 해당 씬이 존재하는지 확인 (중복 방지)
    existing_scene_result = await db.execute(
        select(Scene)
        .where(
            Scene.session_id == session_id,
            Scene.scene_number == session.current_scene
        )
        .order_by(Scene.created_at.desc())
        .limit(1)
    )
    existing_scene = existing_scene_result.scalar_one_or_none()
    if existing_scene:
        # 이미 존재하면 기존 씬 반환
        return SceneResponse(
            scene_number=existing_scene.scene_number,
            image_url=existing_scene.image_url,
            dialogue=existing_scene.dialogue_text,
            choices=[
                ChoiceResponse(
                    id=i,
                    text=c["text"],
                    delta=c["delta"],
                    expression=c.get("expression", "neutral"),
                )
                for i, c in enumerate(existing_scene.choices_offered or [])
            ],
            affection=session.affection,
            status=session.status,
        )

    # 이전 씬 조회 (대화 맥락을 위해) - .first() 사용으로 중복 에러 방지
    previous_choice = None
    previous_dialogue = None
    if session.current_scene > 1:
        prev_scene_result = await db.execute(
            select(Scene)
            .where(
                Scene.session_id == session_id,
                Scene.scene_number == session.current_scene - 1
            )
            .order_by(Scene.created_at.desc())
            .limit(1)
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
            ChoiceResponse(
                id=i,
                text=c["text"],
                delta=c["delta"],
                expression=c.get("expression", "neutral"),
            )
            for i, c in enumerate(content["choices"])
        ],
        affection=session.affection,
        status=session.status,
    )


@router.post("/{session_id}/check-event", response_model=SpecialEventResponse)
async def check_special_event(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    특별 이벤트 발생 체크 (5턴마다 발생)

    Returns:
        is_special_event: 이벤트 발생 여부
        special_image_url: 특별 이미지 URL (이벤트 발생 시)
        event_description: 이벤트 설명
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

    # 5턴마다 특별 이벤트 발생 (5, 10, 15, 20...)
    if session.current_scene > 0 and session.current_scene % SPECIAL_EVENT_INTERVAL == 0:
        # 캐릭터 설정 가져오기
        char_setting = session.character_setting
        if char_setting:
            # 저장된 캐릭터 디자인 사용 (일관성 유지)
            # 저장된 디자인이 없으면 새로 생성하고 저장
            if char_setting.character_design:
                character_design = char_setting.character_design
            else:
                character_design = get_character_design(
                    gender=char_setting.gender,
                    style=char_setting.style,
                )
                char_setting.character_design = character_design

            # 현재 세션에서 이미 본 이벤트 타입 조회
            prev_events_result = await db.execute(
                select(SpecialEventImage.event_type).where(
                    SpecialEventImage.session_id == session_id
                )
            )
            shown_event_types = [row[0] for row in prev_events_result.fetchall()]
            print(f"[SpecialEvent] Already shown events: {shown_event_types}")

            # ========== NTR 캐릭터: 원래 주인의 이미지 먼저 사용 ==========
            if session.is_stolen and session.stolen_from_session_id:
                print(f"[SpecialEvent] Stolen character! Checking original session: {session.stolen_from_session_id}")

                # 원래 세션의 특별 이벤트 이미지 조회
                original_images_result = await db.execute(
                    select(SpecialEventImage).where(
                        SpecialEventImage.session_id == session.stolen_from_session_id
                    )
                )
                original_images = original_images_result.scalars().all()

                # 아직 보지 않은 이미지 찾기
                unseen_images = [
                    img for img in original_images
                    if img.event_type not in shown_event_types
                ]

                if unseen_images:
                    # 아직 보지 않은 이미지가 있으면 그것을 사용
                    reuse_image = unseen_images[0]
                    print(f"[SpecialEvent] Reusing image from original owner: {reuse_image.event_type}")

                    # 현재 세션에 이미지 기록 복사 (이미 본 것으로 표시)
                    new_event_image = SpecialEventImage(
                        session_id=session_id,
                        event_type=reuse_image.event_type,
                        image_url=reuse_image.image_url,
                        video_url=reuse_image.video_url,
                        is_nsfw=reuse_image.is_nsfw,
                    )
                    db.add(new_event_image)
                    await db.commit()

                    return SpecialEventResponse(
                        is_special_event=True,
                        special_image_url=reuse_image.image_url,
                        event_description=f"뺏은 캐릭터의 추억... ({reuse_image.event_type})",
                        show_minigame=True,
                    )
                else:
                    print(f"[SpecialEvent] All original images shown, generating new one")

            # ========== 새 이미지 생성 (Gemini API) ==========
            # neutral 표정 이미지 가져오기 (캐릭터 참조용)
            neutral_image_url = None
            expr_result = await db.execute(
                select(CharacterExpression).where(
                    CharacterExpression.setting_id == char_setting.id,
                    CharacterExpression.expression_type == "neutral"
                )
            )
            neutral_expr = expr_result.scalar_one_or_none()
            if neutral_expr:
                neutral_image_url = neutral_expr.image_url

            # 전신 이벤트 씬 이미지 생성 (Gemini API로 동적 생성, 이전 이벤트 제외)
            special_image_url, event_description, event_name = await generate_special_event_image(
                gender=char_setting.gender,
                style=char_setting.style,
                art_style=char_setting.art_style or "anime",
                character_design=character_design,
                previous_events=shown_event_types,
                reference_image_url=neutral_image_url,
            )

            # 새 이벤트를 DB에 저장 (중복 방지용 기록)
            new_event_image = SpecialEventImage(
                session_id=session_id,
                event_type=event_name,
                image_url=special_image_url,
                is_nsfw=False,
            )
            db.add(new_event_image)
            await db.commit()
            print(f"[SpecialEvent] Saved new event: {event_name}")
        else:
            # 캐릭터 설정이 없는 경우 placeholder
            special_image_url = f"https://placehold.co/1024x768/FF69B4/FFFFFF?text=Special+Event+Scene+{session.current_scene}"
            event_description = "특별 이벤트"

        return SpecialEventResponse(
            is_special_event=True,
            special_image_url=special_image_url,
            event_description=event_description,
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


@router.post("/{session_id}/minigame-result", response_model=MinigameResultResponse)
async def submit_minigame_result(
    session_id: UUID,
    request: MinigameResultRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    미니게임 결과 제출 및 호감도 변화 적용

    Args:
        success: 미니게임 성공 여부

    Returns:
        affection_change: 호감도 변화량
        new_affection: 변경 후 호감도
        message: 결과 메시지
    """
    # 게임 세션 조회
    result = await db.execute(
        select(GameSession)
        .where(GameSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")

    if session.status != "playing":
        raise HTTPException(status_code=400, detail="Game already ended")

    # 미니게임 결과에 따른 호감도 변화
    if request.is_pvp:
        # PvP 게임: 베팅 금액만큼 호감도 변화
        if request.success:
            # 승리: 베팅 금액만큼 획득
            affection_change = request.bet_amount
            message = f"PvP 승리! 호감도 +{affection_change} 획득! 🏆💕"
        else:
            # 패배: 베팅 금액만큼 손실
            affection_change = -request.bet_amount
            message = f"PvP 패배... 호감도 {affection_change} 손실 💔"
    elif request.success:
        # 솔로 미니게임 성공: +10 ~ +15 대폭 상승
        affection_change = random.randint(10, 15)
        message = "미니게임 성공! 호감도가 대폭 상승했습니다! 💕"
    else:
        # 솔로 미니게임 실패: -2 ~ -3 소폭 하락
        affection_change = random.randint(-3, -2)
        message = "미니게임 실패... 다음 기회를 노려보세요."

    # 호감도 적용 (0~100 범위 유지)
    new_affection = max(0, min(100, session.affection + affection_change))
    session.affection = new_affection

    # 엔딩 조건 체크
    game_ended = False
    ending_type = None
    character_stolen = False
    stolen_character_id = None

    if new_affection <= 0:
        # Sad Ending
        session.status = "sad_ending"
        game_ended = True
        ending_type = "sad_ending"
        message = "호감도가 0이 되었습니다... 💔 Sad Ending"

        # PvP에서 호감도 0이 되면 캐릭터 뺏김 처리
        if request.is_pvp and request.opponent_session_id:
            # 상대방 세션 조회
            opponent_result = await db.execute(
                select(GameSession).where(GameSession.id == UUID(request.opponent_session_id))
            )
            opponent_session = opponent_result.scalar_one_or_none()

            if opponent_session:
                # 현재 세션의 캐릭터 설정 조회
                char_result = await db.execute(
                    select(CharacterSetting).where(CharacterSetting.session_id == session_id)
                )
                original_char = char_result.scalar_one_or_none()

                if original_char:
                    # 새 게임 세션 생성 (뺏은 캐릭터용)
                    new_session = GameSession(
                        user_id=opponent_session.user_id,
                        affection=30,  # 호감도 30으로 시작
                        current_scene=1,
                        status="playing",
                        save_slot=0,  # 뺏은 캐릭터는 슬롯 0
                        is_stolen=True,
                        original_owner_id=session.user_id,
                        stolen_from_session_id=session_id,
                    )
                    db.add(new_session)
                    await db.flush()

                    # 캐릭터 설정 복사
                    new_char = CharacterSetting(
                        session_id=new_session.id,
                        gender=original_char.gender,
                        style=original_char.style,
                        mbti=original_char.mbti,
                        art_style=original_char.art_style,
                        character_design=original_char.character_design,
                    )
                    db.add(new_char)

                    character_stolen = True
                    stolen_character_id = str(new_session.id)
                    message = "상대방의 캐릭터를 뺏었습니다! 🏆💕"

    elif new_affection >= 100:
        # Happy Ending
        session.status = "happy_ending"
        game_ended = True
        ending_type = "happy_ending"
        message = "호감도가 MAX! 💕🎉 Happy Ending!"

    await db.commit()
    await db.refresh(session)

    return MinigameResultResponse(
        affection_change=affection_change,
        new_affection=new_affection,
        message=message,
        show_event_scene=request.success and not game_ended,  # 엔딩 시에는 이벤트 씬 표시 안함
        game_ended=game_ended,
        ending_type=ending_type,
        character_stolen=character_stolen,
        stolen_character_id=stolen_character_id,
    )
