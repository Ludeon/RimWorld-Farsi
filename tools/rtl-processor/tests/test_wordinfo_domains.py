"""Unit tests for tools/translation-tools/wordinfo_domains.py."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "translation-tools"))

# ruff: noqa: E402
from wordinfo_domains import DomainWordInfoExtractor, compute_ezafeh, normalize_persian


def test_normalize_persian():
    assert normalize_persian("كتاب") == "کتاب"
    assert normalize_persian("عربي") == "عربی"
    assert normalize_persian("  سلام   دنیا  ") == "سلام دنیا"


def test_compute_ezafeh():
    assert compute_ezafeh("غذا") == "غذا ی"
    assert compute_ezafeh("دارو") == "دارو ی"
    assert compute_ezafeh("کلبه") == "کلبه\u200Cی"
    assert compute_ezafeh("سرباز") == "سرباز"


def test_domain_extraction(tmp_path: Path):
    mod_dir = tmp_path / "Core" / "DefInjected" / "HediffDef"
    mod_dir.mkdir(parents=True)
    xml_file = mod_dir / "Injuries.xml"
    xml_file.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<LanguageData>\n'
        '  <Cut.label>بریدگی</Cut.label>\n'
        '  <Gunshot.label>زخم گلوله</Gunshot.label>\n'
        '</LanguageData>\n',
        encoding="utf-8"
    )

    extractor = DomainWordInfoExtractor(root_dir=tmp_path)
    hediffs = extractor.extract_domain("Core", "HediffDef", ".label")

    assert len(hediffs) == 2
    assert hediffs["Cut"] == "بریدگی"
    assert hediffs["Gunshot"] == "زخم گلوله"
