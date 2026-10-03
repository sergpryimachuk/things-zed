#!/usr/bin/env python3
import json
from pathlib import Path
import re
import jsonschema

root = Path(__file__).resolve().parent.parent
schema = json.loads((root/'scripts/theme-schema.json').read_text())
family = json.loads((root/'themes/things.json').read_text())
jsonschema.Draft7Validator(schema).validate(family)
allowed = schema['definitions']['ThemeStyleContent']['properties']
def colors(value):
    if isinstance(value, dict):
        for k,v in value.items():
            if k not in ('font_style','font_weight'): yield from colors(v)
    elif isinstance(value, list):
        for v in value: yield from colors(v)
    elif isinstance(value, str) and value != 'opaque': yield value
for theme in family['themes']:
    assert not set(theme['style']) - set(allowed), 'Unknown style keys'
    for color in colors(theme['style']):
        assert re.fullmatch(r'#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?', color), color
assert {t['name'] for t in family['themes']} == {'Things Light','Things Dark'}
print('Things Light and Dark pass the official Zed schema; all style keys and colors are valid.')
