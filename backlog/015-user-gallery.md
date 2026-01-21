# Backlog: User Gallery System

## [사용자 갤러리 - 세션 삭제와 무관한 이미지 보관]

### Completed Tests
- [x] Test name: test_get_gallery_with_invalid_user_returns_404
- [x] Expected behavior: 존재하지 않는 user_id로 요청 시 404 반환
- [x] Acceptance criteria: "User not found" 메시지와 함께 404 상태 코드 반환

- [x] Test name: test_premium_user_sees_all_images_without_blur
- [x] Expected behavior: 프리미엄 사용자는 모든 이미지(expression, special, ending) blur 없이 확인
- [x] Acceptance criteria: 모든 이미지 is_blurred: false

- [x] Test name: test_non_premium_user_sees_expression_images_without_blur
- [x] Expected behavior: 비프리미엄 사용자도 6감정 이미지는 blur 없이 확인
- [x] Acceptance criteria: expression 타입 이미지 is_blurred: false

- [x] Test name: test_non_premium_user_sees_special_images_with_blur
- [x] Expected behavior: 비프리미엄 사용자는 특별 이벤트/엔딩 이미지 blur 처리
- [x] Acceptance criteria: special, ending 타입 이미지 is_blurred: true

- [x] Test name: test_save_image_to_gallery
- [x] Expected behavior: 이미지를 사용자 갤러리에 저장
- [x] Acceptance criteria: 201 상태 코드, 저장된 이미지 정보 반환

### Implementation Notes
- UserGallery 모델: 세션과 독립적으로 이미지 저장
- image_type 구분:
  - 'expression': 6감정 이미지 (비프리미엄도 blur 없음)
  - 'special': 특별 이벤트 이미지 (비프리미엄은 blur)
  - 'ending': 엔딩 이미지 (비프리미엄은 blur)
- 세션 삭제 후에도 마이페이지에서 이미지 확인 가능

### Files Changed
- app/models/gallery.py (new - UserGallery 모델)
- app/models/user.py (gallery_images 관계 추가)
- app/models/__init__.py (UserGallery export)
- app/api/users.py (갤러리 API 엔드포인트 추가)
- tests/test_user_gallery.py (new)

### API Endpoints
- GET /api/users/{user_id}/gallery
  - Response 200: { images: [{ id, image_url, image_type, expression_type, is_blurred }] }
  - Response 404: { detail: "User not found" }

- POST /api/users/{user_id}/gallery
  - Request: { image_url: string, image_type: string, expression_type?: string }
  - Response 201: { id, image_url, image_type, expression_type, is_blurred }
  - Response 404: { detail: "User not found" }

### Image Types
- expression: 기본 6감정 (neutral, happy, sad, jealous, shy, excited)
- special: 특별 이벤트 이미지
- ending: 엔딩 이미지

### Blur Policy
| User Type | expression | special | ending |
|-----------|------------|---------|--------|
| Premium   | No Blur    | No Blur | No Blur |
| Free      | No Blur    | Blur    | Blur   |

### Frontend Usage
```tsx
// 마이페이지 갤러리
const { images } = await getGallery(userId);

{images.map(img => (
  <Image
    key={img.id}
    src={img.image_url}
    className={img.is_blurred ? "blur-xl" : ""}
  />
))}
```
