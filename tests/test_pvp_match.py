"""
PvP 매칭 시스템 테스트
TDD Phase 2: WebSocket 기반 PvP 매칭
"""

import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.game import GameSession
from app.models.pvp import PvPMatch


class TestPvPMatchModel:
    """PvP 매칭 모델 테스트"""

    @pytest.mark.asyncio
    async def test_pvp_match_model_exists(self):
        """PvPMatch 모델이 존재하는지 확인"""
        assert PvPMatch is not None

    @pytest.mark.asyncio
    async def test_pvp_match_has_required_fields(self):
        """PvPMatch 모델에 필수 필드가 있는지 확인"""
        # 모델 필드 확인
        assert hasattr(PvPMatch, 'id')
        assert hasattr(PvPMatch, 'player1_session_id')
        assert hasattr(PvPMatch, 'player2_session_id')
        assert hasattr(PvPMatch, 'player1_bet')
        assert hasattr(PvPMatch, 'player2_bet')
        assert hasattr(PvPMatch, 'final_bet')
        assert hasattr(PvPMatch, 'winner_user_id')
        assert hasattr(PvPMatch, 'loser_character_stolen')
        assert hasattr(PvPMatch, 'created_at')

    @pytest.mark.asyncio
    async def test_create_pvp_match(self, test_db: AsyncSession):
        """PvP 매칭 레코드 생성 테스트"""
        # User 1
        user1 = User(
            id=uuid4(),
            google_id="google_pvp_user1",
            email="pvp1@test.com",
            name="PvP User 1",
            mbti="ENFP",
        )
        test_db.add(user1)

        # User 2
        user2 = User(
            id=uuid4(),
            google_id="google_pvp_user2",
            email="pvp2@test.com",
            name="PvP User 2",
            mbti="INTJ",
        )
        test_db.add(user2)
        await test_db.flush()

        # Game Session 1
        session1 = GameSession(
            id=uuid4(),
            user_id=user1.id,
            affection=50,
            current_scene=5,
            status="playing",
            save_slot=1,
        )
        test_db.add(session1)

        # Game Session 2
        session2 = GameSession(
            id=uuid4(),
            user_id=user2.id,
            affection=60,
            current_scene=5,
            status="playing",
            save_slot=1,
        )
        test_db.add(session2)
        await test_db.flush()

        # PvP 매칭 생성
        pvp_match = PvPMatch(
            player1_session_id=session1.id,
            player2_session_id=session2.id,
            player1_bet=10,
            player2_bet=15,
            final_bet=15,  # 높은 쪽으로 결정
            winner_user_id=user1.id,
            loser_character_stolen=False,
        )
        test_db.add(pvp_match)
        await test_db.commit()

        # 조회 확인
        result = await test_db.execute(
            select(PvPMatch).where(PvPMatch.id == pvp_match.id)
        )
        saved_match = result.scalar_one_or_none()

        assert saved_match is not None
        assert saved_match.player1_session_id == session1.id
        assert saved_match.player2_session_id == session2.id
        assert saved_match.player1_bet == 10
        assert saved_match.player2_bet == 15
        assert saved_match.final_bet == 15
        assert saved_match.winner_user_id == user1.id
        assert saved_match.loser_character_stolen is False
