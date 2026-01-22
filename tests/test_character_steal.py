"""
캐릭터 뺏기 로직 테스트
TDD Phase 2: PvP 패배 시 캐릭터 뺏기 시스템
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.character_steal_service import CharacterStealService


class TestCharacterStealCondition:
    """캐릭터 뺏기 조건 테스트"""

    def test_should_steal_when_affection_zero(self):
        """호감도가 0일 때 캐릭터 뺏김"""
        service = CharacterStealService(None)
        assert service.should_steal_character(loser_new_affection=0) is True

    def test_should_steal_when_affection_negative(self):
        """호감도가 음수일 때 캐릭터 뺏김 (실제로는 0으로 처리되지만)"""
        service = CharacterStealService(None)
        # 실제로는 호감도가 음수가 되지 않지만, 로직 테스트
        assert service.should_steal_character(loser_new_affection=-5) is True

    def test_should_not_steal_when_affection_above_zero(self):
        """호감도가 0 초과일 때 캐릭터 유지"""
        service = CharacterStealService(None)
        assert service.should_steal_character(loser_new_affection=1) is False
        assert service.should_steal_character(loser_new_affection=50) is False


class TestStolenSessionCreation:
    """뺏은 캐릭터 세션 생성 테스트"""

    @pytest.mark.asyncio
    async def test_create_stolen_session_with_affection_30(self):
        """뺏은 캐릭터는 호감도 30으로 새 세션 생성"""
        mock_db = AsyncMock()

        service = CharacterStealService(mock_db)

        winner_user_id = str(uuid4())
        loser_session_id = str(uuid4())
        loser_user_id = str(uuid4())

        result = await service.create_stolen_session(
            winner_user_id=winner_user_id,
            loser_session_id=loser_session_id,
            loser_user_id=loser_user_id,
        )

        # 새 세션의 호감도는 30
        assert result["new_affection"] == 30
        # is_stolen 플래그 True
        assert result["is_stolen"] is True
        # original_owner_id는 패자 user_id
        assert result["original_owner_id"] == loser_user_id

    @pytest.mark.asyncio
    async def test_stolen_session_has_correct_owner(self):
        """뺏은 캐릭터 세션의 소유자는 승자"""
        mock_db = AsyncMock()
        service = CharacterStealService(mock_db)

        winner_user_id = str(uuid4())
        loser_session_id = str(uuid4())
        loser_user_id = str(uuid4())

        result = await service.create_stolen_session(
            winner_user_id=winner_user_id,
            loser_session_id=loser_session_id,
            loser_user_id=loser_user_id,
        )

        # 새 세션의 소유자는 승자
        assert result["new_user_id"] == winner_user_id


class TestLoserSessionUpdate:
    """패자 세션 업데이트 테스트"""

    @pytest.mark.asyncio
    async def test_loser_session_marked_as_stolen(self):
        """패자 세션에 is_stolen 플래그 설정"""
        mock_db = AsyncMock()
        service = CharacterStealService(mock_db)

        loser_session_id = str(uuid4())

        result = await service.mark_session_as_stolen(loser_session_id)

        assert result["is_stolen"] is True
        assert result["status"] == "character_stolen"


class TestGameSessionFields:
    """GameSession 모델 필드 테스트"""

    def test_game_session_has_is_stolen_field(self):
        """GameSession에 is_stolen 필드 존재"""
        from app.models.game import GameSession
        # 모델 클래스의 필드 확인
        assert hasattr(GameSession, "is_stolen")

    def test_game_session_has_original_owner_id_field(self):
        """GameSession에 original_owner_id 필드 존재"""
        from app.models.game import GameSession
        assert hasattr(GameSession, "original_owner_id")


class TestCharacterStealFlow:
    """캐릭터 뺏기 전체 플로우 테스트"""

    @pytest.mark.asyncio
    async def test_process_character_steal_full_flow(self):
        """캐릭터 뺏기 전체 플로우 테스트"""
        mock_db = AsyncMock()
        service = CharacterStealService(mock_db)

        winner_user_id = str(uuid4())
        loser_session_id = str(uuid4())
        loser_user_id = str(uuid4())

        result = await service.process_character_steal(
            winner_user_id=winner_user_id,
            loser_session_id=loser_session_id,
            loser_user_id=loser_user_id,
        )

        # 결과에 필요한 정보가 포함되어 있는지 확인
        assert "stolen_session_id" in result
        assert "new_affection" in result
        assert result["new_affection"] == 30
        assert result["is_stolen"] is True
        assert result["original_owner_id"] == loser_user_id
        assert result["new_user_id"] == winner_user_id
