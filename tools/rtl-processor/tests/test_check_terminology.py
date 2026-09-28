"""Unit tests for check_terminology.py."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "qa"))

# ruff: noqa: E402
from check_terminology import TerminologyChecker


def test_checker_detects_prohibited_terms(tmp_path: Path):
    mod_dir = tmp_path / "Core" / "Keyed"
    mod_dir.mkdir(parents=True)
    xml_file = mod_dir / "Test.xml"
    xml_file.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<LanguageData>\n'
        '  <GoodTag>استعمارگر و مکانوید</GoodTag>\n'
        '  <BadTag>کلونیست و مکانیوید</BadTag>\n'
        '</LanguageData>\n',
        encoding="utf-8"
    )

    checker = TerminologyChecker(root_dir=tmp_path)
    violations = checker.check_file(xml_file)

    assert len(violations) == 2
    terms = [v.matched_text for v in violations]
    assert "کلونیست" in terms
    assert "مکانیوید" in terms


def test_checker_fixes_terms(tmp_path: Path):
    mod_dir = tmp_path / "Core" / "Keyed"
    mod_dir.mkdir(parents=True)
    xml_file = mod_dir / "Test.xml"
    xml_file.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<LanguageData>\n'
        '  <BadTag>کلونیست و بلوپرینت</BadTag>\n'
        '</LanguageData>\n',
        encoding="utf-8"
    )

    checker = TerminologyChecker(root_dir=tmp_path)
    checker.run_check(modules=["Core"], fix=True)

    content = xml_file.read_text(encoding="utf-8")
    assert "کلونیست" not in content
    assert "بلوپرینت" not in content
    assert "استعمارگر" in content
    assert "طرح اولیه" in content
