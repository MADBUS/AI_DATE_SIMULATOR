import hashlib
import random
from app.core.config import settings

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
    """
    캐릭터 설정 기반 표정 이미지 생성 프롬프트 생성.

    Args:
        gender: 'male' or 'female'
        style: 'tsundere', 'cool', 'cute', 'sexy', 'pure'
        art_style: 'anime', 'realistic', 'watercolor'
        expression: one of EXPRESSION_TYPES

    Returns:
        Gemini API용 이미지 생성 프롬프트
    """
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


# Placeholder 이미지 URL (실제로는 Gemini API 사용)
PLACEHOLDER_IMAGES = [
    "https://placehold.co/1024x768/FFB6C1/333333?text=Scene+1",
    "https://placehold.co/1024x768/DDA0DD/333333?text=Scene+2",
    "https://placehold.co/1024x768/E6E6FA/333333?text=Scene+3",
]

# 캐릭터별 대화 템플릿
DIALOGUE_TEMPLATES = {
    "tsundere": [
        "뭐야, 왜 나를 쳐다보는 거야... 딴 데 봐!",
        "오늘따라 왜 이렇게 신경 쓰이지... 아무것도 아니야!",
        "네가 와줘서... 아, 아무것도 아니라고!",
        "흥, 별로 기쁘지 않거든... (살짝 미소)",
        "다음에도... 와줄 거지? 아, 그냥 물어본 거야!",
    ],
    "cool": [
        "오늘 만남이 예정되어 있었군요.",
        "흥미롭네요. 당신의 선택이 궁금합니다.",
        "감정이라는 건 복잡한 것 같아요.",
        "논리적으로 생각해보면... 당신과의 시간이 좋습니다.",
        "이런 감정은 처음이에요. 분석이 필요할 것 같네요.",
    ],
    "cute": [
        "안녕~! 오늘도 만나서 너무 기뻐!",
        "우와~ 정말요? 너무 좋아요!",
        "헤헤, 같이 있으면 행복해요~",
        "오늘 뭐 할까요? 저는 뭐든 좋아요!",
        "또 만날 수 있어서 정말 다행이에요~!",
    ],
}

# 선택지 템플릿
CHOICE_TEMPLATES = {
    "positive": [
        {"text": "따뜻하게 웃어준다", "delta": 8},
        {"text": "칭찬해준다", "delta": 7},
        {"text": "손을 잡아준다", "delta": 10},
        {"text": "맛있는 걸 사준다", "delta": 6},
    ],
    "neutral": [
        {"text": "고개를 끄덕인다", "delta": 2},
        {"text": "이야기를 들어준다", "delta": 3},
        {"text": "같이 걷는다", "delta": 1},
        {"text": "날씨 이야기를 한다", "delta": 0},
    ],
    "negative": [
        {"text": "스마트폰을 확인한다", "delta": -5},
        {"text": "다른 곳을 본다", "delta": -4},
        {"text": "하품을 한다", "delta": -7},
        {"text": "시간을 확인한다", "delta": -3},
    ],
}


async def generate_scene_content(
    character, scene_number: int, affection: int
) -> dict:
    """씬 콘텐츠 생성 (이미지 + 대화 + 선택지)"""

    # 이미지 생성 (Placeholder)
    # TODO: 실제 Gemini API 연동
    image_url = random.choice(PLACEHOLDER_IMAGES)

    # 대화 생성
    dialogues = DIALOGUE_TEMPLATES.get(character.type, DIALOGUE_TEMPLATES["cute"])
    dialogue = random.choice(dialogues)

    # 선택지 생성
    choices = []
    choices.append(random.choice(CHOICE_TEMPLATES["positive"]))
    choices.append(random.choice(CHOICE_TEMPLATES["neutral"]))
    choices.append(random.choice(CHOICE_TEMPLATES["negative"]))
    random.shuffle(choices)

    return {
        "image_url": image_url,
        "dialogue": dialogue,
        "choices": choices,
    }


def get_prompt_hash(prompt: str) -> str:
    """프롬프트 해시 생성 (캐싱용)"""
    return hashlib.sha256(prompt.encode()).hexdigest()
