from uuid import UUID
from pydantic import BaseModel, ConfigDict


class MinigameResultCreate(BaseModel):
    """Request body for saving minigame result."""
    result: str  # 'perfect', 'great', 'miss'
    scene_number: int


class MinigameResultResponse(BaseModel):
    """Response schema for minigame result."""
    id: UUID
    result: str
    bonus_affection: int
    new_affection: int

    model_config = ConfigDict(from_attributes=True)
