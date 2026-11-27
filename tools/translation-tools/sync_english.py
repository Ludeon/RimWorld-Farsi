#!/usr/bin/env python3
"""
Sync Original English Language Files into ``src/english/``.

Mirrors ``<RimWorld>/Data/<Module>/Languages/English/`` for all supported
RimWorld modules into the repository's ``src/english/`` reference directory
with normalized file permissions (non-executable regular files).
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

MODULES = ("Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey")
DEFAULT_DEST_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "english"


def _normalize_permissions(directory: Path) -> int:
    """Set standard directory (0755) and file (0644) permissions; return file count."""
    file_count = 0
    for root, _, files in os.walk(directory):
        os.chmod(root, 0o755)
        for filename in files:
            os.chmod(Path(root) / filename, 0o644)
            file_count += 1
    return file_count


def sync_english_modules(
    game_data_dir: Path,
    dest_dir: Path = DEFAULT_DEST_DIR,
    modules: tuple[str, ...] = MODULES,
    dry_run: bool = False,
) -> dict[str, int]:
    """Copy ``Languages/English`` from each module in ``game_data_dir`` to ``dest_dir``."""
    if not game_data_dir.is_dir():
        raise FileNotFoundError(f"Game Data directory not found: {game_data_dir}")

    counts: dict[str, int] = {}
    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)

    for module in modules:
        src = game_data_dir / module / "Languages" / "English"
        if not src.is_dir():
            continue

        target = dest_dir / module
        if dry_run:
            counts[module] = sum(1 for p in src.rglob("*") if p.is_file())
            continue

        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(src, target)
        counts[module] = _normalize_permissions(target)

    return counts


def main() -> int:
    """CLI entrypoint for syncing official English files."""
    parser = argparse.ArgumentParser(
        description="Mirror RimWorld Languages/English files into src/english/."
    )
    parser.add_argument(
        "--game-data-dir",
        required=True,
        type=Path,
        help="Path to RimWorld's Data/ directory (containing Core/, Royalty/, etc.)",
    )
    parser.add_argument(
        "--dest-dir",
        type=Path,
        default=DEFAULT_DEST_DIR,
        help=f"Destination English reference directory (default: {DEFAULT_DEST_DIR})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report modules and file counts without modifying disk",
    )
    args = parser.parse_args()

    try:
        counts = sync_english_modules(
            game_data_dir=args.game_data_dir,
            dest_dir=args.dest_dir,
            dry_run=args.dry_run,
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not counts:
        print(
            f"Error: No <Module>/Languages/English directories found under {args.game_data_dir}",
            file=sys.stderr,
        )
        return 1

    prefix = "[DRY-RUN] " if args.dry_run else ""
    for module, count in counts.items():
        print(f"{prefix}Synced {module}: {count} file(s)")
    print(f"{prefix}Total: {sum(counts.values())} file(s) -> {args.dest_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
