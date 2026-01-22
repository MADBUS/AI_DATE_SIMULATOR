"""
PvP 서비스
Phase 2: 호감도 배팅 및 결과 처리
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession


def calculate_final_bet(player1_bet: int, player2_bet: int) -> int:
    """
    최종 배팅 금액 계산
    양쪽 배팅 중 높은 쪽으로 자동 결정

    Args:
        player1_bet: 플레이어1 배팅 금액
        player2_bet: 플레이어2 배팅 금액

    Returns:
        최종 배팅 금액 (높은 쪽)
    """
    return max(player1_bet, player2_bet)


class PvPService:
    """
    PvP 호감도 배팅 서비스

    - 승자: 상대방 호감도 획득 + 이벤트 씬 표시
    - 패자: 배팅한 호감도 손실 (보유량 초과 시 보유량만큼만)
    - 패자 호감도 0 이하 시 캐릭터 뺏김
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_pvp_result(
        self,
        winner_session_id: str,
        loser_session_id: str,
        winner_current_affection: int,
        loser_current_affection: int,
        final_bet: int,
    ) -> dict:
        """
        PvP 결과 처리

        Args:
            winner_session_id: 승자 세션 ID
            loser_session_id: 패자 세션 ID
            winner_current_affection: 승자 현재 호감도
            loser_current_affection: 패자 현재 호감도
            final_bet: 최종 배팅 금액

        Returns:
            {
                "winner_new_affection": int,
                "loser_new_affection": int,
                "actual_loss": int,
                "character_stolen": bool,
                "show_event_scene": bool
            }
        """
        # 승자 호감도 계산 (최대 100)
        winner_new_affection = min(winner_current_affection + final_bet, 100)

        # 패자 호감도 계산 (보유량 초과 시 보유량만큼만 손실)
        actual_loss = min(final_bet, loser_current_affection)
        loser_new_affection = max(loser_current_affection - final_bet, 0)

        # 캐릭터 뺏기 판정 (호감도 0 이하 시)
        character_stolen = loser_new_affection <= 0

        return {
            "winner_new_affection": winner_new_affection,
            "loser_new_affection": loser_new_affection,
            "actual_loss": actual_loss,
            "character_stolen": character_stolen,
            "show_event_scene": True,  # 승자에게 이벤트 씬 표시
        }
