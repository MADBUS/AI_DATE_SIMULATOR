# Backlog: Special Image Blur System

## [결제 상태에 따른 이미지 Blur 처리 API]

### Completed Tests
- [x] Test name: test_get_special_image_with_invalid_session_returns_404
- [x] Expected behavior: 존재하지 않는 session_id로 요청 시 404 반환
- [x] Acceptance criteria: "Game session not found" 메시지와 함께 404 상태 코드 반환

- [x] Test name: test_get_special_image_for_non_premium_user_returns_blurred
- [x] Expected behavior: 비프리미엄 사용자는 blur 처리된 이미지 반환
- [x] Acceptance criteria: is_blurred: true 반환

- [x] Test name: test_get_special_image_for_premium_user_returns_not_blurred
- [x] Expected behavior: 프리미엄 사용자는 원본 이미지 반환
- [x] Acceptance criteria: is_blurred: false 반환

### Implementation Notes
- 프리미엄 사용자(is_premium=True)는 원본 이미지 표시
- 비프리미엄 사용자는 blur 처리된 이미지 표시
- 프론트엔드에서 is_blurred 값에 따라 CSS blur 효과 적용

### Files Changed
- app/api/scenes.py (get_special_image 엔드포인트 추가, SpecialImageResponse 스키마)
- tests/test_special_image.py (new)
- plan.md (완료 표시)

### API Endpoint
- GET /api/scenes/{session_id}/special-image?image_url={url}
  - Response 200: { image_url: string, is_blurred: boolean }
  - Response 404: { detail: "Game session not found" }

### Frontend Usage
```tsx
<Image
  src={specialImage.image_url}
  className={specialImage.is_blurred ? "blur-xl" : ""}
/>
{specialImage.is_blurred && <PremiumUpgradeModal />}
```
