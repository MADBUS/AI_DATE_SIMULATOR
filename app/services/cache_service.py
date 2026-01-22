"""
Redis Cache Service
TTL 설정:
- session: 1시간 (3600초)
- expression: 24시간 (86400초)
- special: 24시간 (86400초)
"""

import json
from typing import Any, Optional


# TTL Constants (in seconds)
SESSION_TTL = 3600  # 1 hour
EXPRESSION_TTL = 86400  # 24 hours
SPECIAL_IMAGE_TTL = 86400  # 24 hours
VIDEO_TTL = 86400  # 24 hours (애니메이션 비디오)


class CacheService:
    """Redis cache service for game data caching"""

    def __init__(self, redis_client):
        self.redis = redis_client

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set a value in cache with TTL"""
        if isinstance(value, dict):
            value = json.dumps(value)
        await self.redis.set(key, value, ex=ttl)
        return True

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        value = await self.redis.get(key)
        if value is None:
            return None

        # Try to parse as JSON
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value.decode() if isinstance(value, bytes) else value

    async def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        result = await self.redis.delete(key)
        return result > 0

    # Session caching methods
    async def cache_session(self, session_id: str, session_data: dict) -> bool:
        """Cache game session with 1 hour TTL"""
        key = f"session:{session_id}"
        return await self.set(key, session_data, ttl=SESSION_TTL)

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get cached game session"""
        key = f"session:{session_id}"
        return await self.get(key)

    async def invalidate_session(self, session_id: str) -> bool:
        """Invalidate cached session"""
        key = f"session:{session_id}"
        return await self.delete(key)

    # Expression image caching methods
    async def cache_expression(
        self, setting_id: str, expression_type: str, image_url: str
    ) -> bool:
        """Cache expression image URL with 24 hour TTL"""
        key = f"expression:{setting_id}:{expression_type}"
        await self.redis.set(key, image_url, ex=EXPRESSION_TTL)
        return True

    async def get_expression(
        self, setting_id: str, expression_type: str
    ) -> Optional[str]:
        """Get cached expression image URL"""
        key = f"expression:{setting_id}:{expression_type}"
        value = await self.redis.get(key)
        if value is None:
            return None
        return value.decode() if isinstance(value, bytes) else value

    # Special image caching methods
    async def cache_special_image(self, prompt_hash: str, image_url: str) -> bool:
        """Cache special event image URL with 24 hour TTL"""
        key = f"special:{prompt_hash}"
        await self.redis.set(key, image_url, ex=SPECIAL_IMAGE_TTL)
        return True

    async def get_special_image(self, prompt_hash: str) -> Optional[str]:
        """Get cached special image URL"""
        key = f"special:{prompt_hash}"
        value = await self.redis.get(key)
        if value is None:
            return None
        return value.decode() if isinstance(value, bytes) else value

    # Video caching methods (애니메이션 비디오)
    async def cache_video(
        self, setting_id: str, expression_type: str, video_url: str
    ) -> bool:
        """Cache expression video URL with 24 hour TTL"""
        key = f"video:{setting_id}:{expression_type}"
        await self.redis.set(key, video_url, ex=VIDEO_TTL)
        return True

    async def get_video(
        self, setting_id: str, expression_type: str
    ) -> Optional[str]:
        """Get cached expression video URL"""
        key = f"video:{setting_id}:{expression_type}"
        value = await self.redis.get(key)
        if value is None:
            return None
        return value.decode() if isinstance(value, bytes) else value
