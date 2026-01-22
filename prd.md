# AI Love Simulator - Product Requirements Document (PRD)

> **버전**: 1.0  
> **작성일**: 2026-01-14  
> **작성자**: JangYeol Pyun  
> **문서 상태**: Draft → Review → Approved

---

## 📑 목차
1. [개요](#개요)
2. [시장 분석](#시장-분석)
3. [제품 비전](#제품-비전)
4. [핵심 기능](#핵심-기능)
5. [기술 아키텍처](#기술-아키텍처)
6. [비즈니스 모델](#비즈니스-모델)
7. [로드맵](#로드맵)
8. [성공 지표](#성공-지표)
9. [리스크 관리](#리스크-관리)

---

## 1. 개요

### 1.1 프로젝트 개요
**AI Love Simulator**는 생성형 AI(Gemini)를 활용한 대화형 연애 시뮬레이션 웹 애플리케이션입니다.

### 1.2 문제 정의
**현재 문제점**:
- 기존 연애 시뮬레이션 게임은 정해진 시나리오만 반복
- 제작 비용이 높아 다양한 캐릭터/스토리 제공 어려움
- 사용자별 개인화된 경험 부족

**우리의 솔루션**:
- ✅ AI 기반 무한한 시나리오 생성
- ✅ 실시간 이미지 생성으로 몰입감 극대화
- ✅ 사용자 선택에 따라 동적으로 변하는 스토리

### 1.3 타겟 사용자

#### Primary Persona
**이름**: 지민 (여, 23세)  
**직업**: 대학생  
**특징**:
- 연애 경험 적음, 로맨스 콘텐츠 좋아함
- 웹툰, 로맨스 소설 즐겨 읽음
- 부담 없는 가상 연애 경험 원함

**Needs**:
- 😊 재미있는 대화 경험
- 💭 안전한 연애 시뮬레이션
- 📱 모바일에서 간편하게 플레이

#### Secondary Persona
**이름**: 준호 (남, 28세)  
**직업**: 직장인  
**특징**:
- AI 기술에 관심 많음
- 퇴근 후 가볍게 즐길 콘텐츠 찾음
- 캐릭터 수집형 게임 선호

**Needs**:
- 🎮 짧은 세션 플레이 (10-15분)
- 🆕 새로운 AI 경험
- 🏆 다양한 엔딩 수집

### 1.4 핵심 가치 제안

| 기존 서비스 | AI Love Simulator |
|------------|-------------------|
| 정해진 시나리오 | ✨ AI 무한 생성 시나리오 |
| 2D 스프라이트 재사용 | 🎨 상황별 실시간 이미지 |
| 10-20개 엔딩 | 🔄 무한한 스토리 분기 |
| 한 번 하면 끝 | 💾 세이브/로드 시스템 |

---

## 2. 시장 분석

### 2.1 시장 규모
- **글로벌 모바일 게임 시장**: $921억 (2024)
- **연애 시뮬레이션 장르**: 약 5% ($4.6억)
- **AI 챗봇 시장**: $9억 → $42억 (2030 예상)

**기회**: 연애 시뮬레이션 + AI 챗봇 융합 시장 선점

### 2.2 경쟁사 분석

#### 직접 경쟁사
| 서비스 | 강점 | 약점 | 차별점 |
|--------|------|------|--------|
| **Character.AI** | 대화 품질 우수 | 이미지 없음, 게임성 부족 | 우리: 비주얼 노벨 형식 |
| **AI Dungeon** | 자유도 높음 | 텍스트 중심, 연애 특화X | 우리: 연애 최적화 |
| **Dream GF** | 비주얼 강점 | 단순 챗봇, 스토리 없음 | 우리: 게임 메커니즘 |

#### 간접 경쟁사
- **전통 연애 시뮬레이션**: Mystic Messenger, Love & Producer
  - 한계: 개발 비용 높음, 업데이트 느림
- **웹툰/소설**: 네이버 웹툰, 카카오페이지
  - 한계: 일방향 콘텐츠, 상호작용 없음

### 2.3 SWOT 분석

#### Strengths (강점)
- ✅ AI 기반 무한 콘텐츠 생성
- ✅ 낮은 개발 비용 (AI가 콘텐츠 생성)
- ✅ 빠른 업데이트 가능
- ✅ 개인화된 경험

#### Weaknesses (약점)
- ⚠️ AI 생성 품질 일관성 이슈
- ⚠️ Gemini API 비용 (확장시)
- ⚠️ 브랜드 인지도 없음

#### Opportunities (기회)
- 🌟 생성형 AI 붐 (ChatGPT 이후)
- 🌟 Z세대의 AI 친화적 성향
- 🌟 메타버스/가상 관계 트렌드

#### Threats (위협)
- ⚡ 대기업 진입 가능성 (네이버, 카카오)
- ⚡ AI 윤리 이슈 (과몰입, 중독)
- ⚡ 규제 리스크

---

## 3. 제품 비전

### 3.1 Mission Statement
> "AI 기술로 누구나 안전하고 재미있는 감정적 경험을 제공한다"

### 3.2 Vision (3년 후)
- 🎯 MAU 100만 달성
- 🎯 10개국 언어 지원
- 🎯 연매출 10억원 (프리미엄 모델)
- 🎯 업계 대표 AI 연애 시뮬레이션 플랫폼

### 3.3 핵심 원칙
1. **안전성 우선**: 건강하지 못한 관계 묘사 금지
2. **투명성**: AI 생성 콘텐츠임을 명확히 표시
3. **접근성**: 누구나 무료로 기본 기능 이용 가능
4. **품질**: 저품질 AI 출력물 필터링

---

## 4. 핵심 기능

### 4.1 기능 우선순위

#### MVP 기능 (Week 1-3)
- ✅ Google OAuth 로그인
- ✅ 사용자 MBTI 입력 (온보딩 + 마이페이지)
- ✅ 연애 대상자 커스터마이징 (성별, 스타일, MBTI, 그림체)
- ✅ 캐릭터 표정 사전 생성 (6종)
- ✅ MBTI 기반 대화 선택지 시스템
- ✅ 호감도 게이지
- ✅ AI 이미지 생성 (Gemini)
- ✅ 특별 이벤트 (서비스 컷 + blur/원본)
- ✅ 미니게임: 눈 마주치기 (로딩 중)
- ✅ HAPPY/SAD 엔딩 (2종)
- ✅ 세이브/로드 기능
- ✅ 마이페이지

### 4.2 상세 기능 명세

#### 4.2.1 사용자 인증
```
Feature: Google OAuth 로그인
As a 사용자
I want to Google 계정으로 로그인
So that 간편하게 게임을 시작할 수 있다

Acceptance Criteria:
- Google 버튼 클릭시 OAuth 팝업 열림
- 로그인 성공시 메인 화면 이동
- 세션 24시간 유지
- 로그아웃 기능 제공
```

#### 4.2.2 사용자 MBTI 설정
```
Feature: 사용자 MBTI 입력 및 관리
As a 사용자
I want to 내 MBTI를 입력하고 관리할
So that 내 성향에 맞는 선택지 스타일을 받을 수 있다

Flow:
1. 첫 로그인 시 MBTI 입력 (온보딩)
2. 마이페이지에서 언제든 수정 가능

MBTI 활용:
- AI가 선택지 생성 시 사용자 MBTI에 맞는 표현 스타일 적용
- 예: ENFP → 감정적/열정적 표현
- 예: ISTJ → 논리적/실용적 표현

Acceptance Criteria:
- 첫 로그인 시 MBTI 선택 화면 표시
- 16가지 MBTI 타입 선택 가능
- 마이페이지에서 수정 가능
- MBTI 미입력 시 기본값 적용
```

#### 4.2.3 연애 대상자 커스터마이징
```
Feature: 연애 대상자 설정
As a 사용자
I want to 연애 대상자의 특성을 직접 선택할
So that 원하는 이상형과 연애를 경험할 수 있다

커스터마이징 옵션:
1. 성별: 남성 / 여성
2. 스타일: 츤데레, 쿨뷰티, 귀여움, 섹시, 청순 등
3. MBTI: 16가지 타입
4. 그림체: 애니메이션, 실사풍, 수채화 등

DB 저장 및 활용:
- 선택한 설정을 DB에 저장
- AI API 호출마다 해당 정보를 전달하여 말투에 반영

Acceptance Criteria:
- 각 옵션별 선택 UI 제공
- 선택 완료 시 DB 저장
- AI 응답에 설정이 일관되게 반영
```

#### 4.2.4 캐릭터 표정 시스템
```
Feature: 기본 표정 이미지 사전 생성
As a 시스템
I want to 캐릭터 선택 완료 시 6가지 기본 표정을 미리 생성할
So that 게임 중 빠르게 표정을 전환할 수 있다

기본 표정 (6종):
1. 일반 표정 (neutral)
2. 기쁜 표정 (happy)
3. 슬픈 표정 (sad)
4. 질투 표정 (jealous)
5. 부끄러운 표정 (shy)
6. 흥분 표정 (excited)

Flow:
1. 사용자가 연애 대상자 설정 완료
2. AI API로 6개 표정 이미지 생성 요청
3. 생성된 이미지 DB에 저장
4. 게임 중 상황에 맞는 표정 선택하여 표시

Acceptance Criteria:
- 설정 완료 시 6개 이미지 비동기 생성
- 생성 중 로딩 UI 표시
- DB에 캐릭터별 표정 이미지 URL 저장
- 상황에 따라 적절한 표정 자동 선택
```

#### 4.2.5 호감도 시스템
```
Feature: 호감도 기반 게임 진행
As a 사용자
I want to 선택에 따라 호감도가 변동
So that 내 선택이 결과에 영향을 준다는 것을 느낄 수 있다

Mechanics:
- 초기 호감도: 랜덤 30-50
- 범위: 0-100
- 선택지당 변동: -10 ~ +10
- 시각화: 하트 5개 (20점당 1개)

Ending Conditions:
- 호감도 ≤ 10: 즉시 SAD 엔딩
- Scene 10 도달:
  - 호감도 ≥ 70: HAPPY 엔딩
  - 호감도 < 70: SAD 엔딩

Acceptance Criteria:
- 호감도 게이지 실시간 업데이트
- 변동량 애니메이션 (+5, -3 등)
- 엔딩 조건 정확히 트리거
```

#### 4.2.6 AI 이미지 생성
```
Feature: 상황별 배경 이미지 자동 생성
As a 사용자
I want to 각 씬마다 새로운 이미지를 볼
So that 몰입감 있는 경험을 할 수 있다

Technical Specs:
- API: Gemini Pro Vision
- 해상도: 1024x768
- 스타일: Anime visual novel
- 생성 시간: 5-10초
- 캐싱: 동일 프롬프트 재사용

Prompt Template:
"Anime-style illustration of a {character_type} girl in {scene_setting}.
Mood: {affection_mood}. High quality visual novel art style."

Acceptance Criteria:
- 씬당 1장 이미지 생성
- 로딩 중 Skeleton UI 표시
- 생성 실패시 기본 이미지 표시
- 캐시 히트시 1초 이내 로드
```

#### 4.2.7 대화 선택지 시스템
```
Feature: 3지선다 대화 선택
As a 사용자
I want to 3개의 선택지 중 하나를 고를
So that 내가 스토리를 통제한다고 느낄 수 있다

Selection Logic:
- 호감도 범위별 선택지 풀에서 랜덤 3개
- 각 선택지는 호감도 변동값 보유
- 선택 불가능하거나 시간 제한 없음

Choice Categories:
1. 긍정적 (+5 ~ +10): 칭찬, 관심, 공감
2. 중립적 (-2 ~ +2): 일상 대화
3. 부정적 (-5 ~ -10): 무관심, 실수

Acceptance Criteria:
- 선택지 3개 동시 표시
- 클릭시 즉시 다음 씬 이동
- 호감도 변동 애니메이션
- 선택 이력 DB 저장
```

#### 4.2.8 엔딩 시스템
```
Feature: HAPPY/SAD 엔딩 연출
As a 사용자
I want to 내 선택의 결과를 명확히 볼
So that 성취감 또는 재도전 의지를 느낄 수 있다

HAPPY Ending:
- 조건: Scene 10 & 호감도 ≥ 70
- 연출: 축하 애니메이션, 고백 씬
- CTA: "다시 시작", "공유하기"

SAD Ending:
- 조건: 호감도 ≤ 10 OR (Scene 10 & 호감도 < 70)
- 연출: 아쉬움 표현, 이별 씬
- CTA: "다시 도전", "피드백"

Acceptance Criteria:
- 엔딩 조건 정확히 판단
- 엔딩 영상/이미지 표시
- 최종 통계 표시 (총 씬, 최종 호감도)
- 다시 시작시 초기 화면 이동
```

#### 4.2.9 세이브/로드 기능
```
Feature: 게임 진행 상황 저장
As a 사용자
I want to 게임을 나갔다가 이어서 할
So that 한 번에 다 하지 않아도 된다

Save Logic:
- 자동 저장: 선택 직후
- 저장 위치: PostgreSQL + Redis 캐시
- 최대 슬롯: 3개

Load Logic:
- 게임 목록 카드 형태 표시
- 정보: 캐릭터, 진행도, 호감도, 날짜
- 클릭시 해당 상태로 복원

Acceptance Criteria:
- 선택 후 3초 이내 자동 저장
- 로드시 정확한 상태 복원
- 게임 삭제 기능 제공
```

#### 4.2.10 특별 이벤트 시스템
```
Feature: 랜덤 특별 이벤트 (서비스 컷)
As a 사용자
I want to 가끔 특별한 이벤트가 발생할
So that 게임에 더 몰입하고 기대감을 가질 수 있다

이벤트 발생:
- 매 턴마다 일정 확률 (예: 10-15%)로 특별 이벤트 발생
- 야한 서비스 컷 이미지 AI 생성

유료화 모델:
- 일반 고객: 서비스 컷 blur 처리 (흐리게)
- 결제 고객: 원본 이미지 전체 공개

이미지 생성:
- 특별 이벤트 발생 시 AI API로 서비스 컷 생성
- 생성 중 미니게임 표시 (로딩 대기)

Acceptance Criteria:
- 턴마다 랜덤 확률로 이벤트 트리거
- 이미지 생성 중 미니게임 표시
- 일반/결제 고객 구분하여 blur 처리
- 결제 상태 DB에서 확인
```

#### 4.2.11 미니게임: 눈 마주치기
```
Feature: 설레는 타이밍에 눈 마주치기 게임
As a 사용자
I want to 이미지 로딩 중 미니게임을 플레이할
So that 대기 시간이 지루하지 않고 보상도 받을 수 있다

게임 방식:
- 게이지가 좌우로 움직임
- 정확한 타이밍에 터치/클릭하여 "눈 마주치기"
- 정확도에 따라 등급 부여:
  - Perfect: 정중앙 (보너스 호감도 +3)
  - Great: 근접 (보너스 호감도 +1)
  - Miss: 실패 (보너스 없음)

UI 구성:
- 캐릭터 눈 이미지 중앙 배치
- 하트 모양 게이지 좌우 이동
- 터치 시 결과 애니메이션

Acceptance Criteria:
- 이미지 로딩 시 자동 시작
- 게이지 속도 조절 가능 (난이도)
- 결과에 따른 보너스 호감도 적용
- 로딩 완료 시 자동 종료 및 결과 표시
```

#### 4.2.12 마이페이지
```
Feature: 사용자 설정 관리
As a 사용자
I want to 내 정보와 설정을 관리할
So that 언제든 내 MBTI나 기타 설정을 변경할 수 있다

기능:
- MBTI 수정
- 결제 상태 확인
- 게임 통계 (플레이 횟수, 엔딩 달성률)
- 계정 설정 (로그아웃, 탈퇴)

Acceptance Criteria:
- MBTI 변경 즉시 반영
- 결제 상태 실시간 표시
- 통계 데이터 정확히 표시
```

### 4.3 사용자 플로우

```
┌─────────────┐
│  랜딩 페이지 │
└──────┬──────┘
       │ [시작하기]
       ▼
┌─────────────┐
│ Google 로그인│
└──────┬──────┘
       │
       ▼ (첫 로그인 시)
┌─────────────┐
│ MBTI 입력    │ ←── 온보딩
│ (16가지)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│ 게임 선택    │────▶│  새 게임     │
│ (메인 메뉴) │     │  이어하기    │
│             │     │  마이페이지  │
└──────┬──────┘     └──────┬───────┘
       │                    │
       │                    ▼ (새 게임)
       │          ┌──────────────────┐
       │          │ 연애 대상자 설정   │
       │          │ - 성별            │
       │          │ - 스타일          │
       │          │ - MBTI            │
       │          │ - 그림체          │
       │          └──────┬───────────┘
       │                 │
       │                 ▼
       │          ┌──────────────────┐
       │          │ 표정 이미지 생성   │
       │          │ (6종 사전 생성)   │
       │          │ + 미니게임 대기   │
       │          └──────┬───────────┘
       │                 │
       └─────────────────┤
                         ▼
                 ┌─────────────┐
                 │  게임 플레이 │◀─────────┐
                 │  - 표정 이미지│          │
                 │  - 대사      │          │
                 │  - 선택지    │          │
                 └──────┬──────┘          │
                        │                  │
                  [선택]│                  │
                        ▼                  │
                 ┌─────────────┐           │
                 │ 랜덤 확률    │           │
                 │ 특별 이벤트? │           │
                 └──────┬──────┘           │
                   YES  │  NO              │
            ┌───────────┴───────┐          │
            ▼                   │          │
     ┌─────────────┐            │          │
     │ 서비스 컷    │            │          │
     │ + 미니게임   │            │          │
     │ (blur/원본) │            │          │
     └──────┬──────┘            │          │
            └───────────────────┴──────────┘
                        │
                  [엔딩 조건]
                        │
                        ▼
                 ┌─────────────┐
                 │  엔딩 화면   │
                 │ HAPPY / SAD  │
                 └──────┬──────┘
                        │
                  [다시 시작]
                        │
                        ▼
                 메인 메뉴로 복귀
```

### 4.4 UI/UX 가이드라인

#### 디자인 원칙
1. **Simple & Clean**: 복잡한 UI 지양, 게임에 집중
2. **Mobile First**: 모바일 화면 우선 설계
3. **Fast Feedback**: 모든 액션에 즉각 피드백

#### 컬러 팔레트
```
Primary:   #FF6B9D (핑크 - 로맨틱)
Secondary: #C44569 (진한 핑크 - CTA)
Accent:    #FFC371 (오렌지 - 포인트)
BG:        #F8F9FA (밝은 회색)
Text:      #2C3E50 (다크 그레이)
```

#### 타이포그래피
- 헤더: Pretendard Bold, 24-32px
- 본문: Pretendard Regular, 16-18px
- 선택지: Pretendard Medium, 14-16px

#### 애니메이션
- 페이지 전환: Fade 300ms
- 호감도 변화: Scale + Color 500ms
- 선택지 hover: Lift 200ms

---

## 5. 기술 아키텍처

### 5.1 시스템 아키텍처

```
┌───────────────────────────────────────────────┐
│                  사용자                        │
└────────────┬──────────────────────────────────┘
             │
             ▼
┌───────────────────────────────────────────────┐
│            CDN (Vercel Edge)                   │
│         - Static Assets (이미지, CSS)         │
└────────────┬──────────────────────────────────┘
             │
             ▼
┌───────────────────────────────────────────────┐
│         Frontend (Next.js 14)                  │
│  - SSR/SSG (SEO 최적화)                       │
│  - NextAuth.js (OAuth)                        │
│  - Tailwind CSS + Framer Motion               │
│  Deploy: Vercel                                │
└────────────┬──────────────────────────────────┘
             │ HTTPS REST API
             ▼
┌───────────────────────────────────────────────┐
│         Backend (FastAPI)                      │
│  - Python 3.11                                 │
│  - Pydantic (데이터 검증)                      │
│  - SQLAlchemy (ORM)                            │
│  Deploy: Railway / Fly.io                      │
└────┬───────────────┬───────────────────┬──────┘
     │               │                   │
     ▼               ▼                   ▼
┌─────────┐   ┌──────────┐      ┌──────────────┐
│PostgreSQL│   │  Redis   │      │  Gemini API  │
│(Supabase)│   │(Upstash) │      │ (Google AI)  │
│          │   │          │      │              │
│- 게임    │   │- 세션    │      │- 이미지 생성 │
│- 사용자  │   │- 캐시    │      │- 텍스트 생성 │
└─────────┘   └──────────┘      └──────────────┘
```

### 5.2 데이터베이스 설계

> **상세 설계 문서**: `database-design.md` 참조  
> 여기서는 핵심 구조만 요약합니다.

#### Entity Relationship Diagram (ERD)

```
┌──────────────────────┐
│       users          │
│──────────────────────│
│ id (PK)              │
│ google_id            │
│ email                │
│ mbti                 │ ◀── 사용자 MBTI (16가지)
│ is_premium           │ ◀── 결제 상태
│ created_at           │
└──────┬───────────────┘
       │ 1
       │
       │ N
┌──────┴───────────────────┐
│    game_sessions         │
│──────────────────────────│
│ id (PK)                  │
│ user_id (FK)             │
│ affection                │
│ current_scene            │
│ status                   │
│ save_slot                │
│ created_at               │
└──────┬───────────────────┘
       │ 1
       │
       │ 1
┌──────┴───────────────────┐
│  character_settings      │ ◀── 연애 대상자 커스터마이징
│──────────────────────────│
│ id (PK)                  │
│ session_id (FK)          │
│ gender                   │ ◀── 성별 (male/female)
│ style                    │ ◀── 스타일 (tsundere, cool, cute 등)
│ mbti                     │ ◀── 캐릭터 MBTI
│ art_style                │ ◀── 그림체 (anime, realistic 등)
│ created_at               │
└──────┬───────────────────┘
       │ 1
       │
       │ N
┌──────┴───────────────────┐
│  character_expressions   │ ◀── 표정 이미지 (6종)
│──────────────────────────│
│ id (PK)                  │
│ setting_id (FK)          │
│ expression_type          │ ◀── neutral, happy, sad, jealous, shy, excited
│ image_url                │
│ created_at               │
└──────────────────────────┘

┌──────────────────────────┐
│       scenes             │
│──────────────────────────│
│ id (PK)                  │
│ session_id (FK)          │
│ scene_number             │
│ expression_type          │ ◀── 사용된 표정
│ dialogue_text            │
│ choices_offered (JSONB)  │
│ is_special_event         │ ◀── 특별 이벤트 여부
│ special_image_url        │ ◀── 서비스 컷 URL
│ created_at               │
└──────────────────────────┘

┌──────────────────────────┐
│   ai_generated_content   │
│──────────────────────────│
│ id (PK)                  │
│ prompt_hash (UNIQUE)     │
│ content_type             │ ◀── expression, special_event
│ content_data (JSONB)     │
│ cache_hit_count          │
│ created_at               │
└──────────────────────────┘

┌──────────────────────────┐
│    minigame_results      │ ◀── 미니게임 결과
│──────────────────────────│
│ id (PK)                  │
│ session_id (FK)          │
│ scene_number             │
│ result                   │ ◀── perfect, great, miss
│ bonus_affection          │
│ created_at               │
└──────────────────────────┘
```

#### 핵심 테이블 요약

| 테이블 | 용도 | 핵심 필드 |
|--------|------|-----------|
| **users** | 사용자 정보 | google_id, email, mbti, is_premium |
| **game_sessions** | 게임 진행 상태 | affection, current_scene, status, save_slot |
| **character_settings** | 연애 대상자 설정 | gender, style, mbti, art_style |
| **character_expressions** | 표정 이미지 (6종) | expression_type, image_url |
| **scenes** | 각 씬의 상세 정보 | expression_type, dialogue_text, is_special_event |
| **ai_generated_content** | AI 출력 캐싱 | prompt_hash, content_type, content_data |
| **minigame_results** | 미니게임 결과 | result, bonus_affection |

#### 주요 관계 (Relationships)

```sql
-- 1:N 관계
users ────── game_sessions (한 유저가 여러 게임 플레이)
game_sessions ────── scenes (한 게임에 여러 씬)

-- 1:1 관계
game_sessions ────── character_settings (한 게임에 하나의 캐릭터 설정)

-- 1:N 관계 (표정)
character_settings ────── character_expressions (한 설정에 6개 표정)

-- 미니게임
game_sessions ────── minigame_results (한 게임에 여러 미니게임 결과)
```

#### 인덱스 전략

```sql
-- 성능 최적화를 위한 주요 인덱스
CREATE INDEX idx_user_sessions ON game_sessions(user_id, status);
CREATE INDEX idx_active_sessions ON game_sessions(status) WHERE status = 'playing';
CREATE INDEX idx_scenes_lookup ON scenes(session_id, scene_number);
CREATE INDEX idx_ai_cache ON ai_generated_content(prompt_hash);
CREATE INDEX idx_expressions ON character_expressions(setting_id, expression_type);
CREATE INDEX idx_user_premium ON users(is_premium);
```

> **상세 스키마 및 샘플 데이터는 `database-design.md` 참조**

#### Redis Keys

```
# 세션 캐시
session:{session_id} = {game_state_json}
TTL: 3600초 (1시간)

# 이미지 캐시
image:{prompt_hash} = {image_url}
TTL: 86400초 (24시간)

# Rate Limit
rate_limit:{user_id}:gemini = {count}
TTL: 60초
```

### 5.3 API 엔드포인트

#### Authentication
```
POST /api/auth/google
- Request: { id_token: string }
- Response: { access_token: string, user: User }
```

#### Game Management
```
GET /api/games
- Auth: Required
- Response: { sessions: GameSession[] }

POST /api/games/new
- Auth: Required
- Request: { character_type: string }
- Response: { session: GameSession }

GET /api/games/{session_id}
- Auth: Required
- Response: { session: GameSession }

DELETE /api/games/{session_id}
- Auth: Required
- Response: { success: boolean }
```

#### Gameplay
```
POST /api/scenes/generate
- Auth: Required
- Request: { 
    session_id: UUID,
    scene_number: int,
    affection: int
  }
- Response: {
    image_url: string,
    dialogue: string,
    choices: [
      { text: string, delta: int }
    ]
  }

POST /api/choices/select
- Auth: Required
- Request: {
    session_id: UUID,
    choice_index: int,
    affection_delta: int
  }
- Response: {
    new_affection: int,
    next_scene: int,
    status: string  // 'continue' | 'happy_ending' | 'sad_ending'
  }
```

#### AI Integration (Internal)
```
POST /internal/gemini/generate-image
- Request: { prompt: string }
- Response: { image_url: string, cached: boolean }

POST /internal/gemini/generate-choices
- Request: { affection: int, scene: int, character: string }
- Response: { choices: Choice[] }
```

### 5.4 보안 고려사항

#### 인증 & 인가
- JWT 토큰 (24시간 만료)
- HttpOnly 쿠키로 저장
- CORS 설정: 프론트엔드 도메인만 허용

#### API Rate Limiting
```python
# FastAPI Middleware
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    user_id = get_user_from_token(request)
    key = f"rate_limit:{user_id}"
    
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 60)
    
    if count > 100:  # 분당 100회
        return JSONResponse(
            status_code=429,
            content={"error": "Too many requests"}
        )
    
    return await call_next(request)
```

#### 데이터 보호
- 환경변수로 API 키 관리
- Gemini API 키는 백엔드에서만 사용
- 민감 정보 암호화 (AES-256)

---

## 7. 로드맵

### 7.1 개발 로드맵 (3주 MVP)

#### Week 1 (Day 1-7)
| Day | Tasks | 목표 |
|-----|-------|------|
| 1-2 | 인증 시스템 (Google OAuth) | 로그인 완료 |
| 3-4 | 게임 로직 (호감도 시스템) | 코어 메커니즘 완료 |
| 5-6 | DB 설정 + 기본 UI | 데이터 저장 가능 |
| 7 | 통합 테스트 | Week 1 데모 |

#### Week 2 (Day 8-14)
| Day | Tasks | 목표 |
|-----|-------|------|
| 8-9 | Gemini 이미지 생성 통합 | AI 기능 동작 |
| 10-11 | 캐싱 + 호감도 UI | 성능 최적화 |
| 12-13 | 엔딩 화면 구현 | 게임 완결 가능 |
| 14 | 통합 테스트 | 전체 플레이 가능 |

#### Week 3 (Day 15-21)
| Day | Tasks | 목표 |
|-----|-------|------|
| 15-16 | 세이브/로드 기능 | 이어하기 완료 |
| 17-18 | 배포 (Vercel + Railway) | 프로덕션 배포 |
| 19-20 | 최적화 및 버그 수정 | 안정화 |
| 21 | 최종 테스트 & 출시 | 🎉 **MVP 런칭** |

---

## 8. 성공 지표 (KPI)

### 8.1 핵심 게임 플레이 지표

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| **게임 완료율** | 60% | 시작 → 엔딩 도달 비율 |
| **평균 세션 시간** | 15분 | 게임 플레이 시간 |
| **HAPPY 엔딩 비율** | 40% | 전체 엔딩 중 비율 |
| **재플레이율** | 50% | 7일 내 재방문 |
| **평균 호감도** | 55 | 게임 종료 시점 평균 |

### 8.2 기술 성능 지표

| 지표 | 목표 | 중요도 |
|------|------|--------|
| **이미지 생성 시간** | 10초 이내 | ⭐⭐⭐ |
| **API 응답 시간** | 500ms 이내 | ⭐⭐⭐ |
| **캐시 히트율** | 70% 이상 | ⭐⭐ |
| **에러율** | 1% 미만 | ⭐⭐⭐ |

---

## 9. 리스크 관리

### 9.1 기술적 리스크

#### 리스크 1: Gemini API 성능 이슈
**확률**: 🟡 Medium  
**영향도**: 🔴 High

**완화 전략**:
- ✅ 이미지 캐싱 (Redis)
- ✅ Fallback 기본 이미지 준비
- ✅ 로딩 상태 UX 개선
- ✅ 대체 API 조사 (DALL-E, Stable Diffusion)

#### 리스크 2: 확장성 문제
**확률**: 🟡 Medium  
**영향도**: 🟡 Medium

**완화 전략**:
- ✅ 수평 확장 가능 아키텍처
- ✅ DB 인덱싱 최적화
- ✅ CDN 활용
- ✅ 모니터링 (Sentry)

### 9.2 법적/윤리적 리스크

#### 리스크 3: AI 윤리 이슈
**확률**: 🟡 Medium  
**영향도**: 🔴 High

**완화 전략**:
- ✅ 명확한 AI 라벨링
- ✅ 유해 콘텐츠 필터링
- ✅ 과몰입 방지 (게임 시간 표시)
- ✅ 이용 약관 명시

#### 리스크 4: 저작권 문제
**확률**: 🟢 Low  
**영향도**: 🟡 Medium

**완화 전략**:
- ✅ Gemini API 이용 약관 준수
- ✅ 모든 생성 이미지에 워터마크
- ✅ 사용자 업로드 금지

---

## 10. 결론

### 10.1 Why Now?
- ✅ 생성형 AI 기술 성숙 (Gemini, GPT-4)
- ✅ 연애 시뮬레이션 장르 꾸준한 수요
- ✅ 경쟁사 부재 (AI + 게임 융합)

### 10.2 핵심 차별점
1. **AI 기반 무한 콘텐츠**: 정해진 시나리오 없음
2. **실시간 이미지 생성**: 몰입감 극대화
3. **빠른 출시**: 3주 MVP, 낮은 개발 비용
4. **확장 가능**: 캐릭터/엔딩 쉽게 추가

### 10.3 Next Steps
1. ✅ 기술 스택 확정 (완료)
2. ⏳ Week 1 스프린트 시작
3. ⏳ 데이터베이스 스키마 적용
4. ⏳ Google OAuth 설정

---

**문서 버전**: 1.0  
**최종 업데이트**: 2026-01-14  
**작성자**: JangYeol Lee

_이 문서는 프로젝트 진행에 따라 지속적으로 업데이트됩니다._
