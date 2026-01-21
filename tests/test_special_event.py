"""
TDD Tests for Special Event API
TASK-012: 특별 이벤트 시스템
"""

import uuid
import pytest
from unittest.mock import patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.game import GameSession, CharacterSetting


class TestSpecialEventAPI:
    """Tests for POST /api/scenes/{session_id}/check-event endpoint"""

    @pytest.mark.asyncio
    async def test_check_event_with_invalid_session_returns_404(
        self, client: AsyncClient
    ):
        """
        When checking event with a non-existent session_id,
        the API should return 404 Not Found.
        """
        non_existent_session_id = str(uuid.uuid4())

        response = await client.post(
            f"/api/scenes/{non_existent_session_id}/check-event"
        )

        assert response.status_code == 404
        assert "Game session not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_check_event_returns_no_event_when_random_is_high(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When random value is above threshold (0.15),
        the API should return is_special_event: false.
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
            current_scene=3,
            status="playing",
        )
        test_db.add(session)
        await test_db.commit()
        await test_db.refresh(session)

        # Mock random to return 0.5 (above 0.15 threshold)
        with patch("app.api.scenes.random.random", return_value=0.5):
            response = await client.post(
                f"/api/scenes/{session.id}/check-event"
            )

        assert response.status_code == 200
        data = response.json()
        assert data["is_special_event"] is False

    @pytest.mark.asyncio
    async def test_check_event_returns_event_when_random_is_low(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When random value is below threshold (0.15),
        the API should return is_special_event: true with special image.
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
            current_scene=5,
            status="playing",
        )
        test_db.add(session)
        await test_db.commit()
        await test_db.refresh(session)

        # Create character settings
        character_setting = CharacterSetting(
            session_id=session.id,
            gender="female",
            style="tsundere",
            mbti="INTJ",
            art_style="anime",
        )
        test_db.add(character_setting)
        await test_db.commit()

        # Mock random to return 0.1 (below 0.15 threshold)
        with patch("app.api.scenes.random.random", return_value=0.1):
            response = await client.post(
                f"/api/scenes/{session.id}/check-event"
            )

        assert response.status_code == 200
        data = response.json()
        assert data["is_special_event"] is True
        assert "special_image_url" in data
        assert data["show_minigame"] is True

    @pytest.mark.asyncio
    async def test_check_event_for_ended_game_returns_400(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When checking event for an ended game,
        the API should return 400 Bad Request.
        """
        # Create a test user
        user = User(email="test@example.com", name="Test User")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Create an ended game session
        session = GameSession(
            user_id=user.id,
            affection=80,
            current_scene=10,
            status="happy_ending",
        )
        test_db.add(session)
        await test_db.commit()
        await test_db.refresh(session)

        response = await client.post(
            f"/api/scenes/{session.id}/check-event"
        )

        assert response.status_code == 400
        assert "Game already ended" in response.json()["detail"]
