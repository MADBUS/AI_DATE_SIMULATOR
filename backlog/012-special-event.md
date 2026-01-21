# Backlog: Special Event System

## [특별 이벤트 랜덤 발생 API]

### Completed Tests
- [x] Test name: test_check_event_with_invalid_session_returns_404
- [x] Expected behavior: 존재하지 않는 session_id로 요청 시 404 반환
- [x] Acceptance criteria: "Game session not found" 메시지와 함께 404 상태 코드 반환

- [x] Test name: test_check_event_returns_no_event_when_random_is_high
- [x] Expected behavior: random 값이 0.15 이상이면 이벤트 미발생
- [x] Acceptance criteria: is_special_event: false 반환

- [x] Test name: test_check_event_returns_event_when_random_is_low
- [x] Expected behavior: random 값이 0.15 미만이면 이벤트 발생
- [x] Acceptance criteria: is_special_event: true, special_image_url, show_minigame: true 반환

- [x] Test name: test_check_event_for_ended_game_returns_400
- [x] Expected behavior: 종료된 게임에서 이벤트 체크 시 400 반환
- [x] Acceptance criteria: "Game already ended" 메시지와 함께 400 상태 코드 반환

### Implementation Notes
- 15% 확률로 특별 이벤트 발생 (SPECIAL_EVENT_PROBABILITY = 0.15)
- 이벤트 발생 시 특별 이미지 URL 생성 (placeholder)
- 미니게임 표시 플래그 포함
- TODO: 실제 Gemini API로 특별 이미지 생성

### Files Changed
- app/api/scenes.py (check-event 엔드포인트 추가)
- tests/test_special_event.py (new)
- plan.md (완료 표시)

### API Endpoint
- POST /api/scenes/{session_id}/check-event
  - Response 200 (이벤트 발생): { is_special_event: true, special_image_url: string, show_minigame: true }
  - Response 200 (이벤트 미발생): { is_special_event: false }
  - Response 404: { detail: "Game session not found" }
  - Response 400: { detail: "Game already ended" }

### Event Probability
- 15% 확률로 특별 이벤트 발생
- 이벤트 발생 시 서비스 컷 이미지 생성
- 이미지 생성 중 미니게임 표시
