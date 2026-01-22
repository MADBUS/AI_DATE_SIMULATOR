# Backlog: User MBTI 기능

## [User MBTI 입력 및 관리]

### Completed Tests
- [x] Test name: shouldHaveMbtiField
- [x] Expected behavior: User 모델에 mbti 필드가 존재해야 함
- [x] Acceptance criteria: mbti 필드 기본값 None, 4자리 문자열

- [x] Test name: shouldHaveIsPremiumField
- [x] Expected behavior: User 모델에 is_premium 필드가 존재해야 함
- [x] Acceptance criteria: is_premium 필드 기본값 False

- [x] Test name: shouldUpdateUserMbti
- [x] Expected behavior: PATCH /api/users/{user_id}/mbti로 MBTI 업데이트
- [x] Acceptance criteria: 유효한 MBTI(16종)만 허용, 업데이트 후 응답에 포함

- [x] Test name: shouldGetUserWithMbti
- [x] Expected behavior: GET /api/users/{user_id}로 mbti 포함된 사용자 정보 조회
- [x] Acceptance criteria: mbti, is_premium 필드가 응답에 포함

### Implementation Notes
- User 모델: mbti (String(4), nullable), is_premium (Boolean, default=False)
- UserResponse 스키마: mbti, is_premium 필드 추가
- MBTIUpdate 스키마: 16가지 MBTI 유효성 검사
- Users API: GET /{user_id}, PATCH /{user_id}/mbti

### Files Changed
- app/models/user.py
- app/schemas/user.py
- app/api/users.py (new)
- app/api/__init__.py
- tests/test_user_mbti.py (new)
- tests/conftest.py (new)
- pytest.ini (new)
- requirements.txt
- plan.md
- prd.md
