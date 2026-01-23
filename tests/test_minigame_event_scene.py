"""
TDD Tests for Minigame Result - Event Scene Display
Feature: 이벤트 씬 승리 시에만 표시
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.game import GameSession


class TestMinigameEventScene:
    """Tests for show_event_scene in minigame result"""

    @pytest.mark.asyncio
    async def test_minigame_success_returns_show_event_scene_true(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When minigame is successful (success=True),
        the API should return show_event_scene=True.
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
            current_scene=5,
            status="playing",
        )
        test_db.add(session)
        await test_db.commit()
        await test_db.refresh(session)

        payload = {"success": True}

        response = await client.post(
            f"/api/scenes/{session.id}/minigame-result",
            json=payload,
        )

        assert response.status_code == 200

        data = response.json()
        assert "show_event_scene" in data
        assert data["show_event_scene"] is True

    @pytest.mark.asyncio
    async def test_minigame_failure_returns_show_event_scene_false(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When minigame fails (success=False),
        the API should return show_event_scene=False.
        """
        # Create a test user
        user = User(email="test2@example.com", name="Test User 2")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Create a game session
        session = GameSession(
            user_id=user.id,
            affection=50,
            current_scene=5,
            status="playing",
        )
        test_db.add(session)
        await test_db.commit()
        await test_db.refresh(session)

        payload = {"success": False}

        response = await client.post(
            f"/api/scenes/{session.id}/minigame-result",
            json=payload,
        )

        assert response.status_code == 200

        data = response.json()
        assert "show_event_scene" in data
        assert data["show_event_scene"] is False
