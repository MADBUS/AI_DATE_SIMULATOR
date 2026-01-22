# Backlog: 특별 이벤트 시스템 구현

## [주기적 특별 이벤트 및 미니게임 시스템]

### Completed Tasks

- [x] Task: 전신 이벤트 씬 이미지 생성 함수 추가
- [x] Description: gemini_service.py에 특별 이벤트용 전신 이미지 생성
- [x] Changes:
  - `SPECIAL_EVENT_SCENES` 리스트 추가 (5가지 이벤트 타입)
    - romantic_date: 로맨틱한 데이트 장면
    - surprise_gift: 깜짝 선물 장면
    - rain_shelter: 비를 피하는 장면
    - festival: 축제 장면
    - confession: 고백 장면
  - `generate_special_event_image()` 함수 구현
    - 전신 샷 구도로 이미지 생성
    - 랜덤 또는 지정 이벤트 타입 지원
    - 캐릭터 디자인 일관성 유지

- [x] Task: 주기적 특별 이벤트 발생 로직 구현
- [x] Description: 15% 확률 → 5턴마다 주기적 발생으로 변경
- [x] Changes:
  - `SPECIAL_EVENT_INTERVAL = 5` (5턴마다 이벤트 발생)
  - `check_special_event` API 수정
  - `SpecialEventResponse`에 `event_description` 필드 추가
  - Gemini Imagen API로 실제 이벤트 이미지 생성

- [x] Task: 미니게임 결과 API 추가
- [x] Description: 미니게임 성공/실패에 따른 호감도 변화
- [x] Changes:
  - `MinigameResultRequest` 스키마 추가
  - `MinigameResultResponse` 스키마 추가
  - `POST /{session_id}/minigame-result` API 구현
  - 성공 시: +10 ~ +15 호감도 대폭 상승
  - 실패 시: -2 ~ -3 호감도 소폭 하락

### Files Changed
- app/services/gemini_service.py
  - `SPECIAL_EVENT_SCENES`: 5가지 이벤트 타입 정의
  - `generate_special_event_image()`: 전신 이벤트 씬 이미지 생성
- app/api/scenes.py
  - `SPECIAL_EVENT_INTERVAL`: 이벤트 발생 주기 (5턴)
  - `check_special_event()`: 주기적 이벤트 발생 로직
  - `submit_minigame_result()`: 미니게임 결과 처리 API

### Expected Results
- 5턴마다 특별 이벤트 발생 (5, 10, 15, 20...)
- 이벤트 발생 시 전신 캐릭터 이미지 생성
- 미니게임 성공 시 호감도 대폭 상승 (+10~15)
- 미니게임 실패 시 소폭 하락 (-2~3)

### API Endpoints
- `POST /api/scenes/{session_id}/check-event`: 특별 이벤트 체크
- `POST /api/scenes/{session_id}/minigame-result`: 미니게임 결과 제출
