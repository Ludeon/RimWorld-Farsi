#!/usr/bin/env python3
"""
Missing String Extractor for RimWorld Persian Translation

This script parses English XML files and compares them with Persian XML files
to find missing or empty translations, outputting them in key==value format.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import lxml.etree as ET


def parse_xml_file(filepath: Path | str) -> dict[str, str]:
    """
    Parse an XML file safely and return a dictionary of key-value pairs.

    Args:
        filepath: Path to the XML file

    Returns:
        Dictionary with keys as XML tag names and values as text content
    """
    try:
        parser = ET.XMLParser(resolve_entities=False)
        tree = ET.parse(str(filepath), parser)
        root = tree.getroot()
        if root is None:
            return {}

        # Skip LanguageInfo.xml files as they contain metadata, not translations
        if root.tag == "LanguageInfo":
            return {}

        translations: dict[str, str] = {}
        for child in root:
            # Skip comments/processing instructions and nested elements
            if isinstance(child.tag, str) and len(child) == 0:
                key = child.tag.strip()
                value = child.text.strip() if child.text is not None else ""
                if key:
                    translations[key] = value

        return translations
    except ET.XMLSyntaxError as e:
        print(f"Warning: Could not parse {filepath}: {e}")
        return {}
    except FileNotFoundError:
        print(f"Warning: File not found: {filepath}")
        return {}


def find_xml_files(directory: Path | str) -> list[Path]:
    """
    Recursively find all XML files in a directory using Path.rglob.

    Args:
        directory: Root directory to search

    Returns:
        List of paths to XML files
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return []
    return sorted(dir_path.rglob("*.xml"))


def resolve_english_dir(project_root: Path, explicit_dir: Path | None = None) -> Path:
    """Resolve the English reference directory, preferring ``src/english``."""
    if explicit_dir is not None:
        return explicit_dir
    src_english = project_root / "src" / "english"
    if src_english.exists():
        return src_english
    return project_root / "english"


def get_corresponding_persian_path(
    english_path: Path | str,
    project_root: Path | None = None,
    english_dir: Path | None = None,
) -> Path:
    """Convert an English file path to its corresponding Persian path cross-platform.

    Args:
        english_path: Path to English XML file
        project_root: Optional root directory of the project
        english_dir: Optional root directory of English reference files

    Returns:
        Corresponding Persian XML file path
    """
    path_obj = Path(english_path)
    if project_root is not None:
        base_english = english_dir or resolve_english_dir(project_root)
        for candidate_base in (base_english, project_root / "src" / "english", project_root / "english"):
            try:
                rel = path_obj.relative_to(candidate_base)
                # 1. Official Ludeon layout: directly at project root (e.g. Core/DefInjected)
                root_candidate = project_root / rel
                if root_candidate.exists():
                    return root_candidate
                # 2. Legacy fallback: project_root / Data / rel
                data_candidate = project_root / "Data" / rel
                if data_candidate.exists():
                    return data_candidate
                return root_candidate
            except ValueError:
                continue

    parts = list(path_obj.parts)
    if "english" in parts:
        idx = parts.index("english")
        return Path(*parts[idx + 1 :])
    return path_obj


def main() -> None:
    """Main function to find missing translations."""
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    parser = argparse.ArgumentParser(
        description="Compare English reference XML files against Persian translations."
    )
    parser.add_argument(
        "--english-dir",
        type=Path,
        default=None,
        help="Path to English reference directory (default: src/english or english/)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=project_root / "TranslationReport.txt",
        help="Output report file path (default: TranslationReport.txt)",
    )
    args = parser.parse_args()

    english_dir = resolve_english_dir(project_root, args.english_dir)
    output_file = args.output

    if not english_dir.exists():
        print(f"Error: English reference directory not found: {english_dir}")
        sys.exit(1)

    has_persian_modules = (project_root / "Core").exists() or (
        project_root / "Data"
    ).exists()
    if not has_persian_modules:
        print(f"Error: Persian translation modules not found in {project_root}")
        sys.exit(1)

    print("Finding English XML files...")
    english_files = find_xml_files(english_dir)
    print(f"Found {len(english_files)} English XML files")

    missing_translations: dict[str, tuple[str, Path]] = {}

    for english_file in english_files:
        try:
            rel_display = english_file.relative_to(project_root)
        except ValueError:
            rel_display = english_file
        print(f"Processing: {rel_display}")

        # Parse English file
        english_translations = parse_xml_file(english_file)

        # Get corresponding Persian file
        persian_file = get_corresponding_persian_path(
            english_file, project_root, english_dir
        )

        # Parse Persian file
        persian_translations = parse_xml_file(persian_file)

        # Find missing or empty translations
        for key, english_value in english_translations.items():
            persian_value = persian_translations.get(key, "").strip()

            # Consider it missing if:
            # 1. Key doesn't exist in Persian
            # 2. Persian value is empty or None
            # 3. Persian value is the same as English (untranslated)
            if not persian_value or persian_value == english_value:
                missing_translations[key] = (english_value, persian_file)

    print(f"\nFound {len(missing_translations)} missing translations")

    # Write output file
    print(f"Writing results to {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        for key, value in sorted(missing_translations.items()):
            f.write(f"{key}=={value}\n")

    print("Done!")


if __name__ == "__main__":
    main()
