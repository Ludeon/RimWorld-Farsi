"""
XML Validation Script for Persian Translation Files.

This script validates all Persian/Farsi XML files across all RimWorld modules.
If any file fails to parse due to XML syntax errors, the script exits with code 1.

Usage:
    python validate_xml.py                    # Validates all Persian XML files
    python validate_xml.py [directory-path]   # Validates specific directory
"""

import os
import sys
from pathlib import Path

from lxml import etree


def validate_xml_file(file_path: str) -> tuple[bool, str]:
    """Validates a single XML file by attempting to parse it.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path.endswith(".xml"):
        return True, ""  # Skip non-XML files

    try:
        with open(file_path, "rb") as f:
            etree.parse(f)
        return True, ""
    except etree.XMLSyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def validate_directory(
    directory_path: str, show_success: bool = False
) -> tuple[int, int, list[tuple[str, str]]]:
    """Walks a directory and validates all found .xml files.

    Returns:
        Tuple of (total_files, valid_files, errors)
        where errors is a list of (file_path, error_message) tuples
    """
    total_files = 0
    valid_files = 0
    errors = []

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".xml"):
                total_files += 1
                file_path = os.path.join(root, file)
                is_valid, error_msg = validate_xml_file(file_path)

                if is_valid:
                    valid_files += 1
                    if show_success:
                        print(f"  [OK] {os.path.relpath(file_path, directory_path)}")
                else:
                    errors.append((file_path, error_msg))

    return total_files, valid_files, errors


def find_persian_directories(base_path: str) -> list[str]:
    """Find all Persian/Farsi language directories in the repo (root modules or Data folder)."""
    persian_dirs = []
    root_path = Path(base_path)

    # 1. Official Ludeon layout: top-level DLC modules
    known_modules = ["Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey"]
    for mod_name in known_modules:
        mod_dir = root_path / mod_name
        if mod_dir.is_dir() and (
            (mod_dir / "Keyed").exists() or (mod_dir / "DefInjected").exists()
        ):
            persian_dirs.append(str(mod_dir))

    # 2. Legacy fallback: Data/<DLC>/Languages/Persian
    data_path = root_path / "Data"
    if data_path.exists() and data_path.is_dir():
        for module_dir in data_path.iterdir():
            if module_dir.is_dir():
                persian_path = module_dir / "Languages" / "Persian"
                if persian_path.exists() and persian_path.is_dir():
                    persian_dirs.append(str(persian_path))

    return sorted(persian_dirs)


if __name__ == "__main__":
    # Determine what to validate
    if len(sys.argv) == 1:
        # No argument provided - validate all Persian directories
        script_dir = Path(__file__).parent.parent.parent  # Go up to project root
        persian_dirs = find_persian_directories(str(script_dir))

        if not persian_dirs:
            print(
                "[ERROR] No Persian translation directories found (checked root modules and Data/)"
            )
            sys.exit(1)

        print("=" * 70)
        print("XML VALIDATION FOR RIMWORLD FARSI TRANSLATION")
        print("=" * 70)
        print(f"\nFound {len(persian_dirs)} module(s) with Persian translations:\n")

        total_all = 0
        valid_all = 0
        all_errors = []

        for persian_dir in persian_dirs:
            p = Path(persian_dir)
            if p.name == "Persian" and p.parent.name == "Languages":
                module_name = p.parent.parent.name
            else:
                module_name = p.name
            print(f"Module: {module_name}")
            print("-" * 70)

            total, valid, errors = validate_directory(persian_dir, show_success=False)
            total_all += total
            valid_all += valid

            if errors:
                all_errors.extend(errors)
                print(f"  [!] {len(errors)} error(s) found in {total} file(s)")
                for file_path, error_msg in errors:
                    rel_path = os.path.relpath(file_path, persian_dir)
                    print(f"     [ERROR] {rel_path}")
                    print(f"             {error_msg}")
            else:
                print(f"  [OK] All {total} XML file(s) valid")
            print()

        # Summary
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Total XML files checked: {total_all}")
        print(f"Valid files: {valid_all}")
        print(f"Invalid files: {len(all_errors)}")

        if all_errors:
            print(f"\n[!] XML validation FAILED with {len(all_errors)} error(s)")
            sys.exit(1)
        else:
            print("\n[OK] All XML files are valid!")
            sys.exit(0)

    elif len(sys.argv) == 2:
        # Specific directory provided
        path = sys.argv[1]
        if not os.path.isdir(path):
            print(f"[ERROR] Directory not found: {path}")
            sys.exit(1)

        print("=" * 70)
        print(f"Validating XML files in: {path}")
        print("=" * 70)

        total, valid, errors = validate_directory(path, show_success=True)

        print("\n" + "=" * 70)
        print(f"Total: {total} | Valid: {valid} | Errors: {len(errors)}")

        if errors:
            print("\n❌ Errors found:")
            for file_path, error_msg in errors:
                print(f"  {file_path}")
                print(f"    {error_msg}")
            sys.exit(1)
        else:
            print("\n✅ All XML files are valid!")
            sys.exit(0)

    else:
        print("Usage: python validate_xml.py [directory-path]")
        print("  No arguments: Validates all Persian XML files in Data/")
        print("  With directory: Validates specific directory")
        sys.exit(1)
