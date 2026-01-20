from pydantic import BaseModel


class CharacterResponse(BaseModel):
    id: int
    name: str
    type: str
    personality: str
    base_affection_min: int
    base_affection_max: int

    class Config:
        from_attributes = True
