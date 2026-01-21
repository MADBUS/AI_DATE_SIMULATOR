import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, CheckConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID
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
    character_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("characters.id"), nullable=True
    )
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
    character_setting = relationship("CharacterSetting", back_populates="session", uselist=False)


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
    choices_offered: Mapped[dict] = mapped_column(JSON, nullable=True)
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
    tags: Mapped[list] = mapped_column(JSON, nullable=True)

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
    content_data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    character = relationship("Character", back_populates="ai_contents")


class CharacterSetting(Base):
    """User's customization choices for the AI partner per game session."""
    __tablename__ = "character_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("game_sessions.id"), unique=True
    )
    gender: Mapped[str] = mapped_column(String(10))  # 'male', 'female'
    style: Mapped[str] = mapped_column(String(50))  # 'tsundere', 'cool', 'cute', 'sexy', 'pure'
    mbti: Mapped[str] = mapped_column(String(4))  # 'INTJ', 'ENFP', etc.
    art_style: Mapped[str] = mapped_column(String(50))  # 'anime', 'realistic', 'watercolor'
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("GameSession", back_populates="character_setting")
    expressions = relationship("CharacterExpression", back_populates="setting")


class CharacterExpression(Base):
    """Expression images for a character setting (6 types)."""
    __tablename__ = "character_expressions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    setting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("character_settings.id")
    )
    expression_type: Mapped[str] = mapped_column(String(20))  # 'neutral', 'happy', 'sad', 'jealous', 'shy', 'excited'
    image_url: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    setting = relationship("CharacterSetting", back_populates="expressions")
