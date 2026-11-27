"""Unit tests for tools/qa/check_localization_audit.py."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "qa"))

# ruff: noqa: E402
import check_localization_audit as audit


def test_todo_and_en_comment_detection(tmp_path: Path) -> None:
    keyed = tmp_path / "Core" / "Keyed"
    keyed.mkdir(parents=True)
    (keyed / "Menu.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<LanguageData>\n"
        "  <!-- EN: Start -->\n"
        "  <Start>شروع</Start>\n"
        "  <Missing>TODO</Missing>\n"
        "</LanguageData>\n",
        encoding="utf-8",
    )

    todos, en_count, total = audit.check_todo_and_comments(tmp_path, modules=("Core",))
    assert len(todos) == 1
    assert "Missing" in todos[0]
    assert en_count == 1
    assert total == 2


def test_strings_integrity_detects_extensionless_duplicates_and_corrupt_capitals(
    tmp_path: Path,
) -> None:
    adj = tmp_path / "Core" / "Strings" / "Words" / "Adjectives"
    adj.mkdir(parents=True)
    (adj / "CompassDirections").write_text("North\n", encoding="utf-8")
    (adj / "CompassDirections.txt").write_text("شمال\n", encoding="utf-8")

    wp = tmp_path / "Core" / "Strings" / "WordParts"
    wp.mkdir(parents=True)
    (wp / "CapitalLetters.txt").write_text("A\nب\n", encoding="utf-8")

    issues = audit.check_strings_integrity(tmp_path, modules=("Core",))
    assert any("CompassDirections" in i for i in issues)
    assert any("CapitalLetters.txt" in i for i in issues)


def test_rulepack_wordinfo_drift_and_translation_report(tmp_path: Path) -> None:
    rp_dir = tmp_path / "Core" / "DefInjected" / "RulePackDef"
    rp_dir.mkdir(parents=True)
    (rp_dir / "Rules.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<LanguageData>\n"
        "  <Pack.rulePack.rulesStrings>\n"
        "    <li>badRule->of</li>\n"
        "    <li>glued->[bandit]ها</li>\n"
        "  </Pack.rulePack.rulesStrings>\n"
        "</LanguageData>\n",
        encoding="utf-8",
    )

    wi_dir = tmp_path / "Core" / "WordInfo"
    wi_dir.mkdir(parents=True)
    (wi_dir / "ezafeh.txt").write_text("// header\nچیزناموجود;چیزناموجودِ\n", encoding="utf-8")

    report = tmp_path / "TranslationReport.txt"
    report.write_text(
        "========== Missing keyed translations ==========\n"
        "Key1: Sample\n"
        "========== Unnecessary keyed translations ==========\n"
        "OldKey\n",
        encoding="utf-8",
    )

    rp_issues = audit.check_rulepack_hygiene(tmp_path, modules=("Core",))
    assert len(rp_issues) == 2

    drift = audit.check_wordinfo_drift(tmp_path, modules=("Core",))
    assert len(drift) == 1

    parsed = audit.analyze_translation_report(report)
    assert parsed["Missing keyed translations"] == ["Key1: Sample"]
    assert parsed["Unnecessary keyed translations"] == ["OldKey"]
