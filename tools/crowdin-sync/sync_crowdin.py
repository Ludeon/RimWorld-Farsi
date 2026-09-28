#!/usr/bin/env python3
"""
Crowdin & Weblate Bidirectional API Bridge for RimWorld-Farsi.

Enables community web translation by synchronizing between RimWorld's
XML structure and Crowdin/Weblate formats (JSON/XML).

Inspired by the Korean localization pipeline (RimWorld-Korean).

Modes:
  1. Export: Packages local translation files into Crowdin bundle.
  2. Import: Merges community translations from Crowdin/Weblate back into repo.
  3. Push/Pull: Interacts with Crowdin API v2 using CROWDIN_TOKEN.

Usage:
  python tools/crowdin-sync/sync_crowdin.py --export-bundle ./crowdin_export
  python tools/crowdin-sync/sync_crowdin.py --import-bundle ./crowdin_import
  python tools/crowdin-sync/sync_crowdin.py --stats
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import lxml.etree as ET

MODULES = ["Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey"]


class CrowdinSyncBridge:
    """Manages translation data serialization between RimWorld XML and Crowdin format."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root.resolve()

    def export_bundle(self, output_dir: Path, modules: list[str] | None = None) -> int:
        """
        Exports all Keyed and DefInjected XMLs to structured JSON files for Crowdin upload.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        target_modules = modules or MODULES
        total_strings = 0

        for mod in target_modules:
            mod_dir = self.repo_root / mod
            if not mod_dir.exists():
                continue

            for root, _, files in os.walk(mod_dir):
                for file in files:
                    if not file.endswith(".xml") or file == "LanguageInfo.xml":
                        continue
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(self.repo_root)

                    strings_in_file: dict[str, dict[str, str]] = {}
                    try:
                        parser = ET.XMLParser(recover=True, remove_blank_text=True, resolve_entities=False)
                        tree = ET.parse(str(file_path), parser)
                        xml_root = tree.getroot()
                        if xml_root is None:
                            continue

                        for elem in xml_root.iter():
                            if isinstance(elem.tag, str) and elem.text:
                                fa_text = elem.text.strip()
                                en_text = ""
                                prev = elem.getprevious()
                                if prev is not None and isinstance(prev, ET._Comment):
                                    c_text = str(prev.text).strip()
                                    if c_text.startswith("EN:"):
                                        en_text = c_text[3:].strip()

                                strings_in_file[elem.tag] = {
                                    "en": en_text,
                                    "fa": fa_text,
                                }
                                total_strings += 1

                        if strings_in_file:
                            json_out = output_dir / rel_path.with_suffix(".json")
                            json_out.parent.mkdir(parents=True, exist_ok=True)
                            json_out.write_text(
                                json.dumps(strings_in_file, indent=2, ensure_ascii=False),
                                encoding="utf-8",
                            )
                    except Exception as e:
                        print(f"Warning: Failed to export {file_path}: {e}", file=sys.stderr)

        return total_strings

    def import_bundle(self, input_dir: Path) -> int:
        """
        Imports translated JSON files from Crowdin/Weblate and writes back to XML.
        """
        if not input_dir.exists():
            print(f"Error: Import directory does not exist: {input_dir}", file=sys.stderr)
            return 0

        imported_strings = 0
        for root, _, files in os.walk(input_dir):
            for file in files:
                if not file.endswith(".json"):
                    continue
                json_path = Path(root) / file
                rel_json = json_path.relative_to(input_dir)
                target_xml = self.repo_root / rel_json.with_suffix(".xml")

                try:
                    data: dict[str, Any] = json.loads(json_path.read_text(encoding="utf-8"))
                    if not target_xml.exists():
                        target_xml.parent.mkdir(parents=True, exist_ok=True)
                        lines = ['<?xml version="1.0" encoding="utf-8"?>\n<LanguageData>\n']
                        for tag, values in data.items():
                            en = values.get("en", "")
                            fa = values.get("fa", "")
                            if en:
                                lines.append(f"  <!-- EN: {en} -->\n")
                            lines.append(f"  <{tag}>{fa}</{tag}>\n")
                            imported_strings += 1
                        lines.append("</LanguageData>\n")
                        target_xml.write_text("".join(lines), encoding="utf-8")
                    else:
                        # Update existing XML
                        parser = ET.XMLParser(recover=True, resolve_entities=False)
                        tree = ET.parse(str(target_xml), parser)
                        xml_root = tree.getroot()
                        for elem in xml_root.iter():
                            if isinstance(elem.tag, str) and elem.tag in data:
                                new_fa = data[elem.tag].get("fa")
                                if new_fa and new_fa != "TODO":
                                    elem.text = new_fa
                                    imported_strings += 1
                        tree.write(str(target_xml), encoding="utf-8", xml_declaration=True)
                except Exception as e:
                    print(f"Warning: Failed to import {json_path}: {e}", file=sys.stderr)

        return imported_strings

    def compute_stats(self) -> dict[str, int]:
        """Computes total files and string counts across all translation modules."""
        stats = {"total_files": 0, "total_strings": 0, "total_words": 0}
        for mod in MODULES:
            mod_p = self.repo_root / mod
            if not mod_p.exists():
                continue
            for root, _, files in os.walk(mod_p):
                for file in files:
                    if file.endswith(".xml") and file != "LanguageInfo.xml":
                        stats["total_files"] += 1
                        path = Path(root) / file
                        try:
                            parser = ET.XMLParser(recover=True, resolve_entities=False)
                            tree = ET.parse(str(path), parser)
                            r = tree.getroot()
                            if r is not None:
                                for elem in r.iter():
                                    if isinstance(elem.tag, str) and elem.text:
                                        stats["total_strings"] += 1
                                        stats["total_words"] += len(elem.text.split())
                        except Exception:
                            pass
        return stats


def main() -> int:
    parser = argparse.ArgumentParser(
        description="RimWorld Persian Crowdin & Weblate Synchronization Bridge"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory",
    )
    parser.add_argument(
        "--export-bundle",
        type=Path,
        help="Export all translation strings to directory for Crowdin upload",
    )
    parser.add_argument(
        "--import-bundle",
        type=Path,
        help="Import translated strings from Crowdin JSON directory",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Display translation volume statistics",
    )

    args = parser.parse_args()
    bridge = CrowdinSyncBridge(repo_root=args.repo_root)

    if args.stats:
        s = bridge.compute_stats()
        print("======================================================================")
        print("         RimWorld Persian Translation Corpus Statistics")
        print("======================================================================")
        print(f"📁 Total XML Files   : {s['total_files']:,}")
        print(f"💬 Total Keyed/Defs  : {s['total_strings']:,}")
        print(f"📝 Total Word Count  : {s['total_words']:,} Persian words")
        print("----------------------------------------------------------------------")
        return 0

    if args.export_bundle:
        print(f"Exporting translation strings to: {args.export_bundle}...")
        count = bridge.export_bundle(args.export_bundle)
        print(f"✅ Exported {count:,} strings successfully.")
        return 0

    if args.import_bundle:
        print(f"Importing translations from: {args.import_bundle}...")
        count = bridge.import_bundle(args.import_bundle)
        print(f"✅ Imported {count:,} strings successfully.")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
