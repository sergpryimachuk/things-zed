#!/usr/bin/env python3
"""Build native Zed colors from Obsidian Things 2.2.4 tokens."""
import colorsys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def hsl(h, s, l):
    return '#' + ''.join(f'{round(c * 255):02x}' for c in colorsys.hls_to_rgb(h / 360, l / 100, s / 100))

PALETTES = {
    'light': {
        'base': ['#ffffff', '#fcfcfc', '#f6f7f8', '#f6f7f8', '#f0f0f0', '#ebedf0', '#d4d4d4', '#bdbdbd', '#ababab', '#707070', '#5a5a5a', '#222222'],
        'atom': dict(zip(['gray1', 'gray2', 'red', 'green', 'blue', 'purple', 'aqua', 'yellow', 'orange'], ['#383a42', '#383a42', '#e75545', '#4ea24c', '#3d74f6', '#a625a4', '#0084bc', '#e35649', '#986800'])),
        'accent': hsl(215, 75, 60), 'muted': hsl(212, 10, 37), 'faint': hsl(212, 10, 67),
        'hover': '#e2e5e9', 'red': '#e4374b', 'green': '#0cb54f', 'orange': '#d96c00', 'yellow': '#bd8e37', 'cyan': '#2db7b5', 'blue': '#086ddd', 'purple': '#876be0', 'pink': '#c32b74',
    },
    'dark': {
        # The source doesn't override base-05 in dark mode. Use its base-20 for sidebars.
        'base': ['#1c2127', '#181c20', '#282c34', '#181c20', '#2c313c', '#35393e', '#3f3f3f', '#555555', '#666666', '#999999', '#bababa', '#dadada'],
        'atom': dict(zip(['gray1', 'gray2', 'red', 'orange', 'green', 'aqua', 'purple', 'blue', 'yellow'], ['#5c6370', '#abb2bf', '#e06c75', '#d19a66', '#98c379', '#56b6c2', '#c678dd', '#61afef', '#e5c07b'])),
        'accent': hsl(215, 75, 70), 'muted': hsl(212, 15, 78), 'faint': hsl(212, 15, 43),
        'hover': '#3f3f3f', 'red': '#fb464c', 'green': '#44cf6e', 'orange': '#e9973f', 'yellow': '#e0de71', 'cyan': '#53dfdd', 'blue': '#027aff', 'purple': '#a882ff', 'pink': '#fa99cd',
    },
}

