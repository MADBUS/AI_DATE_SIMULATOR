"""
Gemini API Service
캐릭터 성격과 사용자 MBTI를 반영한 대화 및 선택지 생성
이미지 생성 (Imagen 3)
"""

import hashlib
import json
import os
import uuid
from pathlib import Path

from google import genai
from google.genai import types

from app.core.config import settings

# Gemini API 클라이언트 설정
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# 이미지 저장 경로
IMAGES_DIR = Path(__file__).parent.parent.parent / "static" / "images" / "characters"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# 7가지 표정 타입
EXPRESSION_TYPES = [
    "neutral",   # 일반
    "happy",     # 기쁜
    "sad",       # 슬픈
    "jealous",   # 질투
    "shy",       # 부끄러운
    "excited",   # 설렘
    "disgusted", # 극혐
]


def get_character_design(gender: str, style: str) -> dict:
    """
    캐릭터 성격과 성별에 따른 일관된 외모 디자인 반환.
    동일한 gender+style 조합은 항상 같은 외모를 가짐.
    """
    # 성격별 캐릭터 디자인 (성별에 따라 다름) - 동양인 특징 포함
    designs = {
        "female": {
            "tsundere": {
                "hair": "beautiful long twin-tails hairstyle, vibrant crimson red hair with subtle pink gradient highlights, silky shiny straight Asian hair texture, cute hair ribbons",
                "eyes": "sharp expressive amber-gold Asian eyes with monolid or subtle double eyelid, long eyelashes, fierce yet attractive gaze",
                "outfit": "stylish Korean/Japanese school uniform with red ribbon tie, crisp white blouse, fitted blazer, fashionable accessories",
                "features": "flawless porcelain white skin, delicate small Asian nose, soft facial structure, perfectly shaped pink lips, slim petite figure, elegant neck, beautiful East Asian facial features",
            },
            "cool": {
                "hair": "gorgeous long straight jet-black hair flowing past shoulders, elegant side-swept bangs framing face, lustrous silky Asian hair shine",
                "eyes": "mesmerizing deep dark brown eyes with mysterious allure, elegant Asian eye shape, sharp elegant gaze, thick dark lashes",
                "outfit": "sophisticated dark navy blazer over elegant blouse, minimalist silver necklace, refined K-fashion style",
                "features": "flawless pale luminous Korean-style skin, refined elegant East Asian features, graceful long neck, sophisticated beauty, slim elegant proportions",
            },
            "cute": {
                "hair": "adorable short fluffy dark brown hair with cute decorative hair clips and accessories, soft bouncy texture, playful Korean idol style",
                "eyes": "large sparkling dark brown eyes full of life, innocent doe-eyed look with aegyo-sal, cute Asian eye shape",
                "outfit": "lovely pastel pink sweater with cute heart patterns, adorable K-fashion accessories, sweet feminine style",
                "features": "soft round baby face with East Asian features, naturally rosy cheeks, cute small Asian nose, sweet pink lips, petite adorable figure, youthful Korean ulzzang glow",
            },
            "sexy": {
                "hair": "luxurious long wavy dark brown hair cascading elegantly, glamorous soft waves, silky lustrous Asian hair shine",
                "eyes": "captivating deep dark brown eyes with sultry allure, elegant Asian eye shape, thick long lashes, seductive confident gaze",
                "outfit": "elegant off-shoulder evening dress, tasteful gold jewelry, sophisticated glamorous style",
                "features": "flawless radiant Korean glass skin, alluring beauty mark near lips, elegant mature East Asian features, graceful feminine figure, stunning Asian beauty",
            },
            "pure": {
                "hair": "lovely medium-length natural black hair with gentle natural waves, healthy beautiful shine, soft Asian hair texture",
                "eyes": "innocent clear dark brown eyes with gentle warmth, soft kind gaze, natural Asian eye shape with subtle aegyo-sal",
                "outfit": "beautiful simple white sundress with delicate lace details, subtle elegant accessories, pure feminine style",
                "features": "naturally beautiful clear Korean-style skin, soft gentle East Asian features, sweet natural smile, graceful slim figure, wholesome natural Asian beauty",
            },
        },
        "male": {
            "tsundere": {
                "hair": "stylishly messy dark brown hair with natural texture, attractive tousled K-pop idol look, slight layered styling",
                "eyes": "intense sharp dark brown Asian eyes with passionate gaze, strong defined brows, attractive monolid or double eyelid",
                "outfit": "casually stylish Korean school uniform with loose tie, partially unbuttoned collar, effortlessly cool K-drama look",
                "features": "handsome sharp jawline with East Asian bone structure, attractive features, clear healthy fair skin, athletic lean build, brooding handsome Korean actor look",
            },
            "cool": {
                "hair": "elegantly styled dark ash brown hair swept back, sophisticated modern Korean hairstyle, striking color",
                "eyes": "piercing cool dark brown eyes with mysterious depth, intense captivating Asian gaze",
                "outfit": "sleek black turtleneck sweater, minimalist silver earring, refined modern K-fashion style",
                "features": "sharp handsome East Asian features, pale flawless skin, tall elegant build, enigmatic charisma, Korean model-like bone structure",
            },
            "cute": {
                "hair": "soft fluffy dark brown hair with gentle natural texture, warm highlights, boyish charming K-pop style",
                "eyes": "warm bright dark brown eyes full of kindness, friendly gentle gaze, soft Asian eye features",
                "outfit": "cozy casual cream-colored hoodie with simple design, comfortable Korean streetwear style",
                "features": "soft handsome East Asian features, warm healthy fair skin tone, friendly charming smile, lean build, Korean boy-next-door appeal",
            },
            "sexy": {
                "hair": "perfectly styled dark black hair with modern two-block cut, sleek and sophisticated, naturally attractive Korean style",
                "eyes": "intense smoldering dark eyes with confident allure, strong masculine Asian gaze",
                "outfit": "fitted dark dress shirt with top buttons undone, revealing elegant collarbone, refined masculine K-drama style",
                "features": "strong defined jawline with East Asian bone structure, confident attractive smirk, athletic toned build, healthy fair skin, devastatingly handsome Korean actor look",
            },
            "pure": {
                "hair": "neatly styled soft black hair with gentle texture, clean classic Korean hairstyle, well-groomed appearance",
                "eyes": "warm gentle dark brown eyes full of sincerity, kind trustworthy gaze, soft Asian eye shape",
                "outfit": "clean crisp white button-up shirt, simple elegant style, neat well-put-together appearance",
                "features": "gentle handsome East Asian features, clear healthy fair skin, warm genuine smile, lean fit build, honest trustworthy Korean appearance",
            },
        },
    }

    gender_key = "female" if gender == "female" else "male"
    return designs.get(gender_key, designs["female"]).get(style, designs[gender_key]["cute"])


