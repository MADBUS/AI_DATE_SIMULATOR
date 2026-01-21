"""
Minigame API
TASK-008: 미니게임 결과 저장
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.game import GameSession, MinigameResult
from app.schemas.minigame import MinigameResultCreate, MinigameResultResponse

router = APIRouter()

# Bonus affection by result type
BONUS_AFFECTION = {
    "perfect": 3,
    "great": 1,
    "miss": 0,
}


@router.post(
    "/{session_id}/result",
    response_model=MinigameResultResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_minigame_result(
    session_id: UUID,
    data: MinigameResultCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Save minigame result and apply bonus affection.

    Results and bonus:
    - perfect: +3 affection
    - great: +1 affection
    - miss: +0 affection
    """
    # Check if game session exists
    result = await db.execute(
        select(GameSession).where(GameSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game session not found"
        )

    # Calculate bonus affection
    bonus = BONUS_AFFECTION.get(data.result, 0)

    # Update session affection
    new_affection = min(100, session.affection + bonus)
    session.affection = new_affection

    # Save minigame result
    minigame_result = MinigameResult(
        session_id=session_id,
        scene_number=data.scene_number,
        result=data.result,
        bonus_affection=bonus,
    )
    db.add(minigame_result)

    await db.commit()
    await db.refresh(minigame_result)

    return MinigameResultResponse(
        id=minigame_result.id,
        result=minigame_result.result,
        bonus_affection=bonus,
        new_affection=new_affection,
    )
