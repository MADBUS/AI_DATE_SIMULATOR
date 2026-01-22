"""
PvP WebSocket 매칭 시스템
Phase 2: WebSocket 기반 실시간 PvP 매칭
"""

from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, async_session
from app.models.game import GameSession

router = APIRouter()

# 매칭 대기 큐 (메모리 기반, 추후 Redis로 전환)
matching_queue: dict[str, dict] = {}


async def get_db_for_websocket():
    """WebSocket용 DB 세션 생성"""
    from app.core.database import async_session
    async with async_session() as session:
        yield session


@router.websocket("/match/{session_id}")
async def pvp_match_websocket(
    websocket: WebSocket,
    session_id: UUID,
):
    """
    PvP 매칭 WebSocket 엔드포인트

    Flow:
    1. 연결 시 세션 유효성 검증
    2. "connected" 메시지 전송
    3. "join_queue" 액션 수신 시 매칭 큐 등록
    4. 매칭 성공 시 양쪽에 "matched" 메시지 전송
    5. 30초 타임아웃 시 "timeout" 메시지 전송
    """
    # DB 세션 생성
    async with async_session() as db:
        # 세션 유효성 검증
        result = await db.execute(
            select(GameSession).where(GameSession.id == session_id)
        )
        game_session = result.scalar_one_or_none()

        if not game_session:
            await websocket.close(code=4004, reason="Game session not found")
            return

        if game_session.status != "playing":
            await websocket.close(code=4001, reason="Game already ended")
            return

    # WebSocket 연결 수락
    await websocket.accept()

    try:
        # 연결 성공 메시지 전송
        await websocket.send_json({
            "type": "connected",
            "message": "PvP 매칭 서버에 연결되었습니다.",
            "session_id": str(session_id),
        })

        # 메시지 수신 대기
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "join_queue":
                bet_amount = data.get("bet_amount", 0)

                # 매칭 큐에 등록
                matching_queue[str(session_id)] = {
                    "websocket": websocket,
                    "session_id": session_id,
                    "bet_amount": bet_amount,
                }

                # 큐 등록 확인 메시지
                await websocket.send_json({
                    "type": "queue_joined",
                    "message": "매칭 대기열에 등록되었습니다.",
                    "bet_amount": bet_amount,
                })

                # TODO: 매칭 로직 구현 (다른 플레이어 찾기)
                # TODO: 30초 타임아웃 처리

            elif action == "leave_queue":
                # 매칭 큐에서 제거
                if str(session_id) in matching_queue:
                    del matching_queue[str(session_id)]

                await websocket.send_json({
                    "type": "queue_left",
                    "message": "매칭 대기열에서 나갔습니다.",
                })

    except WebSocketDisconnect:
        # 연결 종료 시 큐에서 제거
        if str(session_id) in matching_queue:
            del matching_queue[str(session_id)]
    except Exception as e:
        print(f"WebSocket error: {e}")
        if str(session_id) in matching_queue:
            del matching_queue[str(session_id)]
