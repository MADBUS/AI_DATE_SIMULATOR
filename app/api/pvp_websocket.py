"""
PvP WebSocket 매칭 시스템
Phase 2: WebSocket 기반 실시간 PvP 매칭 + 미니게임 동기화
"""

import asyncio
import random
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, async_session
from app.models.game import GameSession

router = APIRouter()

# 매칭 대기 큐 (메모리 기반, 추후 Redis로 전환)
matching_queue: dict[str, dict] = {}

# 활성 PvP 게임 방 (game_room_id -> {player1, player2, game_state})
active_games: dict[str, dict] = {}


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

                # 매칭 로직: 다른 플레이어 찾기
                await try_match_players(str(session_id))

            elif action == "leave_queue":
                # 매칭 큐에서 제거
                if str(session_id) in matching_queue:
                    del matching_queue[str(session_id)]

                await websocket.send_json({
                    "type": "queue_left",
                    "message": "매칭 대기열에서 나갔습니다.",
                })

            # === 게임 액션 처리 ===
            elif action == "game_action":
                game_room_id = data.get("room_id")
                game_action = data.get("game_action")
                payload = data.get("payload", {})

                await handle_game_action(
                    str(session_id),
                    game_room_id,
                    game_action,
                    payload
                )

    except WebSocketDisconnect:
        # 연결 종료 시 큐에서 제거
        if str(session_id) in matching_queue:
            del matching_queue[str(session_id)]
        # 게임 방에서도 제거
        await cleanup_player_from_games(str(session_id))
    except Exception as e:
        print(f"WebSocket error: {e}")
        if str(session_id) in matching_queue:
            del matching_queue[str(session_id)]
        await cleanup_player_from_games(str(session_id))


async def try_match_players(new_player_id: str):
    """
    새 플레이어가 큐에 들어왔을 때 매칭 시도
    """
    if new_player_id not in matching_queue:
        return

    # 다른 대기 중인 플레이어 찾기
    for player_id, player_data in list(matching_queue.items()):
        if player_id == new_player_id:
            continue

        # 매칭 성공!
        player1 = matching_queue.pop(player_id)
        player2 = matching_queue.pop(new_player_id)

        # 게임 방 생성
        room_id = f"pvp_{player_id}_{new_player_id}"
        game_type = random.choice(["shell", "chase", "mashing"])
        correct_cup = random.randint(0, 2) if game_type == "shell" else None

        active_games[room_id] = {
            "player1": {
                "session_id": player_id,
                "websocket": player1["websocket"],
                "bet": player1["bet_amount"],
                "is_host": True,
                "state": {},  # 게임별 상태
            },
            "player2": {
                "session_id": new_player_id,
                "websocket": player2["websocket"],
                "bet": player2["bet_amount"],
                "is_host": False,
                "state": {},
            },
            "game_type": game_type,
            "correct_cup": correct_cup,
            "started": False,
        }

        # 양쪽에 매칭 성공 메시지 전송
        match_data = {
            "type": "matched",
            "room_id": room_id,
            "game_type": game_type,
            "correct_cup": correct_cup,
        }

        try:
            await player1["websocket"].send_json({
                **match_data,
                "is_host": True,
                "opponent_session_id": new_player_id,
                "opponent_bet": player2["bet_amount"],
            })
            await player2["websocket"].send_json({
                **match_data,
                "is_host": False,
                "opponent_session_id": player_id,
                "opponent_bet": player1["bet_amount"],
            })
        except Exception as e:
            print(f"Failed to send match notification: {e}")
            # 매칭 실패 시 정리
            if room_id in active_games:
                del active_games[room_id]

        return  # 매칭 성공, 종료