def build_expression_prompt(
    gender: str,
    style: str,
    art_style: str,
    expression: str,
) -> str:
    """캐릭터 설정 기반 표정 이미지 생성 프롬프트 생성."""

    # 캐릭터 고정 디자인 가져오기
    design = get_character_design(gender, style)

    # 표정별 상세 설명
    expression_details = {
        "neutral": {
            "face": "serene calm expression with soft natural gentle smile, relaxed facial muscles, approachable friendly demeanor",
            "mood": "peaceful, content, warmly approachable, quietly confident",
            "eyes": "looking directly at viewer with soft gentle gaze, warm and inviting eye contact, relaxed eyelids",
        },
        "happy": {
            "face": "radiant genuine bright smile showing pure joy, raised cheeks creating beautiful smile lines, glowing happy expression",
            "mood": "overflowing with joy, warmth and delight, infectious happiness, cheerful energy",
            "eyes": "sparkling brilliantly with happiness, eyes slightly crescent-shaped from genuine smiling, joyful eye smile",
        },
        "sad": {
            "face": "tender melancholic expression, slightly downturned lips, vulnerable beautiful sadness, emotional depth",
            "mood": "gentle melancholy, touching vulnerability, bittersweet emotion, poignant beauty",
            "eyes": "glistening with unshed tears, deep sorrowful gaze looking slightly downward, emotional depth in eyes",
        },
        "jealous": {
            "face": "adorable pouty expression, slightly puffed cheeks, furrowed brows, cute frustrated look",
            "mood": "endearingly jealous, playfully annoyed, possessive affection, tsundere energy",
            "eyes": "narrowed with cute irritation, looking away with mock annoyance, jealous sidelong glance",
        },
        "shy": {
            "face": "beautifully flushed pink cheeks, adorable bashful smile, head tilted slightly, charmingly flustered",
            "mood": "sweetly embarrassed, heart-fluttering nervousness, endearing shyness, innocent charm",
            "eyes": "shyly avoiding direct eye contact, glancing through lashes, coy bashful look with pink tinted cheeks",
        },
        "excited": {
            "face": "flushed pink cheeks with excited smile, heart-fluttering anticipation, slightly parted lips from excitement, lovingly flustered expression",
            "mood": "butterflies in stomach feeling, romantic excitement mixed with shyness, heart pounding anticipation, lovestruck and slightly embarrassed",
            "eyes": "sparkling eyes filled with adoration and nervous excitement, shy but eager gaze, eyes shimmering with romantic anticipation, looking at viewer with loving expectation",
        },
        "disgusted": {
            "face": "extremely displeased expression, wrinkled nose showing disgust, lips curled in revulsion, face turned slightly away",
            "mood": "utterly repulsed, strongly disapproving, wanting to get away, feeling offended and grossed out",
            "eyes": "eyes narrowed with intense displeasure, looking away with disgust, eyebrows furrowed in strong disapproval, cold rejecting gaze",
        },
    }

    # 그림체별 상세 설명
    art_style_details = {
        "anime": {
            "style": "modern Japanese anime art style, visual novel CG quality, anime key visual",
            "rendering": "cel-shaded coloring with clean precise outlines, flat color areas with soft airbrush shading, vibrant saturated colors, anime-style gradient shading",
            "details": "large sparkling anime eyes with detailed highlights and reflections, stylized small nose and mouth, anime facial proportions, perfectly smooth flawless skin, detailed shiny hair with individual strands",
            "quality": "masterpiece quality anime illustration, trending on Pixiv, professional Japanese game CG, detailed anime art, 8k resolution",
            "avoid": "DO NOT use: realistic proportions, photorealistic rendering, western cartoon style, 3D render look",
        },
        "realistic": {
            "style": "photorealistic portrait photography style, hyperrealistic digital art, lifelike human portrait",
            "rendering": "photorealistic skin rendering with subsurface scattering, natural soft studio lighting, realistic shadows and highlights, cinematic color grading, depth of field",
            "details": "realistic human facial proportions, natural skin texture with pores, realistic eye anatomy with detailed iris, natural lip texture, realistic hair with individual strands and natural shine",
            "quality": "8k ultra HD, professional photography quality, shot on Canon EOS R5, 85mm portrait lens, magazine cover quality, hyperdetailed, trending on ArtStation",
            "avoid": "DO NOT use: anime style, cartoon style, cel-shading, stylized features, large unrealistic eyes, flat coloring",
        },
        "watercolor": {
            "style": "traditional watercolor painting on textured paper, fine art watercolor illustration, romantic watercolor portrait",
            "rendering": "visible watercolor brush strokes, wet-on-wet technique, soft color bleeding at edges, transparent layered washes, granulation texture, paper texture visible",
            "details": "soft dreamy features, gentle color transitions, artistic color choices, delicate facial features, ethereal glow, loose artistic hair rendering",
            "quality": "museum quality watercolor painting, professional traditional art, award-winning watercolor illustration, beautiful fine art piece",
            "avoid": "DO NOT use: digital art look, sharp edges, cel-shading, anime style, photorealistic rendering",
        },
    }

    expr = expression_details.get(expression, expression_details["neutral"])
    art = art_style_details.get(art_style, art_style_details["anime"])

    # 성별 표현 (동양인 명시)
    gender_word = "young East Asian woman, Korean or Japanese" if gender == "female" else "young East Asian man, Korean or Japanese"

    # avoid 항목 가져오기
    avoid_text = art.get('avoid', '')

    prompt = f"""Create a beautiful {art['style']} portrait.

SUBJECT: An attractive {gender_word} with the following features:
- Ethnicity: MUST be East Asian (Korean, Japanese, or Chinese) - this is mandatory
- Hair: {design['hair']}
- Eyes: {design['eyes']}
- Outfit: {design['outfit']}
- Physical features: {design['features']}

CRITICAL ETHNICITY REQUIREMENT:
- The character MUST have distinctly East Asian facial features
- Korean/Japanese/Chinese appearance with appropriate bone structure
- Asian eye shape (monolid or subtle double eyelid)
- Fair to light skin tone typical of East Asians
- DO NOT create Western/Caucasian features

EXPRESSION AND EMOTION:
- Face: {expr['face']}
- Overall mood: {expr['mood']}
- Eyes showing: {expr['eyes']}

MANDATORY ART STYLE REQUIREMENTS:
{art['style']}
{art['rendering']}
{art['details']}
{art['quality']}

COMPOSITION AND LIGHTING:
- Upper body portrait, chest-up framing
- Character looking at the viewer
- Beautiful soft lighting that enhances the {art_style} aesthetic
- Aesthetically pleasing gradient background (soft pink, lavender, or warm tones)
- Perfect composition, visually stunning

IMPORTANT - MUST AVOID:
{avoid_text}
DO NOT include: Western/Caucasian features, text, watermarks, signatures, multiple people, extra limbs, deformed features, bad anatomy, ugly, blurry, low quality"""

    return prompt


