"""
TDD Tests for Gemini Service
TASK-006: Gemini API 설정
"""

import pytest

from app.services.gemini_service import build_expression_prompt, EXPRESSION_TYPES


class TestBuildExpressionPrompt:
    """Tests for build_expression_prompt function"""

    def test_build_expression_prompt_contains_gender(self):
        """
        RED Phase Test 1:
        The prompt should contain the character's gender.
        """
        prompt = build_expression_prompt(
            gender="female",
            style="tsundere",
            art_style="anime",
            expression="happy"
        )

        # The prompt uses "woman" for female, "man" for male
        assert "woman" in prompt.lower()

    def test_build_expression_prompt_contains_style(self):
        """
        The prompt should contain the character's style.
        """
        prompt = build_expression_prompt(
            gender="male",
            style="cool",
            art_style="anime",
            expression="neutral"
        )

        assert "cool" in prompt.lower()

    def test_build_expression_prompt_contains_art_style(self):
        """
        The prompt should contain the art style.
        """
        prompt = build_expression_prompt(
            gender="female",
            style="cute",
            art_style="realistic",
            expression="shy"
        )

        assert "realistic" in prompt.lower()

    def test_build_expression_prompt_contains_expression(self):
        """
        The prompt should contain the expression type.
        """
        prompt = build_expression_prompt(
            gender="female",
            style="tsundere",
            art_style="anime",
            expression="jealous"
        )

        assert "jealous" in prompt.lower()

    def test_expression_types_constant_has_seven_expressions(self):
        """
        EXPRESSION_TYPES should contain exactly 7 expressions.
        """
        assert len(EXPRESSION_TYPES) == 7
        assert "neutral" in EXPRESSION_TYPES
        assert "happy" in EXPRESSION_TYPES
        assert "sad" in EXPRESSION_TYPES
        assert "jealous" in EXPRESSION_TYPES
        assert "shy" in EXPRESSION_TYPES
        assert "excited" in EXPRESSION_TYPES
        assert "disgusted" in EXPRESSION_TYPES
