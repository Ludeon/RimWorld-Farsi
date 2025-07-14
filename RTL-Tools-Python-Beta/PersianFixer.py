# -*- coding: utf-8 -*-
import sys
import os
import re
from lxml import etree

# Persian/Arabic letter contextual forms mapping
LETTER_MAP = {
    'ء': 0xFE80, 'آ': 0xFE81, 'أ': 0xFE83, 'ؤ': 0xFE85, 'إ': 0xFE87, 'ا': 0xFE8D,
    'ب': 0xFE8F, 'پ': 0xFB56, 'ة': 0xFE93, 'ت': 0xFE95, 'ث': 0xFE99, 'ج': 0xFE9D,
    'چ': 0xFB7A, 'ح': 0xFEA1, 'خ': 0xFEA5, 'د': 0xFEA9, 'ذ': 0xFEAB, 'ر': 0xFEAD,
    'ز': 0xFEAF, 'ژ': 0x0698, 'س': 0xFEB1, 'ش': 0xFEB5, 'ص': 0xFEB9, 'ض': 0xFEBD,
    'ط': 0xFEC1, 'ظ': 0xFEC5, 'ع': 0xFEC9, 'غ': 0xFECD, 'ف': 0xFED1, 'ق': 0xFED5,
    'ک': 0xFB8E, 'گ': 0xFB92, 'ل': 0xFEDD, 'م': 0xFEE1, 'ن': 0xFEE5, 'ه': 0xFEE9,
    'و': 0xFEED, 'ی': 0xFBFC, 'ي': 0xFEF1, 'ئ': 0xFE89
}

LAM_ALEF_MAP = {
    'آ': 0xFEF5, 'أ': 0xFEF7, 'إ': 0xFEF9, 'ا': 0xFEFB
}

CONNECTING_LETTERS = 'بپتثجچحخسشصضطظعغفقکگلمنهيیئ'
NON_CONNECTING_LETTERS = 'اأإآدذرزژوؤةىء'
ALEF_VARIATIONS = 'اأإآ'

def is_connecting(letter):
    return letter in CONNECTING_LETTERS

def contextualize(text):
    if not text or not re.search(r'[\u0600-\u06FF]', text):
        return text

    res = ''
    for i, char in enumerate(text):
        # Lam-Alef combination
        if char == 'ل' and i + 1 < len(text) and text[i+1] in ALEF_VARIATIONS:
            continue  # Skip 'ل' as it will be handled with Alef

        if char in ALEF_VARIATIONS and i > 0 and text[i-1] == 'ل':
            prev_char_is_connecting = i > 1 and is_connecting(text[i-2])
            lam_alef_code = LAM_ALEF_MAP.get(char)
            if lam_alef_code:
                res += chr(lam_alef_code + (1 if prev_char_is_connecting else 0))
            else:
                res += char # Should not happen
            continue

        code = LETTER_MAP.get(char)
        if not code:
            res += char
            continue

        prev_char_connects = i > 0 and is_connecting(text[i-1]) and text[i-1] != 'ل'
        next_char_connects = i + 1 < len(text) and is_connecting(char)

        if prev_char_connects and next_char_connects:
            res += chr(code + 3)  # Medial
        elif prev_char_connects:
            res += chr(code + 1)  # Final
        elif next_char_connects:
            res += chr(code + 2)  # Initial
        else:
            res += chr(code)      # Isolated

    return res

def reverse_text(text):
    if not text or not re.search(r'[\u0600-\u06FF\u0590-\u05FF]', text):
        return text
    
    # Regex to split text by placeholders, keeping the placeholders
    parts = re.split(r'({.*?})', text)
    
    # Reverse each part that is not a placeholder
    reversed_parts = [part[::-1] if not re.match(r'{.*?}', part) else part for part in parts]
    
    # Join the parts back together
    return "".join(reversed_parts)

def process_node_text(text):
    if not text or not re.search(r'[\u0600-\u06FF]', text):
        return text

    words = text.split(' ')
    processed_words = []
    for word in words:
        contextualized_word = contextualize(word)
        reversed_word = reverse_text(contextualized_word)
        processed_words.append(reversed_word)
    
    return " ".join(processed_words[::-1])

def parse_file(file_path):
    if not file_path.endswith('.xml'):
        print(f"[WARN] Skipping non-XML file: {file_path}")
        return

    try:
        parser = etree.XMLParser(remove_blank_text=False, resolve_entities=False)
        doc = etree.parse(file_path, parser)
    except etree.XMLSyntaxError as e:
        print(f"[ERROR] Failed to parse {file_path}: {e}")
        return

    if not (doc.xpath('//LanguageInfo') or doc.xpath('//LanguageData')):
        print(f"[INFO] Skipping file with no relevant content: {file_path}")
        return

    for node in doc.xpath('//*[not(*)]'):
        if node.text and node.text.strip():
            node.text = process_node_text(node.text)

    try:
        with open(file_path, 'wb') as f:
            f.write(etree.tostring(doc, pretty_print=True, encoding='utf-8', xml_declaration=True))
        print(f"[INFO] Successfully processed: {file_path}")
    except IOError as e:
        print(f"[ERROR] Failed to write to {file_path}: {e}")

def parse_directory(directory_path):
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.xml'):
                parse_file(os.path.join(root, file))

def main():
    if len(sys.argv) != 2:
        print("Usage: python PersianFixer.py [file-path|directory-path]")
        sys.exit(1)

    path = sys.argv[1]
    if os.path.isdir(path):
        print(f"[INFO] Starting to process directory: {path}")
        parse_directory(path)
    elif os.path.isfile(path):
        print(f"[INFO] Starting to process file: {path}")
        parse_file(path)
    else:
        print(f"[ERROR] Path not found: {path}")
        sys.exit(1)
    print("[INFO] Processing complete.")

if __name__ == "__main__":
    main()
