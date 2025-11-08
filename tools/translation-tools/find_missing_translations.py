#!/usr/bin/env python3
"""
Missing String Extractor for RimWorld Persian Translation

This script parses English XML files and compares them with Persian XML files
to find missing or empty translations, outputting them in key==value format.
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List
import sys

def parse_xml_file(filepath: str) -> Dict[str, str]:
    """
    Parse an XML file and return a dictionary of key-value pairs.

    Args:
        filepath (str): Path to the XML file

    Returns:
        dict: Dictionary with keys as XML tag names and values as text content
    """
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        # Skip LanguageInfo.xml files as they contain metadata, not translations
        if root.tag == 'LanguageInfo':
            return {}

        translations = {}
        for child in root:
            # Only process elements that have simple text content (no nested elements)
            if len(child) == 0:  # len(child) == 0 means no child elements
                # Strip whitespace and normalize
                key = child.tag.strip()
                value = child.text.strip() if child.text is not None else ''
                if key:  # Only add if key is not empty
                    translations[key] = value

        return translations
    except ET.ParseError as e:
        print(f"Warning: Could not parse {filepath}: {e}")
        return {}
    except FileNotFoundError:
        print(f"Warning: File not found: {filepath}")
        return {}

def find_xml_files(directory: str) -> List[str]:
    """
    Recursively find all XML files in a directory.

    Args:
        directory (str): Root directory to search

    Returns:
        list: List of paths to XML files
    """
    xml_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    return xml_files

def get_corresponding_persian_path(english_path: str) -> str:
    """
    Convert an English file path to its corresponding Persian path.

    Args:
        english_path (str): Path to English XML file

    Returns:
        str: Corresponding Persian XML file path
    """
    # Replace 'english/' with 'Persian/' in the path
    return english_path.replace('english/', 'Persian/', 1)

def main():
    """
    Main function to find missing translations.
    """
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    english_dir = project_root / 'english'
    persian_dir = project_root / 'Persian'
    output_file = project_root / 'to_translate.txt'

    if not english_dir.exists():
        print(f"Error: English directory not found: {english_dir}")
        sys.exit(1)

    if not persian_dir.exists():
        print(f"Error: Persian directory not found: {persian_dir}")
        sys.exit(1)

    print("Finding English XML files...")
    english_files = find_xml_files(str(english_dir))
    print(f"Found {len(english_files)} English XML files")

    missing_translations = {}

    for english_file in english_files:
        print(f"Processing: {os.path.relpath(english_file, project_root)}")

        # Parse English file
        english_translations = parse_xml_file(english_file)

        # Get corresponding Persian file
        persian_file = get_corresponding_persian_path(english_file)

        # Parse Persian file
        persian_translations = parse_xml_file(persian_file)

        # Find missing or empty translations
        for key, english_value in english_translations.items():
            persian_value = persian_translations.get(key, '').strip()

            # Consider it missing if:
            # 1. Key doesn't exist in Persian
            # 2. Persian value is empty or None
            if not persian_value:
                missing_translations[key] = english_value

    print(f"\nFound {len(missing_translations)} missing translations")

    # Write output file
    print(f"Writing results to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        for key, value in sorted(missing_translations.items()):
            f.write(f"{key}=={value}\n")

    print("Done!")

if __name__ == '__main__':
    main()