def build(appearance, p):
    b00,b05,b10,b20,b25,b30,b35,b40,b50,b60,b70,b100 = p['base']
    a = p['atom']; accent = p['accent']; selection = '#4c8ce640'
    style = {
        'background.appearance': 'opaque',
        'background': b00, 'surface.background': b20, 'elevated_surface.background': b05,
        'border': b30, 'border.variant': b25, 'border.focused': accent, 'border.selected': accent,
        'border.transparent': '#00000000', 'border.disabled': b25,
        'element.background': b25, 'element.hover': p['hover'], 'element.active': b30,
        'element.selected': selection, 'element.disabled': b20,
        'ghost_element.background': '#00000000', 'ghost_element.hover': p['hover'],
        'ghost_element.active': b30, 'ghost_element.selected': selection, 'ghost_element.disabled': b20,
        'text': b100, 'text.muted': p['muted'], 'text.placeholder': p['faint'],
        'text.disabled': b50, 'text.accent': accent,
        'icon': b70, 'icon.muted': p['faint'], 'icon.placeholder': p['faint'],
        'icon.disabled': b50, 'icon.accent': accent, 'link_text.hover': accent,
        'title_bar.background': b25 if appearance == 'light' else b20,
        'title_bar.inactive_background': b10, 'toolbar.background': b00,
        'tab_bar.background': b20, 'tab.inactive_background': b20, 'tab.active_background': b00,
        'status_bar.background': b20, 'panel.background': b20, 'panel.focused_border': accent,
        'panel.indent_guide': b30, 'panel.indent_guide_active': b40, 'panel.indent_guide_hover': b50,
        'pane.focused_border': accent, 'pane_group.border': b30,
        'editor.background': b00, 'editor.foreground': b100, 'editor.gutter.background': b00,
        'editor.subheader.background': b20, 'editor.active_line.background': b10,
        'editor.highlighted_line.background': b25, 'editor.line_number': p['faint'],
        'editor.active_line_number': accent, 'editor.invisible': b35, 'editor.wrap_guide': b30,
        'editor.active_wrap_guide': b40, 'editor.indent_guide': b30, 'editor.indent_guide_active': b40,
        'editor.document_highlight.read_background': selection,
        'editor.document_highlight.write_background': accent + '59',
        'editor.document_highlight.bracket_background': b25,
        'drop_target.background': accent + '33', 'search.match_background': '#ffd00066',
        'scrollbar.thumb.background': b40 + '80', 'scrollbar.thumb.hover_background': b50 + 'b3',
        'scrollbar.thumb.border': '#00000000', 'scrollbar.track.background': '#00000000',
        'scrollbar.track.border': '#00000000',
        'terminal.background': b00, 'terminal.foreground': b100,
        'terminal.bright_foreground': b100, 'terminal.dim_foreground': p['muted'],
        'terminal.ansi.background': b00,
    }
    # Match the Things Ghostty port's ANSI slots, including semantic brights.
    ansi_names = ['black','red','green','yellow','blue','magenta','cyan','white']
    ansi = (['#383a42','#e75545','#4ea24c','#986800','#3d74f6','#a625a4','#0084bc','#707070',
             '#5a5a5a','#e4374b','#4ea24c','#986800','#086ddd','#876be0','#0084bc','#222222']
            if appearance == 'light' else
            ['#282c34','#e06c75','#98c379','#e5c07b','#61afef','#c678dd','#56b6c2','#abb2bf',
             '#5c6370','#fb464c','#44cf6e','#e0de71','#79a9ec','#a882ff','#53dfdd','#dadada'])
    for i, name in enumerate(ansi_names):
        style['terminal.ansi.' + name] = ansi[i]
        style['terminal.ansi.bright_' + name] = ansi[i + 8]
        style['terminal.ansi.dim_' + name] = ansi[i]
    for token, color in {'error':p['red'], 'deleted':p['red'], 'success':p['green'], 'created':p['green'],
        'warning':p['yellow'], 'modified':p['orange'], 'conflict':p['orange'], 'info':accent,
        'hint':p['cyan'], 'renamed':p['purple'], 'hidden':p['faint'], 'ignored':p['faint'],
        'predictive':p['faint'], 'unreachable':p['faint']}.items():
        style[token] = color
        style[token + '.background'] = color + '1a'
        style[token + '.border'] = color + '66'
    style['players'] = [{'cursor':accent, 'background':accent, 'selection':selection}]
    style['accents'] = [accent, '#ff82b2', '#3eb4bf', '#e5b567', '#e87d3e', '#9e86c8']
    syntax = {}
    groups = {
        'gray2': ['variable', 'variable.special', 'punctuation', 'punctuation.bracket', 'punctuation.delimiter', 'punctuation.special', 'operator', 'embedded'],
        'gray1': ['comment', 'comment.doc'],
        'red': ['attribute', 'property', 'tag'],
        'green': ['string', 'string.special', 'string.special.symbol'],
        'blue': ['function', 'function.method', 'function.special', 'constructor'],
        'purple': ['keyword', 'keyword.control', 'keyword.function', 'keyword.operator', 'keyword.return', 'boolean'],
        'aqua': ['string.escape', 'string.regex', 'type.builtin', 'preproc'],
        'yellow': ['type', 'type.class', 'namespace', 'enum'],
        'orange': ['number', 'constant', 'constant.builtin'],
    }
    for palette, scopes in groups.items():
        for scope in scopes: syntax[scope] = {'color':a[palette]}
    # Light Things uses its normal code gray for comments. Give comments the
    # source UI muted gray to keep their visual role without lowering contrast.
    syntax['comment'] = {'color':p['muted'] if appearance == 'light' else a['gray1'], 'font_style':'italic'}
    syntax['comment.doc'] = dict(syntax['comment'])
    syntax.update({
        'title': {'color':b100, 'font_weight':700},
        'text.literal': {'color':a['green']},
        'text.emphasis': {'color':'#ff82b2', 'font_style':'italic'},
        'text.strong': {'color':'#ff82b2', 'font_weight':700},
        'text.uri': {'color':accent}, 'link_text': {'color':accent},
        'link_uri': {'color':accent}, 'text.reference': {'color':'#3eb4bf'},
        'text.list': {'color':accent}, 'text.todo': {'color':p['yellow'], 'font_weight':700},
        'hint': {'color':p['cyan']}, 'predictive': {'color':p['faint']},
    })
    style['syntax'] = syntax
    return {'name':'Things ' + appearance.title(), 'appearance':appearance, 'style':style}

family = {'$schema':'https://zed.dev/schema/themes/v0.2.0.json', 'name':'Things',
    'author':'Serhii Pryimachuk; adapted from Colin Eckert\'s Things',
    'themes':[build(k,v) for k,v in PALETTES.items()]}
(ROOT / 'themes/things.json').write_text(json.dumps(family, indent=2) + '\n')
