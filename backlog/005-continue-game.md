# Backlog: Continue Game Feature

## [게임 이어하기 기능]

### Tests to Implement (Frontend)
- [ ] Test name: shouldDisplayGameListOnMyPage
- [ ] Expected behavior: 마이페이지에서 사용자의 진행 중인 게임 목록이 표시됨
- [ ] Acceptance criteria: 게임 목록에 캐릭터 정보, 호감도, 진행 상황 표시

- [ ] Test name: shouldNavigateToGameOnContinueClick
- [ ] Expected behavior: "이어하기" 버튼 클릭 시 해당 게임 세션으로 이동
- [ ] Acceptance criteria: /game/{sessionId} 경로로 라우팅

- [ ] Test name: shouldShowContinueOptionOnMainPage
- [ ] Expected behavior: 메인 페이지에서 진행 중인 게임이 있으면 이어하기 옵션 표시
- [ ] Acceptance criteria: "이어하기" 버튼과 "새 게임" 버튼 분리 표시

### Implementation Notes
- Backend API already exists: GET /api/games?user_id={uuid}
- Frontend changes needed:
  1. MyPage: Add game list section with continue buttons
  2. MainPage: Check for existing games, show continue option

### Dependencies
- Existing API: GET /api/games (returns list of GameSessionResponse)
- GameSessionResponse includes: id, character_name, affection, current_scene, status

### Files to Change
- frontend/app/mypage/page.tsx (add game list)
- frontend/app/page.tsx (add continue option)
- frontend/types/index.ts (add GameSession type if needed)
