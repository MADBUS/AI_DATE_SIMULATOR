# Backlog: Minigame Result API

## [미니게임 결과 저장 API]

### Completed Tests
- [x] Test name: test_save_minigame_result_with_invalid_session_returns_404
- [x] Expected behavior: 존재하지 않는 session_id로 요청 시 404 반환
- [x] Acceptance criteria: "Game session not found" 메시지와 함께 404 상태 코드 반환

- [x] Test name: test_save_minigame_result_perfect_adds_bonus_affection
- [x] Expected behavior: 'perfect' 결과 저장 시 +3 호감도 추가
- [x] Acceptance criteria: 201 상태 코드, bonus_affection=3, new_affection 반영

- [x] Test name: test_save_minigame_result_great_adds_bonus_affection
- [x] Expected behavior: 'great' 결과 저장 시 +1 호감도 추가
- [x] Acceptance criteria: 201 상태 코드, bonus_affection=1, new_affection 반영

- [x] Test name: test_save_minigame_result_miss_no_bonus
- [x] Expected behavior: 'miss' 결과 저장 시 호감도 변화 없음
- [x] Acceptance criteria: 201 상태 코드, bonus_affection=0, new_affection 변화 없음

### Implementation Notes
- MinigameResult 모델 생성 (session_id, scene_number, result, bonus_affection)
- POST /api/minigame/{session_id}/result 엔드포인트
- 결과별 보너스: perfect(+3), great(+1), miss(+0)
- 게임 세션 호감도 자동 업데이트

### Files Changed
- app/models/game.py (MinigameResult 모델 추가, GameSession relationship 추가)
- app/models/__init__.py (export 추가)
- app/schemas/minigame.py (new)
- app/api/minigame.py (new)
- app/api/__init__.py (라우터 등록)
- tests/test_minigame.py (new)
- plan.md (완료 표시)

### API Endpoint
- POST /api/minigame/{session_id}/result
  - Request: { result: "perfect"|"great"|"miss", scene_number: int }
  - Response 201: { id, result, bonus_affection, new_affection }
  - Response 404: { detail: "Game session not found" }

### Bonus Affection Rules
- perfect (정중앙): +3 호감도
- great (근접): +1 호감도
- miss (실패): +0 호감도
