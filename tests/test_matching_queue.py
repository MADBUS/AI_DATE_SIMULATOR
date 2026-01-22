"""
매칭 큐 시스템 테스트
TDD Phase 2: Redis 기반 PvP 매칭 큐
"""

import pytest
import asyncio
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.matching_service import MatchingService, MATCHING_TIMEOUT_SECONDS


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


class TestMatchingTimeout:
    """매칭 타임아웃 테스트"""

    def test_timeout_constant_is_30_seconds(self):
        """타임아웃 상수가 30초인지 확인"""
        assert MATCHING_TIMEOUT_SECONDS == 30

    @pytest.mark.asyncio
    async def test_wait_for_match_with_timeout_returns_opponent(self):
        """타임아웃 내에 매칭 성공 시 상대 반환"""
        mock_redis = AsyncMock()
        session_id = str(uuid4())
        opponent_id = str(uuid4())

        # Mock: 첫 번째 호출에서 매칭 성공
        mock_redis.zadd.return_value = 1
        mock_redis.zrange.return_value = [opponent_id.encode()]
        mock_redis.zscore.return_value = 15.0
        mock_redis.zrem.return_value = 1

        service = MatchingService(mock_redis)

        # 짧은 타임아웃으로 테스트 (실제로는 30초)
        result = await service.wait_for_match_with_timeout(
            session_id, bet_amount=10, timeout_seconds=1
        )

        assert result is not None
        assert result["status"] == "matched"
        assert result["opponent_session_id"] == opponent_id

    @pytest.mark.asyncio
    async def test_wait_for_match_timeout_returns_timeout_status(self):
        """타임아웃 시 timeout 상태 반환"""
        mock_redis = AsyncMock()
        session_id = str(uuid4())

        # Mock: 항상 매칭 실패
        mock_redis.zadd.return_value = 1
        mock_redis.zrange.return_value = []
        mock_redis.zrem.return_value = 1

        service = MatchingService(mock_redis)

        # 매우 짧은 타임아웃으로 테스트
        result = await service.wait_for_match_with_timeout(
            session_id, bet_amount=10, timeout_seconds=0.1
        )

        assert result is not None
        assert result["status"] == "timeout"

    @pytest.mark.asyncio
    async def test_wait_for_match_removes_from_queue_on_timeout(self):
        """타임아웃 시 큐에서 제거"""
        mock_redis = AsyncMock()
        session_id = str(uuid4())

        # Mock: 항상 매칭 실패
        mock_redis.zadd.return_value = 1
        mock_redis.zrange.return_value = []
        mock_redis.zrem.return_value = 1

        service = MatchingService(mock_redis)

        await service.wait_for_match_with_timeout(
            session_id, bet_amount=10, timeout_seconds=0.1
        )

        # 타임아웃 후 큐에서 제거되었는지 확인
        mock_redis.zrem.assert_called()
