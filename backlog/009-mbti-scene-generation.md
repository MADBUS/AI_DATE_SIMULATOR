# Backlog: MBTI 기반 선택지 생성

## [MBTI 기반 씬 및 선택지 생성 API]

### Completed Tests
- [x] Test name: test_generate_scene_with_invalid_session_returns_404
- [x] Expected behavior: 존재하지 않는 session_id로 요청 시 404 반환
- [x] Acceptance criteria: "Game session not found" 메시지와 함께 404 상태 코드 반환

- [x] Test name: test_generate_scene_uses_character_settings
- [x] Expected behavior: 캐릭터 설정(style, mbti)이 씬 생성에 반영됨
- [x] Acceptance criteria: 200 상태 코드, dialogue, choices, affection 포함

- [x] Test name: test_generate_scene_returns_three_choices_with_different_deltas
- [x] Expected behavior: 3개 선택지가 각각 다른 delta 값을 가짐
- [x] Acceptance criteria: choices 배열에 id, text, delta 필드 포함

- [x] Test name: test_generate_scene_for_ended_game_returns_400
- [x] Expected behavior: 종료된 게임에서 씬 생성 시 400 반환
- [x] Acceptance criteria: "Game already ended" 메시지와 함께 400 상태 코드 반환

### Implementation Notes
- scenes.py에서 character_setting, user 관계 로드
- generate_scene_content 함수 시그니처 변경:
  - 기존: (character, scene_number, affection)
  - 변경: (character_setting, user_mbti, scene_number, affection)
- 캐릭터 스타일에 따른 대화 템플릿 선택

### Files Changed
- app/api/scenes.py (character_setting, user 로드 및 반영)
- app/services/gemini_service.py (generate_scene_content 시그니처 변경)
- tests/test_scene_generation.py (new)
- plan.md (완료 표시)

### API Endpoint
- POST /api/scenes/{session_id}/generate
  - Response 200: { scene_number, image_url, dialogue, choices[], affection, status }
  - Response 404: { detail: "Game session not found" }
  - Response 400: { detail: "Game already ended" }

### MBTI Integration
- 사용자 MBTI: 선택지 표현 스타일에 영향 (향후 확장)
- 캐릭터 MBTI: 대화 스타일에 영향
- 캐릭터 스타일: 대화 템플릿 선택 (tsundere, cool, cute 등)
