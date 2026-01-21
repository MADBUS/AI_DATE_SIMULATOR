"""
TDD Tests for Character Expressions API
TASK-007: 표정 이미지 6종 사전 생성
"""

import uuid
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.game import GameSession, CharacterSetting


class TestCharacterExpressionsAPI:
    """Tests for POST /api/games/{session_id}/generate-expressions endpoint"""

    @pytest.mark.asyncio
    async def test_generate_expressions_with_invalid_session_returns_404(
        self, client: AsyncClient
    ):
        """
        When generating expressions with a non-existent session_id,
        the API should return 404 Not Found.
        """
        non_existent_session_id = str(uuid.uuid4())

        response = await client.post(
            f"/api/games/{non_existent_session_id}/generate-expressions"
        )

        assert response.status_code == 404
        assert "Game session not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_generate_expressions_without_character_settings_returns_400(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When generating expressions for a session without character settings,
        the API should return 400 Bad Request.
        """
        # Create a test user
        user = User(email="test@example.com", name="Test User")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Create a game session without character settings
        session = GameSession(
            user_id=user.id,
            affection=40,
            current_scene=1,
            status="playing",
        )
        test_db.add(session)
        await test_db.commit()
        await test_db.refresh(session)

        response = await client.post(
            f"/api/games/{session.id}/generate-expressions"
        )

        assert response.status_code == 400
        assert "Character settings not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_generate_expressions_creates_six_expressions(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When generating expressions for a valid session with character settings,
        the API should create 6 expression images and return them.
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

        # Mock the Gemini image generation
        mock_image_url = "https://example.com/generated-image.png"
        with patch(
            "app.api.expressions.generate_expression_image",
            new_callable=AsyncMock,
            return_value=mock_image_url,
        ):
            response = await client.post(
                f"/api/games/{session.id}/generate-expressions"
            )

        assert response.status_code == 201

        data = response.json()
        assert "expressions" in data
        assert len(data["expressions"]) == 6

        # Check all 6 expression types are present
        expression_types = {expr["expression_type"] for expr in data["expressions"]}
        expected_types = {"neutral", "happy", "sad", "jealous", "shy", "excited"}
        assert expression_types == expected_types

        # Check each expression has required fields
        for expr in data["expressions"]:
            assert "id" in expr
            assert "expression_type" in expr
            assert "image_url" in expr
