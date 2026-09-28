"""Unit tests for check_upstream_diff.py."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "translation-tools"))

# ruff: noqa: E402
from check_upstream_diff import UpstreamDiffEngine


def test_diff_engine_detects_missing_tags(tmp_path: Path):
    en_dir = tmp_path / "en"
    fa_dir = tmp_path / "fa"

    en_keyed = en_dir / "Core" / "Languages" / "English" / "Keyed"
    en_keyed.mkdir(parents=True)
    en_file = en_keyed / "Test.xml"
    en_file.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<LanguageData>\n'
        '  <TagOne>First English String</TagOne>\n'
        '  <TagTwo>Second English String</TagTwo>\n'
        '</LanguageData>\n',
        encoding="utf-8"
    )

    fa_keyed = fa_dir / "Core" / "Keyed"
    fa_keyed.mkdir(parents=True)
    fa_file = fa_keyed / "Test.xml"
    fa_file.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<LanguageData>\n'
        '  <!-- EN: First English String -->\n'
        '  <TagOne>رشته اول فارسی</TagOne>\n'
        '</LanguageData>\n',
        encoding="utf-8"
    )

    engine = UpstreamDiffEngine(english_dir=en_dir, persian_dir=fa_dir)
    report = engine.diff_module("Core")

    assert report.missing_tags_count == 1
    assert len(report.file_diffs) == 1
    diff = report.file_diffs[0]
    assert diff.missing_tags[0].tag_path == "TagTwo"
    assert diff.missing_tags[0].english_text == "Second English String"


def test_diff_engine_generates_stubs(tmp_path: Path):
    en_dir = tmp_path / "en"
    fa_dir = tmp_path / "fa"

    en_keyed = en_dir / "Core" / "Keyed"
    en_keyed.mkdir(parents=True)
    (en_keyed / "Test.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<LanguageData>\n'
        '  <TagA>String A</TagA>\n'
        '  <TagB>String B</TagB>\n'
        '</LanguageData>\n',
        encoding="utf-8"
    )

    fa_keyed = fa_dir / "Core" / "Keyed"
    fa_keyed.mkdir(parents=True)
    (fa_keyed / "Test.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<LanguageData>\n'
        '  <!-- EN: String A -->\n'
        '  <TagA>رشته آ</TagA>\n'
        '</LanguageData>\n',
        encoding="utf-8"
    )

    engine = UpstreamDiffEngine(english_dir=en_dir, persian_dir=fa_dir)
    report = engine.diff_module("Core")
    stubs_count = engine.generate_stubs(report)

    assert stubs_count == 1
    updated_fa = (fa_keyed / "Test.xml").read_text(encoding="utf-8")
    assert "<TagB>TODO</TagB>" in updated_fa
    assert "<!-- EN: String B -->" in updated_fa
