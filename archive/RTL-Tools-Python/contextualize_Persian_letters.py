import sys
import os
import re
from lxml import etree

# Persian/Arabic letter contextual forms mapping
LETTER_MAP = {
    'ء': 0xFE80,
    'آ': 0xFE81,
    'أ': 0xFE83,
    'ؤ': 0xFE85,
    'إ': 0xFE87,
    'ا': 0xFE8D,
    'ب': 0xFE8F,
    'پ': 0xFB56,
    'ة': 0xFE93,
    'ت': 0xFE95,
    'ث': 0xFE99,
    'ج': 0xFE9D,
    'چ': 0xFB7A,
    'ح': 0xFEA1,
    'خ': 0xFEA5,
    'د': 0xFEA9,
    'ذ': 0xFEAB,
    'ر': 0xFEAD,
    'ز': 0xFEAF,
    'ژ': 0x0698,
    'س': 0xFEB1,
    'ش': 0xFEB5,
    'ص': 0xFEB9,
    'ض': 0xFEBD,
    'ط': 0xFEC1,
    'ظ': 0xFEC5,
    'ع': 0xFEC9,
    'غ': 0xFECD,
    'ف': 0xFED1,
    'ق': 0xFED5,
    'ک': 0xFB8E,
    'گ': 0xFB92,
    'ل': 0xFEDD,
    'م': 0xFEE1,
    'ن': 0xFEE5,
    'ه': 0xFEE9,
    'و': 0xFEED,
    'ی': 0xFBFC,
    'ي': 0xFEF1,
    'ئ': 0xFE89
}

LAM_ALEF_MAP = {
    'آ': 0xFEF5,
    'أ': 0xFEF7,
    'إ': 0xFEF9,
    'ا': 0xFEFB
}

def parse_directory(directory_path):
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.xml'):
                parse_file(os.path.join(root, file))

def parse_file(file_path):
    if not file_path.endswith('.xml'):
        print(f"[WARN] {file_path} is not an XML file; skipping.")
        return

    parser = etree.XMLParser(remove_blank_text=False)
    with open(file_path, 'rb') as f:
        doc = etree.parse(f, parser)

    if not (doc.xpath('//LanguageInfo') or doc.xpath('//LanguageData')):
        print(f"[WARN] {file_path} contains no expected nodes; skipping.")
        return

    for node in doc.xpath('//*[not(*)]'):
        contextualize_letters(node)

    with open(file_path, 'wb') as f:
        f.write(etree.tostring(doc, pretty_print=True, encoding='utf-8', xml_declaration=True))
    print(f"[INFO] {file_path} parsed and letters contextualized!")

def contextualize_letters(node):
    content = node.text
    if content and re.search(r'[\u0600-\u06FF]', content):
        words = content.split()
        new_words = []
        for word in words:
            new_word = ''
            word_chars = list(word)
            idx = 0
            while idx < len(word_chars):
                letter = word_chars[idx]
                prev_letter = word_chars[idx + 1] if idx < len(word_chars) - 1 else None
                next_letter = word_chars[idx - 1] if idx > 0 else None
                # Lam-Alef combo handling
                if hasattr(contextualize_letters, 'letter_was_combined') and contextualize_letters.letter_was_combined:
                    contextualize_letters.letter_was_combined = False
                    new_word += create_lam_alef_combo(prev_letter, contextualize_letters.combining_alef)
                    idx += 1
                    continue
                if is_alef(letter) and prev_letter and is_lam(prev_letter):
                    contextualize_letters.letter_was_combined = True
                    contextualize_letters.combining_alef = letter
                    idx += 1
                    continue
                # Isolated
                if is_isolated_letter(letter):
                    new_word += letter
                elif is_connecting_letter(letter):
                    new_word += contextual_connecting_letter(letter, prev_letter, next_letter)
                elif is_non_connecting_letter(letter):
                    new_word += contextual_non_connecting_letter(letter, prev_letter)
                else:
                    new_word += letter
                idx += 1
            new_words.append(new_word)
        node.text = ' '.join(new_words)

# State for lam-alef combo
contextualize_letters.letter_was_combined = False
contextualize_letters.combining_alef = ''

def is_connecting_letter(letter):
    return letter in 'بپتثجچحخسشصضطظعغفقکگلمنهيی'

def is_non_connecting_letter(letter):
    return letter in 'اأإآدذرزژوؤةى'

def is_isolated_letter(letter):
    return letter == 'ء'

def is_lam(letter):
    return letter == 'ل'

def is_alef(letter):
    return letter in 'اأإآ'

def create_lam_alef_combo(prev_letter, next_letter):
    combo_code = LAM_ALEF_MAP.get(next_letter)
    if combo_code is None:
        return next_letter
    if prev_letter and not (is_non_connecting_letter(prev_letter) or is_isolated_letter(prev_letter) or re.match(r'[{}]', prev_letter)):
        combo_code += 1
    return chr(combo_code)

def contextual_connecting_letter(letter, prev_letter, next_letter):
    contextual_letter = LETTER_MAP.get(letter)
    if contextual_letter is None:
        print(f"[WARN] Could not find connecting letter: {to_unicode(letter)}")
        return letter
    if prev_letter and re.match(r'[{}]', prev_letter):
        prev_letter = None
    if next_letter and re.match(r'[{}]', next_letter):
        next_letter = None
    if next_letter is None:
        if prev_letter is None or is_non_connecting_letter(prev_letter) or is_isolated_letter(prev_letter):
            return chr(contextual_letter)  # isolated form
        else:
            return chr(contextual_letter + 1)  # end form
    if prev_letter is None or is_non_connecting_letter(prev_letter) or is_isolated_letter(prev_letter):
        return chr(contextual_letter + 2)  # beginning form
    return chr(contextual_letter + 3)  # middle form

def contextual_non_connecting_letter(letter, prev_letter):
    contextual_letter = LETTER_MAP.get(letter)
    if contextual_letter is None:
        print(f"[WARN] Could not find non-connecting letter: {to_unicode(letter)}")
        return letter
    if prev_letter is None or is_non_connecting_letter(prev_letter) or is_isolated_letter(prev_letter):
        return chr(contextual_letter)  # isolated form
    return chr(contextual_letter + 1)  # end form

def to_unicode(text):
    return ''.join(f'\\u{ord(c):04x}' for c in text)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: contextualize_Persian_letters.py [file-path|directory-path]")
        sys.exit(1)

    path = sys.argv[1]
    if os.path.isdir(path):
        parse_directory(path)
    elif os.path.isfile(path):
        parse_file(path)
    else:
        print(f"[EROR] Unknown file or directory path: {path}")
        sys.exit(1)