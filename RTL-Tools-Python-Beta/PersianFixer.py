"""
Combined and tuned script for processing Persian XML translation files.

This script performs two main operations in sequence, replicating the behavior
of the original build process:
1.  Reverses the order of words and the letters within each word for RTL text.
    It correctly handles mixed English/Persian text by only reversing words
    that contain RTL characters.
2.  Converts standard Persian/Arabic letters into their contextual presentation
    forms (isolated, initial, medial, final).

The logic, including specific bugs from the original separate scripts, has been
preserved to ensure identical output.
"""
import sys
import os
import re
from lxml import etree
from typing import List, Optional, Tuple

# --- Constants: Letter Maps and Character Sets ---

# Maps standard letters to their Unicode presentation form start codes.
LETTER_MAP = {
    'ء': 0xFE80, 'آ': 0xFE81, 'أ': 0xFE83, 'ؤ': 0xFE85, 'إ': 0xFE87,
    'ا': 0xFE8D, 'ب': 0xFE8F, 'پ': 0xFB56, 'ة': 0xFE93, 'ت': 0xFE95,
    'ث': 0xFE99, 'ج': 0xFE9D, 'چ': 0xFB7A, 'ح': 0xFEA1, 'خ': 0xFEA5,
    'د': 0xFEA9, 'ذ': 0xFEAB, 'ر': 0xFEAD, 'ز': 0xFEAF, 'ژ': 0x0698,
    'س': 0xFEB1, 'ش': 0xFEB5, 'ص': 0xFEB9, 'ض': 0xFEBD, 'ط': 0xFEC1,
    'ظ': 0xFEC5, 'ع': 0xFEC9, 'غ': 0xFECD, 'ف': 0xFED1, 'ق': 0xFED5,
    'ک': 0xFB8E, 'گ': 0xFB92, 'ل': 0xFEDD, 'م': 0xFEE1, 'ن': 0xFEE5,
    'ه': 0xFEE9, 'و': 0xFEED, 'ی': 0xFBFC, 'ي': 0xFEF1, 'ئ': 0xFE89
}

# Maps 'Alef' variants to their combined 'Lam-Alef' ligature codes.
LAM_ALEF_MAP = {'آ': 0xFEF5, 'أ': 0xFEF7, 'إ': 0xFEF9, 'ا': 0xFEFB}

CONNECTING_LETTERS = 'بپتثجچحخسشصضطظعغفقکگلمنهيی'
NON_CONNECTING_LETTERS = 'اأإآدذرزژوؤةى'
ISOLATED_LETTERS = 'ء'
ALEF_VARIANTS = 'اأإآ'
RTL_CHAR_REGEX = r'[\u0600-\u06FF\u0590-\u05FF]'
PLACEHOLDER_REGEX = r'{.*?}'

# --- Core Processing Logic ---

def process_node(node: etree._Element) -> None:
    """
    Applies the full reversal and contextualization logic to an XML node's text.
    """
    content = node.text
    if not content or not re.search(RTL_CHAR_REGEX, content):
        return

    # 1. Split text into words.
    words = content.split()
    
    # 2. Process each word: first reverse letters (if RTL), then contextualize.
    processed_words = [_process_word(word) for word in words]
    
    # 3. Reverse the order of the fully processed words and join them back.
    processed_words.reverse()
    node.text = ' '.join(processed_words)

def _process_word(word: str) -> str:
    """
    Applies letter reversal (if needed) and contextualization to a single word.
    """
    reversed_word = _reverse_rtl_word_letters(word)
    contextualized_word = _contextualize_word(reversed_word)
    return contextualized_word

def _reverse_rtl_word_letters(word: str) -> str:
    """
    Reverses the letters in a word *only if* it contains RTL characters,
    while preserving any placeholders like {0}.
    """
    placeholders = [(m.group(), m.start()) for m in re.finditer(PLACEHOLDER_REGEX, word)]
    word_no_placeholders = re.sub(PLACEHOLDER_REGEX, '', word)

    # **FIX**: Only reverse letters if the specific word contains RTL characters.
    if not re.search(RTL_CHAR_REGEX, word_no_placeholders):
        return word # Return original word if it's not RTL (e.g., English)

    reversed_word = word_no_placeholders[::-1]

    # Re-insert placeholders at their original indexed positions
    for ph, idx in placeholders:
        reversed_word = reversed_word[:idx] + ph + reversed_word[idx:]
        
    return reversed_word

