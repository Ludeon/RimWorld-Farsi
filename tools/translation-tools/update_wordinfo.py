#!/usr/bin/env python3
"""
RimWorld Persian WordInfo Generator and Synchronizer
=====================================================
Extracts entity names and translatable labels from DefInjected XMLs
across RimWorld Core and DLCs, generating and synchronizing Persian
WordInfo lookup tables:
  - plural.txt: Pluralization lookup table ({lookup: {0}; plural; 1})
  - ezafeh.txt: Ezāfeh connector lookup table ({lookup: {0}; ezafeh; 1})
  - new_words.txt: Newly detected terms requiring translator review
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("update_wordinfo")

ZWNJ = "\u200C"  # Zero-Width Non-Joiner (نیم‌فاصله)

# Recognized DLC folders
DEFAULT_DLCS = ["Core", "Royalty", "Ideology", "Biotech", "Anomaly", "Odyssey"]

# Tags in DefInjected XML files that specify noun titles or entity labels
TARGET_TAG_PATTERNS = re.compile(
    r"^.*(\.label|\.labelMale|\.labelFemale|\.labelPlural|\.chargeNoun|\.pawnSingular|\.customLabel)$|"
    r"^(title|titleFemale|pawnSingular|chargeNoun|customLabel)$",
    re.IGNORECASE,
)

# Persian human / rational beings list for animate plural suffix (-ان / -یان / -گان)
ANIMATE_NOUN_STEMS = {
    "استعمارگر": "استعمارگران",
    "ساکن": "ساکنان",
    "مهاجم": "مهاجمان",
    "جنگجو": "جنگجویان",
    "سرباز": "سربازان",
    "فرمانده": "فرماندهان",
    "پزشک": "پزشکان",
    "پرستار": "پرستاران",
    "زندانی": "زندانیان",
    "برده": "بردگان",
    "نگهبان": "نگهبانان",
    "دانشمند": "دانشمندان",
    "پژوهشگر": "پژوهشگران",
    "کشاورز": "کشاورزان",
    "شکارچی": "شکارچیان",
    "کارگر": "کارگران",
    "معدنچی": "معدنچیان",
    "سازنده": "سازندگان",
    "مهندس": "مهندسان",
    "پیشه‌ور": "پیشه‌وران",
    "آهنگر": "آهنگران",
    "آشپز": "آشپزان",
    "هنرمند": "هنرمندان",
    "شاعر": "شاعران",
    "نویسنده": "نویسندگان",
    "کودک": "کودکان",
    "بچه": "بچه‌ها",
    "نوزاد": "نوزادان",
    "جوان": "جوانان",
    "سالمند": "سالمندان",
    "پیرمرد": "پیرمردان",
    "پیرزن": "پیرزنان",
    "مرد": "مردان",
    "زن": "زنان",
    "انسان": "انسان‌ها",
    "دوست": "دوستان",
    "دشمن": "دشمنان",
    "هم‌پیمان": "هم‌پیمانان",
    "پناهنده": "پناهندگان",
    "بیگانه": "بیگانگان",
    "غریبه": "غریبه‌ها",
    "مکانوید": "مکانویدها",
    "حشره": "حشرات",
    "حیوان": "حیوانات",
}


def normalize_persian_text(text: str) -> str:
    """Normalize Arabic characters to authentic Persian equivalents and strip whitespace."""
    if not text:
        return ""
    text = text.replace("ك", "ک").replace("ي", "ی").replace("ى", "ی")
    # Clean up multi-space
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text


def clean_label(text: str) -> str:
    """Clean label text, removing trailing punct or formatting tags."""
    text = normalize_persian_text(text)
    # Remove XML comments or trailing punctuation
    text = re.sub(r"<!--.*?-->", "", text).strip()
    text = text.rstrip(".:،؛!?؟")
    return text.lower()


def generate_persian_plural(word: str) -> str:
    """
    Generate natural Persian plural for a given noun.
    - Animate/Human terms: -ان / -گان / -یان
    - General/Inanimate: -‌ها with ZWNJ
    """
    word = clean_label(word)
    if not word:
        return ""

    # Check known dictionary first
    if word in ANIMATE_NOUN_STEMS:
        return ANIMATE_NOUN_STEMS[word]

    # If word already ends with ها or ان, keep it
    if word.endswith("ها") or word.endswith("ان"):
        return word

    # Words ending in silent 'ه' (e.g. برده -> بردگان, جنگنده -> جنگنده‌ها)
    if word.endswith("ه"):
        # Most modern tech/item nouns take -‌ها
        return f"{word}{ZWNJ}ها"

    # Words ending in vowels 'ا' or 'و'
    if word.endswith("ا") or word.endswith("و"):
        return f"{word}{ZWNJ}ها"

    # General default rule: noun + ZWNJ + ها
    return f"{word}{ZWNJ}ها"


def generate_persian_ezafeh(word: str) -> str:
    """
    Generate Ezāfeh form for noun-phrase connection:
    - Words ending in vowel 'ا' (Alef) or 'و' (Vav) -> append 'ی' (e.g. چاقو -> چاقوی)
    - Words ending in silent 'ه' -> append '‌ی' (ZWNJ + 'ی': مستعمره -> مستعمره‌ی)
    - Words ending in 'ی' -> append 'ِ' (Kasra)
    - Words ending in standard consonant -> append 'ِ' (Kasra)
    """
    word = clean_label(word)
    if not word:
        return ""

    if word.endswith("ا") or word.endswith("و"):
        return f"{word}ی"

    if word.endswith("ه"):
        return f"{word}{ZWNJ}ی"

    if word.endswith("ی"):
        return f"{word}\u0650"

    # Consonant: append Kasra mark for explicit disambiguation
    return f"{word}\u0650"


def parse_definjected_labels(dlc_dir: Path) -> set[str]:
    """Scan all DefInjected XML files in a DLC folder and extract unique words/labels."""
    definjected_dir = dlc_dir / "DefInjected"
    labels: set[str] = set()

    if not definjected_dir.exists():
        return labels

    for root, _, files in os.walk(definjected_dir):
        for file in files:
            if not file.lower().endswith(".xml"):
                continue
            filepath = Path(root) / file
            try:
                tree = ET.parse(filepath)
                for elem in tree.iter():
                    if TARGET_TAG_PATTERNS.match(elem.tag):
                        val = clean_label(elem.text or "")
                        # Exclude format templates, grammar arrows, or empty strings
                        if val and "->" not in val and "{" not in val and len(val) < 60:
                            labels.add(val)
            except Exception as e:
                logger.warning("Could not parse %s: %s", filepath, e)

    return labels


def load_existing_table(file_path: Path) -> dict[str, str]:
    """Load existing WordInfo table into a dictionary (KEY -> VALUE)."""
    table: dict[str, str] = {}
    if not file_path.exists():
        return table

    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            parts = line.split(";")
            if len(parts) >= 2:
                key = clean_label(parts[0])
                val = normalize_persian_text(parts[1])
                if key:
                    table[key] = val
    return table


def write_table(file_path: Path, header_comment: str, entries: dict[str, str]) -> None:
    """Write table to file in standard RimWorld WordInfo CSV format."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    sorted_entries = sorted(entries.items(), key=lambda x: x[0])

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(header_comment.strip() + "\n")
        for key, val in sorted_entries:
            f.write(f"{key};{val}\n")


