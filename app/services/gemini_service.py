"""
Gemini API Service
캐릭터 성격과 사용자 MBTI를 반영한 대화 및 선택지 생성
"""

import hashlib
import json
import google.generativeai as genai
from app.core.config import settings

# Gemini API 설정
genai.configure(api_key=settings.GEMINI_API_KEY)

# 6가지 표정 타입
EXPRESSION_TYPES = [
    "neutral",   # 일반
    "happy",     # 기쁜
    "sad",       # 슬픈
    "jealous",   # 질투
    "shy",       # 부끄러운
    "excited",   # 흥분
]


def build_expression_prompt(
    gender: str,
    style: str,
    art_style: str,
    expression: str,
) -> str:
    """캐릭터 설정 기반 표정 이미지 생성 프롬프트 생성."""
    style_descriptions = {
        "tsundere": "with a tsundere personality, initially cold but secretly caring",
        "cool": "with a cool and calm demeanor, mysterious and composed",
        "cute": "with a cute and cheerful personality, bright and adorable",
        "sexy": "with an elegant and attractive appearance, confident and alluring",
        "pure": "with an innocent and pure personality, gentle and sincere",
    }

    expression_descriptions = {
        "neutral": "with a neutral, calm expression",
        "happy": "with a happy, joyful smile",
        "sad": "with a sad, melancholic expression",
        "jealous": "with a jealous, slightly annoyed look",
        "shy": "with a shy, blushing expression",
        "excited": "with an excited, enthusiastic expression",
    }

    art_style_descriptions = {
        "anime": "in anime art style, vibrant colors, clean lines",
        "realistic": "in realistic art style, detailed and lifelike",
        "watercolor": "in watercolor art style, soft and dreamy",
    }

    style_desc = style_descriptions.get(style, style_descriptions["cute"])
    expression_desc = expression_descriptions.get(expression, expression_descriptions["neutral"])
    art_desc = art_style_descriptions.get(art_style, art_style_descriptions["anime"])

    prompt = f"""A portrait of a {gender} character {style_desc}, {expression_desc}, {art_desc}.
High quality, detailed, suitable for a dating simulation game.
Upper body shot, looking at the viewer, soft lighting."""

    return prompt


# 캐릭터 스타일 설명 (한국어)
STYLE_DESCRIPTIONS_KR = {
    "tsundere": "츤데레 성격으로, 겉으로는 차갑지만 속으로는 따뜻한",
    "cool": "쿨하고 차분한 성격으로, 신비롭고 침착한",
    "cute": "귀엽고 발랄한 성격으로, 밝고 사랑스러운",
    "sexy": "우아하고 매력적인 성격으로, 자신감 넘치는",
    "pure": "순수하고 청순한 성격으로, 온화하고 진실된",
}

# MBTI별 선택지 스타일
MBTI_CHOICE_STYLES = {
    # 분석형 (NT)
    "INTJ": "논리적이고 전략적인 표현, 직접적이고 효율적인",
    "INTP": "호기심 어린 질문, 분석적이고 탐구적인",
    "ENTJ": "자신감 있고 리더십 있는, 결단력 있는",
    "ENTP": "재치있고 도전적인, 창의적인 아이디어",
    # 외교형 (NF)
    "INFJ": "깊이 있고 의미 있는, 공감적이고 통찰력 있는",
    "INFP": "진심 어린 감정 표현, 이상적이고 낭만적인",
    "ENFJ": "따뜻하고 격려하는, 사람을 이끄는",
    "ENFP": "열정적이고 긍정적인, 상상력이 풍부한",
    # 관리자형 (SJ)
    "ISTJ": "신중하고 책임감 있는, 실용적인",
    "ISFJ": "배려하고 헌신적인, 따뜻한 보살핌",
    "ESTJ": "솔직하고 조직적인, 실행력 있는",
    "ESFJ": "사교적이고 협력적인, 조화를 추구하는",
    # 탐험가형 (SP)
    "ISTP": "간결하고 실용적인, 문제 해결 중심의",
    "ISFP": "부드럽고 예술적인, 감각적인 표현",
    "ESTP": "대담하고 직접적인, 행동 지향적인",
    "ESFP": "재미있고 활발한, 즉흥적이고 유쾌한",
}


