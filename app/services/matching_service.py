"""
PvP 매칭 서비스
Phase 2: Redis 기반 매칭 큐 시스템
"""

import asyncio
from typing import Optional
from redis.asyncio import Redis


# Redis 키
MATCHING_QUEUE_KEY = "pvp:matching_queue"

# 매칭 타임아웃 (초)
MATCHING_TIMEOUT_SECONDS = 30

# 매칭 폴링 간격 (초)
MATCHING_POLL_INTERVAL = 0.5


class MatchingService:
    """
    Redis 기반 PvP 매칭 서비스

    Sorted Set을 사용하여 매칭 큐 관리:
    - Score: 배팅 금액 (비슷한 배팅끼리 매칭)
    - Member: 세션 ID
    """

    def __init__(self, redis: Redis):
        self.redis = redis

    async def add_to_queue(self, session_id: str, bet_amount: int) -> bool:
        """
        매칭 큐에 플레이어 추가

        Args:
            session_id: 게임 세션 ID
            bet_amount: 배팅 호감도

        Returns:
            추가 성공 여부
        """
        result = await self.redis.zadd(
            MATCHING_QUEUE_KEY,
            {session_id: bet_amount}
        )
        return result >= 0

    async def remove_from_queue(self, session_id: str) -> bool:
        """
        매칭 큐에서 플레이어 제거

        Args:
            session_id: 게임 세션 ID

        Returns:
            제거 성공 여부
        """
        result = await self.redis.zrem(MATCHING_QUEUE_KEY, session_id)
        return result > 0

    async def find_match(
        self, session_id: str, bet_amount: int
    ) -> Optional[dict]:
        """
        매칭 상대 찾기

        Args:
            session_id: 자신의 세션 ID
            bet_amount: 자신의 배팅 금액

        Returns:
            매칭된 상대 정보 또는 None
            {
                "opponent_session_id": str,
                "opponent_bet": int
            }
        """
        # 큐에서 모든 대기자 조회 (배팅 금액 순)
        waiting_players = await self.redis.zrange(
            MATCHING_QUEUE_KEY, 0, -1
        )

        for player_bytes in waiting_players:
            player_id = player_bytes.decode() if isinstance(player_bytes, bytes) else player_bytes

            # 자기 자신 제외
            if player_id == session_id:
                continue

            # 상대 배팅 금액 조회
            opponent_bet = await self.redis.zscore(MATCHING_QUEUE_KEY, player_id)

            if opponent_bet is not None:
                # 매칭 성공 - 상대를 큐에서 제거
                await self.redis.zrem(MATCHING_QUEUE_KEY, player_id)

                return {
                    "opponent_session_id": player_id,
                    "opponent_bet": int(opponent_bet),
                }

        return None

    async def get_queue_size(self) -> int:
        """
        현재 매칭 대기 인원 수 조회

        Returns:
            대기 인원 수
        """
        return await self.redis.zcard(MATCHING_QUEUE_KEY)

    async def get_player_bet(self, session_id: str) -> Optional[int]:
        """
        플레이어의 배팅 금액 조회

        Args:
            session_id: 게임 세션 ID

        Returns:
            배팅 금액 또는 None (큐에 없는 경우)
        """
        score = await self.redis.zscore(MATCHING_QUEUE_KEY, session_id)
        return int(score) if score is not None else None

    async def clear_queue(self) -> bool:
        """
        매칭 큐 전체 삭제 (테스트/관리용)

        Returns:
            삭제 성공 여부
        """
        await self.redis.delete(MATCHING_QUEUE_KEY)
        return True

    async def wait_for_match_with_timeout(
        self,
        session_id: str,
        bet_amount: int,
        timeout_seconds: float = MATCHING_TIMEOUT_SECONDS,
    ) -> dict:
        """
        타임아웃 내에 매칭 상대를 찾기

        Args:
            session_id: 자신의 세션 ID
            bet_amount: 배팅 금액
            timeout_seconds: 타임아웃 (기본 30초)

        Returns:
            {
                "status": "matched" | "timeout",
                "opponent_session_id": str | None,
                "opponent_bet": int | None
            }
        """
        start_time = asyncio.get_event_loop().time()
        end_time = start_time + timeout_seconds

        # 먼저 큐에 자신을 등록
        await self.add_to_queue(session_id, bet_amount)

        while asyncio.get_event_loop().time() < end_time:
            # 매칭 상대 찾기
            match_result = await self.find_match(session_id, bet_amount)

            if match_result is not None:
                # 매칭 성공 - 자신도 큐에서 제거
                await self.remove_from_queue(session_id)
                return {
                    "status": "matched",
                    "opponent_session_id": match_result["opponent_session_id"],
                    "opponent_bet": match_result["opponent_bet"],
                }

            # 잠시 대기 후 재시도
            await asyncio.sleep(MATCHING_POLL_INTERVAL)

        # 타임아웃 - 큐에서 제거
        await self.remove_from_queue(session_id)
        return {
            "status": "timeout",
            "opponent_session_id": None,
            "opponent_bet": None,
        }
