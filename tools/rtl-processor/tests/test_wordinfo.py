"""
Unit tests for tools/translation-tools/update_wordinfo.py
"""

import sys
from pathlib import Path

# Ensure translation-tools is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "translation-tools"))

# ruff: noqa: E402
from update_wordinfo import (
    ZWNJ,
    clean_label,
    generate_persian_ezafeh,
    generate_persian_plural,
    load_existing_table,
    normalize_persian_text,
    update_dlc_wordinfo,
    write_table,
)


def test_normalize_persian_text() -> None:
    assert normalize_persian_text("كتاب") == "کتاب"
    assert normalize_persian_text("عربي") == "عربی"
    assert normalize_persian_text("موسيقى") == "موسیقی"
    assert normalize_persian_text("   سلام   دنیا   ") == "سلام دنیا"
    assert normalize_persian_text("") == ""


def test_clean_label() -> None:
    assert clean_label("تفنگ.") == "تفنگ"
    assert clean_label("<!-- comment -->دیوار،") == "دیوار"
    assert clean_label("كفش؟") == "کفش"


def test_generate_persian_plural_animate() -> None:
    # Known human / animate words
    assert generate_persian_plural("استعمارگر") == "استعمارگران"
    assert generate_persian_plural("ساکن") == "ساکنان"
    assert generate_persian_plural("مهاجم") == "مهاجمان"
    assert generate_persian_plural("جنگجو") == "جنگجویان"
    assert generate_persian_plural("پزشک") == "پزشکان"
    assert generate_persian_plural("برده") == "بردگان"
    assert generate_persian_plural("دوست") == "دوستان"


def test_generate_persian_plural_inanimate() -> None:
    # General nouns with ZWNJ + ها
    assert generate_persian_plural("تفنگ") == f"تفنگ{ZWNJ}ها"
    assert generate_persian_plural("میز") == f"میز{ZWNJ}ها"
    assert generate_persian_plural("چاقو") == f"چاقو{ZWNJ}ها"
    assert generate_persian_plural("درخت") == f"درخت{ZWNJ}ها"

    # Already pluralized
    assert generate_persian_plural("سربازان") == "سربازان"
    assert generate_persian_plural("میزها") == "میزها"


def test_generate_persian_ezafeh() -> None:
    # Ending in Vav or Alef -> append ی
    assert generate_persian_ezafeh("آبجو") == "آبجوی"
    assert generate_persian_ezafeh("چاقو") == "چاقوی"
    assert generate_persian_ezafeh("شورا") == "شورای"

    # Ending in silent He -> append ZWNJ + ی
    assert generate_persian_ezafeh("مستعمره") == f"مستعمره{ZWNJ}ی"
    assert generate_persian_ezafeh("سینه") == f"سینه{ZWNJ}ی"

    # Ending in Ye -> append Kasra
    assert generate_persian_ezafeh("کلونی") == "کلونی\u0650"

    # Ending in Consonant -> append Kasra
    assert generate_persian_ezafeh("تفنگ") == "تفنگ\u0650"
    assert generate_persian_ezafeh("آب") == "آب\u0650"


def test_table_io(tmp_path: Path) -> None:
    table_file = tmp_path / "test_table.txt"
    entries = {
        "کتاب": f"کتاب{ZWNJ}ها",
        "تفنگ": f"تفنگ{ZWNJ}ها",
    }
    header = "// Test header\n// KEY;VAL"
    write_table(table_file, header, entries)

    loaded = load_existing_table(table_file)
    assert len(loaded) == 2
    assert loaded["کتاب"] == f"کتاب{ZWNJ}ها"
    assert loaded["تفنگ"] == f"تفنگ{ZWNJ}ها"


def test_update_dlc_wordinfo_mock(tmp_path: Path) -> None:
    dlc_dir = tmp_path / "MockDLC"
    def_dir = dlc_dir / "DefInjected" / "ThingDef"
    def_dir.mkdir(parents=True)

    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<LanguageData>
  <Gun_Pistol.label>تپانچه</Gun_Pistol.label>
  <Apparel_Shield.label>سپر محافظ</Apparel_Shield.label>
</LanguageData>
"""
    (def_dir / "Weapons.xml").write_text(xml_content, encoding="utf-8")

    total, n_plur, n_eza = update_dlc_wordinfo(dlc_dir, dry_run=False)
    assert total == 2
    assert n_plur == 2
    assert n_eza == 2

    # Check generated files
    plural_file = dlc_dir / "WordInfo" / "plural.txt"
    ezafeh_file = dlc_dir / "WordInfo" / "ezafeh.txt"
    assert plural_file.exists()
    assert ezafeh_file.exists()

    plurals = load_existing_table(plural_file)
    assert "تپانچه" in plurals
    assert "سپر محافظ" in plurals