async def generate_scene_content(
    character_setting,
    user_mbti: str | None,
    scene_number: int,
    affection: int,
) -> dict:
    """
    Gemini API를 사용하여 씬 콘텐츠 생성 (대화 + 선택지)

    Args:
        character_setting: CharacterSetting 모델 (gender, style, mbti, art_style)
        user_mbti: 사용자의 MBTI
        scene_number: 현재 씬 번호 (턴 카운트)
        affection: 현재 호감도 (0-100)
    """
    # 캐릭터 정보
    char_gender = character_setting.gender if character_setting else "female"
    char_style = character_setting.style if character_setting else "cute"
    char_mbti = character_setting.mbti if character_setting else "ENFP"

    # 스타일 설명
    style_desc = STYLE_DESCRIPTIONS_KR.get(char_style, STYLE_DESCRIPTIONS_KR["cute"])

    # 사용자 MBTI 스타일
    user_style = MBTI_CHOICE_STYLES.get(user_mbti, "자연스럽고 편안한") if user_mbti else "자연스럽고 편안한"

    # 호감도에 따른 분위기
    if affection >= 70:
        mood = "매우 호감을 느끼며 적극적으로 다가오는"
    elif affection >= 50:
        mood = "관심을 보이며 친근하게 대하는"
    elif affection >= 30:
        mood = "아직 경계하지만 조금씩 마음을 여는"
    else:
        mood = "거리감을 두며 조심스러워하는"

    # Gemini 프롬프트 생성
    prompt = f"""당신은 연애 시뮬레이션 게임의 시나리오 작가입니다.

## 캐릭터 정보
- 성별: {"여성" if char_gender == "female" else "남성"}
- 성격: {style_desc}
- MBTI: {char_mbti}
- 현재 호감도: {affection}/100
- 현재 분위기: {mood}

## 사용자 정보
- MBTI: {user_mbti or "알 수 없음"}
- 선택지 스타일: {user_style}

## 요청
1. 캐릭터가 사용자에게 하는 대사를 1-2문장으로 작성해주세요.
2. 사용자가 선택할 수 있는 3개의 선택지를 작성해주세요.

## 선택지 규칙
- 각 선택지는 사용자의 MBTI 성향({user_style})을 반영해야 합니다.
- 첫 번째 선택지: 호감도를 올리는 긍정적 선택 (delta: +5 ~ +15)
- 두 번째 선택지: 중립적 선택 (delta: -2 ~ +5)
- 세 번째 선택지: 호감도를 낮추는 부정적 선택 (delta: -15 ~ -5)

## 출력 형식 (JSON)
{{
  "dialogue": "캐릭터의 대사",
  "choices": [
    {{"text": "선택지1 텍스트", "delta": 숫자}},
    {{"text": "선택지2 텍스트", "delta": 숫자}},
    {{"text": "선택지3 텍스트", "delta": 숫자}}
  ]
}}

JSON만 출력하세요. 다른 설명은 필요 없습니다."""

    try:
        # Gemini API 호출
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)

        # 응답 파싱
        response_text = response.text.strip()

        # JSON 추출 (```json ... ``` 형식일 수 있음)
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            json_lines = []
            in_json = False
            for line in lines:
                if line.startswith("```json"):
                    in_json = True
                    continue
                elif line.startswith("```"):
                    in_json = False
                    continue
                if in_json:
                    json_lines.append(line)
            response_text = "\n".join(json_lines)

        content = json.loads(response_text)

        # 이미지 URL (placeholder - 실제로는 Gemini Imagen 사용)
        image_url = f"https://placehold.co/1024x768/FFB6C1/333333?text=Turn+{scene_number}"

        return {
            "image_url": image_url,
            "dialogue": content.get("dialogue", "안녕하세요!"),
            "choices": content.get("choices", [
                {"text": "반갑게 인사한다", "delta": 10},
                {"text": "고개를 끄덕인다", "delta": 2},
                {"text": "무시한다", "delta": -10},
            ]),
        }

    except Exception as e:
        print(f"Gemini API error: {e}")
        # 폴백: 기본 템플릿 사용
        return _get_fallback_content(char_style, scene_number, affection)


def _get_fallback_content(style: str, scene_number: int, affection: int) -> dict:
    """Gemini API 실패 시 폴백 콘텐츠"""

    dialogues = {
        "tsundere": [
            "뭐야, 왜 나를 쳐다보는 거야... 딴 데 봐!",
            "오늘따라 왜 이렇게 신경 쓰이지... 아무것도 아니야!",
        ],
        "cool": [
            "오늘 만남이 예정되어 있었군요.",
            "흥미롭네요. 당신의 선택이 궁금합니다.",
        ],
        "cute": [
            "안녕~! 오늘도 만나서 너무 기뻐!",
            "우와~ 정말요? 너무 좋아요!",
        ],
        "sexy": [
            "어머, 왔구나? 기다리고 있었어.",
            "오늘 뭔가 특별한 일이 있을 것 같은 기분이야.",
        ],
        "pure": [
            "안녕하세요! 오늘도 좋은 하루 되세요.",
            "저... 같이 있으면 마음이 편해요.",
        ],
    }

    import random
    dialogue = random.choice(dialogues.get(style, dialogues["cute"]))

    return {
        "image_url": f"https://placehold.co/1024x768/FFB6C1/333333?text=Turn+{scene_number}",
        "dialogue": dialogue,
        "choices": [
            {"text": "따뜻하게 웃어준다", "delta": 10},
            {"text": "고개를 끄덕인다", "delta": 2},
            {"text": "다른 곳을 본다", "delta": -8},
        ],
    }


def get_prompt_hash(prompt: str) -> str:
    """프롬프트 해시 생성 (캐싱용)"""
    return hashlib.sha256(prompt.encode()).hexdigest()
