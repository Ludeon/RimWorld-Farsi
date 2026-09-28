#!/usr/bin/env python3
"""
RimWorld Farsi Localization QA Suite Runner
============================================
Unified executor for all localization quality gates:
  1. XML Well-formedness & Validity
  2. Format Token & Placeholder Integrity
  3. Persian Typography, Authentic Unicode & ZWNJ Rules
  4. ReportString Period Rules
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Add tools/qa and tools/rtl-processor to path
QA_DIR = Path(__file__).resolve().parent
REPO_ROOT = QA_DIR.parent.parent
sys.path.insert(0, str(QA_DIR))
sys.path.insert(0, str(REPO_ROOT / "tools" / "rtl-processor"))

# ruff: noqa: E402
from check_persian_typography import check_all_typography
from check_placeholders import check_all_placeholders
from check_report_strings import check_all_report_strings
from validate_xml import validate_xml_file


def run_qa_suite(
    repo_root: Path,
    dlcs: list[str] | None = None,
    auto_fix: bool = False,
    github: bool = False,
) -> int:
    """Run all QA linters and print structured results."""
    start_time = time.time()
    total_failures = 0
    active_dlcs = dlcs or ["Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey"]

    print("======================================================================")
    print("\033[1mRIMWORLD FARSI LOCALIZATION QUALITY ASSURANCE SUITE\033[0m")
    print(f"Target Root: {repo_root}")
    print(f"Target DLCs: {', '.join(active_dlcs)}")
    print("======================================================================\n")

    # Gate 1: XML Well-formedness
    print("\033[1m[Gate 1/5] Checking XML Well-formedness...\033[0m")
    xml_files: list[Path] = []
    for dlc in active_dlcs:
        dlc_p = repo_root / dlc
        if dlc_p.exists():
            xml_files.extend(sorted(dlc_p.rglob("*.xml")))

    invalid_xmls: list[tuple[Path, str]] = []
    for f in xml_files:
        is_valid, err = validate_xml_file(str(f))
        if not is_valid:
            invalid_xmls.append((f, err or "Unknown XML syntax error"))

    if invalid_xmls:
        total_failures += len(invalid_xmls)
        print(f"  \033[91m[FAIL] Found {len(invalid_xmls)} malformed XML file(s):\033[0m")
        for f, err in invalid_xmls[:10]:
            print(f"    - {f.relative_to(repo_root)}: {err}")
    else:
        print(f"  \033[92m[PASS] All {len(xml_files)} XML translation files are well-formed.\033[0m\n")

    # Gate 2: Format Tokens & Placeholders
    print("\033[1m[Gate 2/5] Checking Format Tokens & Placeholder Integrity...\033[0m")
    placeholder_errs = check_all_placeholders(repo_root, dlcs=active_dlcs)
    if placeholder_errs:
        total_failures += len(placeholder_errs)
        print(f"  \033[91m[FAIL] Found {len(placeholder_errs)} placeholder defect(s):\033[0m")
        for err in placeholder_errs[:15]:
            rel_p = err.file.relative_to(repo_root) if err.file.is_relative_to(repo_root) else err.file
            if github:
                print(f"::error file={rel_p},line={err.line_num},title=Placeholder Defect::{err.message}")
            else:
                print(f"    - {rel_p}:{err.line_num} (<{err.tag}>): {err.message}")
        if len(placeholder_errs) > 15:
            print(f"    ... and {len(placeholder_errs) - 15} more")
    else:
        print("  \033[92m[PASS] All positional tokens, named variables, and macros are valid.\033[0m\n")

    # Gate 3: Persian Typography & ZWNJ Rules
    print("\033[1m[Gate 3/5] Checking Persian Typography, Codepoints & ZWNJ...\033[0m")
    typo_defects, files_fixed = check_all_typography(repo_root, dlcs=active_dlcs, auto_fix=auto_fix)
    if typo_defects and not auto_fix:
        total_failures += len(typo_defects)
        print(f"  \033[91m[FAIL] Found {len(typo_defects)} typography defect(s):\033[0m")
        for d in typo_defects[:15]:
            rel_p = d.file.relative_to(repo_root) if d.file.is_relative_to(repo_root) else d.file
            if github:
                print(f"::error file={rel_p},line={d.line_num},title=Typography [{d.rule}]::{d.message}")
            else:
                print(f"    - {rel_p}:{d.line_num} [{d.rule}]: {d.message}")
        if len(typo_defects) > 15:
            print(f"    ... and {len(typo_defects) - 15} more (run with --fix to automatically repair)")
    elif typo_defects and auto_fix:
        print(f"  \033[92m[PASS] Automatically repaired {len(typo_defects)} defect(s) in {files_fixed} file(s).\033[0m\n")
    else:
        print("  \033[92m[PASS] All Persian characters, punctuation, and ZWNJ rules are valid.\033[0m\n")

    # Gate 4: ReportString Trailing Period Rules
    print("\033[1m[Gate 4/5] Checking ReportString Trailing Periods...\033[0m")
    report_defects, rep_fixed = check_all_report_strings(repo_root, dlcs=active_dlcs, auto_fix=auto_fix)
    if report_defects and not auto_fix:
        total_failures += len(report_defects)
        print(f"  \033[91m[FAIL] Found {len(report_defects)} reportString(s) with trailing period:\033[0m")
        for r in report_defects[:15]:
            rel_p = r.file.relative_to(repo_root) if r.file.is_relative_to(repo_root) else r.file
            if github:
                print(f"::error file={rel_p},line={r.line_num},title=ReportString Period::{r.content}")
            else:
                print(f"    - {rel_p}:{r.line_num} (<{r.tag}>): {r.content}")
    elif report_defects and auto_fix:
        print(f"  \033[92m[PASS] Automatically removed trailing periods from {len(report_defects)} tag(s).\033[0m\n")
    else:
        print("  \033[92m[PASS] No reportString elements have trailing periods.\033[0m\n")

    # Gate 5: Community Terminology Harmonization
    print("\033[1m[Gate 5/5] Checking Community Terminology Harmonization...\033[0m")
    from check_terminology import TerminologyChecker
    term_checker = TerminologyChecker(root_dir=repo_root)
    term_violations = term_checker.run_check(modules=active_dlcs, fix=auto_fix)
    if term_violations and not auto_fix:
        total_failures += len(term_violations)
        print(f"  \033[91m[FAIL] Found {len(term_violations)} non-canonical terminology violation(s):\033[0m")
        for v in term_violations[:15]:
            rel_p = v.file_path.relative_to(repo_root) if v.file_path.is_relative_to(repo_root) else v.file_path
            msg = f"Non-canonical term '{v.matched_text}' for {v.context_desc}. Recommended: '{v.replacement}'"
            if github:
                print(f"::error file={rel_p},line={v.line_number},title=Terminology Violation::{msg}")
            else:
                print(f"    - {rel_p}:{v.line_number} (<{v.tag_name}>): {msg}")
        if len(term_violations) > 15:
            print(f"    ... and {len(term_violations) - 15} more (run with --fix to repair)")
    elif term_violations and auto_fix:
        print(f"  \033[92m[PASS] Automatically harmonized {len(term_violations)} term(s).\033[0m\n")
    else:
        print("  \033[92m[PASS] 100% compliant with canonical glossary (AGENTS.md).\033[0m\n")

    elapsed = time.time() - start_time
    print("======================================================================")
    if total_failures == 0:
        print(f"\033[92mQA RESULT: PASSED (All 5 gates passed in {elapsed:.2f}s)\033[0m")
        print("======================================================================")
        return 0
    else:
        print(f"\033[91mQA RESULT: FAILED ({total_failures} defect(s) detected in {elapsed:.2f}s)\033[0m")
        print("======================================================================")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="RimWorld Farsi QA Suite Runner")
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
        help="Specific DLC name to test (Core, Royalty, etc.)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix repairable typography and reportString defects",
    )
    parser.add_argument(
        "--github",
        action="store_true",
        help="Emit GitHub Actions error annotations",
    )
    args = parser.parse_args()

    dlcs = [args.dlc] if args.dlc else None
    return run_qa_suite(
        repo_root=args.root,
        dlcs=dlcs,
        auto_fix=args.fix,
        github=args.github,
    )


if __name__ == "__main__":
    sys.exit(main())
