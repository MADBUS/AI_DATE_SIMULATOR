"""
솔로 미니게임 트리거 테스트
TDD Phase 2: 매칭 실패 시 솔로 미니게임 트리거 (난이도 상향)
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock

from app.services.solo_minigame_service import (
    SoloMinigameService,
    SOLO_MINIGAME_DIFFICULTY,
    DEFAULT_MINIGAME_DIFFICULTY,
)


class TestSoloMinigameDifficulty:
    """솔로 미니게임 난이도 테스트"""

    def test_solo_difficulty_has_higher_target_count(self):
        """솔로 미니게임은 목표 개수가 더 높음 (7 -> 12)"""
        assert SOLO_MINIGAME_DIFFICULTY["target_count"] == 12
        assert DEFAULT_MINIGAME_DIFFICULTY["target_count"] == 7

    def test_solo_difficulty_has_shorter_time(self):
        """솔로 미니게임은 시간이 더 짧음 (8초 -> 6초)"""
        assert SOLO_MINIGAME_DIFFICULTY["time_seconds"] == 6
        assert DEFAULT_MINIGAME_DIFFICULTY["time_seconds"] == 8

    def test_solo_difficulty_has_smaller_heart_size(self):
        """솔로 미니게임은 하트 크기가 더 작음"""
        # 기본: 50-80px, 솔로: 40-60px
        assert SOLO_MINIGAME_DIFFICULTY["heart_size_min"] == 40
        assert SOLO_MINIGAME_DIFFICULTY["heart_size_max"] == 60
        assert DEFAULT_MINIGAME_DIFFICULTY["heart_size_min"] == 50
        assert DEFAULT_MINIGAME_DIFFICULTY["heart_size_max"] == 80

    def test_solo_difficulty_has_faster_heart_speed(self):
        """솔로 미니게임은 하트 속도가 더 빠름"""
        # 기본: 4-6초, 솔로: 2-4초
        assert SOLO_MINIGAME_DIFFICULTY["heart_duration_min"] == 2
        assert SOLO_MINIGAME_DIFFICULTY["heart_duration_max"] == 4
        assert DEFAULT_MINIGAME_DIFFICULTY["heart_duration_min"] == 4
        assert DEFAULT_MINIGAME_DIFFICULTY["heart_duration_max"] == 6


class TestMatchingTimeoutTrigger:
    """매칭 타임아웃 시 솔로 미니게임 트리거 테스트"""

    @pytest.mark.asyncio
    async def test_trigger_solo_minigame_on_matching_timeout(self):
        """매칭 타임아웃 시 솔로 미니게임 트리거"""
        service = SoloMinigameService()
        session_id = str(uuid4())

        result = await service.trigger_solo_minigame(session_id)

        assert result["trigger_minigame"] is True
        assert result["minigame_type"] == "solo"
        assert result["difficulty"] == SOLO_MINIGAME_DIFFICULTY

    @pytest.mark.asyncio
    async def test_solo_minigame_returns_session_id(self):
        """솔로 미니게임 결과에 세션 ID 포함"""
        service = SoloMinigameService()
        session_id = str(uuid4())

        result = await service.trigger_solo_minigame(session_id)

        assert result["session_id"] == session_id


class TestSoloMinigameResult:
    """솔로 미니게임 결과 테스트"""

    @pytest.mark.asyncio
    async def test_solo_minigame_success_gives_bonus_affection(self):
        """솔로 미니게임 성공 시 호감도 보너스"""
        service = SoloMinigameService()
        session_id = str(uuid4())

        result = await service.process_solo_minigame_result(
            session_id=session_id,
            hearts_touched=12,  # 목표 달성
            time_taken=5.5,
        )

        assert result["success"] is True
        assert result["bonus_affection"] > 0

    @pytest.mark.asyncio
    async def test_solo_minigame_failure_gives_penalty(self):
        """솔로 미니게임 실패 시 호감도 패널티"""
        service = SoloMinigameService()
        session_id = str(uuid4())

        result = await service.process_solo_minigame_result(
            session_id=session_id,
            hearts_touched=5,  # 목표 미달
            time_taken=6.0,
        )

        assert result["success"] is False
        assert result["penalty_affection"] < 0


class TestSoloMinigameResultStructure:
    """솔로 미니게임 결과 구조 테스트"""

    @pytest.mark.asyncio
    async def test_trigger_result_contains_required_fields(self):
        """트리거 결과에 필수 필드 포함"""
        service = SoloMinigameService()
        session_id = str(uuid4())

        result = await service.trigger_solo_minigame(session_id)

        assert "trigger_minigame" in result
        assert "minigame_type" in result
        assert "difficulty" in result
        assert "session_id" in result

    @pytest.mark.asyncio
    async def test_difficulty_contains_all_parameters(self):
        """난이도 설정에 모든 파라미터 포함"""
        service = SoloMinigameService()
        session_id = str(uuid4())

        result = await service.trigger_solo_minigame(session_id)
        difficulty = result["difficulty"]

        assert "target_count" in difficulty
        assert "time_seconds" in difficulty
        assert "heart_size_min" in difficulty
        assert "heart_size_max" in difficulty
        assert "heart_duration_min" in difficulty
        assert "heart_duration_max" in difficulty