async def generate_character_image(
    gender: str,
    style: str,
    art_style: str,
    expression: str,
) -> str:
    """
    Gemini API를 사용하여 캐릭터 이미지 생성

    Args:
        gender: 캐릭터 성별 (male/female)
        style: 캐릭터 성격 (tsundere/cool/cute/sexy/pure)
        art_style: 그림체 (anime/realistic/watercolor)
        expression: 표정 (neutral/happy/sad/jealous/shy/excited)

    Returns:
        생성된 이미지의 URL
    """
    prompt = build_expression_prompt(gender, style, art_style, expression)

    # Imagen 4.0 모델 사용
    models_to_try = [
        'imagen-4.0-generate-001',
        'imagen-4.0-fast-generate-001',
    ]

    for model_name in models_to_try:
        try:
            print(f"Trying image generation with model: {model_name}")
            response = client.models.generate_images(
                model=model_name,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                ),
            )

            if response.generated_images and len(response.generated_images) > 0:
                image_id = str(uuid.uuid4())
                image_filename = f"{image_id}.png"
                image_path = IMAGES_DIR / image_filename

                # 이미지 데이터 가져오기
                generated_image = response.generated_images[0]
                if hasattr(generated_image, 'image') and generated_image.image:
                    image_bytes = generated_image.image.image_bytes
                    if image_bytes and len(image_bytes) > 100:
                        with open(image_path, 'wb') as f:
                            f.write(image_bytes)
                        print(f"Image generated successfully with {model_name}, size: {len(image_bytes)} bytes")
                        return f"/static/images/characters/{image_filename}"
                    else:
                        print(f"Image data too small: {len(image_bytes) if image_bytes else 0} bytes")
                else:
                    print(f"No image data in response from {model_name}")
            else:
                print(f"No generated_images in response from {model_name}")

        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue

    # 모든 모델 실패 시 placeholder 반환
    print(f"All image generation models failed, using placeholder")
    return _get_placeholder_url(expression, gender, style)


