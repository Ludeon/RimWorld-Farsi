"""
Coverage & integration tests for run_qa, validate_xml, find_missing_translations, and install.sh.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "qa"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "rtl-processor"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "translation-tools"))

# ruff: noqa: E402
import find_missing_translations
import run_qa
import validate_xml


def test_validate_xml_file_and_directory(tmp_path: Path) -> None:
    valid_xml = tmp_path / "Good.xml"
    valid_xml.write_text(
        '<?xml version="1.0" encoding="utf-8"?><LanguageData><OK>تایید</OK></LanguageData>',
        encoding="utf-8",
    )
    bad_xml = tmp_path / "Bad.xml"
    bad_xml.write_text("<LanguageData><Open></LanguageData>", encoding="utf-8")

    ok, err = validate_xml.validate_xml_file(str(valid_xml))
    assert ok and err == ""
    ok_bad, err_bad = validate_xml.validate_xml_file(str(bad_xml))
    assert not ok_bad and err_bad

    total, valid_count, errors = validate_xml.validate_directory(str(tmp_path))
    assert total == 2
    assert valid_count == 1
    assert len(errors) == 1


def test_find_missing_translations_parses_clean_xml(tmp_path: Path) -> None:
    xml_path = tmp_path / "Sample.xml"
    xml_path.write_text(
        '<?xml version="1.0" encoding="utf-8"?><LanguageData><Yes>بله</Yes><Empty></Empty></LanguageData>',
        encoding="utf-8",
    )
    parsed = find_missing_translations.parse_xml_file(xml_path)
    assert parsed == {"Yes": "بله", "Empty": ""}

    lang_info = tmp_path / "LanguageInfo.xml"
    lang_info.write_text("<LanguageInfo><friendlyNameEnglish>Persian</friendlyNameEnglish></LanguageInfo>", encoding="utf-8")
    assert find_missing_translations.parse_xml_file(lang_info) == {}


def test_run_qa_suite_pass_and_fail(tmp_path: Path) -> None:
    core_keyed = tmp_path / "Core" / "Keyed"
    core_keyed.mkdir(parents=True)
    good_file = core_keyed / "Menus.xml"
    good_file.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<LanguageData>\n  <!-- EN: OK {0} -->\n  <OK>تایید {0}</OK>\n</LanguageData>\n',
        encoding="utf-8",
    )
    assert run_qa.run_qa_suite(tmp_path, dlcs=["Core"]) == 0

    # Introduce placeholder + typography + reportString + terminology errors
    bad_file = core_keyed / "Bad.xml"
    bad_file.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<LanguageData>\n'
        '  <!-- EN: Colonist {0} -->\n'
        '  <Colonist>کلونیست ها</Colonist>\n'
        '  <Task.reportString>در حال کار.</Task.reportString>\n'
        '</LanguageData>\n',
        encoding="utf-8",
    )
    assert run_qa.run_qa_suite(tmp_path, dlcs=["Core"]) == 1


def test_install_sh_cli_validation_and_local_install(tmp_path: Path) -> None:
    install_sh = REPO_ROOT / "install.sh"

    help_res = subprocess.run(
        ["bash", str(install_sh), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert help_res.returncode == 0
    assert "--local" in help_res.stdout

    bad_flag = subprocess.run(
        ["bash", str(install_sh), "--unknown-flag-xyz"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert bad_flag.returncode != 0

    # Simulate local bundled offline install without touching network
    bundle_dir = tmp_path / "bundle"
    (bundle_dir / "Core" / "Keyed").mkdir(parents=True)
    (bundle_dir / "Core" / "Keyed" / "Menu.xml").write_text(
        "<LanguageData><OK>OK</OK></LanguageData>", encoding="utf-8"
    )
    (bundle_dir / ".release-edition").write_text("essential\n", encoding="utf-8")
    shutil.copy2(install_sh, bundle_dir / "install.sh")

    game_dir = tmp_path / "RimWorld"
    (game_dir / "Data" / "Core" / "Languages").mkdir(parents=True)
    env = os.environ.copy()
    res = subprocess.run(
        ["bash", str(bundle_dir / "install.sh"), "--local", "--no-mod", str(game_dir)],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert res.returncode == 0, res.stderr + res.stdout
    assert (
        game_dir / "Data" / "Core" / "Languages" / "Persian (فارسی)" / "Keyed" / "Menu.xml"
    ).is_file()
