import importlib.util
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "translation-tools"
    / "build_essential.py"
)
SPEC = importlib.util.spec_from_file_location("build_essential", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
build_essential = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_essential)


def test_create_essential_build_replaces_strings_with_english(tmp_path: Path) -> None:
    build_dir = tmp_path / "Data"
    core_keyed = build_dir / "Core" / "Keyed"
    core_strings = build_dir / "Core" / "Strings" / "Words"
    core_keyed.mkdir(parents=True)
    core_strings.mkdir(parents=True)
    (core_keyed / "Menus.xml").write_text("<LanguageData><OK>تایید</OK></LanguageData>", encoding="utf-8")
    (core_strings / "Animals.txt").write_text("مافالو", encoding="utf-8")
    (core_strings / "ExtraPersianOnly.txt").write_text("اضافی", encoding="utf-8")

    # Biotech has no Persian Strings, only English Strings
    bio_keyed = build_dir / "Biotech" / "Keyed"
    bio_keyed.mkdir(parents=True)
    (bio_keyed / "Alerts.xml").write_text("<LanguageData><A>ب</A></LanguageData>", encoding="utf-8")

    en_dir = tmp_path / "src" / "english"
    en_core_strings = en_dir / "Core" / "Strings" / "Words"
    en_core_strings.mkdir(parents=True)
    (en_core_strings / "Animals.txt").write_text("muffalo", encoding="utf-8")

    en_bio_strings = en_dir / "Biotech" / "Strings" / "Names"
    en_bio_strings.mkdir(parents=True)
    (en_bio_strings / "Mech_Unisex.txt").write_text("Bot", encoding="utf-8")

    out_dir = tmp_path / "Data-essential"
    counts = build_essential.create_essential_build(
        build_dir=build_dir,
        output_dir=out_dir,
        english_dir=en_dir,
    )

    assert counts == {"Core": 1, "Biotech": 1}
    assert (out_dir / "Core" / "Keyed" / "Menus.xml").read_text(encoding="utf-8") == "<LanguageData><OK>تایید</OK></LanguageData>"
    assert (out_dir / "Core" / "Strings" / "Words" / "Animals.txt").read_text(encoding="utf-8") == "muffalo"
    assert not (out_dir / "Core" / "Strings" / "Words" / "ExtraPersianOnly.txt").exists()
    assert (out_dir / "Biotech" / "Strings" / "Names" / "Mech_Unisex.txt").read_text(encoding="utf-8") == "Bot"


def test_create_essential_build_handles_nested_module_layout(tmp_path: Path) -> None:
    build_dir = tmp_path / "Data"
    nested_core = build_dir / "Core" / "Core"
    (nested_core / "Keyed").mkdir(parents=True)
    (nested_core / "Strings").mkdir(parents=True)
    (nested_core / "Keyed" / "Misc.xml").write_text("<LanguageData />", encoding="utf-8")
    (nested_core / "Strings" / "Old.txt").write_text("فارسی", encoding="utf-8")

    en_dir = tmp_path / "src" / "english"
    (en_dir / "Core" / "Strings").mkdir(parents=True)
    (en_dir / "Core" / "Strings" / "Names.txt").write_text("Alice", encoding="utf-8")

    out_dir = tmp_path / "Data-essential"
    counts = build_essential.create_essential_build(
        build_dir=build_dir,
        output_dir=out_dir,
        english_dir=en_dir,
    )

    assert counts == {"Core": 1}
    assert not (out_dir / "Core" / "Core" / "Strings" / "Old.txt").exists()
    assert (out_dir / "Core" / "Core" / "Strings" / "Names.txt").read_text(encoding="utf-8") == "Alice"
