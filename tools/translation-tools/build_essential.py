#!/usr/bin/env python3
"""
Build the Essential (English Strings) edition from a processed Persian build.

Copies a processed language build directory and replaces each module's
``Strings/`` directory with the verbatim English ``Strings/`` directory from
``src/english/<Module>/Strings/`` (when present), removing any Persian
``Strings/`` translations that are not yet ready for production.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

MODULES = ("Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey")
DEFAULT_ENGLISH_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "english"


def _resolve_module_root(module_dir: Path, module_name: str) -> Path:
    """Handle both flat (<dir>/<Module>) and nested (<dir>/<Module>/<Module>) layouts."""
    nested = module_dir / module_name
    if nested.is_dir() and (
        (nested / "DefInjected").is_dir()
        or (nested / "Keyed").is_dir()
        or (nested / "LanguageInfo.xml").is_file()
    ):
        return nested
    return module_dir


def create_essential_build(
    build_dir: Path,
    output_dir: Path,
    english_dir: Path = DEFAULT_ENGLISH_DIR,
    modules: tuple[str, ...] = MODULES,
) -> dict[str, int]:
    """Create ``output_dir`` from ``build_dir`` using English ``Strings/`` files.

    Returns a mapping of ``{module_name: english_strings_file_count}`` for each
    module processed.
    """
    if not build_dir.is_dir():
        raise FileNotFoundError(f"Build directory not found: {build_dir}")
    if not english_dir.is_dir():
        raise FileNotFoundError(f"English reference directory not found: {english_dir}")

    if output_dir.exists():
        shutil.rmtree(output_dir)
    shutil.copytree(build_dir, output_dir)

    replaced_counts: dict[str, int] = {}

    for module in modules:
        out_module = output_dir / module
        if not out_module.is_dir():
            continue

        module_root = _resolve_module_root(out_module, module)
        fa_strings = module_root / "Strings"
        if fa_strings.exists():
            shutil.rmtree(fa_strings)

        en_strings = english_dir / module / "Strings"
        if en_strings.is_dir():
            shutil.copytree(en_strings, fa_strings)
            replaced_counts[module] = sum(1 for p in fa_strings.rglob("*") if p.is_file())
        else:
            replaced_counts[module] = 0

    return replaced_counts


def main() -> int:
    """CLI entrypoint for assembling the Essential build directory."""
    parser = argparse.ArgumentParser(
        description="Assemble Essential Persian edition (with English Strings/) from a full build."
    )
    parser.add_argument(
        "--build-dir",
        required=True,
        type=Path,
        help="Path to the processed Full build directory (e.g. Data/)",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Destination path for the Essential build directory",
    )
    parser.add_argument(
        "--english-dir",
        type=Path,
        default=DEFAULT_ENGLISH_DIR,
        help=f"Path to English reference files (default: {DEFAULT_ENGLISH_DIR})",
    )
    args = parser.parse_args()

    try:
        counts = create_essential_build(
            build_dir=args.build_dir,
            output_dir=args.output_dir,
            english_dir=args.english_dir,
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    for module, count in counts.items():
        print(f"Essential {module}: {count} English Strings file(s)")
    print(f"Essential build ready at: {args.output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