def _contextualize_word(word: str) -> str:
    """
    Applies letter contextualization to a single word.
    This function contains the original, buggy logic to ensure identical output.
    """
    new_word = ''
    word_chars = list(word)
    idx = 0
    
    # State for Lam-Alef combinations, reset for each word.
    letter_was_combined = False
    combining_alef = ''
    
    while idx < len(word_chars):
        letter = word_chars[idx]
        
        # !! PRESERVED BUG !!
        # The original script swaps 'previous' and 'next' letter lookups. This
        # is preserved because it operates on an already-reversed string.
        prev_letter = word_chars[idx + 1] if idx < len(word_chars) - 1 else None
        next_letter = word_chars[idx - 1] if idx > 0 else None

        # --- Lam-Alef ligature handling ---
        if letter_was_combined:
            letter_was_combined = False
            new_word += _create_lam_alef_combo(prev_letter, combining_alef)
            idx += 1
            continue

        if letter in ALEF_VARIANTS and prev_letter == 'ل':
            letter_was_combined = True
            combining_alef = letter
            idx += 1
            continue
        
        # --- Standard letter handling ---
        if letter in ISOLATED_LETTERS:
            new_word += letter
        elif letter in CONNECTING_LETTERS:
            new_word += _get_contextual_connecting(letter, prev_letter, next_letter)
        elif letter in NON_CONNECTING_LETTERS:
            new_word += _get_contextual_non_connecting(letter, prev_letter)
        else:
            new_word += letter # Handle placeholders, English chars, etc.
            
        idx += 1
        
    return new_word

# --- Contextual Form Helper Functions ---

def _create_lam_alef_combo(prev_letter: Optional[str], alef_variant: str) -> str:
    combo_code = LAM_ALEF_MAP.get(alef_variant)
    if combo_code is None:
        return alef_variant
    
    if prev_letter and prev_letter in CONNECTING_LETTERS and not re.match(PLACEHOLDER_REGEX, prev_letter):
        combo_code += 1  # Use the connecting form of the ligature
    
    return chr(combo_code)

def _get_contextual_connecting(letter: str, prev_letter: Optional[str], next_letter: Optional[str]) -> str:
    base_code = LETTER_MAP.get(letter)
    if base_code is None: return letter

    connects_from_prev = prev_letter and prev_letter in CONNECTING_LETTERS and not re.match(PLACEHOLDER_REGEX, prev_letter)
    connects_to_next = next_letter and next_letter in (CONNECTING_LETTERS + NON_CONNECTING_LETTERS) and not re.match(PLACEHOLDER_REGEX, next_letter)

    if connects_from_prev and connects_to_next: return chr(base_code + 3)  # Middle
    if connects_from_prev: return chr(base_code + 1)  # Final
    if connects_to_next: return chr(base_code + 2)  # Initial
    return chr(base_code)      # Isolated

def _get_contextual_non_connecting(letter: str, prev_letter: Optional[str]) -> str:
    base_code = LETTER_MAP.get(letter)
    if base_code is None: return letter
        
    if prev_letter and prev_letter in CONNECTING_LETTERS and not re.match(PLACEHOLDER_REGEX, prev_letter):
        return chr(base_code + 1)  # Final
    return chr(base_code)      # Isolated

# --- File and Directory Parsing ---

def process_xml_file(file_path: str) -> None:
    """Parses a single XML file and applies processing to all leaf nodes."""
    if not file_path.endswith('.xml'):
        print(f"[WARN] Skipping non-XML file: {file_path}")
        return

    parser = etree.XMLParser(remove_blank_text=False)
    try:
        with open(file_path, 'rb') as f:
            doc = etree.parse(f, parser)
    except etree.XMLSyntaxError as e:
        print(f"[EROR] Failed to parse {file_path}: {e}")
        return

    if not doc.xpath('//LanguageInfo | //LanguageData'):
        print(f"[WARN] No expected root nodes in {file_path}; skipping.")
        return

    for node in doc.xpath('//*[not(*)]'):
        process_node(node)

    with open(file_path, 'wb') as f:
        f.write(etree.tostring(doc, pretty_print=True, encoding='utf-8', xml_declaration=True))
    print(f"[INFO] Successfully processed: {file_path}")

def process_directory(directory_path: str) -> None:
    """Walks a directory and processes all found .xml files."""
    print("\n--- Starting RTL text processing ---")
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.xml'):
                process_xml_file(os.path.join(root, file))
    print("--- Processing complete! ---")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_persian_final.py [file-path|directory-path]")
        sys.exit(1)

    path = sys.argv[1]
    if os.path.isdir(path):
        process_directory(path)
    elif os.path.isfile(path):
        process_xml_file(path)
    else:
        print(f"[EROR] Path not found: {path}")
        sys.exit(1)