"""
TDD Tests for SpecialEventImage Model
Feature: special_event_images 테이블 생성
"""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.game import GameSession, SpecialEventImage


class TestSpecialEventImageModel:
    """Tests for SpecialEventImage model"""

    @pytest.mark.asyncio
    async def test_create_special_event_image(self, test_db: AsyncSession):
        """
        SpecialEventImage model should be created successfully
        with session_id, event_type, image_url, and is_nsfw fields.
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

        # Create a special event image
        special_image = SpecialEventImage(
            session_id=session.id,
            event_type="romantic_date",
            image_url="https://example.com/special_image.jpg",
            is_nsfw=False,
        )
        test_db.add(special_image)
        await test_db.commit()
        await test_db.refresh(special_image)

        # Verify the image was created
        assert special_image.id is not None
        assert special_image.session_id == session.id
        assert special_image.event_type == "romantic_date"
        assert special_image.image_url == "https://example.com/special_image.jpg"
        assert special_image.is_nsfw is False

    @pytest.mark.asyncio
    async def test_special_event_image_with_video_url(self, test_db: AsyncSession):
        """
        SpecialEventImage should support optional video_url field.
        """
        # Create a test user
        user = User(email="test2@example.com", name="Test User 2")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Create a game session
        session = GameSession(
            user_id=user.id,
            affection=60,
            current_scene=10,
            status="playing",
        )
        test_db.add(session)
        await test_db.commit()
        await test_db.refresh(session)

        # Create a special event image with video
        special_image = SpecialEventImage(
            session_id=session.id,
            event_type="surprise_gift",
            image_url="https://example.com/special_image2.jpg",
            video_url="https://example.com/special_video.mp4",
            is_nsfw=True,
        )
        test_db.add(special_image)
        await test_db.commit()
        await test_db.refresh(special_image)

        # Verify the image was created with video_url
        assert special_image.video_url == "https://example.com/special_video.mp4"
        assert special_image.is_nsfw is True

    @pytest.mark.asyncio
    async def test_query_special_event_images_by_session(self, test_db: AsyncSession):
        """
        Should be able to query special event images by session_id.
        """
        # Create a test user
        user = User(email="test3@example.com", name="Test User 3")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Create a game session
        session = GameSession(
            user_id=user.id,
            affection=70,
            current_scene=15,
            status="playing",
        )
        test_db.add(session)
        await test_db.commit()
        await test_db.refresh(session)

        # Create multiple special event images
        for i, event_type in enumerate(["romantic_date", "rain_shelter", "festival"]):
            special_image = SpecialEventImage(
                session_id=session.id,
                event_type=event_type,
                image_url=f"https://example.com/special_{i}.jpg",
                is_nsfw=False,
            )
            test_db.add(special_image)

        await test_db.commit()

        # Query images by session_id
        result = await test_db.execute(
            select(SpecialEventImage).where(SpecialEventImage.session_id == session.id)
        )
        images = result.scalars().all()

        assert len(images) == 3
        event_types = [img.event_type for img in images]
        assert "romantic_date" in event_types
        assert "rain_shelter" in event_types
        assert "festival" in event_types
