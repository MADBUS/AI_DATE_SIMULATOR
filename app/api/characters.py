from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import Character
from app.schemas.character import CharacterResponse

router = APIRouter()


@router.get("", response_model=list[CharacterResponse])
async def get_characters(db: AsyncSession = Depends(get_db)):
    """캐릭터 목록 조회"""
    result = await db.execute(select(Character))
    characters = result.scalars().all()
    return characters


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: int, db: AsyncSession = Depends(get_db)):
    """캐릭터 상세 조회"""
    result = await db.execute(select(Character).where(Character.id == character_id))
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character
