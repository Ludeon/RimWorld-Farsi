"""
XML Validation Script for Persian Translation Files.

This script validates all XML files in a given directory to ensure they parse correctly.
If any file fails to parse due to XML syntax errors, the script exits with code 1,
failing the GitHub Action.
"""

import os
import sys

from lxml import etree


def validate_xml_file(file_path: str) -> bool:
    """Validates a single XML file by attempting to parse it."""
    if not file_path.endswith(".xml"):
        return True  # Skip non-XML files

    try:
        with open(file_path, "rb") as f:
            etree.parse(f)
        print(f"[OK] Valid XML: {file_path}")
        return True
    except etree.XMLSyntaxError as e:
        print(f"[ERROR] Failed to parse {file_path}: {e}")
        return False


def validate_directory(directory_path: str) -> bool:
    """Walks a directory and validates all found .xml files."""
    all_valid = True
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".xml"):
                file_path = os.path.join(root, file)
                if not validate_xml_file(file_path):
                    all_valid = False
    return all_valid


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_xml.py [directory-path]")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.isdir(path):
        print(f"[ERROR] Directory not found: {path}")
        sys.exit(1)

    print("--- Starting XML validation ---")
    if validate_directory(path):
        print("--- All XML files are valid! ---")
    else:
        print("--- XML validation failed! ---")
        sys.exit(1)