def update_dlc_wordinfo(
    dlc_dir: Path, dry_run: bool = False
) -> tuple[int, int, int]:
    """
    Process a single DLC folder:
    Extracts def labels, updates plural.txt and ezafeh.txt, and logs new words.
    Returns: (total_labels, new_plurals, new_ezafeh)
    """
    dlc_name = dlc_dir.name
    logger.info("Processing WordInfo for %s...", dlc_name)

    labels = parse_definjected_labels(dlc_dir)
    if not labels:
        logger.info("  No DefInjected labels found for %s. Skipping.", dlc_name)
        return (0, 0, 0)

    wordinfo_dir = dlc_dir / "WordInfo"
    plural_file = wordinfo_dir / "plural.txt"
    ezafeh_file = wordinfo_dir / "ezafeh.txt"
    new_words_file = wordinfo_dir / "new_words.txt"

    existing_plurals = load_existing_table(plural_file)
    existing_ezafeh = load_existing_table(ezafeh_file)

    updated_plurals = dict(existing_plurals)
    updated_ezafeh = dict(existing_ezafeh)
    new_words: set[str] = set()

    for word in labels:
        is_new = False
        if word not in updated_plurals:
            updated_plurals[word] = generate_persian_plural(word)
            is_new = True
        if word not in updated_ezafeh:
            updated_ezafeh[word] = generate_persian_ezafeh(word)
            is_new = True
        if is_new:
            new_words.add(word)

    new_plurals_count = len(updated_plurals) - len(existing_plurals)
    new_ezafeh_count = len(updated_ezafeh) - len(existing_ezafeh)

    logger.info(
        "  %s: %d total labels | +%d new plurals | +%d new ezafeh | %d new unreviewed words",
        dlc_name,
        len(labels),
        new_plurals_count,
        new_ezafeh_count,
        len(new_words),
    )

    if not dry_run:
        plural_header = (
            f"// Auto-generated WordInfo plural table for {dlc_name}\n"
            "// Usage syntax: {lookup: {0}; plural; 1}\n"
            "// SINGULAR;PLURAL"
        )
        write_table(plural_file, plural_header, updated_plurals)

        ezafeh_header = (
            f"// Auto-generated WordInfo Ezāfeh table for {dlc_name}\n"
            "// Usage syntax: {lookup: {0}; ezafeh; 1}\n"
            "// BASE;EZAFEH_FORM"
        )
        write_table(ezafeh_file, ezafeh_header, updated_ezafeh)

        if new_words:
            wordinfo_dir.mkdir(parents=True, exist_ok=True)
            with open(new_words_file, "w", encoding="utf-8") as f:
                f.write(f"// New words detected in {dlc_name} needing translator review\n")
                for w in sorted(new_words):
                    f.write(f"{w}\n")

    return (len(labels), new_plurals_count, new_ezafeh_count)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="RimWorld Persian WordInfo Generator & Synchronizer"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent,
        help="Repository root directory (defaults to parent of tools/)",
    )
    parser.add_argument(
        "--dlc",
        type=str,
        default="",
        help="Specific DLC name to process (e.g. Core, Royalty, etc.). Defaults to all.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a trial run without modifying files",
    )
    args = parser.parse_args()

    repo_root = args.root
    if not repo_root.exists():
        logger.error("Repository root does not exist: %s", repo_root)
        return 1

    dlcs_to_process = [args.dlc] if args.dlc else DEFAULT_DLCS
    total_scanned = 0
    total_new_plurals = 0
    total_new_ezafeh = 0

    for dlc_name in dlcs_to_process:
        dlc_path = repo_root / dlc_name
        if dlc_path.exists() and dlc_path.is_dir():
            scanned, n_plur, n_eza = update_dlc_wordinfo(dlc_path, dry_run=args.dry_run)
            total_scanned += scanned
            total_new_plurals += n_plur
            total_new_ezafeh += n_eza
        else:
            logger.warning("DLC folder not found: %s", dlc_path)

    logger.info("==================================================")
    logger.info("Summary: %d labels scanned across %d modules", total_scanned, len(dlcs_to_process))
    logger.info("New Plural entries: %d | New Ezāfeh entries: %d", total_new_plurals, total_new_ezafeh)
    if args.dry_run:
        logger.info("Dry run complete. No files were written.")
    else:
        logger.info("WordInfo synchronization completed successfully.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
