#!/usr/bin/env python3
"""
RimWorld ReportString Period Checker
====================================
Ensures that all <reportString> tags in translation XML files do not end
with a period ('.' or '۔'). RimWorld automatically concatenates report
strings into pawn status bars and activity descriptions; trailing dots
produce double punctuation (e.g. "Eating nutrient paste..").
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Matches tags ending with reportString (case-insensitive) containing trailing dot
REPORT_STRING_DOT_RE = re.compile(
    r"(<([A-Za-z0-9_.\-]*[rR]eportString)>)(.*?)([.\u06D4]+)(</\2>)"
)


@dataclass
class ReportStringDefect:
    file: Path
    line_num: int
    tag: str
    content: str
    suggested: str


def check_file_report_strings(
    file_path: Path, auto_fix: bool = False
) -> tuple[list[ReportStringDefect], bool]:
    """Check and optionally fix trailing dots in reportString tags within a file."""
    defects: list[ReportStringDefect] = []
    file_modified = False

    try:
        with open(file_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception:
        return defects, False

    def replace_dot(m: re.Match) -> str:
        nonlocal file_modified
        open_tag = m.group(1)
        tag_name = m.group(2)
        inner = m.group(3)
        close_tag = m.group(5)

        line_num = content[: m.start()].count("\n") + 1
        suggested = f"{open_tag}{inner}{close_tag}"

        defects.append(
            ReportStringDefect(
                file=file_path,
                line_num=line_num,
                tag=tag_name,
                content=m.group(0),
                suggested=suggested,
            )
        )

        if auto_fix:
            file_modified = True
            return suggested
        return str(m.group(0))

    new_content: str = REPORT_STRING_DOT_RE.sub(replace_dot, content)

    if auto_fix and file_modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

    return defects, file_modified


def check_all_report_strings(
    root_dir: Path, dlcs: list[str] | None = None, auto_fix: bool = False
) -> tuple[list[ReportStringDefect], int]:
    """Scan all XML files in designated DLCs."""
    if dlcs is None:
        dlcs = ["Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey"]

    all_defects: list[ReportStringDefect] = []
    files_fixed = 0

    for dlc in dlcs:
        dlc_path = root_dir / dlc
        if not dlc_path.exists():
            continue

        for root, _, files in os.walk(dlc_path):
            for file in sorted(files):
                if file.lower().endswith(".xml"):
                    fpath = Path(root) / file
                    defects, modified = check_file_report_strings(fpath, auto_fix=auto_fix)
                    all_defects.extend(defects)
                    if modified:
                        files_fixed += 1

    return all_defects, files_fixed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="RimWorld ReportString Period Checker"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent,
        help="Repository root directory",
    )
    parser.add_argument(
        "--dlc",
        type=str,
        default="",
        help="Specific DLC to check (Core, Royalty, etc.)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically remove trailing periods from reportString elements",
    )
    parser.add_argument(
        "--github",
        action="store_true",
        help="Print GitHub Actions workflow annotations",
    )
    args = parser.parse_args()

    repo_root = args.root
    dlcs = [args.dlc] if args.dlc else None

    defects, fixed_count = check_all_report_strings(repo_root, dlcs, auto_fix=args.fix)

    if not defects:
        print("\033[92m[OK] No reportString elements with trailing periods found!\033[0m")
        return 0

    if args.fix:
        print(f"\033[92m[SUCCESS] Automatically removed trailing periods from {len(defects)} reportString(s) across {fixed_count} file(s)!\033[0m")
        return 0

    print(f"\033[91m[ERROR] Found {len(defects)} reportString(s) with invalid trailing period:\033[0m\n")

    for d in defects:
        rel_path = d.file.relative_to(repo_root) if d.file.is_relative_to(repo_root) else d.file
        if args.github:
            print(f"::error file={rel_path},line={d.line_num},title=ReportString Dot Error::reportString must not end with a period: {d.content}")
        else:
            print(f"\033[93m{rel_path}:{d.line_num}\033[0m (\033[1m<{d.tag}>\033[0m)")
            print(f"  Current:   {d.content}")
            print(f"  Suggested: {d.suggested}")
            print()

    return 1


if __name__ == "__main__":
    sys.exit(main())