async def handle_game_action(
    player_id: str,
    room_id: str,
    game_action: str,
    payload: dict
):
    """
    게임 액션 처리 및 상대방에게 전파
    """
    if room_id not in active_games:
        return

    game = active_games[room_id]

    # 플레이어 식별
    if game["player1"]["session_id"] == player_id:
        me = game["player1"]
        opponent = game["player2"]
    elif game["player2"]["session_id"] == player_id:
        me = game["player2"]
        opponent = game["player1"]
    else:
        return

    # 게임 타입별 처리
    game_type = game["game_type"]

    if game_type == "shell":
        # 야바위 게임
        if game_action == "hover":
            # 호버 상태 전파
            try:
                await opponent["websocket"].send_json({
                    "type": "game_update",
                    "game_action": "opponent_hover",
                    "cup_index": payload.get("cup_index"),
                })
            except Exception:
                pass

        elif game_action == "select":
            # 선택 확정 전파
            me["state"]["selected"] = payload.get("cup_index")
            try:
                await opponent["websocket"].send_json({
                    "type": "game_update",
                    "game_action": "opponent_select",
                    "cup_index": payload.get("cup_index"),
                })
            except Exception:
                pass

            # 둘 다 선택했으면 결과 전송
            if "selected" in me["state"] and "selected" in opponent["state"]:
                await send_shell_game_result(room_id)

    elif game_type == "chase":
        # 나잡아봐라 게임
        if game_action == "position":
            # 위치 변경 전파
            me["state"]["position"] = payload.get("position")
            try:
                await opponent["websocket"].send_json({
                    "type": "game_update",
                    "game_action": "opponent_position",
                    "position": payload.get("position"),
                })
            except Exception:
                pass

        elif game_action == "hit":
            # 피격 처리
            me["state"]["hits"] = me["state"].get("hits", 0) + 1
            try:
                await opponent["websocket"].send_json({
                    "type": "game_update",
                    "game_action": "opponent_hit",
                    "hits": me["state"]["hits"],
                })
            except Exception:
                pass

            # 3번 맞으면 패배
            if me["state"]["hits"] >= 3:
                await send_chase_game_result(room_id, loser_id=player_id)

    elif game_type == "mashing":
        # 스페이스바 광클 게임
        if game_action == "score":
            # 스코어 전파
            me["state"]["score"] = payload.get("score", 0)
            try:
                await opponent["websocket"].send_json({
                    "type": "game_update",
                    "game_action": "opponent_score",
                    "score": me["state"]["score"],
                })
            except Exception:
                pass

        elif game_action == "time_up":
            # 시간 종료 - 결과 판정
            await send_mashing_game_result(room_id)


async def send_shell_game_result(room_id: str):
    """야바위 게임 결과 전송"""
    if room_id not in active_games:
        return

    game = active_games[room_id]
    correct = game["correct_cup"]

    p1 = game["player1"]
    p2 = game["player2"]

    p1_correct = p1["state"].get("selected") == correct
    p2_correct = p2["state"].get("selected") == correct

    # 승자 결정
    if p1_correct and not p2_correct:
        winner = p1
        loser = p2
    elif p2_correct and not p1_correct:
        winner = p2
        loser = p1
    elif p1_correct and p2_correct:
        # 둘 다 맞춤 - 호스트 승리
        winner = p1
        loser = p2
    else:
        # 둘 다 틀림 - 호스트 패배
        winner = p2
        loser = p1

    await send_game_result(room_id, winner, loser)


async def send_chase_game_result(room_id: str, loser_id: str):
    """나잡아봐라 게임 결과 전송"""
    if room_id not in active_games:
        return

    game = active_games[room_id]
    p1 = game["player1"]
    p2 = game["player2"]

    if p1["session_id"] == loser_id:
        winner = p2
        loser = p1
    else:
        winner = p1
        loser = p2

    await send_game_result(room_id, winner, loser)


async def send_mashing_game_result(room_id: str):
    """스페이스바 광클 게임 결과 전송"""
    if room_id not in active_games:
        return

    game = active_games[room_id]
    p1 = game["player1"]
    p2 = game["player2"]

    p1_score = p1["state"].get("score", 0)
    p2_score = p2["state"].get("score", 0)

    if p1_score > p2_score:
        winner = p1
        loser = p2
    elif p2_score > p1_score:
        winner = p2
        loser = p1
    else:
        # 동점 - 호스트 승리
        winner = p1
        loser = p2

    await send_game_result(room_id, winner, loser)


async def send_game_result(room_id: str, winner: dict, loser: dict):
    """공통 게임 결과 전송"""
    try:
        await winner["websocket"].send_json({
            "type": "pvp_result",
            "winner": True,
            "opponent_session_id": loser["session_id"],
            "final_bet": loser["bet"],
        })
        await loser["websocket"].send_json({
            "type": "pvp_result",
            "winner": False,
            "opponent_session_id": winner["session_id"],
            "final_bet": winner["bet"],
        })
    except Exception as e:
        print(f"Failed to send game result: {e}")
    finally:
        # 게임 방 정리
        if room_id in active_games:
            del active_games[room_id]


async def cleanup_player_from_games(player_id: str):
    """플레이어가 연결 종료 시 게임 방에서 정리"""
    for room_id, game in list(active_games.items()):
        if game["player1"]["session_id"] == player_id:
            # 상대방에게 승리 알림
            try:
                await game["player2"]["websocket"].send_json({
                    "type": "pvp_result",
                    "winner": True,
                    "opponent_session_id": player_id,
                    "final_bet": game["player1"]["bet"],
                    "reason": "opponent_disconnected",
                })
            except Exception:
                pass
            del active_games[room_id]
            break
        elif game["player2"]["session_id"] == player_id:
            try:
                await game["player1"]["websocket"].send_json({
                    "type": "pvp_result",
                    "winner": True,
                    "opponent_session_id": player_id,
                    "final_bet": game["player2"]["bet"],
                    "reason": "opponent_disconnected",
                })
            except Exception:
                pass
            del active_games[room_id]
            break
