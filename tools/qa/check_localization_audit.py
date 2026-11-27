#!/usr/bin/env python3
"""Read-only Localization Audit Suite for RimWorld-Farsi.

Provides non-destructive audit checks across all six modules without altering
translation XMLs:
  1. ``TODO`` / ``FIXME`` tag scan and ``<!-- EN: ... -->`` coverage count
  2. ``Strings/`` file integrity (duplicate extensionless files, preserved Latin/Roman files)
  3. ``RulePackDef`` hygiene (dangling English connectors, token suffix ZWNJ)
  4. ``WordInfo/`` column-0 drift check across all modules
  5. Short UI label length warnings (button/tab overflow prevention)
  6. Dev Mode ``TranslationReport.txt`` section analyzer
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import lxml.etree as ET

MODULES = ("Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey")
RULE_REF_RE = re.compile(r"\[([A-Za-z_][A-Za-z0-9_]*)\]")
RULE_ARROW_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)(?:\([^)]*\))?\s*->\s*(.*)$")
DANGLING_EN_CONNECTOR_RE = re.compile(r"->\s*(of|for|by|with|and|or|to|in|on)\s*$", re.IGNORECASE)
SUFFIXED_TOKEN_RE = re.compile(r"(\[[A-Za-z0-9_]+\]|\{[A-Za-z0-9_]+\})(ها|های)\b")
SHORT_UI_KEY_RE = re.compile(r"^.*\.(tab|label|button)$", re.IGNORECASE)


@dataclass
class AuditReport:
    """Structured read-only audit findings."""

    todo_hits: list[str] = field(default_factory=list)
    en_commented_tags: int = 0
    total_leaf_tags: int = 0
    strings_issues: list[str] = field(default_factory=list)
    rulepack_issues: list[str] = field(default_factory=list)
    wordinfo_drift: list[str] = field(default_factory=list)
    long_ui_labels: list[str] = field(default_factory=list)


def check_todo_and_comments(
    root_dir: Path, modules: tuple[str, ...] = MODULES
) -> tuple[list[str], int, int]:
    """Count TODO/FIXME markers and EN source comments across XML leaf tags."""
    todo_hits: list[str] = []
    en_commented = 0
    total_leaves = 0
    parser = ET.XMLParser(resolve_entities=False)

    for module in modules:
        mod_dir = root_dir / module
        if not mod_dir.is_dir():
            continue
        for xml_path in sorted(mod_dir.rglob("*.xml")):
            if xml_path.name == "LanguageInfo.xml":
                continue
            try:
                tree = ET.parse(str(xml_path), parser)
            except ET.XMLSyntaxError:
                continue
            root = tree.getroot()
            if root is None:
                continue

            saw_en_comment = False
            for node in root.iter():
                if isinstance(node.tag, type(ET.Comment)):
                    if node.text and "EN:" in node.text:
                        saw_en_comment = True
                    continue
                if not isinstance(node.tag, str) or len(node) > 0:
                    continue
                total_leaves += 1
                if saw_en_comment:
                    en_commented += 1
                    saw_en_comment = False
                txt = (node.text or "").strip()
                if txt in {"TODO", "FIXME"} or txt.startswith("TODO:"):
                    rel = (
                        xml_path.relative_to(root_dir)
                        if xml_path.is_relative_to(root_dir)
                        else xml_path
                    )
                    todo_hits.append(f"{rel}:{node.sourceline or 0}: <{node.tag}>={txt}")

    return todo_hits, en_commented, total_leaves


def check_strings_integrity(
    root_dir: Path, modules: tuple[str, ...] = MODULES
) -> list[str]:
    """Validate ``Strings/`` files for duplicates and required literal Latin tables."""
    issues: list[str] = []
    for module in modules:
        strings_dir = root_dir / module / "Strings"
        if not strings_dir.is_dir():
            continue
        for file_path in sorted(strings_dir.rglob("*")):
            if not file_path.is_file():
                continue
            if file_path.suffix == "" and file_path.with_suffix(".txt").is_file():
                rel = file_path.relative_to(root_dir)
                issues.append(f"Duplicate extensionless Strings file alongside .txt: {rel}")

    capitals = root_dir / "Core" / "Strings" / "WordParts" / "CapitalLetters.txt"
    if capitals.is_file():
        letters = [
            line.strip()
            for line in capitals.read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        ]
        expected = [chr(c) for c in range(ord("A"), ord("Z") + 1)]
        if letters != expected:
            issues.append("Core/Strings/WordParts/CapitalLetters.txt does not match A-Z")

    roman = root_dir / "Core" / "Strings" / "Words" / "Misc" / "Numbers_SmallRoman.txt"
    if roman.is_file():
        vals = [
            line.strip()
            for line in roman.read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        ]
        if vals[:3] != ["I", "II", "III"]:
            issues.append("Core/Strings/Words/Misc/Numbers_SmallRoman.txt modified from Roman numerals")

    return issues


def check_rulepack_hygiene(
    root_dir: Path, modules: tuple[str, ...] = MODULES
) -> list[str]:
    """Inspect ``RulePackDef`` rules for dangling English connectors and token suffixes."""
    issues: list[str] = []
    parser = ET.XMLParser(resolve_entities=False)

    for module in modules:
        rp_dir = root_dir / module / "DefInjected" / "RulePackDef"
        if not rp_dir.is_dir():
            continue
        for xml_path in sorted(rp_dir.rglob("*.xml")):
            try:
                tree = ET.parse(str(xml_path), parser)
            except ET.XMLSyntaxError:
                continue
            root = tree.getroot()
            if root is None:
                continue
            rel = xml_path.relative_to(root_dir)
            for li in root.iter("li"):
                if not isinstance(li.tag, str) or not li.text:
                    continue
                line = li.text.strip()
                m_arrow = RULE_ARROW_RE.match(line)
                if m_arrow and DANGLING_EN_CONNECTOR_RE.search(line):
                    issues.append(
                        f"{rel}:{li.sourceline or 0}: Dangling English connector in '{line}'"
                    )
                if SUFFIXED_TOKEN_RE.search(line):
                    issues.append(
                        f"{rel}:{li.sourceline or 0}: Plural suffix glued directly to token in '{line}'"
                    )

    return issues


def check_wordinfo_drift(
    root_dir: Path, modules: tuple[str, ...] = MODULES
) -> list[str]:
    """Check column-0 terms in ``WordInfo/`` against translated DefInjected labels."""
    drift: list[str] = []
    parser = ET.XMLParser(resolve_entities=False)

    for module in modules:
        mod_dir = root_dir / module
        wi_dir = mod_dir / "WordInfo"
        def_dir = mod_dir / "DefInjected"
        if not wi_dir.is_dir() or not def_dir.is_dir():
            continue

        known_labels: set[str] = set()
        for xml_path in def_dir.rglob("*.xml"):
            try:
                tree = ET.parse(str(xml_path), parser)
            except ET.XMLSyntaxError:
                continue
            for elem in tree.iter():
                if isinstance(elem.tag, str) and elem.text:
                    known_labels.add(elem.text.strip().lower())

        for table_name in ("plural.txt", "ezafeh.txt"):
            table_path = wi_dir / table_name
            if not table_path.is_file():
                continue
            missing_count = 0
            for raw in table_path.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("//") or ";" not in line:
                    continue
                key = line.split(";", 1)[0].strip().lower()
                if key and key not in known_labels:
                    missing_count += 1
            if missing_count:
                drift.append(
                    f"{module}/WordInfo/{table_name}: {missing_count} key(s) not matched directly in {module}/DefInjected labels"
                )

    return drift


def check_ui_label_lengths(
    root_dir: Path,
    modules: tuple[str, ...] = MODULES,
    max_len: int = 32,
) -> list[str]:
    """Flag short UI label keys whose translated string exceeds ``max_len`` characters."""
    warnings: list[str] = []
    parser = ET.XMLParser(resolve_entities=False)

    for module in modules:
        mod_dir = root_dir / module
        for sub in ("Keyed", "DefInjected"):
            sub_dir = mod_dir / sub
            if not sub_dir.is_dir():
                continue
            for xml_path in sorted(sub_dir.rglob("*.xml")):
                try:
                    tree = ET.parse(str(xml_path), parser)
                except ET.XMLSyntaxError:
                    continue
                root = tree.getroot()
                if root is None:
                    continue
                rel = xml_path.relative_to(root_dir)
                for elem in root.iter():
                    if not isinstance(elem.tag, str) or len(elem) > 0 or not elem.text:
                        continue
                    if not SHORT_UI_KEY_RE.match(elem.tag):
                        continue
                    text = elem.text.strip()
                    if len(text) > max_len and "\n" not in text:
                        warnings.append(
                            f"{rel}:{elem.sourceline or 0}: <{elem.tag}> length {len(text)} > {max_len}: '{text}'"
                        )

    return warnings


def analyze_translation_report(report_path: Path) -> dict[str, list[str]]:
    """Parse a RimWorld Dev Mode ``TranslationReport.txt`` into grouped section entries."""
    if not report_path.is_file():
        raise FileNotFoundError(f"TranslationReport not found: {report_path}")

    sections: dict[str, list[str]] = defaultdict(list)
    current = "Summary"
    for raw in report_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("==========") and line.endswith("=========="):
            current = line.strip("= ").strip() or "Section"
        else:
            sections[current].append(line)
    return dict(sections)


def run_audit(
    root_dir: Path, modules: tuple[str, ...] = MODULES, max_len: int = 32
) -> AuditReport:
    """Execute all non-destructive audit checks and return ``AuditReport``."""
    todos, en_count, total_leaves = check_todo_and_comments(root_dir, modules)
    return AuditReport(
        todo_hits=todos,
        en_commented_tags=en_count,
        total_leaf_tags=total_leaves,
        strings_issues=check_strings_integrity(root_dir, modules),
        rulepack_issues=check_rulepack_hygiene(root_dir, modules),
        wordinfo_drift=check_wordinfo_drift(root_dir, modules),
        long_ui_labels=check_ui_label_lengths(root_dir, modules, max_len=max_len),
    )


def main() -> int:
    """CLI entrypoint for localization audit suite."""
    parser = argparse.ArgumentParser(
        description="Read-only RimWorld-Farsi Localization Audit Tool"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent,
        help="Repository root path",
    )
    parser.add_argument(
        "--max-label-len",
        type=int,
        default=32,
        help="Warning threshold for short UI label length",
    )
    parser.add_argument(
        "--report-file",
        type=Path,
        help="Optional RimWorld Dev Mode TranslationReport.txt to summarize",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if TODOs or Strings/ integrity issues are detected",
    )
    args = parser.parse_args()

    if args.report_file is not None:
        sections = analyze_translation_report(args.report_file)
        for sec, items in sections.items():
            print(f"[{sec}] {len(items)} entry(ies)")
        return 0

    rep = run_audit(args.root, max_len=args.max_label_len)
    pct = (
        (rep.en_commented_tags / rep.total_leaf_tags * 100.0)
        if rep.total_leaf_tags
        else 0.0
    )
    print(f"Leaf tags scanned: {rep.total_leaf_tags} | EN comments: {rep.en_commented_tags} ({pct:.1f}%)")
    print(f"TODO/FIXME hits:   {len(rep.todo_hits)}")
    print(f"Strings issues:    {len(rep.strings_issues)}")
    print(f"RulePack warnings: {len(rep.rulepack_issues)}")
    print(f"WordInfo drift:    {len(rep.wordinfo_drift)}")
    print(f"Long UI labels:    {len(rep.long_ui_labels)} (threshold > {args.max_label_len})")

    for label, entries in (
        ("TODO", rep.todo_hits[:10]),
        ("STRINGS", rep.strings_issues[:10]),
        ("RULEPACK", rep.rulepack_issues[:10]),
        ("WORDINFO_DRIFT", rep.wordinfo_drift[:10]),
        ("UI_LABEL", rep.long_ui_labels[:10]),
    ):
        for item in entries:
            print(f"  [{label}] {item}")

    if args.strict and (rep.todo_hits or rep.strings_issues):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
