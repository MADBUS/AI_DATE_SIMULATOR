"""
Character Expressions API
TASK-007: 표정 이미지 6종 사전 생성
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.game import GameSession, CharacterSetting, CharacterExpression
from app.schemas.character import CharacterExpressionResponse, ExpressionsGeneratedResponse

router = APIRouter()

# Expression types to generate
EXPRESSION_TYPES = ["neutral", "happy", "sad", "jealous", "shy", "excited"]


async def generate_expression_image(
    character_setting: CharacterSetting,
    expression_type: str,
) -> str:
    """
    Generate an expression image using Gemini API.
    This is a placeholder - actual implementation will use Gemini.
    """
    # TODO: Implement actual Gemini image generation
    return f"https://example.com/generated/{expression_type}.png"


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
    Generate 6 expression images for a game session's character.

    This endpoint:
    1. Validates that the game session exists
    2. Validates that the session has character settings
    3. Generates 6 expression images (neutral, happy, sad, jealous, shy, excited)
    4. Saves them to the database
    5. Returns the generated expressions
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

    # Generate 6 expression images
    for expression_type in EXPRESSION_TYPES:
        image_url = await generate_expression_image(character_setting, expression_type)

        expression = CharacterExpression(
            setting_id=character_setting.id,
            expression_type=expression_type,
            image_url=image_url,
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
            )
            for expr in expressions
        ]
    )
