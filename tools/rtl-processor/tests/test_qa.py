"""
Unit tests for the RimWorld Farsi QA Suite (tools/qa/)
"""

import sys
from pathlib import Path

# Ensure tools/qa is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "qa"))

# ruff: noqa: E402
from check_persian_typography import (
    ZWNJ,
    check_file_typography,
    fix_typography_in_text,
)
from check_placeholders import (
    check_file_placeholders,
    extract_positional_indices,
    extract_tokens,
)
from check_report_strings import check_file_report_strings


def test_extract_tokens() -> None:
    text = "Hello {0} and {PAWN_nameDef}, take {1}."
    tokens = extract_tokens(text)
    assert len(tokens) == 3
    assert tokens[0] == "0"
    assert tokens[1] == "PAWN_nameDef"
    assert tokens[2] == "1"


def test_extract_positional_indices() -> None:
    text = "Test {0} and {1_label} and {PAWN_nameDef}"
    indices = extract_positional_indices(text)
    assert indices == {"0", "1"}


def test_placeholder_validation_defects(tmp_path: Path) -> None:
    test_file = tmp_path / "test_defect.xml"
    content = """<?xml version="1.0" encoding="utf-8"?>
<LanguageData>
  <!-- EN: {0} has died. Cause: {1}. -->
  <LetterDied>{0} جان باخت.</LetterDied>
  <!-- EN: {PAWN_gender ? He : She} ran. -->
  <PawnRan>{PAWN_gender ? دوید : دوید}.</PawnRan>
  <InvalidBraces>{0 جان باخت</InvalidBraces>
  <PersianNumber>{۰} مورد</PersianNumber>
  <PersianKey>{نام_شخص} آمد</PersianKey>
</LanguageData>
"""
    test_file.write_text(content, encoding="utf-8")
    errors = check_file_placeholders(test_file)

    # Should detect missing {1}, identical gender branches, mismatched braces, Persian digits, Persian key
    assert len(errors) >= 5
    msgs = " ".join(e.message for e in errors)
    assert "Missing positional token(s)" in msgs
    assert "identical branches" in msgs
    assert "Mismatched curly braces" in msgs
    assert "Persian digits" in msgs
    assert "Persian text found in token identifier" in msgs


def test_fix_typography_in_text() -> None:
    # Arabic letters
    raw = "كتاب عربي و موسيقى"
    fixed = fix_typography_in_text(raw)
    assert fixed == "کتاب عربی و موسیقی"

    # ZWNJ verbal prefixes and plurals
    verb_raw = "او می رود و غذا نمی خورد"
    verb_fixed = fix_typography_in_text(verb_raw)
    assert verb_fixed == f"او می{ZWNJ}رود و غذا نمی{ZWNJ}خورد"

    plural_raw = "تفنگ ها و دیوار ها"
    plural_fixed = fix_typography_in_text(plural_raw)
    assert plural_fixed == f"تفنگ{ZWNJ}ها و دیوار{ZWNJ}ها"

    # Persian punctuation
    punct_raw = "آیا مطمئن هستید? بله, من مطمئنم;"
    punct_fixed = fix_typography_in_text(punct_raw)
    assert punct_fixed == "آیا مطمئن هستید؟ بله، من مطمئنم؛"


def test_typography_preserves_placeholders() -> None:
    raw = "سطح {lookup: {0}; Case; 1} افزایش یافت; آیا ادامه می دهید?"
    fixed = fix_typography_in_text(raw)
    # The semicolon inside lookup must NOT become Persian semicolon!
    assert "{lookup: {0}; Case; 1}" in fixed
    # The external semicolon and question mark should be Persian
    assert fixed.endswith("؟")
    assert f"می{ZWNJ}دهید؟" in fixed


def test_typography_file_check_and_fix(tmp_path: Path) -> None:
    test_file = tmp_path / "typo.xml"
    content = """<?xml version="1.0" encoding="utf-8"?>
<LanguageData>
  <TestTag>او می رود با كفش ها?</TestTag>
</LanguageData>
"""
    test_file.write_text(content, encoding="utf-8")

    # Check without fix
    defects, modified = check_file_typography(test_file, auto_fix=False)
    assert len(defects) == 1
    assert not modified

    # Check with fix
    defects_fixed, modified_fixed = check_file_typography(test_file, auto_fix=True)
    assert modified_fixed

    new_content = test_file.read_text(encoding="utf-8")
    assert "ك" not in new_content
    assert "کفش" in new_content
    assert f"می{ZWNJ}رود" in new_content
    assert f"کفش{ZWNJ}ها؟" in new_content


def test_report_strings_check_and_fix(tmp_path: Path) -> None:
    test_file = tmp_path / "report.xml"
    content = """<?xml version="1.0" encoding="utf-8"?>
<LanguageData>
  <Eating.reportString>مصرف {0}.</Eating.reportString>
  <NonReport.description>یک توضیح معمولی.</NonReport.description>
</LanguageData>
"""
    test_file.write_text(content, encoding="utf-8")

    defects, modified = check_file_report_strings(test_file, auto_fix=False)
    assert len(defects) == 1
    assert defects[0].tag == "Eating.reportString"
    assert not modified

    # Fix
    defects_fix, modified_fix = check_file_report_strings(test_file, auto_fix=True)
    assert modified_fix

    new_content = test_file.read_text(encoding="utf-8")
    assert "<Eating.reportString>مصرف {0}</Eating.reportString>" in new_content
    # NonReport description should still have its period!
    assert "<NonReport.description>یک توضیح معمولی.</NonReport.description>" in new_content
