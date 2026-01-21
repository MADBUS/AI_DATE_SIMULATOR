# Backlog: Game Session API

## [게임 세션 조회 API]

### Completed Tests
- [x] Test name: test_get_game_session_with_invalid_id_returns_404
- [x] Expected behavior: 존재하지 않는 session_id로 GET 요청 시 404 반환
- [x] Acceptance criteria: "Game session not found" 메시지와 함께 404 상태 코드 반환

- [x] Test name: test_get_game_session_with_valid_id_returns_session_with_settings
- [x] Expected behavior: 유효한 session_id로 GET 요청 시 게임 세션과 캐릭터 설정 반환
- [x] Acceptance criteria: 200 상태 코드, character_settings 포함

### Implementation Notes
- GET /api/games/{session_id} 엔드포인트 수정
- GameSessionWithSettingsResponse 스키마 사용
- character_setting relationship 로드 (selectinload)
- character_settings가 없는 경우 null 반환

### Files Changed
- app/api/games.py (GET endpoint 수정)
- app/schemas/game.py (character_settings optional로 변경)
- tests/test_game_session.py (new)
- plan.md

### API Endpoint
- GET /api/games/{session_id}
  - Response 200: { id, user_id, affection, current_scene, status, save_slot, character_settings }
  - Response 404: { detail: "Game session not found" }
