"""
TDD Tests for Select Choice with Emotion Response
TASK: 선택지 선택 시 감정 이미지 반환
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.game import GameSession, CharacterSetting, CharacterExpression


class TestSelectChoiceWithEmotionAPI:
    """Tests for POST /api/games/{session_id}/select endpoint with emotion response"""

    @pytest.mark.asyncio
    async def test_select_choice_with_invalid_session_returns_404(
        self, client: AsyncClient
    ):
        """
        When selecting a choice with a non-existent session_id,
        the API should return 404 Not Found.
        """
        non_existent_session_id = str(uuid.uuid4())

        response = await client.post(
            f"/api/games/{non_existent_session_id}/select",
            json={"affection_delta": 5, "expression_type": "happy"}
        )

        assert response.status_code == 404
        assert "Game session not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_select_choice_returns_expression_image_url(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When selecting a choice with expression_type,
        the API should return the corresponding expression image URL from DB.
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
        await test_db.refresh(character_setting)

        # Create expression images (6 types)
        expressions = [
            ("neutral", "https://example.com/neutral.jpg"),
            ("happy", "https://example.com/happy.jpg"),
            ("sad", "https://example.com/sad.jpg"),
            ("jealous", "https://example.com/jealous.jpg"),
            ("shy", "https://example.com/shy.jpg"),
            ("excited", "https://example.com/excited.jpg"),
        ]
        for expr_type, url in expressions:
            expr = CharacterExpression(
                setting_id=character_setting.id,
                expression_type=expr_type,
                image_url=url,
            )
            test_db.add(expr)
        await test_db.commit()

        # Select choice with expression_type
        response = await client.post(
            f"/api/games/{session.id}/select",
            json={"affection_delta": 5, "expression_type": "happy"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "expression_image_url" in data
        assert data["expression_image_url"] == "https://example.com/happy.jpg"
        assert data["expression_type"] == "happy"

    @pytest.mark.asyncio
    async def test_select_choice_with_negative_delta_returns_sad_expression(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When selecting a choice with negative delta and sad expression,
        the API should return the sad expression image URL.
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
            current_scene=4,
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
        await test_db.refresh(character_setting)

        # Create expression image for sad
        sad_expr = CharacterExpression(
            setting_id=character_setting.id,
            expression_type="sad",
            image_url="https://example.com/sad-cool.jpg",
        )
        test_db.add(sad_expr)
        await test_db.commit()

        # Select choice with negative delta
        response = await client.post(
            f"/api/games/{session.id}/select",
            json={"affection_delta": -10, "expression_type": "sad"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["expression_image_url"] == "https://example.com/sad-cool.jpg"
        assert data["expression_type"] == "sad"
        assert data["new_affection"] == 50  # 60 - 10

    @pytest.mark.asyncio
    async def test_select_choice_without_expression_returns_neutral(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When selecting a choice without expression_type,
        the API should return neutral expression as default.
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
            current_scene=2,
            status="playing",
        )
        test_db.add(session)
        await test_db.commit()
        await test_db.refresh(session)

        # Create character settings
        character_setting = CharacterSetting(
            session_id=session.id,
            gender="female",
            style="cute",
            mbti="ENFP",
            art_style="anime",
        )
        test_db.add(character_setting)
        await test_db.commit()
        await test_db.refresh(character_setting)

        # Create neutral expression
        neutral_expr = CharacterExpression(
            setting_id=character_setting.id,
            expression_type="neutral",
            image_url="https://example.com/neutral-cute.jpg",
        )
        test_db.add(neutral_expr)
        await test_db.commit()

        # Select choice without expression_type (should default to neutral)
        response = await client.post(
            f"/api/games/{session.id}/select",
            json={"affection_delta": 3}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["expression_image_url"] == "https://example.com/neutral-cute.jpg"
        assert data["expression_type"] == "neutral"
