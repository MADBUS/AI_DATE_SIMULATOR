# Backlog: Gemini API 설정

## [Gemini API 프롬프트 생성]

### Completed Tests
- [x] Test name: test_build_expression_prompt_contains_gender
- [x] Expected behavior: 프롬프트에 캐릭터 성별이 포함됨
- [x] Acceptance criteria: gender 파라미터가 프롬프트 문자열에 포함

- [x] Test name: test_build_expression_prompt_contains_style
- [x] Expected behavior: 프롬프트에 캐릭터 스타일이 포함됨
- [x] Acceptance criteria: style 파라미터가 프롬프트 문자열에 포함

- [x] Test name: test_build_expression_prompt_contains_art_style
- [x] Expected behavior: 프롬프트에 그림체가 포함됨
- [x] Acceptance criteria: art_style 파라미터가 프롬프트 문자열에 포함

- [x] Test name: test_build_expression_prompt_contains_expression
- [x] Expected behavior: 프롬프트에 표정 타입이 포함됨
- [x] Acceptance criteria: expression 파라미터가 프롬프트 문자열에 포함

- [x] Test name: test_expression_types_constant_has_six_expressions
- [x] Expected behavior: EXPRESSION_TYPES에 6가지 표정이 정의됨
- [x] Acceptance criteria: neutral, happy, sad, jealous, shy, excited 포함

### Implementation Notes
- EXPRESSION_TYPES: 6가지 표정 타입 상수
- build_expression_prompt: 캐릭터 설정 기반 이미지 생성 프롬프트 생성
- 스타일별 설명, 표정별 설명, 그림체별 설명 매핑

### Files Changed
- app/services/gemini_service.py (EXPRESSION_TYPES, build_expression_prompt 추가)
- tests/test_gemini_service.py (new)
- plan.md

### Next Steps
- Gemini API 호출 함수 구현 (실제 이미지 생성)
- CharacterExpression 모델 및 저장 로직
