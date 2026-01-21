"""
TDD Tests for Special Image API (Premium/Blur)
TASK-013: 결제 상태 + Blur 처리
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.game import GameSession, CharacterSetting


class TestSpecialImageAPI:
    """Tests for GET /api/scenes/{session_id}/special-image endpoint"""

    @pytest.mark.asyncio
    async def test_get_special_image_with_invalid_session_returns_404(
        self, client: AsyncClient
    ):
        """
        When requesting special image with a non-existent session_id,
        the API should return 404 Not Found.
        """
        non_existent_session_id = str(uuid.uuid4())

        response = await client.get(
            f"/api/scenes/{non_existent_session_id}/special-image",
            params={"image_url": "https://example.com/image.jpg"}
        )

        assert response.status_code == 404
        assert "Game session not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_special_image_for_non_premium_user_returns_blurred(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When requesting special image for a non-premium user,
        the API should return is_blurred: true.
        """
        # Create a non-premium user
        user = User(email="free@example.com", name="Free User", is_premium=False)
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

        test_image_url = "https://example.com/special-image.jpg"

        response = await client.get(
            f"/api/scenes/{session.id}/special-image",
            params={"image_url": test_image_url}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["image_url"] == test_image_url
        assert data["is_blurred"] is True

    @pytest.mark.asyncio
    async def test_get_special_image_for_premium_user_returns_not_blurred(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When requesting special image for a premium user,
        the API should return is_blurred: false.
        """
        # Create a premium user
        user = User(email="premium@example.com", name="Premium User", is_premium=True)
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

        test_image_url = "https://example.com/special-image.jpg"

        response = await client.get(
            f"/api/scenes/{session.id}/special-image",
            params={"image_url": test_image_url}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["image_url"] == test_image_url
        assert data["is_blurred"] is False