def _get_placeholder_url(expression: str, gender: str, style: str) -> str:
    """이미지 생성 실패 시 placeholder URL 반환"""
    colors = {
        "neutral": "B0C4DE",
        "happy": "FFD700",
        "sad": "87CEEB",
        "jealous": "FF6B6B",
        "shy": "FFB6C1",
        "excited": "FF69B4",
        "disgusted": "556B2F",  # 어두운 올리브색 (불쾌함)
    }
    color = colors.get(expression, "FFB6C1")
    return f"https://placehold.co/512x512/{color}/333333?text={expression}+{gender}+{style}"


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


# 다양한 데이트 상황/장소
DATE_SITUATIONS = [
    "카페에서 커피를 마시며 대화하는 중",
    "공원을 산책하며 대화하는 중",
    "영화관에서 영화를 보기 전 대화하는 중",
    "맛집에서 식사하며 대화하는 중",
    "서점에서 책을 구경하며 대화하는 중",
    "놀이공원에서 놀이기구를 타기 전 대화하는 중",
    "바닷가를 걸으며 대화하는 중",
    "전시회를 관람하며 대화하는 중",
    "노래방에서 노래를 부르기 전 대화하는 중",
    "야경을 보며 대화하는 중",
    "버스정류장에서 버스를 기다리며 대화하는 중",
    "편의점에서 간식을 고르며 대화하는 중",
    "학교/회사 근처에서 우연히 만나 대화하는 중",
    "비 오는 날 처마 밑에서 비를 피하며 대화하는 중",
    "벚꽃길을 걸으며 대화하는 중",
]

