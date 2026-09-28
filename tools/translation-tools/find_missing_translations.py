#!/usr/bin/env python3
"""
Missing String Extractor for RimWorld Persian Translation

This script parses English XML files and compares them with Persian XML files
to find missing or empty translations, outputting them in key==value format.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_xml_file(filepath: Path | str) -> dict[str, str]:
    """
    Parse an XML file and return a dictionary of key-value pairs.

    Args:
        filepath: Path to the XML file

    Returns:
        Dictionary with keys as XML tag names and values as text content
    """
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        # Skip LanguageInfo.xml files as they contain metadata, not translations
        if root.tag == "LanguageInfo":
            return {}

        translations: dict[str, str] = {}
        for child in root:
            # Only process elements that have simple text content (no nested elements)
            if len(child) == 0:  # len(child) == 0 means no child elements
                # Strip whitespace and normalize
                key = child.tag.strip()
                value = child.text.strip() if child.text is not None else ""
                if key:  # Only add if key is not empty
                    translations[key] = value

        return translations
    except ET.ParseError as e:
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


def get_corresponding_persian_path(
    english_path: Path | str, project_root: Path | None = None
) -> Path:
    """Convert an English file path to its corresponding Persian path cross-platform.

    Args:
        english_path: Path to English XML file
        project_root: Optional root directory of the project

    Returns:
        Corresponding Persian XML file path
    """
    path_obj = Path(english_path)
    if project_root is not None:
        try:
            rel = path_obj.relative_to(project_root / "english")
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
            pass

    parts = list(path_obj.parts)
    if "english" in parts:
        idx = parts.index("english")
        parts.pop(idx)  # Map english/<module> to <module>
        return Path(*parts)
    return path_obj


def main() -> None:
    """Main function to find missing translations."""
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    english_dir = project_root / "english"
    output_file = project_root / "TranslationReport.txt"

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
        persian_file = get_corresponding_persian_path(english_file, project_root)

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
