# Backlog: Ending Event System

## [엔딩 이벤트 - 호감도 기반 이미지 생성]

### Completed Tests
- [x] Test name: test_ending_event_with_invalid_session_returns_404
- [x] Expected behavior: 존재하지 않는 session_id로 요청 시 404 반환
- [x] Acceptance criteria: "Game session not found" 메시지와 함께 404 상태 코드 반환

- [x] Test name: test_ending_event_with_high_affection_returns_positive_image
- [x] Expected behavior: 호감도 >= 70이면 happy_ending + 긍정적 이미지
- [x] Acceptance criteria: ending_type: "happy_ending", is_positive: true

- [x] Test name: test_ending_event_with_low_affection_returns_negative_image
- [x] Expected behavior: 호감도 < 70이면 sad_ending + 부정적 이미지
- [x] Acceptance criteria: ending_type: "sad_ending", is_positive: false

- [x] Test name: test_ending_event_for_already_ended_game_returns_400
- [x] Expected behavior: 이미 종료된 게임에서 엔딩 이벤트 요청 시 400 반환
- [x] Acceptance criteria: "Game already ended" 메시지와 함께 400 상태 코드 반환

### Implementation Notes
- 호감도 기준: 70 이상 = happy_ending, 70 미만 = sad_ending
- 엔딩 타입에 따라 긍정적/부정적 이미지 생성
- 게임 상태 자동 업데이트 (playing -> happy_ending/sad_ending)
- TODO: 실제 Gemini API로 엔딩 이미지 생성

### Files Changed
- app/api/games.py (ending-event 엔드포인트 추가)
- app/schemas/game.py (EndingEventResponse 스키마 추가)
- tests/test_ending_event.py (new)
- plan.md (완료 표시)

### API Endpoint
- POST /api/games/{session_id}/ending-event
  - Response 200: { ending_type, final_affection, is_positive, ending_image_url }
  - Response 404: { detail: "Game session not found" }
  - Response 400: { detail: "Game already ended" }

### Ending Criteria
| Affection | Ending Type | Image Mood |
|-----------|-------------|------------|
| >= 70     | happy_ending | romantic/positive |
| < 70      | sad_ending   | melancholic/negative |
