from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import GameSession, Scene
from app.schemas.game import SceneResponse, ChoiceResponse
from app.services.gemini_service import generate_scene_content

router = APIRouter()


@router.post("/{session_id}/generate", response_model=SceneResponse)
async def generate_scene(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """씬 생성 (이미지 + 대화 + 선택지)"""
    # 게임 세션 조회
    result = await db.execute(
        select(GameSession)
        .options(selectinload(GameSession.character))
        .where(GameSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")

    if session.status != "playing":
        raise HTTPException(status_code=400, detail="Game already ended")

    # AI 콘텐츠 생성
    content = await generate_scene_content(
        character=session.character,
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
