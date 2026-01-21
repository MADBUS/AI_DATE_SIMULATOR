# AI Love Simulator - Development Plan

> **기술 스택**: Next.js 14 + FastAPI + PostgreSQL + Redis  
> **기간**: 3주 (2026-01-14 ~ 2026-02-04)  
> **목표**: AI 이미지 생성 + 호감도 시스템 + 엔딩 시스템

---

## 📋 목차
1. [데이터베이스 구조](#1-데이터베이스-구조)
2. [주차별 백로그](#2-주차별-백로그)
3. [상세 태스크](#3-상세-태스크)

---/해 

## 1. 데이터베이스 구조

### 1.1 테이블 목록

| 테이블 | 용도 | 주요 필드 |
|--------|------|-----------|
| **users** | 사용자 정보 | google_id, email, mbti, is_premium |
| **game_sessions** | 게임 진행 상태 | user_id, affection, current_scene, status, save_slot |
| **character_settings** | 연애 대상자 설정 | session_id, gender, style, mbti, art_style |
| **character_expressions** | 표정 이미지 (6종) | setting_id, expression_type, image_url |
| **scenes** | 각 씬 데이터 | session_id, expression_type, dialogue_text, is_special_event |
| **ai_generated_content** | AI 캐시 | prompt_hash, content_type, content_data |
| **minigame_results** | 미니게임 결과 | session_id, result, bonus_affection |

### 1.2 ERD 간소화

```
users (사용자: mbti, is_premium)
  ↓ 1:N
game_sessions (게임)
  ↓ 1:1
character_settings (연애 대상자 설정: 성별, 스타일, MBTI, 그림체)
  ↓ 1:N
character_expressions (표정 이미지 6종)

game_sessions → scenes (씬)
game_sessions → minigame_results (미니게임 결과)
ai_generated_content (AI 캐시: 표정, 서비스 컷)
```

### 1.3 스키마 생성 순서

```sql
-- 1. 사용자
CREATE TABLE users (
    id UUID PRIMARY KEY,
    google_id VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    mbti VARCHAR(4),  -- ENFP, ISTJ 등
    is_premium BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. 게임 세션
CREATE TABLE game_sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    affection INT CHECK (affection >= 0 AND affection <= 100),
    current_scene INT DEFAULT 1,
    status VARCHAR(20) DEFAULT 'playing', -- 'playing', 'happy_ending', 'sad_ending'
    save_slot INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. 연애 대상자 설정
CREATE TABLE character_settings (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES game_sessions(id) UNIQUE,
    gender VARCHAR(10), -- 'male', 'female'
    style VARCHAR(50), -- 'tsundere', 'cool', 'cute', 'sexy', 'pure'
    mbti VARCHAR(4),
    art_style VARCHAR(50), -- 'anime', 'realistic', 'watercolor'
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. 표정 이미지
CREATE TABLE character_expressions (
    id UUID PRIMARY KEY,
    setting_id UUID REFERENCES character_settings(id),
    expression_type VARCHAR(20), -- 'neutral', 'happy', 'sad', 'jealous', 'shy', 'excited'
    image_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. 씬
CREATE TABLE scenes (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES game_sessions(id),
    scene_number INT,
    expression_type VARCHAR(20),
    dialogue_text TEXT,
    choices_offered JSONB,
    is_special_event BOOLEAN DEFAULT FALSE,
    special_image_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6. AI 캐시
CREATE TABLE ai_generated_content (
    id UUID PRIMARY KEY,
    prompt_hash VARCHAR(64) UNIQUE,
    content_type VARCHAR(20), -- 'expression', 'special_event'
    content_data JSONB,
    cache_hit_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. 미니게임 결과
CREATE TABLE minigame_results (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES game_sessions(id),
    scene_number INT,
    result VARCHAR(10), -- 'perfect', 'great', 'miss'
    bonus_affection INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 2. 주차별 백로그

### Week 1: 인증 + 사용자/캐릭터 설정
- [x] 프로젝트 초기화 (Next.js, FastAPI)
- [x] Google OAuth 로그인
- [x] 사용자 MBTI 입력 (온보딩)
- [x] 연애 대상자 커스터마이징 API (성별, 스타일, MBTI, 그림체)
- [x] 게임 세션 생성
- [x] 캐릭터 설정 DB 저장

### Week 2: AI 통합 + 표정 시스템
- [x] Gemini API 연동
- [ ] 표정 이미지 6종 사전 생성
- [ ] 미니게임: 눈 마주치기 (로딩 대기용)
- [ ] MBTI 기반 선택지 생성
- [ ] 게임 화면 UI (표정 전환)
- [ ] 호감도 게이지

### Week 3: 특별 이벤트 + 결제 + 배포
- [ ] 특별 이벤트 랜덤 발생
- [ ] 서비스 컷 blur/원본 처리 (결제 상태)
- [ ] 마이페이지 (MBTI 수정)
- [ ] 엔딩 화면
- [ ] 게임 저장/불러오기
- [ ] Redis 캐싱
- [ ] Vercel 배포 (프론트)
- [ ] Railway 배포 (백엔드)

---

## 3. 상세 태스크

### 🔴 Week 1: 기반 구축

#### TASK-001: 환경 설정
**담당**: 개발자  
**시간**: 2시간

**프론트엔드**
```bash
npx create-next-app@latest ai-love-simulator --typescript --tailwind --app
npm install next-auth axios zustand framer-motion
```

**백엔드**
```bash
mkdir ai-love-backend && cd ai-love-backend
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn sqlalchemy asyncpg redis google-generativeai
```

**완료 조건**:
- ✅ 프론트엔드 실행 (`npm run dev`)
- ✅ 백엔드 실행 (`uvicorn app.main:app --reload`)

---

#### TASK-002: 데이터베이스 생성
**담당**: 개발자

1. Supabase 프로젝트 생성
2. 위의 스키마 SQL 실행 (7개 테이블)

**완료 조건**:
- ✅ Supabase 연결 성공
- ✅ 테이블 7개 생성 (users, game_sessions, character_settings, character_expressions, scenes, ai_generated_content, minigame_results)

---

#### TASK-003: Google OAuth + MBTI 온보딩
**담당**: 개발자

**구현 파일**:
- `app/api/auth/[...nextauth]/route.ts`
- `components/auth/LoginButton.tsx`
- `app/onboarding/page.tsx` (MBTI 선택)

**API**:
- `POST /api/auth/users` - 사용자 생성/조회
- `PATCH /api/users/{user_id}/mbti` - MBTI 업데이트

**완료 조건**:
- ✅ Google 로그인 버튼 동작
- ✅ 첫 로그인 시 MBTI 선택 화면
- ✅ MBTI 16가지 선택 UI
- ✅ 사용자 정보 + MBTI DB 저장

---

#### TASK-004: 연애 대상자 커스터마이징 API
**담당**: 개발자

**목표**: 사용자가 AI 파트너의 특성(성별, 스타일, MBTI, 그림체)을 선택하여 새로운 게임 세션을 시작할 수 있는 API 엔드포인트를 TDD 방식으로 개발합니다.

**구현 파일**:
- **테스트 (신규)**: `tests/api/test_character_settings.py`
- **API 라우터 (신규)**: `app/api/character_settings.py`
- **스키마 (신규/수정)**: `app/schemas/character.py`, `app/schemas/game.py`
- **모델 (신규/수정)**: `app/models/character.py`, `app/models/game.py`
- **메인 앱**: `app/main.py` (라우터 추가)

**API 설계**:
- **`POST /api/character_settings/`**
  - **설명**: 사용자 ID와 캐릭터 설정을 받아 새로운 게임 세션과 캐릭터 설정을 생성합니다.
  - **요청 본문** (`schemas.CharacterSettingCreate`):
    ```json
    {
      "user_id": "a-valid-user-uuid",
      "gender": "female",
      "style": "tsundere",
      "mbti": "INTJ",
      "art_style": "anime"
    }
    ```
  - **성공 응답 (201 Created)** (`schemas.GameSession`):
    ```json
    {
      "id": "new-game-session-uuid",
      "user_id": "a-valid-user-uuid",
      "affection": 42,
      "current_scene": 1,
      "status": "playing",
      "save_slot": 1,
      "character_settings": {
        "id": "new-character-setting-uuid",
        "gender": "female",
        "style": "tsundere",
        "mbti": "INTJ",
        "art_style": "anime"
      }
    }
    ```
  - **실패 응답**:
    - `404 Not Found`: `user_id`가 존재하지 않을 경우.
    - `422 Unprocessable Entity`: 요청 본문이 유효하지 않을 경우.

**TDD 구현 단계**:
1.  **RED**:
    - `tests/api/` 폴더를 생성합니다.
    - `tests/api/test_character_settings.py` 파일을 생성합니다.
    - `test_create_game_with_character_settings` 함수 내에, 존재하지 않는 `user_id`로 `/api/character_settings/`에 POST 요청을 보내고 `404 Not Found` 응답이 오는지 확인하는 테스트 코드를 작성합니다.
    - 테스트를 실행하여 `404`가 아닌 다른 오류(예: 엔드포인트 없음)로 실패하는 것을 확인합니다.
2.  **GREEN**:
    - `app/api/character_settings.py` 파일과 `APIRouter`를 생성합니다.
    - `app/main.py`에 위에서 생성한 라우터를 포함시킵니다.
    - `app/schemas/character.py`에 `CharacterSettingCreate`와 `CharacterSetting` 스키마를 정의합니다.
    - `app/schemas/game.py`에 `GameSession` 응답 스키마(캐릭터 설정 포함)를 정의합니다.
    - `POST /api/character_settings/` 엔드포인트의 기본 로직을 구현합니다. (DB 연동 없이, 받은 데이터를 그대로 반환)
    - 테스트가 `404`로 실패하도록 (사용자 조회 로직 추가) 수정합니다.
3.  **RED**:
    - 이번에는 유효한 `user_id`로 요청 시, 새로운 `GameSession`과 `CharacterSetting`이 성공적으로 생성되고 `201 Created` 상태 코드와 함께 해당 세션 정보가 반환되는지 확인하는 테스트를 추가합니다. 이 테스트는 DB 로직이 없으므로 실패합니다.
4.  **GREEN**:
    - `app/models/`에 필요한 SQLAlchemy 모델(`GameSession`, `CharacterSetting`)이 `plan.md`의 정의와 일치하는지 확인/수정합니다.
    - 엔드포인트에 실제 DB 세션을 주입하고, 전달받은 데이터로 `GameSession`과 `CharacterSetting` 객체를 생성하여 DB에 저장하는 로직을 구현합니다.
    - 초기 호감도를 30-50 사이의 랜덤 값으로 설정하는 로직을 추가합니다.
    - 모든 테스트가 통과하는지 확인합니다.
5.  **REFACTOR**:
    - 코드의 중복을 제거하고, 가독성을 높입니다.
    - 서비스 로직이 있다면 서비스 계층으로 분리하는 것을 고려합니다.
    - 모든 테스트가 여전히 통과하는지 확인합니다.

**완료 조건**:
- ✅ 위 TDD 단계에 따라 작성된 모든 테스트가 통과합니다.
- ✅ `POST /api/character_settings/` 엔드포인트가 성공적으로 동작하여 DB에 데이터를 생성합니다.

---

#### TASK-005: 게임 세션 생성
**담당**: 개발자

**API**:
- `POST /api/games/new` - 게임 생성 (호감도 랜덤 30-50)
- `GET /api/games/{session_id}` - 게임 조회

**로직**:
```python
# 호감도 초기화
initial_affection = random.randint(30, 50)

# 엔딩 조건
if affection <= 10:
    return "sad_ending"
if scene >= 10:
    return "happy_ending" if affection >= 70 else "sad_ending"
return "playing"
```

**완료 조건**:
- ✅ 게임 세션 생성
- ✅ 캐릭터 설정 연결
- ✅ 호감도 랜덤 초기화
- ✅ 슬롯 시스템 (1-3)

---

### 🟡 Week 2: AI 통합 + 표정 시스템

#### TASK-006: Gemini API 설정
**담당**: 개발자

**파일**:
- `app/services/gemini.py`

**기능**:
```python
async def generate_expression_images(character_settings):
    """캐릭터 설정 기반 6개 표정 이미지 생성"""
    expressions = ['neutral', 'happy', 'sad', 'jealous', 'shy', 'excited']

    for expr in expressions:
        prompt = build_prompt(character_settings, expr)
        image_url = await gemini.generate_image(prompt)
        await save_expression(character_settings.id, expr, image_url)
```

**완료 조건**:
- ✅ Gemini API 키 설정
- ✅ 표정별 프롬프트 생성
- ✅ 6개 이미지 비동기 생성

---

#### TASK-007: 표정 이미지 사전 생성
**담당**: 개발자

**API**:
- `POST /api/games/{session_id}/generate-expressions` - 6개 표정 생성

**표정 종류**:
1. neutral (일반)
2. happy (기쁜)
3. sad (슬픈)
4. jealous (질투)
5. shy (부끄러운)
6. excited (흥분)

**완료 조건**:
- ✅ 캐릭터 설정 기반 프롬프트 생성
- ✅ 6개 이미지 생성 및 DB 저장
- ✅ 생성 중 미니게임 표시

---

#### TASK-008: 미니게임 - 눈 마주치기
**담당**: 개발자

**구현 파일**:
- `components/minigame/EyeContactGame.tsx`

**게임 방식**:
```
┌─────────────────────────┐
│      👁️ 캐릭터 눈 👁️     │
├─────────────────────────┤
│  ←──────💗──────→       │  (하트 게이지 좌우 이동)
├─────────────────────────┤
│      [터치하세요!]       │
└─────────────────────────┘

결과:
- Perfect (정중앙): +3 호감도
- Great (근접): +1 호감도
- Miss (실패): 0
```

**완료 조건**:
- ✅ 게이지 좌우 이동 애니메이션
- ✅ 터치/클릭 판정
- ✅ 결과별 보너스 호감도
- ✅ minigame_results 테이블 저장

---

#### TASK-009: MBTI 기반 선택지 생성
**담당**: 개발자

**API**:
- `POST /api/scenes/{session_id}/generate` - 씬 + 선택지 생성

**로직**:
```python
async def generate_choices(user_mbti, character_settings, affection):
    """사용자 MBTI에 맞는 선택지 스타일 생성"""
    prompt = f"""
    사용자 MBTI: {user_mbti}
    캐릭터 스타일: {character_settings.style}
    캐릭터 MBTI: {character_settings.mbti}
    현재 호감도: {affection}

    위 정보를 바탕으로 3개의 선택지를 생성하세요.
    사용자의 MBTI 성향에 맞는 표현 스타일을 사용하세요.
    """
    return await gemini.generate_choices(prompt)
```

**완료 조건**:
- ✅ 사용자 MBTI 반영 프롬프트
- ✅ 캐릭터 설정 반영
- ✅ 호감도 기반 선택지 생성

---

#### TASK-010: 게임 화면 UI
**담당**: 개발자

**파일**:
- `app/game/page.tsx`

**화면 구성**:
```
┌─────────────────────────┐
│ 호감도: ❤️❤️❤️🤍🤍 (60) │
├─────────────────────────┤
│  [캐릭터 표정 이미지]     │  ← 상황에 따라 6개 중 선택
├─────────────────────────┤
│  대사: "안녕하세요..."   │  ← MBTI 반영 말투
├─────────────────────────┤
│  [선택지 1]              │  ← 사용자 MBTI 스타일
│  [선택지 2]              │
│  [선택지 3]              │
└─────────────────────────┘
```

**완료 조건**:
- ✅ 표정 이미지 상황별 전환
- ✅ 호감도 게이지
- ✅ MBTI 스타일 선택지 표시

---

#### TASK-011: 선택 처리 + 호감도
**담당**: 개발자

**API**:
- `POST /api/games/{session_id}/select`

**로직**:
```python
# 호감도 계산 (미니게임 보너스 포함)
new_affection = old_affection + delta + minigame_bonus

# 엔딩 체크
if new_affection <= 10:
    return "sad_ending"
if scene >= 10:
    return "happy_ending" if new_affection >= 70 else "sad_ending"
```

**완료 조건**:
- ✅ 호감도 업데이트
- ✅ 미니게임 보너스 반영
- ✅ 엔딩 조건 체크

---

### 🟢 Week 3: 특별 이벤트 + 결제 + 배포

#### TASK-012: 특별 이벤트 시스템
**담당**: 개발자

**API**:
- `POST /api/scenes/{session_id}/check-event` - 이벤트 발생 체크

**로직**:
```python
async def check_special_event(session_id, scene_number):
    """10-15% 확률로 특별 이벤트 발생"""
    if random.random() < 0.15:  # 15% 확률
        # 서비스 컷 이미지 생성
        special_image = await generate_special_image(session_id)
        return {
            "is_special_event": True,
            "special_image_url": special_image,
            "show_minigame": True
        }
    return {"is_special_event": False}
```

**완료 조건**:
- ✅ 랜덤 확률 이벤트 발생
- ✅ 서비스 컷 이미지 생성
- ✅ 이미지 생성 중 미니게임 표시

---

#### TASK-013: 결제 상태 + Blur 처리
**담당**: 개발자

**로직**:
```python
async def get_special_image(user_id, image_url):
    """결제 상태에 따라 blur 처리"""
    user = await get_user(user_id)
    if user.is_premium:
        return {"image_url": image_url, "is_blurred": False}
    else:
        return {"image_url": image_url, "is_blurred": True}
```

**프론트엔드**:
```tsx
<Image
  src={specialImage.url}
  className={specialImage.is_blurred ? "blur-xl" : ""}
/>
{!user.isPremium && <PremiumUpgradeModal />}
```

**완료 조건**:
- ✅ is_premium 상태 체크
- ✅ blur CSS 처리
- ✅ 결제 유도 모달

---

#### TASK-014: 마이페이지
**담당**: 개발자

**구현 파일**:
- `app/mypage/page.tsx`

**기능**:
- MBTI 수정
- 결제 상태 확인
- 게임 통계

**API**:
- `GET /api/users/{user_id}` - 사용자 정보
- `PATCH /api/users/{user_id}/mbti` - MBTI 수정

**완료 조건**:
- ✅ MBTI 수정 UI
- ✅ 결제 상태 표시
- ✅ 통계 표시

---

#### TASK-015: 엔딩 화면
**담당**: 개발자

**화면**:
- HAPPY 엔딩: 축하 메시지 + 특별 이미지
- SAD 엔딩: 아쉬움 메시지
- 버튼: "다시 시작", "메인으로"

**완료 조건**:
- ✅ 엔딩 타입별 화면
- ✅ 최종 호감도 표시
- ✅ 다시 시작 기능

---

#### TASK-016: 게임 저장/불러오기
**담당**: 개발자

**API**:
- `GET /api/games?user_id={user_id}` - 저장된 게임 목록

**화면**:
```
저장된 게임
- 슬롯 1: 여자/츤데레/ENFP (호감도 65, 씬 7)
- 슬롯 2: 남자/쿨뷰티/INTJ (호감도 45, 씬 4)
[+ 새 게임]
```

**완료 조건**:
- ✅ 게임 목록 표시
- ✅ 캐릭터 설정 정보 표시
- ✅ 이어하기 버튼

---

#### TASK-017: Redis 캐싱
**담당**: 개발자

**캐시 키**:
```
session:{session_id} = {game_state}  # TTL: 1시간
expression:{setting_id}:{type} = {image_url}  # TTL: 24시간
special:{prompt_hash} = {image_url}  # TTL: 24시간
```

**완료 조건**:
- ✅ 세션 캐싱
- ✅ 표정 이미지 캐싱
- ✅ 서비스 컷 캐싱

---

#### TASK-018: Vercel 배포
**담당**: 개발자

```bash
vercel --prod
```

**환경변수**:
- `NEXT_PUBLIC_API_URL`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

**완료 조건**:
- ✅ 프로덕션 배포
- ✅ 도메인 연결

---

#### TASK-019: Railway 배포
**담당**: 개발자

**Dockerfile**:
```dockerfile
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**완료 조건**:
- ✅ 백엔드 배포
- ✅ API 동작 확인

---

## 4. API 명세 요약

### 인증
- `POST /api/auth/users` - 사용자 생성/조회
- `PATCH /api/users/{user_id}/mbti` - MBTI 수정

### 사용자
- `GET /api/users/{user_id}` - 사용자 정보 조회

### 게임
- `POST /api/games/new` - 게임 + 캐릭터 설정 생성
- `GET /api/games?user_id={id}` - 게임 목록
- `GET /api/games/{session_id}` - 게임 조회
- `GET /api/games/{session_id}/settings` - 캐릭터 설정 조회
- `POST /api/games/{session_id}/generate-expressions` - 표정 6개 생성
- `POST /api/games/{session_id}/select` - 선택 처리

### 씬
- `POST /api/scenes/{session_id}/generate` - 씬 + 선택지 생성
- `POST /api/scenes/{session_id}/check-event` - 특별 이벤트 체크

### 미니게임
- `POST /api/minigame/{session_id}/result` - 미니게임 결과 저장

---

## 5. 체크리스트

### Week 1: 인증 + 사용자/캐릭터 설정
- [ ] 프로젝트 초기화
- [ ] DB 스키마 생성 (7개 테이블)
- [ ] Google OAuth + MBTI 온보딩
- [ ] 연애 대상자 커스터마이징 UI
- [ ] 게임 세션 생성

### Week 2: AI 통합 + 표정 시스템
- [ ] Gemini API 설정
- [ ] 표정 이미지 6종 사전 생성
- [ ] 미니게임: 눈 마주치기
- [ ] MBTI 기반 선택지 생성
- [ ] 게임 화면 UI (표정 전환)
- [ ] 선택 처리 + 호감도

### Week 3: 특별 이벤트 + 결제 + 배포
- [ ] 특별 이벤트 시스템
- [ ] 결제 상태 + blur 처리
- [ ] 마이페이지
- [ ] 엔딩 화면
- [ ] 게임 저장/불러오기
- [ ] Redis 캐싱
- [ ] Vercel 배포
- [ ] Railway 배포
- [ ] 최종 테스트

---

**Last Updated**: 2026-01-20