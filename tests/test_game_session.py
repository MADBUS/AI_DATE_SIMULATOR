"""
TDD Tests for Game Session API
TASK-005: 게임 세션 생성 및 조회
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.game import GameSession, CharacterSetting


class TestGameSessionAPI:
    """Tests for GET /api/games/{session_id} endpoint"""

    @pytest.mark.asyncio
    async def test_get_game_session_with_invalid_id_returns_404(
        self, client: AsyncClient
    ):
        """
        RED Phase Test 1:
        When getting a game session with a non-existent session_id,
        the API should return 404 Not Found.
        """
        non_existent_session_id = str(uuid.uuid4())

        response = await client.get(f"/api/games/{non_existent_session_id}")

        assert response.status_code == 404
        assert "Game session not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_game_session_with_valid_id_returns_session_with_settings(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        RED Phase Test 2:
        When getting a game session with a valid session_id,
        the API should return the session with character_settings included.
        """
        # Create a test user
        user = User(
            email="test@example.com",
            name="Test User",
        )
        test_db.add(user)
        await test_db.flush()

        # Create a game session
        game_session = GameSession(
            user_id=user.id,
            affection=42,
            current_scene=1,
            status="playing",
            save_slot=1,
        )
        test_db.add(game_session)
        await test_db.flush()

        # Create character settings
        character_setting = CharacterSetting(
            session_id=game_session.id,
            gender="female",
            style="tsundere",
            mbti="INTJ",
            art_style="anime",
        )
        test_db.add(character_setting)
        await test_db.commit()

        response = await client.get(f"/api/games/{game_session.id}")

        assert response.status_code == 200

        data = response.json()
        assert data["id"] == str(game_session.id)
        assert data["affection"] == 42
        assert data["status"] == "playing"
        assert data["current_scene"] == 1
        assert data["save_slot"] == 1

        # Check character_settings in response
        assert "character_settings" in data
        settings = data["character_settings"]
        assert settings["gender"] == "female"
        assert settings["style"] == "tsundere"
        assert settings["mbti"] == "INTJ"
        assert settings["art_style"] == "anime"
