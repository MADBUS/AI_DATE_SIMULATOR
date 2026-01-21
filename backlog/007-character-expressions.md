# Backlog: Character Expressions API

## [표정 이미지 6종 사전 생성]

### Completed Tests
- [x] Test name: test_generate_expressions_with_invalid_session_returns_404
- [x] Expected behavior: 존재하지 않는 session_id로 요청 시 404 반환
- [x] Acceptance criteria: "Game session not found" 메시지와 함께 404 상태 코드 반환

- [x] Test name: test_generate_expressions_without_character_settings_returns_400
- [x] Expected behavior: 캐릭터 설정이 없는 세션으로 요청 시 400 반환
- [x] Acceptance criteria: "Character settings not found" 메시지와 함께 400 상태 코드 반환

- [x] Test name: test_generate_expressions_creates_six_expressions
- [x] Expected behavior: 유효한 세션으로 요청 시 6개 표정 이미지 생성
- [x] Acceptance criteria: 201 상태 코드, 6개 표정 타입 모두 포함 (neutral, happy, sad, jealous, shy, excited)

### Implementation Notes
- CharacterExpression 모델 생성 (setting_id, expression_type, image_url)
- POST /api/games/{session_id}/generate-expressions 엔드포인트
- Gemini 이미지 생성은 placeholder로 구현 (TODO: 실제 연동)

### Files Changed
- app/models/game.py (CharacterExpression 모델 추가)
- app/models/__init__.py (export 추가)
- app/schemas/character.py (CharacterExpressionResponse, ExpressionsGeneratedResponse 추가)
- app/api/expressions.py (new)
- app/api/__init__.py (라우터 등록)
- tests/test_character_expressions.py (new)
- plan.md (완료 표시)

### API Endpoint
- POST /api/games/{session_id}/generate-expressions
  - Response 201: { expressions: [{ id, expression_type, image_url }, ...] }
  - Response 404: { detail: "Game session not found" }
  - Response 400: { detail: "Character settings not found for this session" }

### Expression Types
1. neutral (일반)
2. happy (기쁜)
3. sad (슬픈)
4. jealous (질투)
5. shy (부끄러운)
6. excited (흥분)
