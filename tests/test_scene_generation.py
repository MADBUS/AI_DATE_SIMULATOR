"""
TDD Tests for Scene Generation API
TASK-009: MBTI 기반 선택지 생성
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.game import GameSession, CharacterSetting


class TestSceneGenerationAPI:
    """Tests for POST /api/scenes/{session_id}/generate endpoint"""

    @pytest.mark.asyncio
    async def test_generate_scene_with_invalid_session_returns_404(
        self, client: AsyncClient
    ):
        """
        When generating scene with a non-existent session_id,
        the API should return 404 Not Found.
        """
        non_existent_session_id = str(uuid.uuid4())

        response = await client.post(
            f"/api/scenes/{non_existent_session_id}/generate"
        )

        assert response.status_code == 404
        assert "Game session not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_generate_scene_uses_character_settings(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When generating scene for a session with character settings,
        the API should use character_setting (style, mbti) for content generation.
        """
        # Create a test user with MBTI
        user = User(email="test@example.com", name="Test User", mbti="ENFP")
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

        response = await client.post(
            f"/api/scenes/{session.id}/generate"
        )

        assert response.status_code == 200

        data = response.json()
        assert "scene_number" in data
        assert "dialogue" in data
        assert "choices" in data
        assert "affection" in data
        assert "status" in data
        assert len(data["choices"]) == 3

    @pytest.mark.asyncio
    async def test_generate_scene_returns_three_choices_with_different_deltas(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        Generated scene should have 3 choices with positive, neutral, and negative deltas.
        """
        # Create a test user with MBTI
        user = User(email="test@example.com", name="Test User", mbti="INFJ")
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

        # Create character settings
        character_setting = CharacterSetting(
            session_id=session.id,
            gender="male",
            style="cool",
            mbti="ENTJ",
            art_style="realistic",
        )
        test_db.add(character_setting)
        await test_db.commit()

        response = await client.post(
            f"/api/scenes/{session.id}/generate"
        )

        assert response.status_code == 200

        data = response.json()
        choices = data["choices"]
        assert len(choices) == 3

        # Check each choice has required fields
        for choice in choices:
            assert "id" in choice
            assert "text" in choice
            assert "delta" in choice

    @pytest.mark.asyncio
    async def test_generate_scene_for_ended_game_returns_400(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When generating scene for an ended game,
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
            f"/api/scenes/{session.id}/generate"
        )

        assert response.status_code == 400
        assert "Game already ended" in response.json()["detail"]
