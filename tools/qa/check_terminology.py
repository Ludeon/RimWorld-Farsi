#!/usr/bin/env python3
"""
RimWorld Persian Community Terminology Harmonization Linter.

Verifies that translations strictly adhere to canonical terminology defined
in the official glossary (AGENTS.md) and flags prohibited legacy/slang loanwords.

Examples of enforced terminology:
  - Mechanoid -> مکانوید (Reject: مچانوید، مکانیوید)
  - Drop pod  -> کپسول پرتاب (Reject: دراپ پاد)
  - Blueprint -> طرح اولیه (Reject: بلوپرینت)
  - Colonist  -> استعمارگر (Reject: کلونیست)
  - Psycaster -> روان‌پیما (Reject: سایکستر)

Usage:
  python tools/qa/check_terminology.py
  python tools/qa/check_terminology.py --github
  python tools/qa/check_terminology.py --fix
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import lxml.etree as ET

MODULES = ["Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey"]

# Canonical terms and prohibited/slang alternatives
# Format: {ProhibitedPattern: (CanonicalReplacement, ContextDescription)}
PROHIBITED_TERMS: dict[str, tuple[str, str]] = {
    r"\bکلونیست\b": ("استعمارگر", "Colonist"),
    r"\bکلونیست‌ها\b": ("استعمارگران / استعمارگرها", "Colonists"),
    r"\bمچانوید\b": ("مکانوید", "Mechanoid"),
    r"\bمکانیوید\b": ("مکانوید", "Mechanoid"),
    r"\bدراپ پاد\b": ("کپسول پرتاب", "Drop pod"),
    r"\bدراپ‌پاد\b": ("کپسول پرتاب", "Drop pod"),
    r"\bبلوپرینت\b": ("طرح اولیه", "Blueprint"),
    r"\bسایکستر\b": ("روان‌پیما", "Psycaster"),
    r"\bزنوتایپ\b": ("گونه ژنتیکی / بیوتک", "Xenotype"),
}


@dataclass
class TerminologyViolation:
    file_path: Path
    tag_name: str
    line_number: int
    matched_text: str
    replacement: str
    context_desc: str


class TerminologyChecker:
    """Scans XML translation files for prohibited slang and non-canonical terminology."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir.resolve()
        self.compiled_rules = [
            (re.compile(pattern), repl, desc)
            for pattern, (repl, desc) in PROHIBITED_TERMS.items()
        ]

    def check_file(self, file_path: Path) -> list[TerminologyViolation]:
        violations: list[TerminologyViolation] = []
        try:
            parser = ET.XMLParser(recover=True, remove_blank_text=True, resolve_entities=False)
            tree = ET.parse(str(file_path), parser)
            root = tree.getroot()
            if root is None:
                return violations

            for elem in root.iter():
                if isinstance(elem.tag, str) and elem.text:
                    text = elem.text
                    for regex, repl, desc in self.compiled_rules:
                        match = regex.search(text)
                        if match:
                            violations.append(
                                TerminologyViolation(
                                    file_path=file_path,
                                    tag_name=elem.tag,
                                    line_number=elem.sourceline or 0,
                                    matched_text=match.group(0),
                                    replacement=repl,
                                    context_desc=desc,
                                )
                            )
        except Exception as e:
            print(f"Warning: Failed to parse XML {file_path}: {e}", file=sys.stderr)

        return violations

    def fix_file(self, file_path: Path) -> int:
        """Automatically replaces prohibited terms with canonical terms."""
        content = file_path.read_text(encoding="utf-8")
        original = content
        for regex, repl, _ in self.compiled_rules:
            # For xenotype or combined options, choose primary canonical
            clean_repl = repl.split(" / ")[0].strip()
            content = regex.sub(clean_repl, content)

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            return 1
        return 0

    def run_check(self, modules: list[str] | None = None, fix: bool = False) -> list[TerminologyViolation]:
        target_modules = modules or MODULES
        all_violations: list[TerminologyViolation] = []
        fixed_files = 0

        for mod in target_modules:
            mod_dir = self.root_dir / mod
            if not mod_dir.exists():
                continue

            for root, _, files in os.walk(mod_dir):
                for file in files:
                    if file.endswith(".xml") and file != "LanguageInfo.xml":
                        path = Path(root) / file
                        if fix:
                            if self.fix_file(path):
                                fixed_files += 1
                        violations = self.check_file(path)
                        all_violations.extend(violations)

        if fix:
            print(f"Fixed terminology in {fixed_files} files.")

        return all_violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="RimWorld Persian Community Terminology Harmonization Linter"
    )
    parser.add_argument(
        "--root-dir",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory (default: current directory)",
    )
    parser.add_argument(
        "--github",
        action="store_true",
        help="Format output as GitHub Actions annotations",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix terminology inconsistencies in files",
    )
    parser.add_argument(
        "--module",
        choices=MODULES,
        help="Check a specific module only",
    )

    args = parser.parse_args()
    checker = TerminologyChecker(root_dir=args.root_dir)
    modules = [args.module] if args.module else MODULES

    violations = checker.run_check(modules=modules, fix=args.fix)

    if not violations:
        print("✅ Terminology Harmonization: 100% compliant with canonical glossary (AGENTS.md).")
        return 0

    print(f"⚠️  Found {len(violations)} terminology inconsistencies:")
    for v in violations:
        rel_path = v.file_path.relative_to(args.root_dir)
        msg = f"Non-canonical term '{v.matched_text}' found for {v.context_desc}. Recommended: '{v.replacement}'"
        if args.github:
            print(f"::warning file={rel_path},line={v.line_number},title=Terminology Inconsistency::{msg}")
        else:
            print(f"  - [{rel_path}:{v.line_number}] <{v.tag_name}>: {msg}")

    return 1 if not args.fix else 0


if __name__ == "__main__":
    sys.exit(main())
