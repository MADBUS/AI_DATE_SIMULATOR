from uuid import UUID
from pydantic import BaseModel, ConfigDict


class CharacterResponse(BaseModel):
    id: int
    name: str
    type: str
    personality: str
    base_affection_min: int
    base_affection_max: int

    model_config = ConfigDict(from_attributes=True)


class CharacterSettingCreate(BaseModel):
    """Request body for creating character settings with a new game session."""
    user_id: UUID
    gender: str  # 'male', 'female'
    style: str  # 'tsundere', 'cool', 'cute', 'sexy', 'pure'
    mbti: str  # 'INTJ', 'ENFP', etc.
    art_style: str  # 'anime', 'realistic', 'watercolor'


class CharacterSettingResponse(BaseModel):
    """Response schema for character settings."""
    id: UUID
    gender: str
    style: str
    mbti: str
    art_style: str

    model_config = ConfigDict(from_attributes=True)


class CharacterExpressionResponse(BaseModel):
    """Response schema for a single character expression."""
    id: UUID
    expression_type: str
    image_url: str

    model_config = ConfigDict(from_attributes=True)


class ExpressionsGeneratedResponse(BaseModel):
    """Response schema for generated expressions."""
    expressions: list[CharacterExpressionResponse]
