"""
TDD Tests for User Gallery API
사용자 갤러리 - 세션 삭제와 무관하게 이미지 보관
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class TestUserGalleryAPI:
    """Tests for GET /api/users/{user_id}/gallery endpoint"""

    @pytest.mark.asyncio
    async def test_get_gallery_with_invalid_user_returns_404(
        self, client: AsyncClient
    ):
        """
        When requesting gallery with a non-existent user_id,
        the API should return 404 Not Found.
        """
        non_existent_user_id = str(uuid.uuid4())

        response = await client.get(
            f"/api/users/{non_existent_user_id}/gallery"
        )

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_premium_user_sees_all_images_without_blur(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        Premium users should see all images (expression + special) without blur.
        """
        from app.models.gallery import UserGallery

        # Create a premium user
        user = User(
            email="premium@example.com",
            name="Premium User",
            is_premium=True
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Add expression images (6 types)
        for expr_type in ["neutral", "happy", "sad", "jealous", "shy", "excited"]:
            gallery_item = UserGallery(
                user_id=user.id,
                image_url=f"https://example.com/{expr_type}.jpg",
                image_type="expression",
                expression_type=expr_type,
            )
            test_db.add(gallery_item)

        # Add special event images
        special_item = UserGallery(
            user_id=user.id,
            image_url="https://example.com/special-event.jpg",
            image_type="special",
        )
        test_db.add(special_item)

        # Add ending image
        ending_item = UserGallery(
            user_id=user.id,
            image_url="https://example.com/happy-ending.jpg",
            image_type="ending",
        )
        test_db.add(ending_item)
        await test_db.commit()

        response = await client.get(f"/api/users/{user.id}/gallery")

        assert response.status_code == 200
        data = response.json()
        assert len(data["images"]) == 8  # 6 expressions + 1 special + 1 ending

        # All images should NOT be blurred for premium user
        for image in data["images"]:
            assert image["is_blurred"] is False

    @pytest.mark.asyncio
    async def test_non_premium_user_sees_expression_images_without_blur(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        Non-premium users should see expression images without blur.
        """
        from app.models.gallery import UserGallery

        # Create a non-premium user
        user = User(
            email="free@example.com",
            name="Free User",
            is_premium=False
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Add expression images
        for expr_type in ["neutral", "happy", "sad"]:
            gallery_item = UserGallery(
                user_id=user.id,
                image_url=f"https://example.com/{expr_type}.jpg",
                image_type="expression",
                expression_type=expr_type,
            )
            test_db.add(gallery_item)
        await test_db.commit()

        response = await client.get(f"/api/users/{user.id}/gallery")

        assert response.status_code == 200
        data = response.json()

        # Expression images should NOT be blurred
        expression_images = [img for img in data["images"] if img["image_type"] == "expression"]
        for image in expression_images:
            assert image["is_blurred"] is False

    @pytest.mark.asyncio
    async def test_non_premium_user_sees_special_images_with_blur(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        Non-premium users should see special/ending images WITH blur.
        """
        from app.models.gallery import UserGallery

        # Create a non-premium user
        user = User(
            email="free2@example.com",
            name="Free User 2",
            is_premium=False
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Add special event image
        special_item = UserGallery(
            user_id=user.id,
            image_url="https://example.com/special.jpg",
            image_type="special",
        )
        test_db.add(special_item)

        # Add ending image
        ending_item = UserGallery(
            user_id=user.id,
            image_url="https://example.com/ending.jpg",
            image_type="ending",
        )
        test_db.add(ending_item)
        await test_db.commit()

        response = await client.get(f"/api/users/{user.id}/gallery")

        assert response.status_code == 200
        data = response.json()

        # Special and ending images should be blurred for non-premium
        for image in data["images"]:
            if image["image_type"] in ["special", "ending"]:
                assert image["is_blurred"] is True

    @pytest.mark.asyncio
    async def test_save_image_to_gallery(
        self, client: AsyncClient, test_db: AsyncSession
    ):
        """
        When saving an image to gallery, it should be stored for the user.
        """
        # Create a user
        user = User(email="gallery@example.com", name="Gallery User")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # Save image to gallery
        response = await client.post(
            f"/api/users/{user.id}/gallery",
            json={
                "image_url": "https://example.com/new-image.jpg",
                "image_type": "special",
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["image_url"] == "https://example.com/new-image.jpg"
        assert data["image_type"] == "special"
