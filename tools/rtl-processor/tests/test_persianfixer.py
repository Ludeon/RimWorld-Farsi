"""
Comprehensive test suite for PersianFixer RTL processing functionality.

This module provides extensive test coverage for the Persian text processing
functions, ensuring robust handling of RTL text, placeholders, and edge cases.
"""

import pytest
import os
import sys
import re
from pathlib import Path

# Add the parent directory to the path so we can import PersianFixer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PersianFixer import (
    reverse_text_and_contextualize,
    _reverse_rtl_word_letters,
    _contextualize_word,
    _process_word,
    LETTER_MAP,
    RTL_CHAR_REGEX,
    PLACEHOLDER_REGEX
)  # noqa: E402


class TestReverseTextAndContextualize:
    """Test cases for the main reverse_text_and_contextualize function."""

    @pytest.mark.parametrize("input_text,expected", [
        ("", ""),
        ("Hello world", "Hello world"),
        ("Hello 123 {0}", "Hello 123 {0}"),
        ("سلام دنیا", None),  # Should be different from input
        ("Hello سلام world دنیا", None),  # Should be different from input
    ])
    def test_basic_cases(self, input_text, expected):
        """Test basic input cases."""
        result = reverse_text_and_contextualize(input_text)
        if expected is not None:
            assert result == expected
        else:
            # For Persian text, just ensure it's different and contains expected elements
            if any('\u0600' <= c <= '\u06FF' for c in input_text):
                assert result != input_text
                assert len(result) > 0

    def test_persian_processing(self):
        """Test that Persian text is properly processed."""
        input_text = "سلام دنیا"
        result = reverse_text_and_contextualize(input_text)

        # Should be different from input
        assert result != input_text
        # Should contain presentation form characters (contextualized Persian)
        assert any('\uFB00' <= c <= '\uFEFF' for c in result)
        # Should maintain word count
        assert len(result.split()) == len(input_text.split())

    def test_placeholder_preservation(self):
        """Test that placeholders are preserved (order may change due to text reversal)."""
        test_cases = [
            "سلام {0} دنیا",
            "{0}سلام",
            "سلام{0}",
            "پیش از {0} بعد",
            "{param1} و {param2}",
        ]

        for input_text in test_cases:
            result = reverse_text_and_contextualize(input_text)
            # Extract placeholders from input and result
            input_placeholders = set(re.findall(PLACEHOLDER_REGEX, input_text))
            result_placeholders = set(re.findall(PLACEHOLDER_REGEX, result))

            # All placeholders should be preserved (order may change due to reversal)
            assert input_placeholders == result_placeholders

    def test_mixed_content(self):
        """Test mixed English and Persian content."""
        input_text = "Hello سلام world دنیا test"
        result = reverse_text_and_contextualize(input_text)

        # English words should remain unchanged
        assert "Hello" in result
        assert "world" in result
        assert "test" in result

        # Persian parts should be transformed
        assert result != input_text

    def test_numbers_and_symbols(self):
        """Test handling of numbers and special characters."""
        input_text = "سلام 123 دنیا! @test#"
        result = reverse_text_and_contextualize(input_text)

        assert "123" in result
        assert "!" in result
        assert "@test#" in result

    def test_whitespace_handling(self):
        """Test proper whitespace handling."""
        test_cases = [
            "سلام   دنیا",  # Multiple spaces
            "  سلام دنیا  ",  # Leading/trailing spaces
            "سلام\nدنیا",  # Newlines
            "سلام\tدنیا",  # Tabs
        ]

        for input_text in test_cases:
            result = reverse_text_and_contextualize(input_text)
            # Should not crash and should produce valid output
            assert isinstance(result, str)
            assert len(result) > 0

    def test_complex_persian_text(self):
        """Test complex Persian text with various characters."""
        input_text = "این یک متن پارسی با کاراکترهای مختلف است: أ ب پ ت ث ج چ ح خ د ذ ر ز ژ س ش ص ض ط ظ ع غ ف ق ک گ ل م ن ه و ی"
        result = reverse_text_and_contextualize(input_text)

        assert result != input_text
        assert len(result) > 0
        # Should contain Persian characters
        assert any('\u0600' <= c <= '\u06FF' for c in result)

    @pytest.mark.parametrize("placeholder", [
        "{0}", "{1}", "{PAWN_nameDef}", "{PAWN_label}",
        "{PAWN_pronoun}", "{PAWN_objective}", "{PAWN_possessive}",
        "{asdf!@#}", "{param_123}", "{TEST}"
    ])
    def test_various_placeholders(self, placeholder):
        """Test various placeholder formats."""
        input_text = f"سلام {placeholder} دنیا"
        result = reverse_text_and_contextualize(input_text)

        assert placeholder in result
        assert result != input_text


