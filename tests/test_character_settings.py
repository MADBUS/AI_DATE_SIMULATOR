"""
TDD Tests for Character Settings API
TASK-004: 연애 대상자 커스터마이징 API
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class TestCharacterSettingsAPI:
    """Tests for POST /api/character_settings/ endpoint"""

    @pytest.mark.asyncio
    async def test_create_character_settings_with_invalid_user_returns_404(
        self, client: AsyncClient
    ):
        """
        RED Phase Test 1:
        When creating character settings with a non-existent user_id,
        the API should return 404 Not Found.
        """
        non_existent_user_id = str(uuid.uuid4())

        payload = {
            "user_id": non_existent_user_id,
            "gender": "female",
            "style": "tsundere",
            "mbti": "INTJ",
            "art_style": "anime"
        }

        response = await client.post("/api/character_settings/", json=payload)

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_character_settings_with_valid_user_returns_201(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        RED Phase Test 2:
        When creating character settings with a valid user_id,
        the API should return 201 Created with the game session and character settings.
        """
        # Create a test user
        user = User(
            email="test@example.com",
            name="Test User",
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        payload = {
            "user_id": str(user.id),
            "gender": "female",
            "style": "tsundere",
            "mbti": "INTJ",
            "art_style": "anime"
        }

        response = await client.post("/api/character_settings/", json=payload)

        assert response.status_code == 201

        data = response.json()
        assert "id" in data
        assert data["user_id"] == str(user.id)
        assert data["status"] == "playing"
        assert data["current_scene"] == 1
        assert 30 <= data["affection"] <= 50  # Random affection between 30-50

        # Check character_settings in response
        assert "character_settings" in data
        settings = data["character_settings"]
        assert settings["gender"] == "female"
        assert settings["style"] == "tsundere"
        assert settings["mbti"] == "INTJ"
        assert settings["art_style"] == "anime"
