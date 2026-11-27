#!/usr/bin/env python3
"""
Portable Dev-Language Round-Trip Sync Tool for RimWorld-Farsi.

Manages a raw UTF-8 development language folder (default: ``Parsi``) inside a
local RimWorld installation so RimWorld's built-in Dev Mode tools
(``Cleanup translation files``, ``Save translation report``) can run cleanly
against raw UTF-8 source translations without touching the pre-shaped
``Persian (فارسی)`` play pack or corrupting repo-specific metadata.

Game path resolution order (no personal paths hardcoded in the repository):
  1. Explicit ``--game-path`` CLI argument
  2. ``RIMWORLD_GAME_PATH`` environment variable
  3. Gitignored ``.rimworld-local.json`` config in repository root
  4. Standard cross-platform RimWorld installation paths
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

MODULES = ("Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey")
DEFAULT_LANG_FOLDER = "Parsi"
DEFAULT_NATIVE_NAME = "Parsi (Dev Raw)"
LOCAL_CONFIG_FILENAME = ".rimworld-local.json"
SYNCABLE_SUBDIRS = ("Keyed", "DefInjected", "Backstories", "Strings")
PROTECTED_TOP_ITEMS = {"LanguageInfo.xml", "WordInfo", "LangIcon.png"}


@dataclass
class SyncStats:
    """Summary of push or pull operations."""

    modules_synced: int = 0
    files_copied: int = 0
    files_pruned: int = 0
    todo_tags: list[str] = field(default_factory=list)


def get_generic_candidate_paths() -> list[Path]:
    """Return standard cross-platform RimWorld directories without user-specific paths."""
    home = Path.home()
    candidates = [
        home / ".steam" / "steam" / "steamapps" / "common" / "RimWorld",
        home / ".local" / "share" / "Steam" / "steamapps" / "common" / "RimWorld",
        home
        / ".var"
        / "app"
        / "com.valvesoftware.Steam"
        / ".local"
        / "share"
        / "Steam"
        / "steamapps"
        / "common"
        / "RimWorld",
        home / "Games" / "RimWorld",
        home / "Games" / "Heroic" / "RimWorld",
        home / "GOG Games" / "RimWorld",
        home
        / "Library"
        / "Application Support"
        / "Steam"
        / "steamapps"
        / "common"
        / "RimWorld"
        / "RimWorldMac.app",
    ]
    if os.name == "nt":
        for drive in ("C:", "D:", "E:", "F:"):
            candidates.append(
                Path(drive) / "Program Files (x86)" / "Steam" / "steamapps" / "common" / "RimWorld"
            )
            candidates.append(Path(drive) / "SteamLibrary" / "steamapps" / "common" / "RimWorld")
            candidates.append(Path(drive) / "GOG Games" / "RimWorld")
    return candidates


def is_valid_game_dir(path: Path) -> bool:
    """Check whether ``path`` looks like a RimWorld root directory."""
    return (path / "Data" / "Core").is_dir()


def load_saved_game_path(repo_root: Path) -> Path | None:
    """Read ``.rimworld-local.json`` in ``repo_root`` if present and valid."""
    config_file = repo_root / LOCAL_CONFIG_FILENAME
    if not config_file.is_file():
        return None
    try:
        data = json.loads(config_file.read_text(encoding="utf-8"))
        raw = data.get("game_path")
        if isinstance(raw, str) and raw.strip():
            return Path(raw.strip()).expanduser()
    except (OSError, json.JSONDecodeError):
        return None
    return None


def save_local_game_path(repo_root: Path, game_path: Path) -> Path:
    """Persist ``game_path`` to the gitignored ``.rimworld-local.json`` file."""
    config_file = repo_root / LOCAL_CONFIG_FILENAME
    payload = {"game_path": str(game_path.resolve())}
    config_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return config_file


def resolve_game_path(repo_root: Path, explicit_path: Path | None = None) -> Path:
    """Resolve and validate the RimWorld installation directory."""
    if explicit_path is not None:
        candidate = explicit_path.expanduser().resolve()
        if not is_valid_game_dir(candidate):
            raise FileNotFoundError(
                f"Invalid RimWorld directory (missing Data/Core): {candidate}"
            )
        return candidate

    env_val = os.environ.get("RIMWORLD_GAME_PATH", "").strip()
    if env_val:
        candidate = Path(env_val).expanduser().resolve()
        if is_valid_game_dir(candidate):
            return candidate
        raise FileNotFoundError(
            f"RIMWORLD_GAME_PATH points to invalid RimWorld directory: {candidate}"
        )

    saved = load_saved_game_path(repo_root)
    if saved is not None and is_valid_game_dir(saved):
        return saved.resolve()

    for candidate in get_generic_candidate_paths():
        if is_valid_game_dir(candidate):
            return candidate.resolve()

    raise FileNotFoundError(
        "Could not locate RimWorld installation. Pass --game-path, set "
        "RIMWORLD_GAME_PATH, or save it with --save-path."
    )


def rewrite_dev_language_info(
    lang_info_path: Path,
    lang_folder: str = DEFAULT_LANG_FOLDER,
    native_name: str = DEFAULT_NATIVE_NAME,
) -> None:
    """Update a game-side ``LanguageInfo.xml`` for standalone raw dev inspection."""
    content = lang_info_path.read_text(encoding="utf-8")
    content = re.sub(
        r"<friendlyNameNative>.*?</friendlyNameNative>",
        f"<friendlyNameNative>{native_name}</friendlyNameNative>",
        content,
        flags=re.DOTALL,
    )
    content = re.sub(
        r"<friendlyNameEnglish>.*?</friendlyNameEnglish>",
        f"<friendlyNameEnglish>{lang_folder}</friendlyNameEnglish>",
        content,
        flags=re.DOTALL,
    )
    content = re.sub(
        r"<languageWorkerClass>.*?</languageWorkerClass>",
        "<languageWorkerClass>LanguageWorker_English</languageWorkerClass>",
        content,
        flags=re.DOTALL,
    )
    lang_info_path.write_text(content, encoding="utf-8")


def push_dev_language(
    repo_root: Path,
    game_path: Path,
    lang_folder: str = DEFAULT_LANG_FOLDER,
    native_name: str = DEFAULT_NATIVE_NAME,
    skip_strings: bool = False,
    dry_run: bool = False,
) -> SyncStats:
    """Copy raw UTF-8 translation modules from ``repo_root`` to the game's dev language folder."""
    stats = SyncStats()
    subdirs = tuple(d for d in SYNCABLE_SUBDIRS if not (skip_strings and d == "Strings"))

    for module in MODULES:
        src_mod = repo_root / module
        game_mod = game_path / "Data" / module
        if not src_mod.is_dir() or not game_mod.is_dir():
            continue

        dest_lang = game_mod / "Languages" / lang_folder
        stats.modules_synced += 1

        if not dry_run:
            if dest_lang.exists():
                shutil.rmtree(dest_lang)
            dest_lang.mkdir(parents=True, exist_ok=True)

            # Purge cached .tar so RimWorld reads updated raw XMLs
            tar_file = game_mod / "Languages" / f"{lang_folder}.tar"
            if tar_file.exists():
                tar_file.unlink()

        for subdir in subdirs:
            src_sub = src_mod / subdir
            if not src_sub.is_dir():
                continue
            file_count = sum(1 for p in src_sub.rglob("*") if p.is_file())
            stats.files_copied += file_count
            if not dry_run:
                shutil.copytree(src_sub, dest_lang / subdir)

        for top_file in ("LanguageInfo.xml", "LangIcon.png"):
            src_file = src_mod / top_file
            if not src_file.is_file():
                continue
            stats.files_copied += 1
            if not dry_run:
                dest_file = dest_lang / top_file
                shutil.copy2(src_file, dest_file)
                if top_file == "LanguageInfo.xml":
                    rewrite_dev_language_info(
                        dest_file, lang_folder=lang_folder, native_name=native_name
                    )

    return stats


