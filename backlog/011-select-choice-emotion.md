# Backlog: Select Choice with Emotion Image

## [선택지 선택 시 감정 이미지 반환 API]

### Completed Tests
- [x] Test name: test_select_choice_with_invalid_session_returns_404
- [x] Expected behavior: 존재하지 않는 session_id로 요청 시 404 반환
- [x] Acceptance criteria: "Game session not found" 메시지와 함께 404 상태 코드 반환

- [x] Test name: test_select_choice_returns_expression_image_url
- [x] Expected behavior: expression_type과 함께 선택지 선택 시 해당 감정 이미지 URL 반환
- [x] Acceptance criteria: expression_image_url 필드에 DB에서 조회한 이미지 URL 반환

- [x] Test name: test_select_choice_with_negative_delta_returns_sad_expression
- [x] Expected behavior: 부정적 선택지(sad)와 함께 선택 시 슬픈 표정 이미지 반환
- [x] Acceptance criteria: expression_type: "sad", expression_image_url 반환

- [x] Test name: test_select_choice_without_expression_returns_neutral
- [x] Expected behavior: expression_type 없이 선택 시 기본값 neutral 반환
- [x] Acceptance criteria: expression_type: "neutral" 기본값 사용

### Implementation Notes
- POST /api/games/{session_id}/select 엔드포인트 확장
- ChoiceSelect 스키마에 expression_type 필드 추가 (optional, default: neutral)
- SelectChoiceResponse 스키마 생성 (expression_type, expression_image_url 포함)
- CharacterExpression 테이블에서 해당 감정 이미지 조회

### Files Changed
- app/api/games.py (select_choice 엔드포인트 수정)
- app/schemas/game.py (ChoiceSelect, SelectChoiceResponse 수정/추가)
- tests/test_select_choice_emotion.py (new)

### API Endpoint
- POST /api/games/{session_id}/select
  - Request: { affection_delta: int, expression_type?: string }
  - Response 200: { new_affection, next_scene, status, expression_type, expression_image_url }
  - Response 404: { detail: "Game session not found" }

### Expression Types
- neutral (기본)
- happy (기쁜)
- sad (슬픈)
- jealous (질투)
- shy (부끄러운)
- excited (흥분)

### Frontend Usage
```tsx
const response = await selectChoice(sessionId, {
  affection_delta: choice.delta,
  expression_type: choice.expression
});

// 캐릭터 이미지 업데이트
setCharacterImage(response.expression_image_url);
```
