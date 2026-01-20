from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class GameSessionCreate(BaseModel):
    character_id: int
    save_slot: int = 1


class GameSessionResponse(BaseModel):
    id: UUID
    character_id: int
    character_name: str | None = None
    character_type: str | None = None
    affection: int
    current_scene: int
    status: str
    save_slot: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChoiceResponse(BaseModel):
    id: int
    text: str
    delta: int


class SceneResponse(BaseModel):
    scene_number: int
    image_url: str | None
    dialogue: str
    choices: list[ChoiceResponse]
    affection: int
    status: str


class ChoiceSelect(BaseModel):
    choice_index: int
    affection_delta: int


class ChoiceResult(BaseModel):
    new_affection: int
    next_scene: int
    status: str  # 'continue', 'happy_ending', 'sad_ending'
