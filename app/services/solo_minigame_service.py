"""
솔로 미니게임 서비스
Phase 2: 매칭 실패 시 솔로 미니게임 트리거 (난이도 상향)
"""

# 기본 미니게임 난이도 (일반 PvP 매칭 성공 시)
DEFAULT_MINIGAME_DIFFICULTY = {
    "target_count": 7,          # 목표 하트 개수
    "time_seconds": 8,          # 제한 시간 (초)
    "heart_size_min": 50,       # 하트 최소 크기 (px)
    "heart_size_max": 80,       # 하트 최대 크기 (px)
    "heart_duration_min": 4,    # 하트 표시 최소 시간 (초)
    "heart_duration_max": 6,    # 하트 표시 최대 시간 (초)
}

# 솔로 미니게임 난이도 (매칭 실패 시 - 난이도 상향)
SOLO_MINIGAME_DIFFICULTY = {
    "target_count": 12,         # 목표 하트 개수 (7 -> 12)
    "time_seconds": 6,          # 제한 시간 (8초 -> 6초)
    "heart_size_min": 40,       # 하트 최소 크기 (50 -> 40px)
    "heart_size_max": 60,       # 하트 최대 크기 (80 -> 60px)
    "heart_duration_min": 2,    # 하트 표시 최소 시간 (4 -> 2초)
    "heart_duration_max": 4,    # 하트 표시 최대 시간 (6 -> 4초)
}

# 솔로 미니게임 보상/패널티
SOLO_MINIGAME_SUCCESS_BONUS = 10  # 성공 시 호감도 보너스
SOLO_MINIGAME_FAILURE_PENALTY = -5  # 실패 시 호감도 패널티


class SoloMinigameService:
    """
    솔로 미니게임 서비스

    매칭 실패(타임아웃) 시 난이도가 상향된 솔로 미니게임을 트리거합니다.
    - 목표: 7개 → 12개
    - 시간: 8초 → 6초
    - 하트 크기: 50-80px → 40-60px
    - 하트 속도: 4-6초 → 2-4초
    """

    async def trigger_solo_minigame(self, session_id: str) -> dict:
        """
        솔로 미니게임 트리거

        Args:
            session_id: 게임 세션 ID

        Returns:
            {
                "trigger_minigame": bool,
                "minigame_type": str,
                "difficulty": dict,
                "session_id": str
            }
        """
        return {
            "trigger_minigame": True,
            "minigame_type": "solo",
            "difficulty": SOLO_MINIGAME_DIFFICULTY,
            "session_id": session_id,
        }

    async def process_solo_minigame_result(
        self,
        session_id: str,
        hearts_touched: int,
        time_taken: float,
    ) -> dict:
        """
        솔로 미니게임 결과 처리

        Args:
            session_id: 게임 세션 ID
            hearts_touched: 터치한 하트 개수
            time_taken: 걸린 시간 (초)

        Returns:
            {
                "success": bool,
                "bonus_affection": int (성공 시),
                "penalty_affection": int (실패 시)
            }
        """
        target = SOLO_MINIGAME_DIFFICULTY["target_count"]
        time_limit = SOLO_MINIGAME_DIFFICULTY["time_seconds"]

        # 성공 조건: 목표 개수 달성 AND 시간 내 완료
        success = hearts_touched >= target and time_taken <= time_limit

        if success:
            return {
                "success": True,
                "bonus_affection": SOLO_MINIGAME_SUCCESS_BONUS,
            }
        else:
            return {
                "success": False,
                "penalty_affection": SOLO_MINIGAME_FAILURE_PENALTY,
            }
