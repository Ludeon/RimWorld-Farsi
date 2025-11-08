import sys
import os
import re
from lxml import etree

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

    # Check for expected root nodes
    if not (doc.xpath('//LanguageInfo') or doc.xpath('//LanguageData')):
        print(f"[WARN] {file_path} contains no expected nodes; skipping.")
        return

    # Process all leaf nodes
    for node in doc.xpath('//*[not(*)]'):
        reverse_node(node)

    with open(file_path, 'wb') as f:
        f.write(etree.tostring(doc, pretty_print=True, encoding='utf-8', xml_declaration=True))
    print(f"[INFO] {file_path} parsed and strings reversed!")

def reverse_node(node):
    content = node.text
    if content and re.search(r'[\u0600-\u06FF\u0590-\u05FF]', content):  # Arabic or Hebrew
        words = content.split()
        new_words = []
        for word in words:
            # Find placeholders like {0}, {PAWN_FIRST_NAME}
            placeholders = [(m.group(), m.start()) for m in re.finditer(r'{.*?}', word)]
            word_no_placeholders = word
            for ph, _ in placeholders:
                word_no_placeholders = word_no_placeholders.replace(ph, '', 1)
            if re.search(r'[\u0600-\u06FF\u0590-\u05FF]', word_no_placeholders):
                word_no_placeholders = word_no_placeholders[::-1]
            # Re-insert placeholders at original positions
            for ph, idx in placeholders:
                word_no_placeholders = word_no_placeholders[:idx] + ph + word_no_placeholders[idx:]
            new_words.append(word_no_placeholders)
        new_words.reverse()
        node.text = ' '.join(new_words)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: reverse_rtl_text.py [file-path|directory-path]")
        sys.exit(1)

    path = sys.argv[1]
    if os.path.isdir(path):
        parse_directory(path)
    elif os.path.isfile(path):
        parse_file(path)
    else:
        print(f"[EROR] Unknown file or directory path: {path}")
        sys.exit(1)