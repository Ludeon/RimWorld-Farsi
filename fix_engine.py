import re
import urllib.request
import urllib.parse
import json
import time

ZWNJ = '\u200c'

def clean_persian(text):
    text = text.replace('ي', 'ی').replace('ك', 'ک')
    text = re.sub(r' (ها)([\s\.,،؛]|$)', ZWNJ + r'\1\2', text)
    text = re.sub(r' (ای)([\s\.,،؛]|$)', ZWNJ + r'\1\2', text)
    text = re.sub(r' (تر)([\s\.,،؛]|$)', ZWNJ + r'\1\2', text)
    text = re.sub(r' (ترین)([\s\.,،؛]|$)', ZWNJ + r'\1\2', text)
    return text.strip()

def translate_str(text):
    text = text.strip()
    if not text:
        return text
    tokens = []
    def repl_token(m):
        idx = len(tokens)
        tokens.append(m.group(0))
        return f"XK{idx}ZX"
    
    protected = re.sub(r'\{[^}]+\}|\[[^\]]+\]|\(\*[^)]+\)', repl_token, text)
    translated = protected
    for attempt in range(4):
        try:
            url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=fa&dt=t&q=' + urllib.parse.quote(protected)
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                translated = ''.join([part[0] for part in data[0] if part and part[0]])
            break
        except Exception:
            time.sleep(0.3)
    
    for idx, tok in enumerate(tokens):
        pat = rf'XK\s*{idx}\s*ZX'
        translated = re.sub(pat, tok, translated, flags=re.IGNORECASE)
        translated = translated.replace(f"XK{idx}ZX", tok)
    return clean_persian(translated)

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    en_comment_accum = []
    in_en_comment = False

    for line in lines:
        if '<!-- EN:' in line and '-->' in line:
            # Single line EN comment
            m = re.search(r'<!--\s*EN:(.*?)\s*-->', line)
            en_comment_accum = [m.group(1).strip()]
            new_lines.append(line)
        elif '<!-- EN:' in line:
            in_en_comment = True
            m = re.search(r'<!--\s*EN:(.*)', line)
            en_comment_accum = [m.group(1).strip()]
            new_lines.append(line)
        elif in_en_comment:
            if '-->' in line:
                in_en_comment = False
                m = re.search(r'(.*?)\s*-->', line)
                en_comment_accum.append(m.group(1).strip())
            else:
                en_comment_accum.append(line.strip())
            new_lines.append(line)
        elif '>TODO<' in line:
            # This line has a TODO tag! e.g. <Tag>TODO</Tag>
            tag_m = re.search(r'<([^>]+)>TODO</\1>', line)
            if tag_m:
                tag = tag_m.group(1)
                full_en = ' '.join(en_comment_accum).strip()
                if 'rulesStrings' in tag:
                    # rulesStrings block
                    rule_lines = []
                    for raw_l in en_comment_accum:
                        raw_l = raw_l.strip()
                        if not raw_l: continue
                        if '->' in raw_l:
                            head, body = raw_l.split('->', 1)
                            head = head.replace('<li>', '').strip()
                            t_body = translate_str(body.replace('</li>', '').strip())
                            rule_lines.append(f"    <li>{head}->{t_body}</li>")
                        elif raw_l.startswith('<li>') and raw_l.endswith('</li>'):
                            inner = raw_l[4:-5]
                            rule_lines.append(f"    <li>{translate_str(inner)}</li>")
                    block = '\n' + '\n'.join(rule_lines) + '\n  '
                    replaced_line = re.sub(r'<([^>]+)>TODO</\1>', f'<{tag}>{block}</{tag}>', line)
                    new_lines.append(replaced_line)
                else:
                    fa = translate_str(full_en)
                    if '&' in fa and '&amp;' not in fa:
                        fa = fa.replace('&', '&amp;')
                    replaced_line = re.sub(r'<([^>]+)>TODO</\1>', f'<{tag}>{fa}</{tag}>', line)
                    new_lines.append(replaced_line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == '__main__':
    import sys
    fix_file(sys.argv[1])
