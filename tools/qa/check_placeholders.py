#!/usr/bin/env python3
"""
RimWorld Placeholder & Token Integrity Validator
================================================
Validates that translation strings preserve all format tokens ({0}, {1}, {PAWN_nameDef}),
maintain correct macro syntax ({PAWN_gender ? male : female}), and do not translate
inside parameter braces.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Match anything within single curly braces
PLACEHOLDER_RE = re.compile(r"\{([^{}\n]*)\}")
EN_COMMENT_RE = re.compile(r"<!--\s*EN:\s*(.*?)\s*-->")
XML_TAG_RE = re.compile(r"<([A-Za-z0-9_.\-]+)>(.*?)</\1>")

# Gender macro: {SYMBOL_gender ? MASC : FEM (: NEUTER)?}
GENDER_MACRO_RE = re.compile(
    r"^\s*([A-Za-z0-9_]+_gender|[A-Za-z0-9_]+_Gender)\s*\?\s*([^:]*)\s*:\s*([^:}]*)(?:\s*:\s*([^:}]*))?\s*$"
)

# Detect Persian or Arabic characters inside token keys (before any ? or :)
PERSIAN_IN_KEY_RE = re.compile(r"[\u0600-\u06FF\uFB50-\uFEFC]")
PERSIAN_DIGITS_RE = re.compile(r"[۰-۹]")


@dataclass
class PlaceholderError:
    file: Path
    line_num: int
    tag: str
    message: str
    content: str


def extract_tokens(text: str) -> list[str]:
    """Extract all raw contents between curly braces."""
    return PLACEHOLDER_RE.findall(text)


def extract_positional_indices(text: str) -> set[str]:
    """Extract positional argument indices like '0' from '{0}' or '{0_label}'."""
    indices = set()
    for token in extract_tokens(text):
        m = re.match(r"^(\d+)", token.strip())
        if m:
            indices.add(m.group(1))
    return indices


def check_file_placeholders(file_path: Path) -> list[PlaceholderError]:
    """Inspect a single XML file for placeholder and macro defects."""
    errors: list[PlaceholderError] = []

    try:
        with open(file_path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception as e:
        errors.append(
            PlaceholderError(file_path, 1, "FILE_READ", f"Failed to read file: {e}", "")
        )
        return errors

    last_en_text: str | None = None
    last_en_line = 0

    for idx, line in enumerate(lines, start=1):
        # Look for English source comment: <!-- EN: ... -->
        en_match = EN_COMMENT_RE.search(line)
        if en_match:
            last_en_text = en_match.group(1)
            last_en_line = idx
            continue

        # Look for translated XML tag: <Tag>...</Tag>
        tag_match = XML_TAG_RE.search(line)
        if tag_match:
            tag_name = tag_match.group(1)
            tag_content = tag_match.group(2)

            # 1. Check for unbalanced curly braces
            open_count = tag_content.count("{")
            close_count = tag_content.count("}")
            if open_count != close_count:
                errors.append(
                    PlaceholderError(
                        file=file_path,
                        line_num=idx,
                        tag=tag_name,
                        message=f"Mismatched curly braces: {open_count} open vs {close_count} close",
                        content=line.strip(),
                    )
                )

            # 2. Extract FA tokens
            fa_tokens = extract_tokens(tag_content)

            # Check individual tokens
            for token in fa_tokens:
                # Check for Persian numbers like {۰} instead of {0}
                if PERSIAN_DIGITS_RE.search(token):
                    errors.append(
                        PlaceholderError(
                            file=file_path,
                            line_num=idx,
                            tag=tag_name,
                            message=f"Persian digits used inside token: '{{{token}}}'. Must use standard Latin digits.",
                            content=line.strip(),
                        )
                    )

                # Check for Persian text inside the symbol/key name (before ? or :)
                key_part = token.split("?")[0].split(":")[0].strip()
                if PERSIAN_IN_KEY_RE.search(key_part):
                    errors.append(
                        PlaceholderError(
                            file=file_path,
                            line_num=idx,
                            tag=tag_name,
                            message=f"Persian text found in token identifier: '{{{key_part}}}'. Identifiers must remain in English.",
                            content=line.strip(),
                        )
                    )

                # Check gender macro
                if "_gender" in token.lower() and "?" in token:
                    macro_m = GENDER_MACRO_RE.match(token)
                    if macro_m:
                        val_masc = macro_m.group(2).strip()
                        val_fem = macro_m.group(3).strip()
                        if val_masc == val_fem and val_masc != "":
                            errors.append(
                                PlaceholderError(
                                    file=file_path,
                                    line_num=idx,
                                    tag=tag_name,
                                    message=f"Gender macro has identical branches ('{val_masc}'): '{{{token}}}'",
                                    content=line.strip(),
                                )
                            )
                    else:
                        # Malformed gender macro syntax
                        errors.append(
                            PlaceholderError(
                                file=file_path,
                                line_num=idx,
                                tag=tag_name,
                                message=f"Malformed gender macro syntax: '{{{token}}}'",
                                content=line.strip(),
                            )
                        )

            # 3. Compare with EN source if comment is within 3 lines
            if last_en_text and (idx - last_en_line <= 3):
                en_indices = extract_positional_indices(last_en_text)
                fa_indices = extract_positional_indices(tag_content)

                # Check for missing positional arguments
                missing = en_indices - fa_indices
                if missing:
                    errors.append(
                        PlaceholderError(
                            file=file_path,
                            line_num=idx,
                            tag=tag_name,
                            message=f"Missing positional token(s) {sorted(missing)} present in English comment: '{last_en_text}'",
                            content=line.strip(),
                        )
                    )

                # Check for extra positional arguments not in English
                extra = fa_indices - en_indices
                if extra:
                    errors.append(
                        PlaceholderError(
                            file=file_path,
                            line_num=idx,
                            tag=tag_name,
                            message=f"Extra positional token(s) {sorted(extra)} not present in English comment: '{last_en_text}'",
                            content=line.strip(),
                        )
                    )

            # Reset comment
            last_en_text = None

    return errors


def check_all_placeholders(
    root_dir: Path, dlcs: list[str] | None = None
) -> list[PlaceholderError]:
    """Scan all XML files in designated DLCs."""
    if dlcs is None:
        dlcs = ["Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey"]

    all_errors: list[PlaceholderError] = []

    for dlc in dlcs:
        dlc_path = root_dir / dlc
        if not dlc_path.exists():
            continue

        for root, _, files in os.walk(dlc_path):
            for file in sorted(files):
                if file.lower().endswith(".xml"):
                    fpath = Path(root) / file
                    errs = check_file_placeholders(fpath)
                    all_errors.extend(errs)

    return all_errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="RimWorld Placeholder & Token Integrity Validator"
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
        "--github",
        action="store_true",
        help="Print GitHub Actions workflow annotations",
    )
    args = parser.parse_args()

    repo_root = args.root
    dlcs = [args.dlc] if args.dlc else None

    errors = check_all_placeholders(repo_root, dlcs)

    if not errors:
        print("\033[92m[OK] All placeholders and format tokens are valid!\033[0m")
        return 0

    print(f"\033[91m[ERROR] Found {len(errors)} placeholder defect(s):\033[0m\n")

    for err in errors:
        rel_path = err.file.relative_to(repo_root) if err.file.is_relative_to(repo_root) else err.file
        if args.github:
            print(
                f"::error file={rel_path},line={err.line_num},title=Placeholder Error::{err.message}"
            )
        else:
            print(f"\033[93m{rel_path}:{err.line_num}\033[0m (\033[1m<{err.tag}>\033[0m)")
            print(f"  \033[91m{err.message}\033[0m")
            if err.content:
                print(f"  {err.content}")
            print()

    return 1


if __name__ == "__main__":
    sys.exit(main())