def _find_todo_tags(xml_path: Path) -> list[str]:
    """Return line references for any ``>TODO<`` stubs inside ``xml_path``."""
    todos: list[str] = []
    try:
        for idx, line in enumerate(xml_path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            if re.search(r">\s*TODO\s*<", line):
                todos.append(f"{xml_path.name}:{idx}: {line.strip()}")
    except OSError:
        pass
    return todos


def _prepare_pulled_bytes(
    src_file: Path, target_file: Path, preserve_eol: bool
) -> tuple[bytes, bool]:
    """Read ``src_file`` bytes, optionally matching ``target_file``'s line endings.

    Returns ``(bytes_to_write, changed)``.
    """
    src_bytes = src_file.read_bytes()
    if not target_file.is_file():
        return src_bytes, True

    target_bytes = target_file.read_bytes()
    if preserve_eol:
        target_uses_crlf = b"\r\n" in target_bytes
        src_uses_crlf = b"\r\n" in src_bytes
        if not target_uses_crlf and src_uses_crlf:
            src_bytes = src_bytes.replace(b"\r\n", b"\n")
        elif target_uses_crlf and not src_uses_crlf:
            src_bytes = src_bytes.replace(b"\n", b"\r\n")

    return src_bytes, src_bytes != target_bytes


def pull_dev_language(
    repo_root: Path,
    game_path: Path,
    lang_folder: str = DEFAULT_LANG_FOLDER,
    skip_strings: bool = False,
    prune: bool = False,
    preserve_eol: bool = False,
    dry_run: bool = False,
) -> SyncStats:
    """Pull cleaned raw UTF-8 translations from ``game_path`` back into ``repo_root``.

    Strictly protects ``LanguageInfo.xml``, ``WordInfo/``, and ``LangIcon.png`` in the repo.
    """
    stats = SyncStats()
    subdirs = tuple(d for d in SYNCABLE_SUBDIRS if not (skip_strings and d == "Strings"))

    for module in MODULES:
        repo_mod = repo_root / module
        src_lang = game_path / "Data" / module / "Languages" / lang_folder
        if not repo_mod.is_dir() or not src_lang.is_dir():
            continue

        stats.modules_synced += 1

        for subdir in subdirs:
            src_sub = src_lang / subdir
            repo_sub = repo_mod / subdir

            if not src_sub.is_dir():
                continue

            # Track relative files from game dev folder
            src_rel_files = {
                p.relative_to(src_sub): p
                for p in src_sub.rglob("*")
                if p.is_file()
            }

            if prune and repo_sub.is_dir():
                repo_rel_files = [
                    p for p in repo_sub.rglob("*") if p.is_file()
                ]
                for repo_file in repo_rel_files:
                    rel = repo_file.relative_to(repo_sub)
                    if rel not in src_rel_files:
                        stats.files_pruned += 1
                        if not dry_run:
                            repo_file.unlink()

            for rel, src_file in sorted(src_rel_files.items()):
                # Defensive guard: never overwrite protected metadata even if misplaced
                if rel.parts and rel.parts[0] in PROTECTED_TOP_ITEMS:
                    continue

                target_file = repo_sub / rel
                payload, changed = _prepare_pulled_bytes(
                    src_file, target_file, preserve_eol=preserve_eol
                )
                if src_file.suffix.lower() == ".xml":
                    stats.todo_tags.extend(_find_todo_tags(src_file))

                if not changed:
                    continue

                stats.files_copied += 1
                if not dry_run:
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    target_file.write_bytes(payload)

    return stats


def main() -> int:
    """CLI entrypoint."""
    repo_root = Path(__file__).resolve().parent.parent.parent

    parser = argparse.ArgumentParser(
        description="Push/pull raw UTF-8 dev language ('Parsi') for RimWorld Dev Mode cleanup."
    )
    parser.add_argument(
        "action",
        choices=("push", "pull"),
        help="'push' deploys raw repo XMLs to Data/<DLC>/Languages/Parsi; 'pull' brings cleaned files back.",
    )
    parser.add_argument(
        "--game-path",
        type=Path,
        default=None,
        help="Path to RimWorld installation (or set RIMWORLD_GAME_PATH / .rimworld-local.json)",
    )
    parser.add_argument(
        "--save-path",
        action="store_true",
        help=f"Save resolved --game-path into gitignored {LOCAL_CONFIG_FILENAME}",
    )
    parser.add_argument(
        "--lang-folder",
        default=DEFAULT_LANG_FOLDER,
        help=f"Target language folder name inside game Data/<DLC>/Languages/ (default: {DEFAULT_LANG_FOLDER})",
    )
    parser.add_argument(
        "--native-name",
        default=DEFAULT_NATIVE_NAME,
        help=f"Display name in RimWorld language selector (default: '{DEFAULT_NATIVE_NAME}')",
    )
    parser.add_argument(
        "--skip-strings",
        action="store_true",
        help="Skip syncing Strings/ directory",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="(pull only) Delete files in synced repo subdirs that were removed by RimWorld cleanup",
    )
    parser.add_argument(
        "--preserve-eol",
        action="store_true",
        help="(pull only) Preserve existing repo file line endings (LF/CRLF) and skip unchanged files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview counts without modifying files",
    )
    args = parser.parse_args()

    try:
        game_path = resolve_game_path(repo_root, args.game_path)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.save_path and not args.dry_run:
        cfg = save_local_game_path(repo_root, game_path)
        print(f"Saved local game path to gitignored config: {cfg.name}")

    prefix = "[DRY-RUN] " if args.dry_run else ""
    if args.action == "push":
        stats = push_dev_language(
            repo_root=repo_root,
            game_path=game_path,
            lang_folder=args.lang_folder,
            native_name=args.native_name,
            skip_strings=args.skip_strings,
            dry_run=args.dry_run,
        )
        print(
            f"{prefix}Pushed raw dev language '{args.lang_folder}' ({args.native_name}): "
            f"{stats.modules_synced} module(s), {stats.files_copied} file(s)."
        )
    else:
        stats = pull_dev_language(
            repo_root=repo_root,
            game_path=game_path,
            lang_folder=args.lang_folder,
            skip_strings=args.skip_strings,
            prune=args.prune,
            preserve_eol=args.preserve_eol,
            dry_run=args.dry_run,
        )
        print(
            f"{prefix}Pulled cleaned files from '{args.lang_folder}': "
            f"{stats.modules_synced} module(s), {stats.files_copied} file(s) synced, "
            f"{stats.files_pruned} obsolete file(s) pruned."
        )
        if stats.todo_tags:
            print(f"Detected {len(stats.todo_tags)} TODO stub(s) in pulled XMLs:")
            for item in stats.todo_tags[:15]:
                print(f"  - {item}")
            if len(stats.todo_tags) > 15:
                print(f"  ... and {len(stats.todo_tags) - 15} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
