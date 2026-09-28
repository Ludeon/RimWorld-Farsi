#!/usr/bin/env python3
"""
Granular WordInfo Domain Suite for RimWorld-Farsi.

Extracts domain-specific terminology into targeted WordInfo lookup tables
inspired by the German (RimWorld-de) localization pipeline:
  1. Hediffs (HediffDef) -> WordInfo/hediffs.txt (Diseases, injuries, bionics, chronic states)
  2. Pawn Capacities (PawnCapacityDef) -> WordInfo/capacities.txt (Consciousness, Moving, etc.)
  3. Character Traits (TraitDef) -> WordInfo/traits.txt (Personality traits & mental breaks)

Usage:
  python tools/translation-tools/wordinfo_domains.py
  python tools/translation-tools/wordinfo_domains.py --module Biotech
  python tools/translation-tools/wordinfo_domains.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import lxml.etree as ET

MODULES = ["Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey"]
ZWNJ = "\u200C"


def normalize_persian(text: str) -> str:
    """Replaces Arabic variants with Persian codepoints and trims whitespace."""
    if not text:
        return ""
    text = text.replace("\u0643", "\u06A9")  # ك -> ک
    text = text.replace("\u064A", "\u06CC")  # ي -> ی
    text = text.replace("\u0649", "\u06CC")  # ى -> ی
    text = " ".join(text.split())
    return text.strip()


def compute_ezafeh(word: str) -> str:
    """Computes grammatical Persian Ezāfeh connector for a noun."""
    if not word:
        return ""
    last_char = word[-1]
    # Nouns ending in vowels: ا or و take 'ی' connector
    if last_char in ("ا", "و"):
        return f"{word} ی"
    # Nouns ending in ه / silent-e take ZWNJ + 'ی'
    elif last_char in ("ه", "ة"):
        return f"{word}{ZWNJ}ی"
    # Standard nouns ending in consonants take silent kasreh
    else:
        return word


class DomainWordInfoExtractor:
    """Scans DefInjected XMLs for specific Def types and outputs domain tables."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir.resolve()

    def extract_domain(
        self, module: str, def_type: str, tag_suffix: str = ".label"
    ) -> dict[str, str]:
        """
        Extracts entries from <Module>/DefInjected/<DefType>/*.xml
        Returns {identifier: persian_label}.
        """
        results: dict[str, str] = {}
        target_dir = self.root_dir / module / "DefInjected" / def_type
        if not target_dir.exists():
            return results

        for root, _, files in os.walk(target_dir):
            for file in sorted(files):
                if not file.endswith(".xml"):
                    continue
                file_path = Path(root) / file
                try:
                    parser = ET.XMLParser(recover=True, remove_blank_text=True, resolve_entities=False)
                    tree = ET.parse(str(file_path), parser)
                    xml_root = tree.getroot()
                    if xml_root is None:
                        continue

                    for elem in xml_root:
                        if isinstance(elem.tag, str) and elem.tag.endswith(tag_suffix) and elem.text:
                            label = normalize_persian(elem.text)
                            if label and label != "TODO":
                                def_name = elem.tag[: -len(tag_suffix)]
                                results[def_name] = label
                except Exception as e:
                    print(f"Warning: Failed to parse {file_path}: {e}", file=sys.stderr)

        return results

    def write_table(self, file_path: Path, entries: dict[str, str], header_comment: str) -> int:
        """Writes domain lookup table in standard key: value or list format."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {header_comment}\n",
            "# Format: DefName: PersianLabel | EzāfehForm\n",
        ]
        for key in sorted(entries.keys()):
            label = entries[key]
            ezafeh = compute_ezafeh(label)
            lines.append(f"{key}: {label} | {ezafeh}\n")

        file_path.write_text("".join(lines), encoding="utf-8")
        return len(entries)

    def process_module(self, module: str, dry_run: bool = False) -> dict[str, int]:
        """Processes Hediffs, Capacities, and Traits for a given module."""
        stats: dict[str, int] = {}
        wordinfo_dir = self.root_dir / module / "WordInfo"

        # 1. Hediffs
        hediffs = self.extract_domain(module, "HediffDef", ".label")
        if hediffs:
            stats["hediffs"] = len(hediffs)
            if not dry_run:
                self.write_table(
                    wordinfo_dir / "hediffs.txt",
                    hediffs,
                    f"RimWorld Farsi - {module} Hediff Defs (Diseases & Implants)",
                )

        # 2. Pawn Capacities
        capacities = self.extract_domain(module, "PawnCapacityDef", ".label")
        if capacities:
            stats["capacities"] = len(capacities)
            if not dry_run:
                self.write_table(
                    wordinfo_dir / "capacities.txt",
                    capacities,
                    f"RimWorld Farsi - {module} Pawn Capacities (هوشیاری، بینایی، ...)",
                )

        # 3. Traits
        traits = self.extract_domain(module, "TraitDef", ".degreeLabels.0")
        traits_fallback = self.extract_domain(module, "TraitDef", ".label")
        traits.update(traits_fallback)
        if traits:
            stats["traits"] = len(traits)
            if not dry_run:
                self.write_table(
                    wordinfo_dir / "traits.txt",
                    traits,
                    f"RimWorld Farsi - {module} Character Traits (ویژگی‌های شخصیتی)",
                )

        return stats


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Granular WordInfo Domain Generator for RimWorld-Farsi"
    )
    parser.add_argument(
        "--module",
        choices=MODULES,
        help="Process a specific module (default: all modules)",
    )
    parser.add_argument(
        "--root-dir",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview extraction counts without writing files",
    )

    args = parser.parse_args()
    extractor = DomainWordInfoExtractor(root_dir=args.root_dir)

    target_modules = [args.module] if args.module else MODULES

    print("======================================================================")
    print("      RimWorld Farsi - Granular WordInfo Domain Generator")
    print("======================================================================")

    total_hediffs = 0
    total_capacities = 0
    total_traits = 0

    for mod in target_modules:
        stats = extractor.process_module(mod, dry_run=args.dry_run)
        h = stats.get("hediffs", 0)
        c = stats.get("capacities", 0)
        t = stats.get("traits", 0)
        total_hediffs += h
        total_capacities += c
        total_traits += t
        print(f"📦 Module {mod:10}: {h:3} hediffs, {c:2} capacities, {t:3} traits extracted.")

    action_label = "[DRY-RUN] Would generate" if args.dry_run else "Successfully generated"
    print("----------------------------------------------------------------------")
    print(f"Summary: {action_label} {total_hediffs} Hediffs, {total_capacities} Capacities, and {total_traits} Traits across {len(target_modules)} modules.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
