#!/usr/bin/env python3
"""Install local Things themes while preserving Zed's JSONC settings text."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
THEME = {'mode':'system', 'light':'Things Light', 'dark':'Things Dark'}

def tokens(text):
    """Yield JSONC tokens with source spans, ignoring whitespace and comments."""
    i = 0
    while i < len(text):
        if text[i].isspace(): i += 1; continue
        if text.startswith('//', i):
            end = text.find('\n', i); i = len(text) if end < 0 else end; continue
        if text.startswith('/*', i):
            end = text.find('*/', i + 2)
            if end < 0: raise ValueError('Unclosed JSONC comment')
            i = end + 2; continue
        start = i
        if text[i] == '"':
            i += 1
            while i < len(text):
                if text[i] == '\\': i += 2; continue
                if text[i] == '"': i += 1; break
                i += 1
            else: raise ValueError('Unclosed JSON string')
        elif text[i] in '{}[],:': i += 1
        else:
            while i < len(text) and not text[i].isspace() and text[i] not in '{}[],:/': i += 1
            if i == start: raise ValueError('Invalid JSONC token')
        yield text[start:i], start, i

def parse_jsonc(text):
    ts = list(tokens(text))
    return json.loads(''.join(t[0] for n,t in enumerate(ts)
        if not (t[0] == ',' and n + 1 < len(ts) and ts[n + 1][0] in (']','}'))))

def update_theme(text):
    data = parse_jsonc(text)
    if not isinstance(data, dict): raise ValueError('Zed settings must be an object')
    ts = list(tokens(text))
    depth = 0; spans = []
    for n, (value, start, end) in enumerate(ts):
        if depth == 1 and value == '"theme"' and ts[n + 1][0] == ':':
            vn = n + 2; ve = vn; vd = 0
            while ve < len(ts):
                v = ts[ve][0]
                if ve > vn and vd == 0: break
                if v in ('{','['): vd += 1
                elif v in ('}',']'): vd -= 1
                ve += 1
            spans.append((ts[vn][1], ts[ve - 1][2]))
        if value in ('{','['): depth += 1
        elif value in ('}',']'): depth -= 1
    replacement = json.dumps(THEME, indent=2).replace('\n', '\n  ')
    if spans:
        for start, end in reversed(spans): text = text[:start] + replacement + text[end:]
    else:
        closing = ts[-1][1]
        if len(ts) > 2 and ts[-2][0] != ',':
            insert = ts[-2][2]
            text = text[:insert] + ',' + text[insert:]
            closing += 1
        text = text[:closing].rstrip() + '\n  "theme": ' + replacement + ',\n' + text[closing:]
    updated = parse_jsonc(text)
    assert updated['theme'] == THEME
    assert {k:v for k,v in updated.items() if k != 'theme'} == {k:v for k,v in data.items() if k != 'theme'}
    return text

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config-dir', type=Path, default=Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home()/'.config')))/'zed')
    args = parser.parse_args()
    config = args.config_dir.expanduser()
    settings = config/'settings.json'; destination = config/'themes/things.json'
    old = settings.read_text() if settings.exists() else '{}\n'
    updated = update_theme(old)  # Parse and verify before writing anything.
    theme = (ROOT/'themes/things.json').read_text()
    json.loads(theme)
    backup = config/'things-backups'/datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup.mkdir(parents=True)
    manifest = {'settings_existed':settings.exists(), 'theme_existed':destination.exists()}
    for src, name in [(settings,'settings.json'), (destination,'things.json')]:
        if src.exists(): shutil.copy2(src, backup/name)
    (backup/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(theme)
    # Zed may watch settings, so atomically replace them after installing themes.
    temporary = config/'.things-settings.tmp'
    temporary.write_text(updated)
    temporary.chmod(settings.stat().st_mode & 0o777 if settings.exists() else 0o600)
    temporary.replace(settings)
    print(f'Installed Things Light / Dark in {destination}')
    print(f'Activated system appearance. Backup: {backup}')
    print('If a running Zed window keeps the old theme, restart Zed or select Things Light in the theme selector.')

if __name__ == '__main__': main()
