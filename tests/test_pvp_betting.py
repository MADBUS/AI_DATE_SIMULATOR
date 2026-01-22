"""
PvP 호감도 배팅 로직 테스트
TDD Phase 2: 호감도 배팅 및 결과 처리
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from app.services.pvp_service import PvPService, calculate_final_bet


class TestFinalBetCalculation:
    """최종 배팅 금액 결정 테스트"""

    def test_final_bet_is_higher_of_two_bets(self):
        """양쪽 배팅 중 높은 쪽으로 자동 결정"""
        # player1: 10, player2: 15 -> final: 15
        assert calculate_final_bet(10, 15) == 15

        # player1: 20, player2: 5 -> final: 20
        assert calculate_final_bet(20, 5) == 20

    def test_final_bet_when_equal(self):
        """양쪽 배팅이 같을 때"""
        assert calculate_final_bet(10, 10) == 10

    def test_final_bet_with_zero(self):
        """한쪽이 0을 배팅했을 때"""
        assert calculate_final_bet(0, 15) == 15
        assert calculate_final_bet(20, 0) == 20


class TestWinnerAffectionGain:
    """승자 호감도 획득 테스트"""

    @pytest.mark.asyncio
    async def test_winner_gains_final_bet_affection(self):
        """승자는 최종 배팅 금액만큼 호감도 획득"""
        mock_db = AsyncMock()
        service = PvPService(mock_db)

        # 플레이어1 승리, 최종 배팅 15
        result = await service.process_pvp_result(
            winner_session_id=str(uuid4()),
            loser_session_id=str(uuid4()),
            winner_current_affection=50,
            loser_current_affection=40,
            final_bet=15
        )

        # 승자 호감도 = 50 + 15 = 65
        assert result["winner_new_affection"] == 65

    @pytest.mark.asyncio
    async def test_winner_affection_capped_at_100(self):
        """승자 호감도는 100을 초과할 수 없음"""
        mock_db = AsyncMock()
        service = PvPService(mock_db)

        result = await service.process_pvp_result(
            winner_session_id=str(uuid4()),
            loser_session_id=str(uuid4()),
            winner_current_affection=95,
            loser_current_affection=40,
            final_bet=20
        )

        # 승자 호감도 = min(95 + 20, 100) = 100
        assert result["winner_new_affection"] == 100


class TestLoserAffectionLoss:
    """패자 호감도 손실 테스트"""

    @pytest.mark.asyncio
    async def test_loser_loses_final_bet_affection(self):
        """패자는 최종 배팅 금액만큼 호감도 손실"""
        mock_db = AsyncMock()
        service = PvPService(mock_db)

        result = await service.process_pvp_result(
            winner_session_id=str(uuid4()),
            loser_session_id=str(uuid4()),
            winner_current_affection=50,
            loser_current_affection=40,
            final_bet=15
        )

        # 패자 호감도 = 40 - 15 = 25
        assert result["loser_new_affection"] == 25

    @pytest.mark.asyncio
    async def test_loser_affection_capped_at_current_when_insufficient(self):
        """보유량 초과 시 보유량만큼만 손실"""
        mock_db = AsyncMock()
        service = PvPService(mock_db)

        result = await service.process_pvp_result(
            winner_session_id=str(uuid4()),
            loser_session_id=str(uuid4()),
            winner_current_affection=50,
            loser_current_affection=10,  # 보유량 10
            final_bet=25  # 배팅 25
        )

        # 패자 호감도 = max(10 - 25, 0) = 0 (보유량만큼만 손실)
        assert result["loser_new_affection"] == 0
        # 실제 손실량은 10
        assert result["actual_loss"] == 10

    @pytest.mark.asyncio
    async def test_loser_affection_never_negative(self):
        """패자 호감도는 0 미만이 될 수 없음"""
        mock_db = AsyncMock()
        service = PvPService(mock_db)

        result = await service.process_pvp_result(
            winner_session_id=str(uuid4()),
            loser_session_id=str(uuid4()),
            winner_current_affection=50,
            loser_current_affection=5,
            final_bet=100
        )

        assert result["loser_new_affection"] >= 0


class TestCharacterStolen:
    """캐릭터 뺏기 판정 테스트"""

    @pytest.mark.asyncio
    async def test_character_stolen_when_affection_reaches_zero(self):
        """패자 호감도가 0이 되면 캐릭터 뺏김"""
        mock_db = AsyncMock()
        service = PvPService(mock_db)

        result = await service.process_pvp_result(
            winner_session_id=str(uuid4()),
            loser_session_id=str(uuid4()),
            winner_current_affection=50,
            loser_current_affection=10,
            final_bet=15
        )

        # 패자 호감도가 0 이하이므로 캐릭터 뺏김
        assert result["loser_new_affection"] == 0
        assert result["character_stolen"] is True

    @pytest.mark.asyncio
    async def test_character_not_stolen_when_affection_above_zero(self):
        """패자 호감도가 0 초과면 캐릭터 유지"""
        mock_db = AsyncMock()
        service = PvPService(mock_db)

        result = await service.process_pvp_result(
            winner_session_id=str(uuid4()),
            loser_session_id=str(uuid4()),
            winner_current_affection=50,
            loser_current_affection=30,
            final_bet=10
        )

        # 패자 호감도 = 30 - 10 = 20 > 0
        assert result["loser_new_affection"] == 20
        assert result["character_stolen"] is False


class TestPvPResultStructure:
    """PvP 결과 구조 테스트"""

    @pytest.mark.asyncio
    async def test_result_contains_required_fields(self):
        """결과에 필수 필드가 포함되어 있는지 확인"""
        mock_db = AsyncMock()
        service = PvPService(mock_db)

        result = await service.process_pvp_result(
            winner_session_id=str(uuid4()),
            loser_session_id=str(uuid4()),
            winner_current_affection=50,
            loser_current_affection=40,
            final_bet=15
        )

        assert "winner_new_affection" in result
        assert "loser_new_affection" in result
        assert "actual_loss" in result
        assert "character_stolen" in result
        assert "show_event_scene" in result

    @pytest.mark.asyncio
    async def test_winner_gets_event_scene(self):
        """승자에게 이벤트 씬 표시"""
        mock_db = AsyncMock()
        service = PvPService(mock_db)

        result = await service.process_pvp_result(
            winner_session_id=str(uuid4()),
            loser_session_id=str(uuid4()),
            winner_current_affection=50,
            loser_current_affection=40,
            final_bet=15
        )

        # 승자에게 이벤트 씬 표시
        assert result["show_event_scene"] is True
