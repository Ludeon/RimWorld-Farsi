import re
import urllib.request
import urllib.parse
import json
import time
import os
import sys
from concurrent.futures import ThreadPoolExecutor

ZWNJ = '\u200c'

def clean_persian(text):
    text = text.replace('ي', 'ی').replace('ك', 'ک')
    text = re.sub(r' (ها)([\s\.,،؛]|$)', ZWNJ + r'\1\2', text)
    text = re.sub(r' (ای)([\s\.,،؛]|$)', ZWNJ + r'\1\2', text)
    text = re.sub(r' (تر)([\s\.,،؛]|$)', ZWNJ + r'\1\2', text)
    text = re.sub(r' (ترین)([\s\.,،؛]|$)', ZWNJ + r'\1\2', text)
    return text.strip()

def translate_line(line):
    rule_match = re.match(r'^(<li>)([^->]+->)(.*)(</li>)$', line)
    if rule_match:
        prefix_tag = rule_match.group(1)
        rule_head = rule_match.group(2)
        rule_body = rule_match.group(3)
        suffix_tag = rule_match.group(4)
        translated_body = translate_text_content(rule_body)
        return f"    {prefix_tag}{rule_head}{translated_body}{suffix_tag}"
    else:
        return translate_text_content(line)

def translate_text_content(text):
    if not text.strip():
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
            time.sleep(0.2 + attempt * 0.3)

    for idx, tok in enumerate(tokens):
        pat = rf'XK\s*{idx}\s*ZX'
        translated = re.sub(pat, tok, translated, flags=re.IGNORECASE)
        translated = translated.replace(f"XK{idx}ZX", tok)
    
    return clean_persian(translated)

def process_rules_block(en_comment):
    lines = en_comment.strip().split('\n')
    translated_lines = []
    for l in lines:
        l_s = l.strip()
        if not l_s:
            continue
        if l_s.startswith('<li>') and l_s.endswith('</li>'):
            translated_lines.append(translate_line(l_s))
        elif '->' in l_s:
            parts = l_s.split('->', 1)
            t_body = translate_text_content(parts[1])
            translated_lines.append(f"    <li>{parts[0]}->{t_body}</li>")
        else:
            t_body = translate_text_content(l_s)
            translated_lines.append(f"    <li>{t_body}</li>")
    return '\n' + '\n'.join(translated_lines) + '\n  '

def translate_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = re.compile(r'(<!--\s*EN:(.*?)\s*-->\s*<([^>]+)>)(TODO)(</\3>)', re.DOTALL)
    matches = list(pattern.finditer(content))
    if not matches:
        return 0

    en_texts = [m.group(2) for m in matches]
    tags = [m.group(3) for m in matches]
    
    tasks = []
    for en, tag in zip(en_texts, tags):
        if 'rulesStrings' in tag or '<li>' in en:
            tasks.append((True, en))
        else:
            tasks.append((False, en))

    def worker(task):
        is_rule, txt = task
        if is_rule:
            return process_rules_block(txt)
        else:
            res = translate_text_content(txt.strip())
            if '&' in res and '&amp;' not in res and '&lt;' not in res:
                res = res.replace('&', '&amp;')
            return res

    with ThreadPoolExecutor(max_workers=16) as executor:
        fa_texts = list(executor.map(worker, tasks))

    new_content = content
    for m, fa_text in zip(reversed(matches), reversed(fa_texts)):
        prefix = m.group(1)
        suffix = m.group(5)
        replacement = f"{prefix}{fa_text}{suffix}"
        new_content = new_content[:m.start()] + replacement + new_content[m.end():]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return len(matches)

if __name__ == '__main__':
    target_dir = sys.argv[1] if len(sys.argv) > 1 else 'Core'
    import glob
    files = glob.glob(f'{target_dir}/**/*.xml', recursive=True)
    count = 0
    translated_tags = 0
    for f in sorted(files):
        num = translate_file(f)
        if num > 0:
            count += 1
            translated_tags += num
            print(f"[{count}] {f}: {num} tags translated", flush=True)
    print(f"Total: {translated_tags} tags translated across {count} files in {target_dir}")
