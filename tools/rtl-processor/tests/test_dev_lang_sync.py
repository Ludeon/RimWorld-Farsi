import importlib.util
import sys
from pathlib import Path

import pytest

MODULE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "translation-tools"
    / "dev_lang_sync.py"
)
SPEC = importlib.util.spec_from_file_location("dev_lang_sync", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
dev_lang_sync = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = dev_lang_sync
SPEC.loader.exec_module(dev_lang_sync)


def _setup_fake_repo_and_game(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    game = tmp_path / "RimWorld"

    core_repo = repo / "Core"
    (core_repo / "Keyed").mkdir(parents=True)
    (core_repo / "WordInfo").mkdir(parents=True)
    (core_repo / "Strings").mkdir(parents=True)
    (core_repo / "Keyed" / "Menus.xml").write_text(
        "<LanguageData><OK>تایید</OK></LanguageData>", encoding="utf-8"
    )
    (core_repo / "WordInfo" / "ezafeh.txt").write_text("خانه", encoding="utf-8")
    (core_repo / "Strings" / "Names.txt").write_text("علی", encoding="utf-8")
    (core_repo / "LanguageInfo.xml").write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<LanguageInfo>
  <friendlyNameNative>پارسی</friendlyNameNative>
  <friendlyNameEnglish>Persian</friendlyNameEnglish>
  <languageWorkerClass>RTL_Persian.LanguageWorker_Persian</languageWorkerClass>
</LanguageInfo>
""",
        encoding="utf-8",
    )

    (game / "Data" / "Core" / "Languages").mkdir(parents=True)
    return repo, game


def test_resolve_game_path_via_saved_local_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("RIMWORLD_GAME_PATH", raising=False)
    repo, game = _setup_fake_repo_and_game(tmp_path)
    dev_lang_sync.save_local_game_path(repo, game)

    resolved = dev_lang_sync.resolve_game_path(repo)
    assert resolved == game.resolve()


def test_push_dev_language_keeps_raw_utf8_and_sets_dev_language_info(
    tmp_path: Path,
) -> None:
    repo, game = _setup_fake_repo_and_game(tmp_path)
    tar_cache = game / "Data" / "Core" / "Languages" / "Parsi.tar"
    tar_cache.write_text("stale", encoding="utf-8")

    stats = dev_lang_sync.push_dev_language(repo, game, skip_strings=True)
    assert stats.modules_synced == 1
    assert not tar_cache.exists()

    pushed_xml = game / "Data" / "Core" / "Languages" / "Parsi" / "Keyed" / "Menus.xml"
    assert "تایید" in pushed_xml.read_text(encoding="utf-8")
    assert not (game / "Data" / "Core" / "Languages" / "Parsi" / "Strings").exists()

    lang_info = (
        game / "Data" / "Core" / "Languages" / "Parsi" / "LanguageInfo.xml"
    ).read_text(encoding="utf-8")
    assert "<friendlyNameNative>Parsi (Dev Raw)</friendlyNameNative>" in lang_info
    assert "<friendlyNameEnglish>Parsi</friendlyNameEnglish>" in lang_info
    assert (
        "<languageWorkerClass>LanguageWorker_English</languageWorkerClass>" in lang_info
    )


def test_pull_dev_language_protects_repo_metadata_and_wordinfo(tmp_path: Path) -> None:
    repo, game = _setup_fake_repo_and_game(tmp_path)
    dev_lang_sync.push_dev_language(repo, game)

    # Simulate RimWorld Dev Mode cleanup editing Keyed, deleting an obsolete file, and modifying LanguageInfo
    parsi_dir = game / "Data" / "Core" / "Languages" / "Parsi"
    (parsi_dir / "Keyed" / "Menus.xml").write_text(
        "<LanguageData><OK>تایید</OK><NewKey>TODO</NewKey></LanguageData>",
        encoding="utf-8",
    )
    (repo / "Core" / "Keyed" / "Obsolete.xml").write_text(
        "<LanguageData />", encoding="utf-8"
    )

    stats = dev_lang_sync.pull_dev_language(repo, game, skip_strings=True, prune=True)
    assert stats.modules_synced == 1
    assert stats.files_pruned == 1
    assert len(stats.todo_tags) == 1

    # Protected files in repo must remain untouched
    repo_lang_info = (repo / "Core" / "LanguageInfo.xml").read_text(encoding="utf-8")
    assert "RTL_Persian.LanguageWorker_Persian" in repo_lang_info
    assert (repo / "Core" / "WordInfo" / "ezafeh.txt").read_text(
        encoding="utf-8"
    ) == "خانه"
    assert not (repo / "Core" / "Keyed" / "Obsolete.xml").exists()
    assert "NewKey" in (repo / "Core" / "Keyed" / "Menus.xml").read_text(
        encoding="utf-8"
    )


def test_pull_preserve_eol_skips_crlf_only_rewrites(tmp_path: Path) -> None:
    repo, game = _setup_fake_repo_and_game(tmp_path)
    repo_xml = repo / "Core" / "Keyed" / "Menus.xml"
    repo_xml.write_bytes(b"<LanguageData>\n  <OK>ok</OK>\n</LanguageData>\n")

    dev_lang_sync.push_dev_language(repo, game)
    game_xml = game / "Data" / "Core" / "Languages" / "Parsi" / "Keyed" / "Menus.xml"
    game_xml.write_bytes(b"<LanguageData>\r\n  <OK>ok</OK>\r\n</LanguageData>\r\n")

    stats = dev_lang_sync.pull_dev_language(
        repo, game, skip_strings=True, preserve_eol=True
    )
    assert stats.files_copied == 0
    assert repo_xml.read_bytes() == b"<LanguageData>\n  <OK>ok</OK>\n</LanguageData>\n"