# 다양한 대화 주제
CONVERSATION_TOPICS = [
    "서로의 취미에 대해",
    "좋아하는 음식에 대해",
    "최근 있었던 재미있는 일에 대해",
    "어린 시절 추억에 대해",
    "좋아하는 영화/드라마에 대해",
    "미래의 꿈이나 목표에 대해",
    "좋아하는 음악에 대해",
    "여행 가고 싶은 곳에 대해",
    "요즘 고민에 대해",
    "첫인상에 대해",
    "이상형에 대해",
    "좋아하는 계절에 대해",
    "반려동물에 대해",
    "주말에 주로 하는 일에 대해",
    "스트레스 푸는 방법에 대해",
]


async def generate_scene_content(
    character_setting,
    user_mbti: str | None,
    scene_number: int,
    affection: int,
    previous_choice: str | None = None,
    previous_dialogue: str | None = None,
) -> dict:
    """
    Gemini API를 사용하여 씬 콘텐츠 생성 (대화 + 선택지)

    Args:
        character_setting: CharacterSetting 모델 (gender, style, mbti, art_style)
        user_mbti: 사용자의 MBTI
        scene_number: 현재 씬 번호 (턴 카운트)
        affection: 현재 호감도 (0-100)
        previous_choice: 사용자가 이전에 선택한 선택지 텍스트
        previous_dialogue: 이전 캐릭터의 대사
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

    # 랜덤 상황과 주제 선택
    import random
    situation = random.choice(DATE_SITUATIONS)
    topic = random.choice(CONVERSATION_TOPICS)

    # 이전 대화 맥락 구성
    previous_context = ""
    if previous_dialogue and previous_choice:
        previous_context = f"""
## 이전 대화 (반드시 이어서 대화해야 함!)
- 캐릭터가 한 말: "{previous_dialogue}"
- 사용자의 선택/반응: "{previous_choice}"
- 중요: 캐릭터의 다음 대사는 사용자의 선택에 대한 자연스러운 반응이어야 합니다!
"""
    elif scene_number == 1:
        previous_context = """
