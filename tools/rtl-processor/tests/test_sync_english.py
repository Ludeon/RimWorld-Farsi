import importlib.util
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "translation-tools"
    / "sync_english.py"
)
SPEC = importlib.util.spec_from_file_location("sync_english", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
sync_english = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync_english)


def test_sync_english_modules_copies_and_normalizes(tmp_path: Path) -> None:
    game_data = tmp_path / "Data"
    core_en = game_data / "Core" / "Languages" / "English" / "Keyed"
    core_en.mkdir(parents=True)
    sample = core_en / "Menu_Options.xml"
    sample.write_text("<LanguageData><OK>OK</OK></LanguageData>", encoding="utf-8")
    sample.chmod(0o755)

    dest = tmp_path / "src" / "english"
    stale_dir = dest / "Core"
    stale_dir.mkdir(parents=True)
    (stale_dir / "Stale.xml").write_text("<LanguageData />", encoding="utf-8")

    counts = sync_english.sync_english_modules(game_data, dest_dir=dest)
    assert counts == {"Core": 1}
    copied = dest / "Core" / "Keyed" / "Menu_Options.xml"
    assert copied.is_file()
    assert (copied.stat().st_mode & 0o111) == 0
    assert not (dest / "Core" / "Stale.xml").exists()


def test_sync_english_dry_run_does_not_write(tmp_path: Path) -> None:
    game_data = tmp_path / "Data"
    royalty_en = game_data / "Royalty" / "Languages" / "English" / "Keyed"
    royalty_en.mkdir(parents=True)
    (royalty_en / "Misc.xml").write_text("<LanguageData />", encoding="utf-8")

    dest = tmp_path / "src" / "english"
    counts = sync_english.sync_english_modules(game_data, dest_dir=dest, dry_run=True)
    assert counts == {"Royalty": 1}
    assert not dest.exists()
