"""Unit tests for tools/qa/generate_badges.py."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "qa"))

# ruff: noqa: E402
from generate_badges import BadgeGenerator, make_svg_badge


def test_make_svg_badge():
    svg = make_svg_badge("TestLabel", "TestValue", "#2ecc71")
    assert "<svg" in svg
    assert "TestLabel" in svg
    assert "TestValue" in svg
    assert "#2ecc71" in svg


def test_badge_generator_runs(tmp_path: Path):
    repo_dir = tmp_path / "repo"
    out_dir = tmp_path / "badges"

    core_keyed = repo_dir / "Core" / "Keyed"
    core_keyed.mkdir(parents=True)
    (core_keyed / "Test.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<LanguageData>\n'
        '  <Tag>سلام دنیا</Tag>\n'
        '</LanguageData>\n',
        encoding="utf-8"
    )

    gen = BadgeGenerator(repo_root=repo_dir)
    badges = gen.generate_all(output_dir=out_dir)

    assert len(badges) == 4
    assert (out_dir / "coverage.svg").exists()
    assert (out_dir / "qa_status.svg").exists()
    assert (out_dir / "corpus.svg").exists()
    assert (out_dir / "engine.svg").exists()