## 첫 만남
- 이것은 첫 번째 대화입니다. 자연스러운 인사나 만남으로 시작해주세요.
"""

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

## 현재 상황
- 장소/상황: {situation}
- 대화 주제: {topic}
- 턴 번호: {scene_number}
{previous_context}

## 캐릭터 감정 타입 (7가지)
각 선택지에 따라 캐릭터가 보여줄 감정을 다음 중 하나로 지정해야 합니다:
- "happy": 기쁘고 즐거운 상태 (칭찬, 좋은 대화, 재미있을 때)
- "shy": 부끄럽고 수줍은 상태 (직접적인 호감 표현, 칭찬, 스킨십 언급)
- "excited": 설레고 두근거리는 상태 (로맨틱한 상황, 고백, 기대될 때)
- "neutral": 평범하고 차분한 상태 (일상적인 대화)
- "sad": 슬프거나 실망한 상태 (거절, 무관심, 서운할 때)
- "jealous": 질투하는 상태 (다른 이성 얘기할 때만! 남용 금지)
- "disgusted": 극혐, 역겨워하는 상태 (무례하거나 불쾌한 말을 들었을 때)

## 요청
1. 캐릭터가 사용자에게 하는 대사를 1-2문장으로 작성해주세요.
   - 이전 대화가 있다면, 사용자의 선택에 대한 자연스러운 반응으로 시작하세요!
   - 현재 상황과 대화 주제에 맞는 대사를 작성하세요.
2. 사용자가 선택할 수 있는 3개의 선택지를 작성해주세요.
   - 선택지는 현재 대화 맥락에 맞아야 합니다.
   - 매번 다른 종류의 선택지를 만들어주세요 (이전과 비슷한 선택지 금지!)
3. 각 선택지에는 반드시 캐릭터의 감정 반응(expression)을 포함해야 합니다.

## 선택지 규칙
- 각 선택지는 사용자의 MBTI 성향({user_style})을 반영해야 합니다.
- 3개의 선택지 중 하나는 긍정적, 하나는 중립적, 하나는 부정적이어야 합니다.
- 긍정적 선택: 호감도 +1 ~ +2
  - 감정: happy(50%), shy(30%), excited(20%) 중 랜덤 선택
- 중립적 선택: 호감도 -1 ~ +1
  - 감정: neutral(60%), happy(20%), shy(20%) 중 랜덤 선택
- 부정적 선택: 호감도 -5 ~ -6
  - 감정: sad(40%), disgusted(40%), jealous(20%) 중 랜덤 선택

## 매우 중요: 선택지 순서 랜덤화
- 선택지 순서를 반드시 무작위로 섞어주세요!
- 긍정적 선택지가 항상 첫 번째에 오면 안 됩니다!
- 예시 순서: [부정, 긍정, 중립] 또는 [중립, 부정, 긍정] 또는 [긍정, 부정, 중립] 등
- 매번 다른 순서로 배치해주세요.

## 매우 중요: 감정 다양성
- 3개의 선택지가 모두 같은 감정이면 절대 안 됩니다!
- 반드시 서로 다른 감정을 사용하세요!
- jealous(질투)는 다른 이성 얘기할 때만 사용하세요. 남용 금지!
- disgusted(극혐)는 정말 무례하거나 불쾌한 선택지에만 사용하세요.
- happy, shy, sad를 주로 사용하고, jealous/disgusted는 가끔만 사용하세요.

## 출력 형식 (JSON)
{{
  "dialogue": "캐릭터의 대사",
  "choices": [
    {{"text": "선택지1 텍스트", "delta": 숫자, "expression": "감정타입"}},
    {{"text": "선택지2 텍스트", "delta": 숫자, "expression": "감정타입"}},
    {{"text": "선택지3 텍스트", "delta": 숫자, "expression": "감정타입"}}
  ]
}}

JSON만 출력하세요. 다른 설명은 필요 없습니다."""

    try:
        # Gemini API 호출 (새로운 SDK)
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
        )

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

        # 이미지 URL (placeholder - 실제로는 character_expressions에서 가져옴)
        image_url = f"https://placehold.co/1024x768/FFB6C1/333333?text=Turn+{scene_number}"

        return {
            "image_url": image_url,
            "dialogue": content.get("dialogue", "안녕하세요!"),
            "choices": content.get("choices", [
                {"text": "고개를 끄덕인다", "delta": 0, "expression": "neutral"},
                {"text": "반갑게 인사한다", "delta": 2, "expression": "happy"},
                {"text": "무시한다", "delta": -5, "expression": "sad"},
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
            {"text": "다른 곳을 본다", "delta": -5, "expression": "sad"},
            {"text": "따뜻하게 웃어준다", "delta": 2, "expression": "happy"},
            {"text": "고개를 끄덕인다", "delta": 0, "expression": "neutral"},
        ],
    }


def get_prompt_hash(prompt: str) -> str:
    """프롬프트 해시 생성 (캐싱용)"""
    return hashlib.sha256(prompt.encode()).hexdigest()
