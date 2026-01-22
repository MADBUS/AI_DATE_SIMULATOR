"""
PvP WebSocket 매칭 시스템 테스트
TDD Phase 2: WebSocket 기반 PvP 매칭
"""

import pytest
from uuid import uuid4
from unittest.mock import patch, AsyncMock, MagicMock
from starlette.testclient import TestClient

from app.main import app
from app.models.user import User
from app.models.game import GameSession


class TestPvPWebSocketEndpoint:
    """PvP WebSocket 엔드포인트 테스트"""

    def test_websocket_endpoint_exists_and_connects(self):
        """WebSocket 엔드포인트가 존재하고 연결 가능한지 확인 (유효한 세션 mock)"""
        session_id = uuid4()

        # Mock the database query to return a valid session
        mock_session = MagicMock()
        mock_session.id = session_id
        mock_session.status = "playing"
        mock_session.user_id = uuid4()
        mock_session.affection = 50

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result
        mock_db.__aenter__.return_value = mock_db
        mock_db.__aexit__.return_value = None

        with patch("app.api.pvp_websocket.async_session", return_value=mock_db):
            with TestClient(app) as client:
                with client.websocket_connect(f"/ws/pvp/match/{session_id}") as websocket:
                    # Should receive connected message
                    data = websocket.receive_json()
                    assert data["type"] == "connected"
                    assert "message" in data
                    assert data["session_id"] == str(session_id)

    def test_websocket_invalid_session_disconnects(self):
        """존재하지 않는 세션으로 연결 시 연결 종료"""
        fake_session_id = uuid4()

        # Mock the database query to return None (session not found)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result
        mock_db.__aenter__.return_value = mock_db
        mock_db.__aexit__.return_value = None

        with patch("app.api.pvp_websocket.async_session", return_value=mock_db):
            with TestClient(app) as client:
                with pytest.raises(Exception):
                    with client.websocket_connect(f"/ws/pvp/match/{fake_session_id}") as websocket:
                        pass

    def test_websocket_join_matchmaking_queue(self):
        """매칭 큐 참가 테스트"""
        session_id = uuid4()

        # Mock the database query to return a valid session
        mock_session = MagicMock()
        mock_session.id = session_id
        mock_session.status = "playing"
        mock_session.user_id = uuid4()
        mock_session.affection = 50

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result
        mock_db.__aenter__.return_value = mock_db
        mock_db.__aexit__.return_value = None

        with patch("app.api.pvp_websocket.async_session", return_value=mock_db):
            with TestClient(app) as client:
                with client.websocket_connect(f"/ws/pvp/match/{session_id}") as websocket:
                    # Receive connected message
                    data = websocket.receive_json()
                    assert data["type"] == "connected"

                    # Send join queue message with bet amount
                    websocket.send_json({
                        "action": "join_queue",
                        "bet_amount": 10
                    })

                    # Should receive queue joined confirmation
                    data = websocket.receive_json()
                    assert data["type"] == "queue_joined"
                    assert data["bet_amount"] == 10

    def test_websocket_leave_matchmaking_queue(self):
        """매칭 큐 탈퇴 테스트"""
        session_id = uuid4()

        # Mock the database query to return a valid session
        mock_session = MagicMock()
        mock_session.id = session_id
        mock_session.status = "playing"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result
        mock_db.__aenter__.return_value = mock_db
        mock_db.__aexit__.return_value = None

        with patch("app.api.pvp_websocket.async_session", return_value=mock_db):
            with TestClient(app) as client:
                with client.websocket_connect(f"/ws/pvp/match/{session_id}") as websocket:
                    # Receive connected message
                    data = websocket.receive_json()
                    assert data["type"] == "connected"

                    # Join queue first
                    websocket.send_json({
                        "action": "join_queue",
                        "bet_amount": 10
                    })
                    data = websocket.receive_json()
                    assert data["type"] == "queue_joined"

                    # Leave queue
                    websocket.send_json({
                        "action": "leave_queue"
                    })
                    data = websocket.receive_json()
                    assert data["type"] == "queue_left"