class TestInternalFunctions:
    """Test internal helper functions."""

    def test_reverse_rtl_word_letters_basic(self):
        """Test basic RTL word letter reversal."""
        # Test Persian word
        result = _reverse_rtl_word_letters("سلام")
        assert result == "مالس"

        # Test English word (should remain unchanged)
        result = _reverse_rtl_word_letters("hello")
        assert result == "hello"

    def test_reverse_rtl_word_letters_with_placeholders(self):
        """Test RTL reversal with placeholders."""
        result = _reverse_rtl_word_letters("س{0}لام")
        assert "{0}" in result
        assert result != "س{0}لام"

    def test_contextualize_word_basic(self):
        """Test basic word contextualization."""
        # Test word that should be contextualized
        result = _contextualize_word("مالس")  # reversed "سلام"
        assert result != "مالس"
        assert len(result) > 0

    def test_process_word_integration(self):
        """Test the complete word processing pipeline."""
        result = _process_word("سلام")
        assert result != "سلام"
        assert len(result) > 0

        # Test English word
        result = _process_word("hello")
        assert result == "hello"

    def test_letter_map_completeness(self):
        """Test that LETTER_MAP contains expected mappings."""
        expected_letters = "ءآأؤإابپةتثجچحخدذرزژسشصضطظعغفقکگلمنهویيئ"

        for letter in expected_letters:
            assert letter in LETTER_MAP, f"Letter {letter} missing from LETTER_MAP"

        # Test that all values are integers (Unicode code points)
        # Allow broader range for presentation forms and ligatures
        for code in LETTER_MAP.values():
            assert isinstance(code, int)
            assert 0x0600 <= code <= 0x06FF or 0xFB00 <= code <= 0xFEFF


class TestRegexPatterns:
    """Test regex pattern constants."""

    def test_rtl_char_regex(self):
        """Test RTL character detection regex."""
        rtl_text = "سلام دنیا أ ب پ"
        english_text = "Hello world"

        assert re.search(RTL_CHAR_REGEX, rtl_text) is not None
        assert re.search(RTL_CHAR_REGEX, english_text) is None

    def test_placeholder_regex(self):
        """Test placeholder detection regex."""
        text_with_placeholders = "سلام {0} دنیا {PAWN_nameDef} test"
        text_without = "سلام دنیا"

        placeholders = re.findall(PLACEHOLDER_REGEX, text_with_placeholders)
        assert "{0}" in placeholders
        assert "{PAWN_nameDef}" in placeholders

        no_placeholders = re.findall(PLACEHOLDER_REGEX, text_without)
        assert len(no_placeholders) == 0


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_and_none_inputs(self):
        """Test empty and None inputs."""
        assert reverse_text_and_contextualize("") == ""

        # None input returns None (not an error)
        result = reverse_text_and_contextualize(None)  # type: ignore
        assert result is None

    def test_very_long_text(self):
        """Test processing of very long text."""
        long_text = "سلام " * 1000 + "دنیا"
        result = reverse_text_and_contextualize(long_text)

        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain presentation form characters (contextualized Persian)
        assert any('\uFB00' <= c <= '\uFEFF' for c in result)

    def test_special_characters(self):
        """Test handling of special Unicode characters."""
        special_text = "سلام 🌟 دنیا 🔥 test"
        result = reverse_text_and_contextualize(special_text)

        assert "🌟" in result
        assert "🔥" in result
        assert "test" in result

    def test_xml_like_content(self):
        """Test processing of XML-like content."""
        xml_content = '<tag>سلام دنیا</tag>'
        result = reverse_text_and_contextualize(xml_content)

        # Should process the Persian text inside and reverse everything
        assert result != xml_content
        # Tags get reversed too: '<tag>' becomes '>gat<'
        assert '>gat<' in result
        # Persian content should be contextualized
        assert any('\uFB00' <= c <= '\uFEFF' for c in result)


class TestIdempotency:
    """Test that functions are idempotent (stable output)."""

    def test_double_processing(self):
        """Test that processing twice gives same result as once."""
        input_text = "سلام دنیا {0} test"

        first_result = reverse_text_and_contextualize(input_text)
        second_result = reverse_text_and_contextualize(first_result)

        # Second processing should not change the result
        assert first_result == second_result

    def test_word_level_idempotency(self):
        """Test idempotency at word processing level."""
        word = "سلام"

        first_result = _process_word(word)
        second_result = _process_word(first_result)

        assert first_result == second_result


# Performance tests
class TestPerformance:
    """Performance regression tests."""

    def test_processing_speed(self):
        """Test that processing completes within reasonable time."""
        import time

        test_text = "این یک متن تست برای بررسی عملکرد پردازش متن پارسی است که باید سریع انجام شود."

        start_time = time.time()
        result = reverse_text_and_contextualize(test_text)
        end_time = time.time()

        processing_time = end_time - start_time

        # Should complete in less than 1 second
        assert processing_time < 1.0
        assert result != test_text
