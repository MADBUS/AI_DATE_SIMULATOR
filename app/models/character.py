from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(50))  # 'tsundere', 'cool', 'cute'
    personality: Mapped[str] = mapped_column(Text)
    base_affection_min: Mapped[int] = mapped_column(Integer, default=30)
    base_affection_max: Mapped[int] = mapped_column(Integer, default=50)
    avatar_prompt: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    game_sessions = relationship("GameSession", back_populates="character")
    choice_templates = relationship("ChoiceTemplate", back_populates="character")
    ai_contents = relationship("AIGeneratedContent", back_populates="character")
