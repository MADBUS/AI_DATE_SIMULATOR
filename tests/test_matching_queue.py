"""
매칭 큐 시스템 테스트
TDD Phase 2: Redis 기반 PvP 매칭 큐
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.matching_service import MatchingService


class TestMatchingQueue:
    """매칭 큐 시스템 테스트"""

    @pytest.mark.asyncio
    async def test_matching_service_exists(self):
        """MatchingService 클래스가 존재하는지 확인"""
        assert MatchingService is not None

    @pytest.mark.asyncio
    async def test_add_to_queue(self):
        """매칭 큐에 플레이어 추가 테스트"""
        mock_redis = AsyncMock()
        mock_redis.zadd.return_value = 1

        service = MatchingService(mock_redis)
        session_id = uuid4()
        bet_amount = 10

        result = await service.add_to_queue(str(session_id), bet_amount)

        assert result is True
        mock_redis.zadd.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_from_queue(self):
        """매칭 큐에서 플레이어 제거 테스트"""
        mock_redis = AsyncMock()
        mock_redis.zrem.return_value = 1

        service = MatchingService(mock_redis)
        session_id = uuid4()

        result = await service.remove_from_queue(str(session_id))

        assert result is True
        mock_redis.zrem.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_match_returns_opponent_when_available(self):
        """매칭 상대가 있을 때 상대 반환 테스트"""
        mock_redis = AsyncMock()
        session_id = str(uuid4())
        opponent_id = str(uuid4())

        # Mock: 큐에 다른 플레이어가 있음
        mock_redis.zrange.return_value = [opponent_id.encode()]
        mock_redis.zscore.return_value = 15.0  # opponent bet amount
        mock_redis.zrem.return_value = 1

        service = MatchingService(mock_redis)

        result = await service.find_match(session_id, bet_amount=10)

        assert result is not None
        assert result["opponent_session_id"] == opponent_id
        assert result["opponent_bet"] == 15

    @pytest.mark.asyncio
    async def test_find_match_returns_none_when_no_opponent(self):
        """매칭 상대가 없을 때 None 반환 테스트"""
        mock_redis = AsyncMock()
        session_id = str(uuid4())

        # Mock: 큐가 비어있음
        mock_redis.zrange.return_value = []

        service = MatchingService(mock_redis)

        result = await service.find_match(session_id, bet_amount=10)

        assert result is None

    @pytest.mark.asyncio
    async def test_find_match_excludes_self(self):
        """매칭 시 자기 자신은 제외하는지 테스트"""
        mock_redis = AsyncMock()
        session_id = str(uuid4())

        # Mock: 큐에 자기 자신만 있음
        mock_redis.zrange.return_value = [session_id.encode()]

        service = MatchingService(mock_redis)

        result = await service.find_match(session_id, bet_amount=10)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_queue_size(self):
        """큐 사이즈 조회 테스트"""
        mock_redis = AsyncMock()
        mock_redis.zcard.return_value = 5

        service = MatchingService(mock_redis)

        result = await service.get_queue_size()

        assert result == 5
        mock_redis.zcard.assert_called_once()
