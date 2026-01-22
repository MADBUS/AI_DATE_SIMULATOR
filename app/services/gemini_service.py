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

# 비디오 저장 경로
VIDEOS_DIR = Path(__file__).parent.parent.parent / "static" / "videos" / "characters"
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

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

# 7가지 비디오 표정 타입 (애니메이션용)
VIDEO_EXPRESSION_TYPES = [
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
    캐릭터 외모를 랜덤하게 생성.
    매번 새로운 조합의 캐릭터가 생성됨.
    """
    import random

    # 공통 동양인 특징
    asian_features = "East Asian facial features, Korean/Japanese appearance"

    # 여성 옵션
    female_options = {
        "hair_colors": [
            "jet black", "dark brown", "chestnut brown", "dark auburn",
            "burgundy brown", "natural black with subtle highlights",
            "deep chocolate brown", "warm caramel brown", "ash brown",
        ],
        "hair_styles": [
            "long straight hair flowing past shoulders",
            "medium-length hair with gentle waves",
            "short bob cut with bangs",
            "long wavy hair with soft curls",
            "shoulder-length layered cut",
            "long hair with side-swept bangs",
            "cute twin-tails with ribbons",
            "elegant ponytail",
            "half-up half-down style",
            "long hair with see-through bangs",
        ],
        "eye_colors": [
            "deep dark brown", "warm brown", "dark chocolate brown",
            "soft hazel brown", "clear brown with golden flecks",
        ],
        "outfits": [
            "elegant blouse with high-waisted skirt, K-fashion style",
            "cozy oversized sweater, cute casual look",
            "stylish school uniform with ribbon tie",
            "simple white dress with delicate details",
            "trendy crop top with high-waisted jeans",
            "sophisticated blazer over feminine top",
            "cute cardigan with pleated skirt",
            "elegant off-shoulder top, refined style",
            "casual hoodie dress, comfortable chic",
            "romantic floral blouse with fitted pants",
        ],
        "features": [
            "flawless porcelain skin, delicate features, sweet smile",
            "clear glass skin, soft round face, cute dimples",
            "radiant fair skin, elegant features, graceful neck",
            "naturally beautiful skin, gentle features, warm expression",
            "luminous Korean-style skin, refined features, attractive smile",
        ],
    }

    # 남성 옵션
    male_options = {
        "hair_colors": [
            "jet black", "dark brown", "natural black",
            "deep brown", "ash brown", "dark chocolate",
            "soft black", "warm brown", "cool-toned brown",
        ],
        "hair_styles": [
            "stylishly messy textured hair, K-pop idol style",
            "neatly styled comma hair, clean look",
            "modern two-block cut, sophisticated style",
            "soft fluffy hair, boyish charm",
            "slicked back hair, refined look",
            "natural layered cut, effortless style",
            "textured fringe, youthful look",
            "side-parted hair, classic handsome",
            "tousled wavy hair, casual attractive",
            "clean short cut, neat appearance",
        ],
        "eye_colors": [
            "deep dark brown", "intense brown", "warm chocolate brown",
            "sharp dark eyes", "gentle brown",
        ],
        "outfits": [
            "crisp white shirt, clean classic style",
            "casual hoodie, comfortable streetwear",
            "fitted black turtleneck, sleek modern look",
            "stylish blazer over t-shirt, smart casual",
            "denim jacket with simple tee, effortless cool",
            "knit sweater, warm cozy look",
            "school uniform with loose tie, youthful charm",
            "leather jacket, edgy attractive style",
            "simple polo shirt, preppy look",
            "fitted henley shirt, casual masculine",
        ],
        "features": [
            "sharp jawline, handsome features, confident look",
            "soft handsome features, warm smile, friendly appearance",
            "defined features, clear skin, attractive gaze",
            "gentle masculine features, kind eyes, trustworthy look",
            "chiseled features, fair skin, charismatic presence",
        ],
    }

    # 성별에 따른 옵션 선택
    options = female_options if gender == "female" else male_options

    # 성격에 따른 스타일 힌트
    style_hints = {
        "tsundere": "with a hint of tsundere charm, slightly fierce expression base",
        "cool": "with cool mysterious aura, composed elegant presence",
        "cute": "with adorable sweet charm, bright youthful energy",
        "sexy": "with elegant alluring presence, confident attractive aura",
        "pure": "with innocent pure charm, gentle warm presence",
    }

    # 랜덤 선택
    hair_color = random.choice(options["hair_colors"])
    hair_style = random.choice(options["hair_styles"])
    eye_color = random.choice(options["eye_colors"])
    outfit = random.choice(options["outfits"])
    features = random.choice(options["features"])
    style_hint = style_hints.get(style, style_hints["cute"])

    return {
        "hair": f"{hair_style}, beautiful {hair_color} hair, silky shiny Asian hair texture",
        "eyes": f"expressive {eye_color} Asian eyes with attractive gaze, natural eyelashes",
        "outfit": outfit,
        "features": f"{features}, {asian_features}, {style_hint}",
    }


def build_expression_prompt(
    gender: str,
    style: str,
    art_style: str,
    expression: str,
    character_design: dict | None = None,
) -> str:
    """캐릭터 설정 기반 표정 이미지 생성 프롬프트 생성."""

    # 캐릭터 디자인 사용 (전달받은 것 또는 새로 생성)
    design = character_design if character_design else get_character_design(gender, style)

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


def build_video_prompt(
    gender: str,
    style: str,
    art_style: str,
    expression: str,
    character_design: dict | None = None,
) -> str:
    """
    캐릭터 설정 기반 표정 애니메이션 비디오 생성 프롬프트 생성.

    Args:
        gender: 캐릭터 성별 (male/female)
        style: 캐릭터 성격 (tsundere/cool/cute/sexy/pure)
        art_style: 그림체 (anime/realistic/watercolor)
        expression: 표정 (neutral/happy/sad/jealous/shy/excited/disgusted)
        character_design: 캐릭터 디자인 (동일 캐릭터 유지를 위해 전달)

    Returns:
        비디오 생성용 프롬프트 문자열
    """
    # 캐릭터 디자인 사용 (전달받은 것 또는 새로 생성)
    design = character_design if character_design else get_character_design(gender, style)

    # 표정별 애니메이션 설명
    video_expression_details = {
        "neutral": {
            "animation": "gentle idle animation with subtle breathing motion",
            "face": "serene calm expression transitioning to soft natural smile",
            "mood": "peaceful, content, warmly approachable",
        },
        "happy": {
            "animation": "joyful animation with bright smile appearing",
            "face": "expression brightening into radiant genuine smile",
            "mood": "overflowing with joy, warm and delightful",
        },
        "sad": {
            "animation": "melancholic animation with downcast gaze",
            "face": "expression softening into tender sadness",
            "mood": "gentle melancholy, touching vulnerability",
        },
        "jealous": {
            "animation": "pouty animation with slight head turn away",
            "face": "adorable pout forming with puffed cheeks",
            "mood": "endearingly jealous, playfully annoyed",
        },
        "shy": {
            "animation": "bashful animation with slight head tilt and looking away",
            "face": "cheeks flushing pink with bashful smile",
            "mood": "sweetly embarrassed, charmingly flustered",
        },
        "excited": {
            "animation": "excited animation with eyes sparkling",
            "face": "expression lighting up with anticipation",
            "mood": "heart-fluttering excitement, romantic anticipation",
        },
        "disgusted": {
            "animation": "displeased animation with face turning away",
            "face": "expression showing strong displeasure",
            "mood": "utterly repulsed, strongly disapproving",
        },
    }

    # 그림체별 비디오 스타일 설명
    video_art_style_details = {
        "anime": {
            "style": "anime-style character animation, visual novel quality",
            "rendering": "smooth 2D animation with anime aesthetics",
        },
        "realistic": {
            "style": "photorealistic character video, lifelike movement",
            "rendering": "realistic human motion and expressions",
        },
        "watercolor": {
            "style": "artistic watercolor-style animation",
            "rendering": "dreamy soft motion with artistic flair",
        },
    }

    expr = video_expression_details.get(expression, video_expression_details["neutral"])
    art = video_art_style_details.get(art_style, video_art_style_details["anime"])

    # 성별 표현
    gender_word = "young East Asian woman" if gender == "female" else "young East Asian man"

    prompt = f"""Create a short bust-up character animation video.

SUBJECT: An attractive {gender_word} with the following features:
- Hair: {design['hair']}
- Eyes: {design['eyes']}
- Outfit: {design['outfit']}
- Features: {design['features']}

EXPRESSION TYPE: {expression}
ANIMATION TYPE: {expr['animation']}
EXPRESSION DETAILS: {expr['face']}
MOOD: {expr['mood']}

UPPER BODY COMPOSITION (CRITICAL):
- Chest-up framing, shoulder level view
- Face and upper body as main focus
- Character centered in frame with stable fixed camera
- Looking at viewer with natural eye contact
- Gentle hair movement and sway

ANIMATION DETAILS:
- Subtle breathing motion and natural idle animation
- Soft facial expression transitions
- Gentle head and shoulder movements
- Natural blink animation
- Smooth seamless loop (2-4 seconds)

VIDEO STYLE: {art['style']}
RENDERING: {art['rendering']}

IMPORTANT:
- East Asian appearance (Korean/Japanese features)
- Single character only
- High quality animated video
- Stationary camera, no camera movement

DO NOT include: text, watermarks, multiple characters, Western features, legs, feet, walking, lower body"""

    return prompt


async def generate_character_video(
    gender: str,
    style: str,
    art_style: str,
    expression: str,
    character_design: dict | None = None,
) -> str:
    """
    Gemini Veo API를 사용하여 캐릭터 애니메이션 비디오 생성

    Args:
        gender: 캐릭터 성별 (male/female)
        style: 캐릭터 성격 (tsundere/cool/cute/sexy/pure)
        art_style: 그림체 (anime/realistic/watercolor)
        expression: 표정 (neutral/happy/sad/jealous/shy/excited/disgusted)
        character_design: 캐릭터 디자인 (동일 캐릭터 유지를 위해 전달)

    Returns:
        생성된 비디오의 URL
    """
    prompt = build_video_prompt(gender, style, art_style, expression, character_design)

    # Veo 모델 사용
    models_to_try = [
        'veo-2.0-generate-001',
    ]

    for model_name in models_to_try:
        try:
            print(f"Trying video generation with model: {model_name}")

            # 비디오 생성 요청
            operation = client.models.generate_videos(
                model=model_name,
                prompt=prompt,
            )

            # 비디오 생성 완료 대기
            while not operation.done:
                import time
                time.sleep(5)
                operation = client.operations.get(operation)

            if operation.response and operation.response.generated_videos:
                generated_video = operation.response.generated_videos[0]

                video_id = str(uuid.uuid4())
                video_filename = f"{video_id}.mp4"
                video_path = VIDEOS_DIR / video_filename

                # 비디오 데이터 저장
                if hasattr(generated_video, 'video') and generated_video.video:
                    video_bytes = generated_video.video.video_bytes
                    if video_bytes and len(video_bytes) > 100:
                        with open(video_path, 'wb') as f:
                            f.write(video_bytes)
                        print(f"Video generated successfully with {model_name}, size: {len(video_bytes)} bytes")
                        return f"/static/videos/characters/{video_filename}"

            print(f"No video data in response from {model_name}")

        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue

    # 모든 모델 실패 시 placeholder 반환
    print(f"All video generation models failed, using placeholder")
    return _get_video_placeholder_url(expression, gender, style)


def _get_video_placeholder_url(expression: str, gender: str, style: str) -> str:
    """비디오 생성 실패 시 placeholder URL 반환"""
    return f"/static/videos/placeholder_{expression}.mp4"


async def generate_character_image(
    gender: str,
    style: str,
    art_style: str,
    expression: str,
    character_design: dict | None = None,
) -> str:
    """
    Gemini API를 사용하여 캐릭터 이미지 생성

    Args:
        gender: 캐릭터 성별 (male/female)
        style: 캐릭터 성격 (tsundere/cool/cute/sexy/pure)
        art_style: 그림체 (anime/realistic/watercolor)
        expression: 표정 (neutral/happy/sad/jealous/shy/excited)
        character_design: 캐릭터 디자인 (동일 캐릭터 유지를 위해 전달)

    Returns:
        생성된 이미지의 URL
    """
    prompt = build_expression_prompt(gender, style, art_style, expression, character_design)

    # Imagen 모델 (4.0 -> 3.0 폴백)
    models_to_try = [
        'imagen-4.0-generate-001',
        'imagen-4.0-fast-generate-001',
        'imagen-3.0-generate-002',
        'imagen-3.0-fast-generate-001',
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
            error_str = str(e)
            print(f"Model {model_name} failed: {error_str}")
            # 429 할당량 초과 시 다음 모델로 빠르게 넘어감
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                print(f"Quota exceeded for {model_name}, trying next model...")
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


# 특별 이벤트 씬 타입
SPECIAL_EVENT_SCENES = [
    {
        "name": "romantic_date",
        "description": "로맨틱한 데이트 장면",
        "scene": "romantic sunset date scene, couple watching beautiful sunset together",
        "mood": "romantic, warm, intimate",
    },
    {
        "name": "surprise_gift",
        "description": "깜짝 선물 장면",
        "scene": "receiving a surprise gift, holding a beautifully wrapped present",
        "mood": "surprised, happy, touched",
    },
    {
        "name": "rain_shelter",
        "description": "비를 피하는 장면",
        "scene": "sheltering from rain together under one umbrella, close together",
        "mood": "intimate, cozy, romantic",
    },
    {
        "name": "festival",
        "description": "축제 장면",
        "scene": "at a beautiful festival with fireworks in the background, festive atmosphere",
        "mood": "excited, joyful, magical",
    },
    {
        "name": "confession",
        "description": "고백 장면",
        "scene": "heartfelt confession moment, holding hands, emotional atmosphere",
        "mood": "nervous, sincere, loving",
    },
]


async def generate_special_event_image(
    gender: str,
    style: str,
    art_style: str,
    character_design: dict | None = None,
    event_type: str | None = None,
    reference_image_url: str | None = None,
) -> tuple[str, str]:
    """
    특별 이벤트 전신 씬 이미지 생성

    Args:
        gender: 캐릭터 성별 (male/female)
        style: 캐릭터 성격 (tsundere/cool/cute/sexy/pure)
        art_style: 그림체 (anime/realistic/watercolor)
        character_design: 캐릭터 디자인 (동일 캐릭터 유지)
        event_type: 이벤트 타입 (None이면 랜덤 선택)
        reference_image_url: 참조할 캐릭터 이미지 URL (neutral 표정)

    Returns:
        (이미지 URL, 이벤트 설명)
    """
    import random

    # 이벤트 타입 선택
    if event_type:
        event = next((e for e in SPECIAL_EVENT_SCENES if e["name"] == event_type), None)
    if not event_type or not event:
        event = random.choice(SPECIAL_EVENT_SCENES)

    # 캐릭터 디자인
    design = character_design if character_design else get_character_design(gender, style)

    # 성별 표현
    gender_word = "young East Asian woman, Korean or Japanese" if gender == "female" else "young East Asian man, Korean or Japanese"

    # 그림체 설정
    art_style_prompts = {
        "anime": "modern Japanese anime art style, visual novel CG quality, beautiful anime illustration, consistent character design",
        "realistic": "photorealistic portrait photography style, cinematic lighting, magazine quality, same person throughout",
        "watercolor": "traditional watercolor painting style, soft dreamy artistic illustration, consistent character appearance",
    }
    art_prompt = art_style_prompts.get(art_style, art_style_prompts["anime"])

    # 전신 이벤트 씬 프롬프트 (캐릭터 일관성 강조)
    prompt = f"""Create a beautiful full-body special event illustration.

CRITICAL - CHARACTER CONSISTENCY:
This MUST be the EXACT SAME character with these SPECIFIC features:
- Hair: {design['hair']}
- Eyes: {design['eyes']}
- Face: {design['features']}
These features are NON-NEGOTIABLE and must match exactly.

SUBJECT: An attractive {gender_word}
The character must have IDENTICAL appearance to the reference - same face shape, same hairstyle, same eye color, same skin tone.

SCENE: {event['scene']}
MOOD: {event['mood']}

OUTFIT: Elegant outfit suitable for the romantic scene (dress, formal wear, or date outfit)

COMPOSITION:
- Full body shot showing the entire character from head to toe
- Character is the main focus, centered in frame
- Beautiful scenic background matching the event theme
- Cinematic composition with depth
- Warm, romantic, emotional lighting
- High quality, detailed artwork

ART STYLE: {art_prompt}

ABSOLUTE REQUIREMENTS:
- East Asian appearance (Korean/Japanese features)
- SAME character as the reference - identical face, hair, eyes
- Beautiful, emotionally engaging romantic scene
- Single character only

DO NOT include: text, watermarks, multiple characters, Western/Caucasian features, deformed anatomy, different character design"""

    # Imagen 모델 (4.0 -> 3.0 폴백)
    models_to_try = [
        'imagen-4.0-generate-001',
        'imagen-4.0-fast-generate-001',
        'imagen-3.0-generate-002',
        'imagen-3.0-fast-generate-001',
    ]

    for model_name in models_to_try:
        try:
            print(f"Generating special event image with model: {model_name}")
            response = client.models.generate_images(
                model=model_name,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                ),
            )

            if response.generated_images and len(response.generated_images) > 0:
                image_id = str(uuid.uuid4())
                image_filename = f"event_{image_id}.png"
                image_path = IMAGES_DIR / image_filename

                generated_image = response.generated_images[0]
                if hasattr(generated_image, 'image') and generated_image.image:
                    image_bytes = generated_image.image.image_bytes
                    if image_bytes and len(image_bytes) > 100:
                        with open(image_path, 'wb') as f:
                            f.write(image_bytes)
                        print(f"Special event image generated successfully: {len(image_bytes)} bytes")
                        return (f"/static/images/characters/{image_filename}", event['description'])

        except Exception as e:
            error_str = str(e)
            print(f"Special event image generation failed with {model_name}: {error_str}")
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                print(f"Quota exceeded for {model_name}, trying next model...")
            continue

    # 실패 시 placeholder
    placeholder = f"https://placehold.co/1024x768/FF69B4/FFFFFF?text=Special+Event+{event['name']}"
    return (placeholder, event['description'])


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

    import random

    # 이전 대화 맥락 구성 및 상황 설정
    previous_context = ""
    dialogue_instruction = ""
    situation_context = ""

    if previous_dialogue and previous_choice:
        # 이전 대화가 있으면 → 대화 흐름 유지 (새 상황/주제 없음)
        previous_context = f"""
####### 최우선 필수 사항 #######
사용자가 방금 선택한 행동/말: "{previous_choice}"

캐릭터는 반드시 위 선택에 대해 직접적으로 반응해야 합니다!
주제를 바꾸지 말고, 현재 대화 흐름을 이어가세요!

예시:
- 사용자 선택: "예쁘다고 말한다" → 캐릭터: "에, 에잇... 갑자기 그런 말 하면 어떡해! (부끄러워하며)"
- 사용자 선택: "딴 데를 본다" → 캐릭터: "...왜 그래? 내 말 듣고 있어?"
- 사용자 선택: "손을 잡는다" → 캐릭터: "어...! 갑자기 왜 그래... 심장이 너무 빨리 뛰잖아."
###############################
"""
        dialogue_instruction = f"""
### 대사 작성 필수 규칙 ###
1. 캐릭터의 대사는 반드시 "{previous_choice}"에 대한 직접적인 반응으로 시작해야 합니다!
2. 사용자의 선택을 무시하고 갑자기 새로운 주제로 바꾸면 안 됩니다!
3. 현재 대화의 흐름과 분위기를 유지하세요!
4. 선택에 대한 감정적 반응(기쁨/부끄러움/슬픔/화남 등)을 먼저 보여주세요.
"""
        # 이전 대화가 있으면 상황 컨텍스트 없음 (대화 흐름 우선)
        situation_context = f"- 턴 번호: {scene_number} (대화 진행 중 - 흐름 유지)"

    elif scene_number == 1:
        # 첫 턴 → 새로운 상황과 주제 설정
        situation = random.choice(DATE_SITUATIONS)
        topic = random.choice(CONVERSATION_TOPICS)
        previous_context = f"""
## 첫 만남
- 이것은 첫 번째 대화입니다.
- 상황: {situation}
- 대화 주제: {topic}
- 자연스러운 인사나 만남으로 시작해주세요.
"""
        dialogue_instruction = ""
        situation_context = f"- 장소/상황: {situation}\n- 대화 주제: {topic}\n- 턴 번호: {scene_number}"

    else:
        # 이전 대화 정보가 없는 경우 (예외 상황)
        situation = random.choice(DATE_SITUATIONS)
        previous_context = ""
        dialogue_instruction = ""
        situation_context = f"- 장소/상황: {situation}\n- 턴 번호: {scene_number}"

    # Gemini 프롬프트 생성
    prompt = f"""당신은 연애 시뮬레이션 게임의 시나리오 작가입니다.
{previous_context}
## 캐릭터 정보
- 성별: {"여성" if char_gender == "female" else "남성"}
- 성격: {style_desc}
- MBTI: {char_mbti}
- 현재 호감도: {affection}/100
- 현재 분위기: {mood}

## 현재 상황
{situation_context}

## 사용자 정보
- MBTI: {user_mbti or "알 수 없음"}
- 선택지 스타일: {user_style}

## 캐릭터 감정 타입과 사용 예시
선택지의 내용에 따라 캐릭터가 어떤 감정을 보일지 정확하게 선택하세요:

### "happy" - 기쁨, 즐거움
사용자가 이런 말/행동을 했을 때: 재미있는 농담, 함께 즐기자는 제안, 긍정적 동의, 맛있는 거 사줄게
예시: "같이 영화 보자" → happy / "맛있겠다!" → happy

### "shy" - 부끄러움, 수줍음
사용자가 이런 말/행동을 했을 때: 직접적인 칭찬, 외모 칭찬, 손잡기/스킨십, 좋아한다는 표현
예시: "오늘 예쁘다" → shy / "손 잡아도 돼?" → shy / "너랑 있으면 좋아" → shy

### "excited" - 설렘, 두근거림
사용자가 이런 말/행동을 했을 때: 고백, 데이트 신청, 로맨틱한 분위기 조성, 미래 약속
예시: "다음에 또 만나자" → excited / "너한테 할 말 있어" → excited

### "neutral" - 평범, 차분
사용자가 이런 말/행동을 했을 때: 일상적인 대답, 정보 질문, 무난한 반응
예시: "그렇구나" → neutral / "뭐 먹을까?" → neutral

### "sad" - 슬픔, 실망
사용자가 이런 말/행동을 했을 때: 거절, 관심 없는 반응, 약속 취소, 차가운 대답
예시: "오늘 바빠서 안 돼" → sad / "별로야" → sad / "가봐야 해" → sad

### "jealous" - 질투, 삐짐
사용자가 이런 말/행동을 했을 때: 다른 이성 언급, 다른 사람 칭찬, 바람기 있는 말
예시: "그 여자/남자 예쁘더라" → jealous / "친구가 연락왔어" → jealous

### "disgusted" - 극혐, 불쾌
사용자가 이런 말/행동을 했을 때: 무례한 말, 성희롱, 모욕, 역겨운 농담
예시: "뚱뚱하네" → disgusted / (무례한 발언) → disgusted

## 요청
{dialogue_instruction}
1. 캐릭터가 사용자에게 하는 대사를 1-2문장으로 작성해주세요.
   - 반드시 사용자의 이전 선택에 대한 직접적인 반응으로 시작하세요!
   - 선택을 무시하고 갑자기 다른 주제로 넘어가면 안 됩니다!
2. 사용자가 선택할 수 있는 3개의 선택지를 작성해주세요.
   - 선택지는 캐릭터의 대사에 대한 자연스러운 응답이어야 합니다.
   - 매번 다른 종류의 선택지를 만들어주세요.
3. 각 선택지에는 반드시 캐릭터의 감정 반응(expression)을 포함해야 합니다.

## 선택지 규칙
3개의 선택지를 만들되, 반드시 선택지 내용에 맞는 감정을 지정하세요!

### 긍정적 선택지 (호감도 +1 ~ +2)
- 칭찬, 호감 표현, 함께하자는 제안 등
- 내용에 따라: 칭찬/호감 → shy, 재미있는 제안 → happy, 로맨틱 → excited

### 중립적 선택지 (호감도 -1 ~ +1)
- 무난한 대답, 일상적 반응
- 대부분 neutral, 가벼운 긍정이면 happy

### 부정적 선택지 (호감도 -5 ~ -6)
- 거절, 무관심, 불쾌한 말
- 내용에 따라: 거절/무관심 → sad, 무례한 말 → disgusted, 다른 이성 언급 → jealous

## 핵심: 선택지 내용과 감정 일치
잘못된 예:
- "예쁘다" 선택지에 happy (X) → shy가 맞음 (칭찬받으면 부끄러움)
- "다른 사람 만나야 해" 선택지에 sad (X) → jealous가 맞음 (질투)
- "재미없어" 선택지에 neutral (X) → sad가 맞음 (실망)

올바른 예:
- "같이 밥 먹자" → happy (즐거운 제안)
- "손 잡고 싶어" → shy (스킨십 = 부끄러움)
- "바빠서 못 만나" → sad (거절 = 슬픔)
- "그 남자/여자 괜찮던데?" → jealous (다른 이성 = 질투)

## 선택지 순서: 반드시 섞어서 배치
[부정, 긍정, 중립] 또는 [중립, 부정, 긍정] 또는 [긍정, 중립, 부정] 등 랜덤하게

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
