# Backlog: Character Settings API

## [연애 대상자 커스터마이징 API]

### Completed Tests
- [x] Test name: test_create_character_settings_with_invalid_user_returns_404
- [x] Expected behavior: 존재하지 않는 user_id로 POST 요청 시 404 반환
- [x] Acceptance criteria: "User not found" 메시지와 함께 404 상태 코드 반환

- [x] Test name: test_create_character_settings_with_valid_user_returns_201
- [x] Expected behavior: 유효한 user_id로 POST 요청 시 게임 세션과 캐릭터 설정 생성
- [x] Acceptance criteria: 201 상태 코드, 호감도 30-50 랜덤, character_settings 포함

### Implementation Notes
- CharacterSetting 모델: session_id (FK), gender, style, mbti, art_style
- GameSession과 1:1 관계 설정
- 초기 호감도 30-50 랜덤 설정
- GameSessionWithSettingsResponse 스키마로 응답

### Files Changed
- app/models/game.py (CharacterSetting 모델 추가, GameSession 수정)
- app/models/__init__.py (CharacterSetting export)
- app/schemas/character.py (CharacterSettingCreate, CharacterSettingResponse 추가)
- app/schemas/game.py (GameSessionWithSettingsResponse 추가)
- app/api/character_settings.py (new)
- app/api/__init__.py (router 등록)
- tests/test_character_settings.py (new)
- plan.md

### API Endpoint
- POST /api/character_settings/
  - Request: { user_id, gender, style, mbti, art_style }
  - Response 201: { id, user_id, affection, current_scene, status, save_slot, character_settings }
  - Response 404: { detail: "User not found" }
