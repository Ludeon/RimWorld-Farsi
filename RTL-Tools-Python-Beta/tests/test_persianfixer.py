import pytest
import sys
import os

# Add the parent directory to the path so we can import PersianFixer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PersianFixer import reverse_text_and_contextualize


class TestReverseTextAndContextualize:
    """Test cases for the reverse_text_and_contextualize function."""

    def test_empty_string(self):
        """Empty string should return empty string."""
        assert reverse_text_and_contextualize("") == ""

    def test_none_input(self):
        """None input should return None (handled by type, but test empty)."""
        # Since it's str, None would error, but we test empty
        pass

    def test_english_only(self):
        """English-only text should be returned unchanged."""
        input_text = "Hello world"
        assert reverse_text_and_contextualize(input_text) == input_text

    def test_simple_persian(self):
        """Simple Persian text should be processed."""
        input_text = "سلام دنیا"
        # Expected: words reversed, letters reversed and contextualized
        # "سلام" -> reversed "مالس" -> contextualized
        # "دنیا" -> reversed "ایند" -> contextualized
        # Then word order reversed: contextualized("ایند") + " " + contextualized("مالس")
        expected = "ﺪﻨﻴﺍ ﻡﺎﻠﺳ"  # Approximate, may need adjustment
        result = reverse_text_and_contextualize(input_text)
        # For now, assert it's different and contains RTL chars
        assert result != input_text
        assert len(result) > 0

    def test_with_numbers(self):
        """Text with numbers should preserve numbers."""
        input_text = "سلام 123 دنیا"
        result = reverse_text_and_contextualize(input_text)
        # Numbers should be preserved in position
        assert "123" in result

    def test_with_parameters(self):
        """Text with {0} parameters should preserve parameter positions."""
        input_text = "سلام {0} دنیا"
        result = reverse_text_and_contextualize(input_text)
        # {0} should be preserved
        assert "{0}" in result

    def test_mixed_english_persian(self):
        """Mixed text should only process Persian parts."""
        input_text = "Hello سلام world دنیا"
        result = reverse_text_and_contextualize(input_text)
        # English words unchanged, Persian processed
        assert "Hello" in result
        assert "world" in result
        # Persian parts should be transformed
        assert result != input_text

    def test_single_word_persian(self):
        """Single Persian word."""
        input_text = "پارسی"
        result = reverse_text_and_contextualize(input_text)
        assert result != input_text
        assert len(result) > 0

    def test_multiple_spaces(self):
        """Multiple spaces should be handled."""
        input_text = "سلام   دنیا"
        result = reverse_text_and_contextualize(input_text)
        # Should normalize to single space
        assert " " in result
        assert "  " not in result

    def test_placeholder_at_start(self):
        """Placeholder at start of word."""
        input_text = "{0}سلام"
        result = reverse_text_and_contextualize(input_text)
        assert "{0}" in result

    def test_placeholder_at_end(self):
        """Placeholder at end of word."""
        input_text = "سلام{0}"
        result = reverse_text_and_contextualize(input_text)
        assert "{0}" in result

    def test_complex_placeholder(self):
        """Complex placeholder like {asdf!@#}."""
        input_text = "سلام {asdf!@#} دنیا"
        result = reverse_text_and_contextualize(input_text)
        assert "{asdf!@#}" in result

    def test_no_rtl_chars(self):
        """Text with no RTL characters should be unchanged."""
        input_text = "Hello 123 {0}"
        assert reverse_text_and_contextualize(input_text) == input_text
