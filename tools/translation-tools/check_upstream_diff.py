#!/usr/bin/env python3
"""
Upstream Game Update Diff Engine & Stub Generator for RimWorld-Farsi.

Compares local Persian translation XML files against upstream English game files
(from RimWorld updates/DLCs) to automatically detect:
  1. Missing translation files.
  2. Missing translation tags within existing files.
  3. Modified English source strings.

Can generate structured TODO translation stubs with original `<!-- EN: ... -->` comments.

Usage:
  python tools/translation-tools/check_upstream_diff.py --english-dir /path/to/RimWorld/Data
  python tools/translation-tools/check_upstream_diff.py --english-dir /path/to/English --module Biotech
  python tools/translation-tools/check_upstream_diff.py --english-dir /path/to/English --generate-stubs
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import lxml.etree as ET

MODULES = ["Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey"]


@dataclass
class TagDiff:
    """Represents a single tag diff between upstream English and local Persian."""
    tag_path: str
    english_text: str
    persian_text: str | None = None
    diff_type: str = "missing"  # "missing" or "modified"


@dataclass
class FileDiff:
    """Represents differences for a single XML file."""
    relative_path: str
    is_new_file: bool = False
    missing_tags: list[TagDiff] = field(default_factory=list)
    modified_tags: list[TagDiff] = field(default_factory=list)


@dataclass
class ModuleDiffReport:
    """Diff report for a whole module (e.g. Core, Biotech)."""
    module: str
    total_english_files: int = 0
    total_persian_files: int = 0
    new_files_count: int = 0
    missing_tags_count: int = 0
    file_diffs: list[FileDiff] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class UpstreamDiffEngine:
    """
    Parses and compares English and Persian XML trees.
    """

    def __init__(self, english_dir: Path, persian_dir: Path):
        self.english_dir = english_dir.resolve()
        self.persian_dir = persian_dir.resolve()

    @staticmethod
    def _extract_tags(file_path: Path) -> dict[str, tuple[str, str | None]]:
        """
        Extracts leaf tags from an XML file.
        Returns a dict: {tag_name: (inner_text, en_comment_if_present)}.
        """
        result: dict[str, tuple[str, str | None]] = {}
        if not file_path.exists():
            return result

        try:
            parser = ET.XMLParser(recover=True, remove_blank_text=True, resolve_entities=False)
            tree = ET.parse(str(file_path), parser)
            root = tree.getroot()
            if root is None:
                return result

            # Iterate over elements and check preceding comments
            for elem in root.iter():
                # Leaf element check: has text, no child elements
                if len(elem) == 0 and elem.text is not None:
                    tag_name = elem.tag
                    text = elem.text.strip()
                    # Check preceding sibling for EN comment
                    en_comment: str | None = None
                    prev = elem.getprevious()
                    if prev is not None and isinstance(prev, ET._Comment):
                        comment_text = str(prev.text).strip()
                        if comment_text.startswith("EN:"):
                            en_comment = comment_text[3:].strip()
                    result[tag_name] = (text, en_comment)
        except Exception as e:
            print(f"Warning: Failed to parse XML {file_path}: {e}", file=sys.stderr)

        return result

    def diff_module(self, module_name: str) -> ModuleDiffReport:
        """
        Compares English and Persian files for a specific module.
        """
        report = ModuleDiffReport(module=module_name)

        # Detect layout: English may be inside Data/<Module>/Languages/English or Data/<Module>/
        en_mod_path = self.english_dir / module_name
        if not en_mod_path.exists():
            # Check if english_dir is already the module or languages root
            en_mod_path = self.english_dir

        en_lang_path = en_mod_path / "Languages" / "English"
        if not en_lang_path.exists():
            en_lang_path = en_mod_path

        fa_mod_path = self.persian_dir / module_name
        if not fa_mod_path.exists():
            return report

        en_files: list[Path] = []
        for root, _, files in os.walk(en_lang_path):
            for f in files:
                if f.endswith(".xml") and f != "LanguageInfo.xml":
                    en_files.append(Path(root) / f)

        report.total_english_files = len(en_files)

        for en_file in sorted(en_files):
            rel_path = en_file.relative_to(en_lang_path)
            fa_file = fa_mod_path / rel_path

            file_diff = FileDiff(relative_path=str(rel_path))

            if not fa_file.exists():
                file_diff.is_new_file = True
                report.new_files_count += 1
                en_tags = self._extract_tags(en_file)
                for tag, (en_text, _) in en_tags.items():
                    tag_diff = TagDiff(tag_path=tag, english_text=en_text, diff_type="missing")
                    file_diff.missing_tags.append(tag_diff)
                    report.missing_tags_count += 1
                report.file_diffs.append(file_diff)
                continue

            en_tags = self._extract_tags(en_file)
            fa_tags = self._extract_tags(fa_file)

            for tag, (en_text, _) in en_tags.items():
                if tag not in fa_tags:
                    tag_diff = TagDiff(tag_path=tag, english_text=en_text, diff_type="missing")
                    file_diff.missing_tags.append(tag_diff)
                    report.missing_tags_count += 1
                else:
                    fa_text, en_comment = fa_tags[tag]
                    # Check if upstream English changed compared to recorded EN comment
                    if en_comment and en_comment != en_text:
                        tag_diff = TagDiff(
                            tag_path=tag,
                            english_text=en_text,
                            persian_text=fa_text,
                            diff_type="modified",
                        )
                        file_diff.modified_tags.append(tag_diff)

            if file_diff.missing_tags or file_diff.modified_tags:
                report.file_diffs.append(file_diff)

        # Count total Persian files
        fa_files = list(fa_mod_path.glob("**/*.xml"))
        report.total_persian_files = len(fa_files)

        return report

    def generate_stubs(self, report: ModuleDiffReport) -> int:
        """
        Appends missing tags formatted as:
          <!-- EN: original English text -->
          <tag>TODO</tag>
        into the corresponding Persian XML files.
        """
        stubs_created = 0
        fa_mod_path = self.persian_dir / report.module

        for file_diff in report.file_diffs:
            if not file_diff.missing_tags:
                continue

            target_file = fa_mod_path / file_diff.relative_path

            if file_diff.is_new_file or not target_file.exists():
                target_file.parent.mkdir(parents=True, exist_ok=True)
                lines = ['<?xml version="1.0" encoding="utf-8"?>\n<LanguageData>\n']
                for tag_diff in file_diff.missing_tags:
                    lines.append(f'  <!-- EN: {tag_diff.english_text} -->\n')
                    lines.append(f'  <{tag_diff.tag_path}>TODO</{tag_diff.tag_path}>\n')
                    stubs_created += 1
                lines.append('</LanguageData>\n')
                target_file.write_text("".join(lines), encoding="utf-8")
            else:
                # Append before closing </LanguageData>
                content = target_file.read_text(encoding="utf-8")
                stub_lines: list[str] = []
                for tag_diff in file_diff.missing_tags:
                    stub_lines.append(f'  <!-- EN: {tag_diff.english_text} -->\n')
                    stub_lines.append(f'  <{tag_diff.tag_path}>TODO</{tag_diff.tag_path}>\n')
                    stubs_created += 1

                stub_block = "".join(stub_lines)
                if "</LanguageData>" in content:
                    new_content = content.replace("</LanguageData>", f"{stub_block}</LanguageData>")
                else:
                    new_content = content + "\n" + stub_block

                target_file.write_text(new_content, encoding="utf-8")

        return stubs_created


def main() -> int:
    parser = argparse.ArgumentParser(
        description="RimWorld Upstream Translation Diff Engine & Stub Generator"
    )
    parser.add_argument(
        "--english-dir",
        required=True,
        type=Path,
        help="Path to English language source directory or game Data/ folder",
    )
    parser.add_argument(
        "--persian-dir",
        type=Path,
        default=Path.cwd(),
        help="Path to Persian translation repository root (default: current directory)",
    )
    parser.add_argument(
        "--module",
        choices=MODULES,
        help="Specific module to diff (default: all modules)",
    )
    parser.add_argument(
        "--generate-stubs",
        action="store_true",
        help="Automatically generate TODO translation stubs in target Persian files",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        help="Path to write JSON diff summary report",
    )

    args = parser.parse_args()

    engine = UpstreamDiffEngine(english_dir=args.english_dir, persian_dir=args.persian_dir)
    target_modules = [args.module] if args.module else MODULES

    all_reports: list[ModuleDiffReport] = []
    total_missing = 0
    total_modified = 0

    print("======================================================================")
    print("       RimWorld Upstream Translation Diff Engine")
    print("======================================================================")

    for mod in target_modules:
        report = engine.diff_module(mod)
        all_reports.append(report)
        missing_count = report.missing_tags_count
        mod_modified = sum(len(f.modified_tags) for f in report.file_diffs)
        total_missing += missing_count
        total_modified += mod_modified

        status_icon = "✅" if missing_count == 0 and mod_modified == 0 else "⚠️"
        print(f"{status_icon} Module {mod:10}: {missing_count} missing tags, {mod_modified} modified upstream strings")

        if args.generate_stubs and missing_count > 0:
            created = engine.generate_stubs(report)
            print(f"   -> Generated {created} translation stubs for {mod}")

    print("----------------------------------------------------------------------")
    print(f"Summary: {total_missing} missing tags, {total_modified} modified upstream strings across {len(target_modules)} modules.")

    if args.output_json:
        output_data = [r.to_dict() for r in all_reports]
        args.output_json.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Report written to: {args.output_json}")

    return 0 if total_missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
