"""
TDD Tests for Ending Event API
TASK-015: 엔딩 이벤트 (호감도 기반 이미지 생성)
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.game import GameSession, CharacterSetting


class TestEndingEventAPI:
    """Tests for POST /api/games/{session_id}/ending-event endpoint"""

    @pytest.mark.asyncio
    async def test_ending_event_with_invalid_session_returns_404(
        self, client: AsyncClient
    ):
        """
        When requesting ending event with a non-existent session_id,
        the API should return 404 Not Found.
        """
        non_existent_session_id = str(uuid.uuid4())

        response = await client.post(
            f"/api/games/{non_existent_session_id}/ending-event"
        )

        assert response.status_code == 404
        assert "Game session not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_ending_event_with_high_affection_returns_positive_image(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When affection >= 70, ending event should return positive image
        and set status to happy_ending.
        """
        # Create a test user
        user = User(email="happy@example.com", name="Happy User")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Create a game session with high affection at scene 10
        session = GameSession(
            user_id=user.id,
            affection=75,
            current_scene=10,
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

        response = await client.post(f"/api/games/{session.id}/ending-event")

        assert response.status_code == 200
        data = response.json()
        assert data["ending_type"] == "happy_ending"
        assert data["final_affection"] == 75
        assert "ending_image_url" in data
        assert data["is_positive"] is True

    @pytest.mark.asyncio
    async def test_ending_event_with_low_affection_returns_negative_image(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When affection < 70, ending event should return negative image
        and set status to sad_ending.
        """
        # Create a test user
        user = User(email="sad@example.com", name="Sad User")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Create a game session with low affection at scene 10
        session = GameSession(
            user_id=user.id,
            affection=45,
            current_scene=10,
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
            mbti="ISTP",
            art_style="realistic",
        )
        test_db.add(character_setting)
        await test_db.commit()

        response = await client.post(f"/api/games/{session.id}/ending-event")

        assert response.status_code == 200
        data = response.json()
        assert data["ending_type"] == "sad_ending"
        assert data["final_affection"] == 45
        assert "ending_image_url" in data
        assert data["is_positive"] is False

    @pytest.mark.asyncio
    async def test_ending_event_for_already_ended_game_returns_400(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When requesting ending event for an already ended game,
        the API should return 400 Bad Request.
        """
        # Create a test user
        user = User(email="ended@example.com", name="Ended User")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Create an already ended game session
        session = GameSession(
            user_id=user.id,
            affection=80,
            current_scene=10,
            status="happy_ending",
        )
        test_db.add(session)
        await test_db.commit()
        await test_db.refresh(session)

        response = await client.post(f"/api/games/{session.id}/ending-event")

        assert response.status_code == 400
        assert "Game already ended" in response.json()["detail"]
