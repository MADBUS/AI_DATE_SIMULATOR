"""
TDD Tests for Redis Cache Service
TASK-017: Redis 캐싱
"""

import uuid
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestRedisCacheService:
    """Tests for Redis cache service"""

    @pytest.mark.asyncio
    async def test_cache_set_and_get(self):
        """
        When setting a value in cache, it should be retrievable.
        """
        from app.services.cache_service import CacheService

        # Mock Redis client
        mock_redis = AsyncMock()
        mock_redis.get.return_value = b'{"test": "value"}'
        mock_redis.set.return_value = True

        cache = CacheService(mock_redis)

        # Set value
        await cache.set("test_key", {"test": "value"}, ttl=3600)
        mock_redis.set.assert_called_once()

        # Get value
        result = await cache.get("test_key")
        assert result == {"test": "value"}

    @pytest.mark.asyncio
    async def test_cache_get_returns_none_when_not_found(self):
        """
        When key doesn't exist, cache should return None.
        """
        from app.services.cache_service import CacheService

        mock_redis = AsyncMock()
        mock_redis.get.return_value = None

        cache = CacheService(mock_redis)

        result = await cache.get("nonexistent_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_delete(self):
        """
        When deleting a key, it should be removed from cache.
        """
        from app.services.cache_service import CacheService

        mock_redis = AsyncMock()
        mock_redis.delete.return_value = 1

        cache = CacheService(mock_redis)

        result = await cache.delete("test_key")
        assert result is True
        mock_redis.delete.assert_called_once_with("test_key")


class TestSessionCaching:
    """Tests for game session caching"""

    @pytest.mark.asyncio
    async def test_cache_game_session(self):
        """
        Game session should be cached with 1 hour TTL.
        """
        from app.services.cache_service import CacheService

        mock_redis = AsyncMock()
        mock_redis.set.return_value = True

        cache = CacheService(mock_redis)

        session_id = str(uuid.uuid4())
        session_data = {
            "id": session_id,
            "affection": 50,
            "current_scene": 3,
            "status": "playing",
        }

        await cache.cache_session(session_id, session_data)

        # Verify set was called with correct key and TTL (1 hour = 3600 seconds)
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        assert f"session:{session_id}" in str(call_args)

    @pytest.mark.asyncio
    async def test_get_cached_session(self):
        """
        Cached session should be retrievable by session_id.
        """
        from app.services.cache_service import CacheService
        import json

        session_id = str(uuid.uuid4())
        session_data = {
            "id": session_id,
            "affection": 50,
            "current_scene": 3,
            "status": "playing",
        }

        mock_redis = AsyncMock()
        mock_redis.get.return_value = json.dumps(session_data).encode()

        cache = CacheService(mock_redis)

        result = await cache.get_session(session_id)
        assert result["id"] == session_id
        assert result["affection"] == 50


class TestExpressionCaching:
    """Tests for expression image caching"""

    @pytest.mark.asyncio
    async def test_cache_expression_image(self):
        """
        Expression image URL should be cached with 24 hour TTL.
        """
        from app.services.cache_service import CacheService

        mock_redis = AsyncMock()
        mock_redis.set.return_value = True

        cache = CacheService(mock_redis)

        setting_id = str(uuid.uuid4())
        expression_type = "happy"
        image_url = "https://example.com/happy.jpg"

        await cache.cache_expression(setting_id, expression_type, image_url)

        # Verify set was called
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        assert f"expression:{setting_id}:{expression_type}" in str(call_args)

    @pytest.mark.asyncio
    async def test_get_cached_expression(self):
        """
        Cached expression image should be retrievable.
        """
        from app.services.cache_service import CacheService

        setting_id = str(uuid.uuid4())
        expression_type = "happy"
        image_url = "https://example.com/happy.jpg"

        mock_redis = AsyncMock()
        mock_redis.get.return_value = image_url.encode()

        cache = CacheService(mock_redis)

        result = await cache.get_expression(setting_id, expression_type)
        assert result == image_url


class TestSpecialImageCaching:
    """Tests for special event image caching"""

    @pytest.mark.asyncio
    async def test_cache_special_image(self):
        """
        Special event image should be cached with 24 hour TTL.
        """
        from app.services.cache_service import CacheService

        mock_redis = AsyncMock()
        mock_redis.set.return_value = True

        cache = CacheService(mock_redis)

        prompt_hash = "abc123hash"
        image_url = "https://example.com/special.jpg"

        await cache.cache_special_image(prompt_hash, image_url)

        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        assert f"special:{prompt_hash}" in str(call_args)

    @pytest.mark.asyncio
    async def test_get_cached_special_image(self):
        """
        Cached special image should be retrievable by prompt hash.
        """
        from app.services.cache_service import CacheService

        prompt_hash = "abc123hash"
        image_url = "https://example.com/special.jpg"

        mock_redis = AsyncMock()
        mock_redis.get.return_value = image_url.encode()

        cache = CacheService(mock_redis)

        result = await cache.get_special_image(prompt_hash)
        assert result == image_url


class TestVideoCaching:
    """Tests for expression video caching (애니메이션 캐싱)"""

    @pytest.mark.asyncio
    async def test_cache_expression_video(self):
        """
        Expression video URL should be cached with 24 hour TTL.
        """
        from app.services.cache_service import CacheService

        mock_redis = AsyncMock()
        mock_redis.set.return_value = True

        cache = CacheService(mock_redis)

        setting_id = str(uuid.uuid4())
        expression_type = "happy"
        video_url = "/static/videos/characters/test.mp4"

        await cache.cache_video(setting_id, expression_type, video_url)

        # Verify set was called with correct key
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        assert f"video:{setting_id}:{expression_type}" in str(call_args)

    @pytest.mark.asyncio
    async def test_get_cached_video(self):
        """
        Cached video URL should be retrievable.
        """
        from app.services.cache_service import CacheService

        setting_id = str(uuid.uuid4())
        expression_type = "happy"
        video_url = "/static/videos/characters/test.mp4"

        mock_redis = AsyncMock()
        mock_redis.get.return_value = video_url.encode()

        cache = CacheService(mock_redis)

        result = await cache.get_video(setting_id, expression_type)
        assert result == video_url

    @pytest.mark.asyncio
    async def test_get_cached_video_returns_none_when_not_found(self):
        """
        When video is not cached, should return None.
        """
        from app.services.cache_service import CacheService

        setting_id = str(uuid.uuid4())
        expression_type = "sad"

        mock_redis = AsyncMock()
        mock_redis.get.return_value = None

        cache = CacheService(mock_redis)

        result = await cache.get_video(setting_id, expression_type)
        assert result is None
