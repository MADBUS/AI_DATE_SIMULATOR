"""
캐릭터 뺏기 서비스
Phase 2: PvP 패배 시 캐릭터 뺏기 시스템
"""

import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession


class CharacterStealService:
    """
    캐릭터 뺏기 서비스

    - 패자 호감도 0 이하 시 캐릭터 뺏김
    - 뺏은 캐릭터는 호감도 30으로 새 세션 생성
    - game_sessions에 is_stolen, original_owner_id 설정
    """

    # 뺏은 캐릭터의 초기 호감도
    STOLEN_CHARACTER_INITIAL_AFFECTION = 30

    def __init__(self, db: AsyncSession):
        self.db = db

    def should_steal_character(self, loser_new_affection: int) -> bool:
        """
        캐릭터 뺏기 조건 확인

        Args:
            loser_new_affection: 패자의 새 호감도

        Returns:
            캐릭터를 뺏어야 하는지 여부
        """
        return loser_new_affection <= 0

    async def create_stolen_session(
        self,
        winner_user_id: str,
        loser_session_id: str,
        loser_user_id: str,
    ) -> dict:
        """
        뺏은 캐릭터로 새 세션 생성

        Args:
            winner_user_id: 승자 user_id
            loser_session_id: 패자 session_id (캐릭터 정보 복사용, 특별 이미지 재사용용)
            loser_user_id: 패자 user_id (original_owner_id로 저장)

        Returns:
            {
                "stolen_session_id": str,
                "new_user_id": str,
                "new_affection": int,
                "is_stolen": bool,
                "original_owner_id": str,
                "stolen_from_session_id": str
            }
        """
        new_session_id = str(uuid.uuid4())

        return {
            "stolen_session_id": new_session_id,
            "new_user_id": winner_user_id,
            "new_affection": self.STOLEN_CHARACTER_INITIAL_AFFECTION,
            "is_stolen": True,
            "original_owner_id": loser_user_id,
            "stolen_from_session_id": loser_session_id,  # 원래 세션 ID (특별 이미지 재사용용)
        }

    async def mark_session_as_stolen(self, session_id: str) -> dict:
        """
        세션을 뺏긴 상태로 마킹

        Args:
            session_id: 뺏긴 세션 ID

        Returns:
            {
                "is_stolen": bool,
                "status": str
            }
        """
        return {
            "is_stolen": True,
            "status": "character_stolen",
        }

    async def process_character_steal(
        self,
        winner_user_id: str,
        loser_session_id: str,
        loser_user_id: str,
    ) -> dict:
        """
        캐릭터 뺏기 전체 플로우 처리

        1. 패자 세션을 뺏긴 상태로 마킹
        2. 승자에게 새 세션 생성 (뺏은 캐릭터)

        Args:
            winner_user_id: 승자 user_id
            loser_session_id: 패자 session_id
            loser_user_id: 패자 user_id

        Returns:
            {
                "stolen_session_id": str,
                "new_user_id": str,
                "new_affection": int,
                "is_stolen": bool,
                "original_owner_id": str,
                "stolen_from_session_id": str
            }
        """
        # 패자 세션 마킹
        await self.mark_session_as_stolen(loser_session_id)

        # 승자에게 새 세션 생성
        stolen_session = await self.create_stolen_session(
            winner_user_id=winner_user_id,
            loser_session_id=loser_session_id,
            loser_user_id=loser_user_id,
        )

        return stolen_session
