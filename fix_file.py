import re
import translate_engine

pattern = re.compile(r'<!--\s*EN:(.*?)\s*-->\s*<([^>]+)>TODO</\2>', re.DOTALL)

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    def replace_match(m):
        en_text = m.group(1).strip()
        tag = m.group(2)
        
        if 'rulesStrings' in tag or '<li>' in en_text:
            fa = translate_engine.process_rules_block(en_text)
            return f"<!-- EN:{m.group(1)} -->\n  <{tag}>{fa}</{tag}>"
        else:
            fa = translate_engine.translate_text_content(en_text)
            if '&' in fa and '&amp;' not in fa and '&lt;' not in fa:
                fa = fa.replace('&', '&amp;')
            return f"<!-- EN:{m.group(1)} -->\n  <{tag}>{fa}</{tag}>"

    new_content = pattern.sub(replace_match, content)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == '__main__':
    import sys
    process_file(sys.argv[1])
    print(f"Processed {sys.argv[1]}")
