# AI Love Simulator - Development Plan

> **기술 스택**: Next.js 14 + FastAPI + PostgreSQL + Redis  
> **기간**: 3주 (2026-01-14 ~ 2026-02-04)  
> **목표**: AI 이미지 생성 + 호감도 시스템 + 엔딩 시스템

---

## 📋 목차
1. [데이터베이스 구조](#1-데이터베이스-구조)
2. [주차별 백로그](#2-주차별-백로그)
3. [상세 태스크](#3-상세-태스크)

---

## 1. 데이터베이스 구조

### 1.1 테이블 목록

| 테이블 | 용도 | 주요 필드 |
|--------|------|-----------|
| **users** | 사용자 정보 | google_id, email, name |
| **characters** | 캐릭터 마스터 (3종) | name, type, personality, avatar_prompt |
| **game_sessions** | 게임 진행 상태 | user_id, character_id, affection, current_scene, status |
| **scenes** | 각 씬 데이터 | session_id, image_url, dialogue_text, choices_offered |
| **choice_templates** | 선택지 마스터 | character_id, choice_text, affection_delta |
| **ai_generated_content** | AI 캐시 | prompt_hash, content_data |

### 1.2 ERD 간소화

```
users (사용자)
  ↓ 1:N
game_sessions (게임)
  ↓ 1:N
scenes (씬)
  
characters (캐릭터) → game_sessions
choice_templates (선택지) → characters
ai_generated_content (AI 캐시) → characters
```

### 1.3 스키마 생성 순서

```sql
-- 1. 사용자
CREATE TABLE users (
    id UUID PRIMARY KEY,
    google_id VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. 캐릭터
CREATE TABLE characters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    type VARCHAR(50), -- 'tsundere', 'cool', 'cute'
    personality TEXT,
    base_affection_min INT DEFAULT 30,
    base_affection_max INT DEFAULT 50,
    avatar_prompt TEXT
);

-- 3. 게임 세션
CREATE TABLE game_sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    character_id INT REFERENCES characters(id),
    affection INT CHECK (affection >= 0 AND affection <= 100),
    current_scene INT DEFAULT 1,
    status VARCHAR(20) DEFAULT 'playing', -- 'playing', 'happy_ending', 'sad_ending'
    save_slot INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. 씬
CREATE TABLE scenes (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES game_sessions(id),
    scene_number INT,
    image_url TEXT,
    dialogue_text TEXT,
    choices_offered JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. 선택지 템플릿
CREATE TABLE choice_templates (
    id SERIAL PRIMARY KEY,
    character_id INT REFERENCES characters(id),
    affection_min INT,
    affection_max INT,
    choice_text TEXT,
    affection_delta INT,
    tags TEXT[]
);

-- 6. AI 캐시
CREATE TABLE ai_generated_content (
    id UUID PRIMARY KEY,
    character_id INT REFERENCES characters(id),
    prompt_hash VARCHAR(64) UNIQUE,
    content_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 2. 주차별 백로그

### Week 1: 인증 + 게임 로직
- [x] 프로젝트 초기화 (Next.js, FastAPI)
- [ ] Google OAuth 로그인
- [ ] 캐릭터 선택
- [ ] 게임 세션 생성
- [ ] 선택지 생성 로직

### Week 2: AI 통합 + UI
- [ ] Gemini API 연동
- [ ] 씬 생성 (이미지 + 대화)
- [ ] 게임 화면 UI
- [ ] 호감도 게이지
- [ ] 엔딩 화면

### Week 3: 세이브/로드 + 배포
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
**시간**: 2시간

1. Supabase 프로젝트 생성
2. 위의 스키마 SQL 실행
3. 캐릭터 3개 초기 데이터 삽입

```sql
INSERT INTO characters (name, type, personality, base_affection_min, base_affection_max, avatar_prompt) VALUES
('사쿠라', 'tsundere', '겉으로는 차갑지만 속으로는 따뜻함', 30, 40, 'Anime girl with pink hair, tsundere expression'),
('유리', 'cool', '냉정하고 이성적인 매력', 35, 45, 'Anime girl with black hair, glasses, cool look'),
('모모', 'cute', '밝고 귀여운 성격', 40, 50, 'Anime girl with blonde twin tails, cheerful smile');
```

**완료 조건**:
- ✅ Supabase 연결 성공
- ✅ 테이블 6개 생성
- ✅ 캐릭터 3개 삽입

---

#### TASK-003: Google OAuth
**담당**: 개발자  
**시간**: 3시간

**구현 파일**:
- `app/api/auth/[...nextauth]/route.ts`
- `components/auth/LoginButton.tsx`

**API**:
- `POST /api/auth/users` - 사용자 생성/조회

**완료 조건**:
- ✅ Google 로그인 버튼 동작
- ✅ 로그인 후 사용자 정보 DB 저장
- ✅ 세션 유지

---

#### TASK-004: 캐릭터 선택
**담당**: 개발자  
**시간**: 3시간

**구현 파일**:
- `app/characters/page.tsx`
- `app/api/characters.py`

**API**:
- `GET /api/characters` - 캐릭터 목록

**완료 조건**:
- ✅ 캐릭터 3개 카드 표시
- ✅ 클릭 시 게임 시작

---

#### TASK-005: 게임 세션 생성
**담당**: 개발자  
**시간**: 4시간

**API**:
- `POST /api/games/new` - 게임 생성 (호감도 랜덤 30-50)
- `GET /api/games/{session_id}` - 게임 조회

**로직**:
```python
# 호감도 초기화
initial_affection = random.randint(
    character.base_affection_min, 
    character.base_affection_max
)

# 엔딩 조건
if affection <= 10:
    return "sad_ending"
if scene >= 10:
    return "happy_ending" if affection >= 70 else "sad_ending"
return "playing"
```

**완료 조건**:
- ✅ 게임 세션 생성
- ✅ 호감도 랜덤 초기화
- ✅ 슬롯 시스템 (1-3)

---

#### TASK-006: 선택지 생성
**담당**: 개발자  
**시간**: 5시간

**선택지 초기 데이터**:
```sql
-- 각 캐릭터별 8개씩 (긍정 3개, 중립 3개, 부정 2개)
INSERT INTO choice_templates VALUES
(1, 0, 100, '칭찬한다', 8, ARRAY['positive']),
(1, 0, 100, '커피를 권한다', 3, ARRAY['neutral']),
(1, 0, 100, '스마트폰을 본다', -5, ARRAY['negative']);
```

**API**:
- `GET /api/games/{session_id}/choices` - 선택지 3개

**로직**:
- 현재 호감도 범위에 맞는 선택지 필터링
- 긍정/중립/부정 각 1개씩 선택

**완료 조건**:
- ✅ 선택지 24개 삽입 (캐릭터당 8개)
- ✅ 호감도 기반 필터링
- ✅ 3개 선택지 반환

---

### 🟡 Week 2: AI 통합

#### TASK-007: Gemini API 설정
**담당**: 개발자  
**시간**: 3시간

**파일**:
- `app/services/gemini.py`

**기능**:
```python
async def generate_image(character_prompt, affection):
    # 프롬프트 생성
    mood = "happy" if affection > 60 else "neutral"
    prompt = f"{character_prompt}, mood: {mood}"
    
    # 캐시 확인
    hash = sha256(prompt)
    cached = await redis.get(f"ai:image:{hash}")
    if cached:
        return cached
    
    # Gemini 호출 (실제로는 Placeholder)
    image_url = "https://placeholder.com/image.jpg"
    
    # 캐시 저장
    await redis.set(f"ai:image:{hash}", image_url, ttl=86400)
    return image_url
```

**완료 조건**:
- ✅ Gemini API 키 설정
- ✅ 이미지 생성 함수 (Placeholder)
- ✅ Redis 캐싱

---

#### TASK-008: 씬 생성 API
**담당**: 개발자  
**시간**: 4시간

**API**:
- `POST /api/scenes/{session_id}/generate`

**응답**:
```json
{
  "scene_number": 1,
  "image_url": "https://...",
  "dialogue": "안녕하세요. 반가워요.",
  "choices": [
    {"id": 1, "text": "칭찬한다", "delta": 8},
    {"id": 2, "text": "커피 권한다", "delta": 3},
    {"id": 3, "text": "스마트폰 본다", "delta": -5}
  ],
  "affection": 35
}
```

**완료 조건**:
- ✅ 이미지 + 대화 + 선택지 통합
- ✅ DB에 씬 저장

---

#### TASK-009: 선택 처리
**담당**: 개발자  
**시간**: 3시간

**API**:
- `POST /api/games/{session_id}/select`

**로직**:
```python
# 호감도 계산
new_affection = max(0, min(100, old_affection + delta))

# 씬 진행
session.affection = new_affection
session.current_scene += 1

# 엔딩 체크
if new_affection <= 10:
    session.status = "sad_ending"
elif session.current_scene >= 10:
    session.status = "happy_ending" if new_affection >= 70 else "sad_ending"
```

**완료 조건**:
- ✅ 호감도 업데이트
- ✅ 다음 씬 이동
- ✅ 엔딩 조건 체크

---

#### TASK-010: 게임 화면 UI
**담당**: 개발자  
**시간**: 6시간

**파일**:
- `app/game/page.tsx`

**화면 구성**:
```
┌─────────────────────────┐
│ 호감도: ❤️❤️❤️🤍🤍 (60) │
├─────────────────────────┤
│  [캐릭터 이미지]         │
├─────────────────────────┤
│  대사: "안녕하세요..."   │
├─────────────────────────┤
│  [선택지 1]              │
│  [선택지 2]              │
│  [선택지 3]              │
└─────────────────────────┘
```

**완료 조건**:
- ✅ 이미지 표시
- ✅ 호감도 게이지
- ✅ 선택지 버튼

---

#### TASK-011: 엔딩 화면
**담당**: 개발자  
**시간**: 3시간

**화면**:
- HAPPY 엔딩: 💕 축하 메시지
- SAD 엔딩: 💔 아쉬움 메시지
- 버튼: "다시 시작", "메인으로"

**완료 조건**:
- ✅ 엔딩 타입별 화면
- ✅ 최종 호감도 표시
- ✅ 다시 시작 기능

---

### 🟢 Week 3: 완성

#### TASK-012: 게임 목록
**담당**: 개발자  
**시간**: 3시간

**API**:
- `GET /api/games?user_id={user_id}` - 저장된 게임 목록

**화면**:
```
저장된 게임
- 슬롯 1: 사쿠라 (호감도 65, 씬 7)
- 슬롯 2: 유리 (호감도 45, 씬 4)
[+ 새 게임]
```

**완료 조건**:
- ✅ 게임 목록 표시
- ✅ 이어하기 버튼

---

#### TASK-013: Redis 자동 저장
**담당**: 개발자  
**시간**: 2시간

**로직**:
```python
# 선택시마다 자동 저장
await redis.set(
    f"game:session:{session_id}",
    {"affection": 65, "scene": 7},
    ttl=3600
)
```

**완료 조건**:
- ✅ 선택시 Redis 저장
- ✅ 1시간 TTL

---

#### TASK-014: Vercel 배포
**담당**: 개발자  
**시간**: 2시간

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

#### TASK-015: Railway 배포
**담당**: 개발자  
**시간**: 2시간

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

### 캐릭터
- `GET /api/characters` - 캐릭터 목록

### 게임
- `POST /api/games/new` - 게임 생성
- `GET /api/games?user_id={id}` - 게임 목록
- `GET /api/games/{session_id}` - 게임 조회
- `GET /api/games/{session_id}/choices` - 선택지 조회
- `POST /api/games/{session_id}/select` - 선택 처리

### 씬
- `POST /api/scenes/{session_id}/generate` - 씬 생성

---

## 5. 체크리스트

### Week 1
- [ ] 프로젝트 초기화
- [ ] DB 스키마 생성
- [ ] Google OAuth
- [ ] 캐릭터 선택
- [ ] 게임 세션 생성
- [ ] 선택지 생성

### Week 2
- [ ] Gemini API 설정
- [ ] 씬 생성 API
- [ ] 선택 처리
- [ ] 게임 화면 UI
- [ ] 엔딩 화면

### Week 3
- [ ] 게임 목록
- [ ] Redis 자동 저장
- [ ] Vercel 배포
- [ ] Railway 배포
- [ ] 최종 테스트

---

**Last Updated**: 2026-01-14