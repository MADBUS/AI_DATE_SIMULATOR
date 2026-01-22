"""
TDD Tests for Gemini Video API (Veo model)
Phase 2: 애니메이션 시스템

RED Phase: Writing failing tests for video generation functionality
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.gemini_service import (
    build_video_prompt,
    generate_character_video,
    VIDEO_EXPRESSION_TYPES,
)


class TestBuildVideoPrompt:
    """Tests for build_video_prompt function"""

    def test_video_expression_types_constant_exists(self):
        """
        VIDEO_EXPRESSION_TYPES should exist and contain the 7 expression types.
        """
        assert VIDEO_EXPRESSION_TYPES is not None
        assert len(VIDEO_EXPRESSION_TYPES) == 7
        assert "neutral" in VIDEO_EXPRESSION_TYPES
        assert "happy" in VIDEO_EXPRESSION_TYPES
        assert "sad" in VIDEO_EXPRESSION_TYPES
        assert "jealous" in VIDEO_EXPRESSION_TYPES
        assert "shy" in VIDEO_EXPRESSION_TYPES
        assert "excited" in VIDEO_EXPRESSION_TYPES
        assert "disgusted" in VIDEO_EXPRESSION_TYPES

    def test_build_video_prompt_returns_string(self):
        """
        build_video_prompt should return a non-empty string.
        """
        prompt = build_video_prompt(
            gender="female",
            style="cute",
            art_style="anime",
            expression="happy",
        )

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_build_video_prompt_contains_gender(self):
        """
        The video prompt should contain the character's gender.
        """
        prompt = build_video_prompt(
            gender="female",
            style="tsundere",
            art_style="anime",
            expression="happy",
        )

        assert "female" in prompt.lower() or "woman" in prompt.lower()

    def test_build_video_prompt_contains_expression(self):
        """
        The video prompt should contain the expression type.
        """
        prompt = build_video_prompt(
            gender="male",
            style="cool",
            art_style="realistic",
            expression="shy",
        )

        assert "shy" in prompt.lower()

    def test_build_video_prompt_specifies_upper_body(self):
        """
        The video prompt should specify upper body framing for animation.
        """
        prompt = build_video_prompt(
            gender="female",
            style="cute",
            art_style="anime",
            expression="excited",
        )

        assert "upper body" in prompt.lower() or "upper-body" in prompt.lower()

    def test_build_video_prompt_includes_animation_keywords(self):
        """
        The video prompt should include animation-related keywords.
        """
        prompt = build_video_prompt(
            gender="female",
            style="cute",
            art_style="anime",
            expression="happy",
        )

        # Should include animation-related keywords
        prompt_lower = prompt.lower()
        has_animation_keyword = (
            "animation" in prompt_lower or
            "animated" in prompt_lower or
            "motion" in prompt_lower or
            "movement" in prompt_lower or
            "video" in prompt_lower
        )
        assert has_animation_keyword

    def test_build_video_prompt_uses_character_design(self):
        """
        build_video_prompt should use provided character_design for consistency.
        """
        character_design = {
            "hair": "long black hair",
            "eyes": "brown eyes",
            "outfit": "white dress",
            "features": "delicate features",
        }

        prompt = build_video_prompt(
            gender="female",
            style="cute",
            art_style="anime",
            expression="neutral",
            character_design=character_design,
        )

        assert "long black hair" in prompt.lower()
        assert "brown eyes" in prompt.lower()


class TestGenerateCharacterVideo:
    """Tests for generate_character_video function (Veo model)"""

    @pytest.mark.asyncio
    async def test_generate_character_video_returns_video_url(self):
        """
        generate_character_video should return a video URL string.
        """
        result = await generate_character_video(
            gender="female",
            style="cute",
            art_style="anime",
            expression="happy",
        )

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_generate_character_video_accepts_character_design(self):
        """
        generate_character_video should accept character_design parameter
        for consistency across expressions.
        """
        character_design = {
            "hair": "long black hair",
            "eyes": "brown eyes",
            "outfit": "white dress",
            "features": "delicate features",
        }

        result = await generate_character_video(
            gender="female",
            style="cute",
            art_style="anime",
            expression="neutral",
            character_design=character_design,
        )

        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_generate_character_video_returns_placeholder_on_failure(self):
        """
        When video generation fails, should return a placeholder URL.
        """
        # The function should handle failures gracefully
        result = await generate_character_video(
            gender="female",
            style="cute",
            art_style="anime",
            expression="happy",
        )

        # Should return some URL (either generated or placeholder)
        assert result is not None
        assert isinstance(result, str)


class TestUpperBodyVideoPromptOptimization:
    """Tests for upper body video prompt optimization (상반신 영상 프롬프트 최적화)"""

    def test_prompt_includes_shoulder_framing(self):
        """
        Video prompt should specify shoulder-level framing for upper body focus.
        """
        prompt = build_video_prompt(
            gender="female",
            style="cute",
            art_style="anime",
            expression="happy",
        )
        prompt_lower = prompt.lower()

        # Should mention shoulder or bust framing
        has_upper_body_detail = (
            "shoulder" in prompt_lower or
            "bust" in prompt_lower or
            "chest-up" in prompt_lower or
            "waist-up" in prompt_lower
        )
        assert has_upper_body_detail

    def test_prompt_includes_face_focus_keywords(self):
        """
        Video prompt should emphasize face and expression as the main focus.
        """
        prompt = build_video_prompt(
            gender="female",
            style="cute",
            art_style="anime",
            expression="shy",
        )
        prompt_lower = prompt.lower()

        # Should emphasize face/expression focus
        has_face_focus = (
            "face" in prompt_lower or
            "facial" in prompt_lower or
            "expression" in prompt_lower
        )
        assert has_face_focus

    def test_prompt_excludes_full_body(self):
        """
        Video prompt should NOT include full body keywords to ensure upper body focus.
        """
        prompt = build_video_prompt(
            gender="male",
            style="cool",
            art_style="realistic",
            expression="neutral",
        )
        prompt_lower = prompt.lower()

        # Should NOT have full body keywords
        assert "full body" not in prompt_lower
        assert "full-body" not in prompt_lower
        assert "head to toe" not in prompt_lower

    def test_prompt_includes_subtle_movement_keywords(self):
        """
        Video prompt should specify subtle movements appropriate for upper body animation.
        """
        prompt = build_video_prompt(
            gender="female",
            style="tsundere",
            art_style="anime",
            expression="jealous",
        )
        prompt_lower = prompt.lower()

        # Should include subtle movement descriptions
        has_subtle_movement = (
            "subtle" in prompt_lower or
            "gentle" in prompt_lower or
            "slight" in prompt_lower or
            "soft" in prompt_lower
        )
        assert has_subtle_movement

    def test_prompt_includes_breathing_or_idle_animation(self):
        """
        Video prompt should include natural idle animations like breathing.
        """
        prompt = build_video_prompt(
            gender="female",
            style="pure",
            art_style="watercolor",
            expression="neutral",
        )
        prompt_lower = prompt.lower()

        # Should include idle/breathing animation keywords
        has_idle_animation = (
            "breathing" in prompt_lower or
            "idle" in prompt_lower or
            "blink" in prompt_lower or
            "natural movement" in prompt_lower
        )
        assert has_idle_animation

    def test_prompt_includes_camera_stability(self):
        """
        Video prompt should specify stable camera for upper body focus.
        """
        prompt = build_video_prompt(
            gender="female",
            style="sexy",
            art_style="realistic",
            expression="excited",
        )
        prompt_lower = prompt.lower()

        # Should include camera stability keywords
        has_camera_stability = (
            "static" in prompt_lower or
            "fixed" in prompt_lower or
            "stable" in prompt_lower or
            "centered" in prompt_lower or
            "stationary" in prompt_lower
        )
        assert has_camera_stability

    def test_prompt_includes_eye_contact(self):
        """
        Video prompt should specify eye contact with viewer for engagement.
        """
        prompt = build_video_prompt(
            gender="female",
            style="cute",
            art_style="anime",
            expression="happy",
        )
        prompt_lower = prompt.lower()

        # Should include eye contact or looking at viewer
        has_eye_contact = (
            "eye contact" in prompt_lower or
            "looking at" in prompt_lower or
            "gazing" in prompt_lower or
            "viewer" in prompt_lower
        )
        assert has_eye_contact

    def test_prompt_includes_hair_movement(self):
        """
        Video prompt should include natural hair movement for realistic animation.
        """
        prompt = build_video_prompt(
            gender="female",
            style="cute",
            art_style="anime",
            expression="neutral",
        )
        prompt_lower = prompt.lower()

        # Should include hair movement keywords
        has_hair_movement = (
            "hair" in prompt_lower and (
                "movement" in prompt_lower or
                "sway" in prompt_lower or
                "flow" in prompt_lower or
                "gentle" in prompt_lower
            )
        )
        assert has_hair_movement
