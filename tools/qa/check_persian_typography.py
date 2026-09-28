#!/usr/bin/env python3
"""
RimWorld Persian Typography & Character Validator
=================================================
Enforces authentic Persian Unicode standards across translation XML files:
  - Rejects Arabic codepoint contamination (ك -> ک, ي -> ی, ى -> ی).
  - Enforces proper Persian punctuation (؟, ،, ؛) in Persian text contexts.
  - Validates Zero-Width Non-Joiner (ZWNJ / U+200C) rules for verbal prefixes (می‌/نمی‌) and plurals (ها).
  - Supports automated correction with --fix flag.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ZWNJ = "\u200C"

# Character replacements for normalization
CHAR_REPLACEMENTS = {
    "\u0643": "ک",  # Arabic Kaf -> Persian Keheh
    "\u064A": "ی",  # Arabic Yeh -> Persian Yeh
    "\u0649": "ی",  # Arabic Alef Maksura -> Persian Yeh
}

# Regex to find XML tag content: <tag>content</tag>
XML_TAG_CONTENT_RE = re.compile(r"(<([A-Za-z0-9_.\-]+)>)(.*?)(</\2>)", re.DOTALL)

# Patterns for Persian punctuation in Persian contexts
PERSIAN_QUESTION_RE = re.compile(r"([\u0600-\u06FF])\s*\?")
PERSIAN_COMMA_RE = re.compile(r"([\u0600-\u06FF])\s*,\s*([\u0600-\u06FF])")
PERSIAN_SEMICOLON_RE = re.compile(r"([\u0600-\u06FF])\s*;(?![a-zA-Z0-9#]+;)")

# ZWNJ patterns (verbal prefixes and plural suffix)
PREFIX_MI_RE = re.compile(r"(^|[\s«\(])(می|نمی) ([آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی])")
SUFFIX_HA_RE = re.compile(r"([آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی]) ها([\s،؛.!؟»\)\],]|$)")


@dataclass
class TypographyDefect:
    file: Path
    line_num: int
    rule: str
    message: str
    original: str
    suggested: str


def sanitize_placeholders_and_entities(text: str) -> tuple[str, list[str]]:
    """Temporarily replace {...} and &...; tokens to prevent punctuation false positives."""
    masked: list[str] = []

    def mask_token(m: re.Match) -> str:
        idx = len(masked)
        masked.append(m.group(0))
        return f"__TOKEN_{idx}__"

    # Mask braces first
    text_masked = re.sub(r"\{[^{}]*\}", mask_token, text)
    # Mask HTML/XML entities like &amp;
    text_masked = re.sub(r"&[a-zA-Z0-9#]+;", mask_token, text_masked)
    return text_masked, masked


def unmask_tokens(text: str, masked: list[str]) -> str:
    """Restore masked tokens."""
    for idx, token in enumerate(masked):
        text = text.replace(f"__TOKEN_{idx}__", token)
    return text


def fix_typography_in_text(text: str) -> str:
    """Apply typography fixes to plain Persian text."""
    # 1. Arabic character replacements
    for bad_ch, good_ch in CHAR_REPLACEMENTS.items():
        text = text.replace(bad_ch, good_ch)

    # 2. Mask XML entities and RimWorld format tokens before punctuation fixes
    text, tokens = sanitize_placeholders_and_entities(text)

    # 3. Persian punctuation
    text = PERSIAN_QUESTION_RE.sub(r"\1؟", text)
    text = PERSIAN_COMMA_RE.sub(r"\1، \2", text)
    text = PERSIAN_SEMICOLON_RE.sub(r"\1؛", text)

    # 4. ZWNJ verbal prefixes and plurals
    text = PREFIX_MI_RE.sub(rf"\1\2{ZWNJ}\3", text)
    text = SUFFIX_HA_RE.sub(rf"\1{ZWNJ}ها\2", text)

    # 5. Restore tokens
    text = unmask_tokens(text, tokens)
    return text


def check_file_typography(
    file_path: Path, auto_fix: bool = False
) -> tuple[list[TypographyDefect], bool]:
    """Inspect and optionally fix a single XML translation file."""
    defects: list[TypographyDefect] = []
    file_modified = False

    try:
        with open(file_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        defects.append(
            TypographyDefect(
                file=file_path,
                line_num=1,
                rule="FILE_ERROR",
                message=f"Failed to read file: {e}",
                original="",
                suggested="",
            )
        )
        return defects, False

    new_content_chunks: list[str] = []
    last_end = 0

    for match in XML_TAG_CONTENT_RE.finditer(content):
        start, end = match.span()
        open_tag, tag_name, inner_text, close_tag = match.groups()

        # Append preceding non-tag text (comments, headers, formatting)
        new_content_chunks.append(content[last_end:start])

        if inner_text and re.search(r"[\u0600-\u06FF]", inner_text):
            fixed_text = fix_typography_in_text(inner_text)
            if fixed_text != inner_text:
                line_num = content[:start].count("\n") + 1

                # Classify defect
                rule_name = "ARABIC_CHAR"
                msg = "Arabic character codepoints or non-standard typography found"
                if any(k in inner_text for k in CHAR_REPLACEMENTS):
                    rule_name = "ARABIC_CHAR"
                    msg = "Arabic character (ك/ي) detected. Use authentic Persian (ک/ی)."
                elif PERSIAN_QUESTION_RE.search(inner_text) or PERSIAN_COMMA_RE.search(inner_text):
                    rule_name = "PUNCTUATION"
                    msg = "English punctuation (?, ,) used in Persian context. Use (؟،)."
                elif PREFIX_MI_RE.search(inner_text) or SUFFIX_HA_RE.search(inner_text):
                    rule_name = "ZWNJ"
                    msg = "Missing Zero-Width Non-Joiner (نیم‌فاصله) before plural or verb prefix."

                defects.append(
                    TypographyDefect(
                        file=file_path,
                        line_num=line_num,
                        rule=rule_name,
                        message=msg,
                        original=inner_text.strip(),
                        suggested=fixed_text.strip(),
                    )
                )

                if auto_fix:
                    new_content_chunks.append(f"{open_tag}{fixed_text}{close_tag}")
                    file_modified = True
                else:
                    new_content_chunks.append(match.group(0))
            else:
                new_content_chunks.append(match.group(0))
        else:
            new_content_chunks.append(match.group(0))

        last_end = end

    new_content_chunks.append(content[last_end:])

    if auto_fix and file_modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("".join(new_content_chunks))

    return defects, file_modified


def check_all_typography(
    root_dir: Path, dlcs: list[str] | None = None, auto_fix: bool = False
) -> tuple[list[TypographyDefect], int]:
    """Scan all XML files in designated DLCs."""
    if dlcs is None:
        dlcs = ["Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey"]

    all_defects: list[TypographyDefect] = []
    files_fixed = 0

    for dlc in dlcs:
        dlc_path = root_dir / dlc
        if not dlc_path.exists():
            continue

        for root, _, files in os.walk(dlc_path):
            for file in sorted(files):
                if file.lower().endswith(".xml"):
                    fpath = Path(root) / file
                    defects, modified = check_file_typography(fpath, auto_fix=auto_fix)
                    all_defects.extend(defects)
                    if modified:
                        files_fixed += 1

    return all_defects, files_fixed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="RimWorld Persian Typography & Character Validator"
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
        help="Automatically fix typography defects in place",
    )
    parser.add_argument(
        "--github",
        action="store_true",
        help="Print GitHub Actions workflow annotations",
    )
    args = parser.parse_args()

    repo_root = args.root
    dlcs = [args.dlc] if args.dlc else None

    defects, fixed_count = check_all_typography(repo_root, dlcs, auto_fix=args.fix)

    if not defects:
        print("\033[92m[OK] All Persian typography, characters, and ZWNJ rules are valid!\033[0m")
        return 0

    if args.fix:
        print(f"\033[92m[SUCCESS] Automatically repaired {len(defects)} defect(s) across {fixed_count} file(s)!\033[0m")
        return 0

    print(f"\033[91m[ERROR] Found {len(defects)} typography defect(s):\033[0m\n")

    for d in defects[:40]:  # Limit output in CLI if many
        rel_path = d.file.relative_to(repo_root) if d.file.is_relative_to(repo_root) else d.file
        if args.github:
            print(f"::error file={rel_path},line={d.line_num},title=Typography [{d.rule}]::{d.message}")
        else:
            print(f"\033[93m{rel_path}:{d.line_num}\033[0m [\033[1m{d.rule}\033[0m]")
            print(f"  \033[91m{d.message}\033[0m")
            print(f"  Current:   {d.original}")
            print(f"  Suggested: {d.suggested}")
            print()

    if len(defects) > 40:
        print(f"\033[93m... and {len(defects) - 40} more defects (run with --fix to automatically resolve them).\033[0m")

    return 1


if __name__ == "__main__":
    sys.exit(main())
