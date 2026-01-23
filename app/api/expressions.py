"""
Character Expressions API
TASK-007: 표정 이미지 7종 사전 생성
Note: 비디오 생성은 API 부하로 인해 비활성화됨
캐릭터 재사용: 같은 설정(gender, style, mbti, art_style)의 기존 캐릭터가 있으면 재사용
"""

import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.game import GameSession, CharacterSetting, CharacterExpression
from app.schemas.character import CharacterExpressionResponse, ExpressionsGeneratedResponse
from app.services.gemini_service import (
    generate_character_image,
    get_character_design,
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Expression types to generate (7가지)
EXPRESSION_TYPES = ["neutral", "happy", "sad", "jealous", "shy", "excited", "disgusted"]


async def find_reusable_character(
    db: AsyncSession,
    user_id: UUID,
    gender: str,
    style: str,
    mbti: str,
    art_style: str,
) -> CharacterSetting | None:
    """
    같은 설정(gender, style, mbti, art_style)의 기존 캐릭터를 찾아 재사용.
    단, 현재 사용자가 이미 사용한 캐릭터(playing/ended 포함, stolen 제외)는 제외.
    """
    # 1. 현재 사용자가 사용한 캐릭터의 character_design 목록 조회
    # (뺏긴 캐릭터 is_stolen=True는 제외 - 원래 주인의 세션)
    user_sessions_result = await db.execute(
        select(GameSession)
        .options(selectinload(GameSession.character_setting))
        .where(
            GameSession.user_id == user_id,
            # 뺏긴 캐릭터는 제외 (is_stolen이 True인 경우는 뺏어온 캐릭터이므로 포함해야 함)
            # 원래 주인에게서 뺏긴 것은 character_stolen 로직에서 처리됨
        )
    )
    user_sessions = user_sessions_result.scalars().all()

    # 사용자가 사용한 character_design 목록 (JSON 비교를 위해 문자열로 변환)
    used_designs = set()
    for session in user_sessions:
        if session.character_setting and session.character_setting.character_design:
            # JSON을 정렬된 문자열로 변환하여 비교
            import json
            design_str = json.dumps(session.character_setting.character_design, sort_keys=True)
            used_designs.add(design_str)

    logger.info(f"[CharacterReuse] User {user_id} has used {len(used_designs)} character designs")

    # 2. 같은 설정의 기존 캐릭터 조회 (표정이 있는 것만)
    existing_chars_result = await db.execute(
        select(CharacterSetting)
        .options(selectinload(CharacterSetting.expressions))
        .where(
            CharacterSetting.gender == gender,
            CharacterSetting.style == style,
            CharacterSetting.mbti == mbti,
            CharacterSetting.art_style == art_style,
            CharacterSetting.character_design.isnot(None),
        )
    )
    existing_chars = existing_chars_result.scalars().all()

    logger.info(f"[CharacterReuse] Found {len(existing_chars)} existing characters with same settings")

    # 3. 사용자가 사용하지 않은 캐릭터 찾기
    import json
    for char in existing_chars:
        # 표정이 있어야 재사용 가능
        if not char.expressions or len(char.expressions) < len(EXPRESSION_TYPES):
            continue

        if char.character_design:
            design_str = json.dumps(char.character_design, sort_keys=True)
            if design_str not in used_designs:
                logger.info(f"[CharacterReuse] Found reusable character: {char.id}")
                return char

    logger.info(f"[CharacterReuse] No reusable character found, will generate new one")
    return None


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
    Generate 7 expression images for a game session's character.

    This endpoint:
    1. Validates that the game session exists
    2. Validates that the session has character settings
    3. 먼저 같은 설정의 기존 캐릭터가 있으면 재사용 (Gemini API 호출 최소화)
    4. 없으면 새로 생성 (7 expression images)
    5. Returns the generated expressions

    Note: Video generation is disabled due to API load constraints.
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

    # ============ 캐릭터 재사용 체크 ============
    # 같은 설정(gender, style, mbti, art_style)의 기존 캐릭터가 있으면 재사용
    reusable_char = await find_reusable_character(
        db=db,
        user_id=session.user_id,
        gender=character_setting.gender,
        style=character_setting.style,
        mbti=character_setting.mbti,
        art_style=character_setting.art_style or "anime",
    )

    if reusable_char:
        logger.info(f"[CharacterReuse] Reusing character {reusable_char.id} for session {session_id}")

        # 기존 캐릭터의 디자인 복사
        character_setting.character_design = reusable_char.character_design

        # 기존 캐릭터의 표정 이미지 복사
        for orig_expr in reusable_char.expressions:
            new_expr = CharacterExpression(
                setting_id=character_setting.id,
                expression_type=orig_expr.expression_type,
                image_url=orig_expr.image_url,
                video_url=orig_expr.video_url,
            )
            db.add(new_expr)
            expressions.append(new_expr)

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

    # ============ 새 캐릭터 생성 ============
    logger.info(f"[CharacterReuse] Generating new character for session {session_id}")

    # 캐릭터 디자인을 한 번만 생성 (모든 표정에서 동일한 캐릭터 유지)
    # 이미 저장된 디자인이 있으면 재사용, 없으면 새로 생성
    if character_setting.character_design:
        character_design = character_setting.character_design
    else:
        character_design = get_character_design(
            gender=character_setting.gender,
            style=character_setting.style,
        )
        # 생성된 디자인을 CharacterSetting에 저장
        character_setting.character_design = character_design

    # Generate expression images using Gemini API (동일 캐릭터 디자인 사용)
    # 비디오 생성은 API 부하로 인해 비활성화
    for expression_type in EXPRESSION_TYPES:
        # 이미지 생성 (Imagen 4.0)
        image_url = await generate_character_image(
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
            video_url=None,  # 비디오 비활성화
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
