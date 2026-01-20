import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GameSession(Base):
    __tablename__ = "game_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey("characters.id"))
    affection: Mapped[int] = mapped_column(Integer, default=30)
    current_scene: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(
        String(20), default="playing"
    )  # 'playing', 'happy_ending', 'sad_ending'
    save_slot: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        CheckConstraint("affection >= 0 AND affection <= 100", name="affection_range"),
    )

    # Relationships
    user = relationship("User", back_populates="game_sessions")
    character = relationship("Character", back_populates="game_sessions")
    scenes = relationship("Scene", back_populates="session")


class Scene(Base):
    __tablename__ = "scenes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("game_sessions.id")
    )
    scene_number: Mapped[int] = mapped_column(Integer)
    image_url: Mapped[str] = mapped_column(Text, nullable=True)
    dialogue_text: Mapped[str] = mapped_column(Text, nullable=True)
    choices_offered: Mapped[dict] = mapped_column(JSONB, nullable=True)
    selected_choice_index: Mapped[int] = mapped_column(Integer, nullable=True)
    affection_delta: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("GameSession", back_populates="scenes")


class ChoiceTemplate(Base):
    __tablename__ = "choice_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey("characters.id"))
    affection_min: Mapped[int] = mapped_column(Integer, default=0)
    affection_max: Mapped[int] = mapped_column(Integer, default=100)
    choice_text: Mapped[str] = mapped_column(Text)
    affection_delta: Mapped[int] = mapped_column(Integer)
    tags: Mapped[list] = mapped_column(ARRAY(String), nullable=True)

    # Relationships
    character = relationship("Character", back_populates="choice_templates")


class AIGeneratedContent(Base):
    __tablename__ = "ai_generated_content"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    character_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("characters.id"), nullable=True
    )
    prompt_hash: Mapped[str] = mapped_column(String(64), unique=True)
    content_type: Mapped[str] = mapped_column(String(20))  # 'image', 'dialogue'
    content_data: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    character = relationship("Character", back_populates="ai_contents")
