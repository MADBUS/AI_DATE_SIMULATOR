"""
TDD Tests for Minigame API
TASK-008: 미니게임 - 눈 마주치기 (백엔드 결과 저장)
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.game import GameSession


class TestMinigameAPI:
    """Tests for POST /api/minigame/{session_id}/result endpoint"""

    @pytest.mark.asyncio
    async def test_save_minigame_result_with_invalid_session_returns_404(
        self, client: AsyncClient
    ):
        """
        When saving minigame result with a non-existent session_id,
        the API should return 404 Not Found.
        """
        non_existent_session_id = str(uuid.uuid4())

        payload = {
            "result": "perfect",
            "scene_number": 1,
        }

        response = await client.post(
            f"/api/minigame/{non_existent_session_id}/result",
            json=payload,
        )

        assert response.status_code == 404
        assert "Game session not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_save_minigame_result_perfect_adds_bonus_affection(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When saving a 'perfect' minigame result,
        the API should add +3 bonus affection.
        """
        # Create a test user
        user = User(email="test@example.com", name="Test User")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Create a game session
        session = GameSession(
            user_id=user.id,
            affection=40,
            current_scene=1,
            status="playing",
        )
        test_db.add(session)
        await test_db.commit()
        await test_db.refresh(session)

        payload = {
            "result": "perfect",
            "scene_number": 1,
        }

        response = await client.post(
            f"/api/minigame/{session.id}/result",
            json=payload,
        )

        assert response.status_code == 201

        data = response.json()
        assert data["result"] == "perfect"
        assert data["bonus_affection"] == 3
        assert data["new_affection"] == 43  # 40 + 3

    @pytest.mark.asyncio
    async def test_save_minigame_result_great_adds_bonus_affection(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When saving a 'great' minigame result,
        the API should add +1 bonus affection.
        """
        # Create a test user
        user = User(email="test@example.com", name="Test User")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Create a game session
        session = GameSession(
            user_id=user.id,
            affection=50,
            current_scene=2,
            status="playing",
        )
        test_db.add(session)
        await test_db.commit()
        await test_db.refresh(session)

        payload = {
            "result": "great",
            "scene_number": 2,
        }

        response = await client.post(
            f"/api/minigame/{session.id}/result",
            json=payload,
        )

        assert response.status_code == 201

        data = response.json()
        assert data["result"] == "great"
        assert data["bonus_affection"] == 1
        assert data["new_affection"] == 51  # 50 + 1

    @pytest.mark.asyncio
    async def test_save_minigame_result_miss_no_bonus(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When saving a 'miss' minigame result,
        the API should add 0 bonus affection.
        """
        # Create a test user
        user = User(email="test@example.com", name="Test User")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Create a game session
        session = GameSession(
            user_id=user.id,
            affection=60,
            current_scene=3,
            status="playing",
        )
        test_db.add(session)
        await test_db.commit()
        await test_db.refresh(session)

        payload = {
            "result": "miss",
            "scene_number": 3,
        }

        response = await client.post(
            f"/api/minigame/{session.id}/result",
            json=payload,
        )

        assert response.status_code == 201

        data = response.json()
        assert data["result"] == "miss"
        assert data["bonus_affection"] == 0
        assert data["new_affection"] == 60  # No change
