"""
PvP 매칭 모델
Phase 2: WebSocket 기반 PvP 시스템
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PvPMatch(Base):
    """PvP 매칭 기록"""
    __tablename__ = "pvp_matches"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    player1_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("game_sessions.id")
    )
    player2_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("game_sessions.id")
    )
    player1_bet: Mapped[int] = mapped_column(Integer, default=0)
    player2_bet: Mapped[int] = mapped_column(Integer, default=0)
    final_bet: Mapped[int] = mapped_column(Integer, default=0)
    winner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    loser_character_stolen: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    player1_session = relationship(
        "GameSession", foreign_keys=[player1_session_id]
    )
    player2_session = relationship(
        "GameSession", foreign_keys=[player2_session_id]
    )
    winner = relationship("User", foreign_keys=[winner_user_id])
