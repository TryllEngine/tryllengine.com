"""Step 1 of the site build: annotate Claude Design pages before baking.

The design export renders client-side from an <x-dc> template with {{bindings}}
and <sc-for> loops. Before we render it to static HTML, every binding is
mirrored into a data-* attribute so the baked page can be re-hydrated by
assets/js/site.js without the design runtime:

    attr="{{expr}}"       ->  data-b-attr="expr"
    onClick="{{expr}}"    ->  data-on-click="expr"
    <tag>{{expr}}</tag>   ->  <tag data-t="expr">
    <sc-for list="{{l}}" as="q"> children  ->  data-loop="L0" data-lk="<n>"

Loop metadata is written next to each page as <page>.loops.json.

Usage: py -3 annotate.py <design-export-dir> <out-dir>
"""
import json
import os
import re
import shutil
import sys

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'param', 'source', 'track', 'wbr'}
TAG_RE = re.compile(r'<(/?)([a-zA-Z][\w:-]*)((?:\s[^<>]*?)?)(/?)>', re.S)
ATTR_RE = re.compile(r'([\w:-]+)="\{\{\s*([^}]*?)\s*\}\}"')
PARTIAL_RE = re.compile(r'([\w:-]+)="([^"]*\{\{[^"]*)"')


def annotate(tpl, page):
    inserts = []          # (pos, text)
    stack = []            # [tag, start_tag_end_pos, loop_id_if_sc_for, child_count, has_elem_child]
    loops = {}
    warnings = []
    pos = 0
    for m in TAG_RE.finditer(tpl):
        text = tpl[pos:m.start()]
        pos = m.end()
        if '{{' in text and stack:
            parent = stack[-1]
            mt = re.fullmatch(r'\s*\{\{\s*([^}]*?)\s*\}\}\s*', text)
            if mt:
                parent[5].append((mt.group(1), m.start() - len(text), m.start()))
            else:
                warnings.append(f'{page}: mixed text binding {text.strip()[:60]!r}')
        closing, tag, attrs, selfclose = m.group(1), m.group(2), m.group(3), m.group(4)
        low = tag.lower()
        if closing:
            while stack:
                top = stack.pop()
                if len(top[5]) == 1 and not top[4]:
                    inserts.append((top[1], f' data-t="{top[5][0][0]}"'))
                elif top[5]:
                    # Text binding next to elements: give it its own span.
                    for expr, s, e in top[5]:
                        inserts.append((s, f'<span data-t="{expr}">'))
                        inserts.append((e, '</span>'))
                if top[0].lower() == low:
                    break
            continue
        add = []
        for a, expr in ATTR_RE.findall(attrs):
            if low == 'sc-for':
                continue
            if a.lower().startswith('on'):
                add.append(f'data-on-{a[2:].lower()}="{expr}"')
            else:
                add.append(f'data-b-{a.lower()}="{expr}"')
        for a, val in PARTIAL_RE.findall(attrs):
            if not re.fullmatch(r'\{\{[^}]*\}\}', val):
                warnings.append(f'{page}: partial binding {a}="{val[:60]}"')
        # direct child of an <sc-for>?
        if stack and stack[-1][2]:
            loop = stack[-1]
            add.append(f'data-loop="{loop[2]}" data-lk="{loop[3]}"')
            loops[loop[2]]['k'] = loop[3] + 1
            loop[3] += 1
        if stack:
            stack[-1][4] = True
        end = m.end() - (2 if selfclose else 1)
        if add:
            inserts.append((end, ' ' + ' '.join(add)))
        if selfclose or low in VOID:
            continue
        loop_id = None
        if low == 'sc-for':
            lm = re.search(r'list="\{\{\s*([^}]*?)\s*\}\}"', attrs)
            am = re.search(r'\bas="([^"]*)"', attrs)
            loop_id = f'L{len(loops)}'
            outer = next((s[2] for s in reversed(stack) if s[2]), None)
            loops[loop_id] = {'list': lm.group(1), 'as': am.group(1), 'k': 0, 'parent': outer}
            if outer:
                warnings.append(f'{page}: nested loop {loop_id} inside {outer}')
        stack.append([tag, end, loop_id, 0, False, []])
    for p, t in sorted(inserts, reverse=True):
        tpl = tpl[:p] + t + tpl[p:]
    # Second pass: keep each loop's item markup (to create items that were not
    # rendered at bake time) and mark where the loop ends.
    ids = iter(loops)

    def loop_end(m):
        lid = next(ids)
        item = re.sub(r'\s[\w:-]+="\{\{[^}]*\}\}"', '', m.group(1))
        loops[lid]['tpl'] = item.strip()
        in_svg = tpl[:m.start()].count('<svg') > tpl[:m.start()].count('</svg>')
        loops[lid]['svg'] = in_svg
        end = f'<g data-loop-end="{lid}"></g>' if in_svg else f'<template data-loop-end="{lid}"></template>'
        return m.group(0) + end

    tpl = re.sub(r'<sc-for\b[^>]*>(.*?)</sc-for>', loop_end, tpl, flags=re.S)
    return tpl, loops, warnings


def main(src, out):
    os.makedirs(out, exist_ok=True)
    all_warnings = []
    for name in sorted(os.listdir(src)):
        path = os.path.join(src, name)
        if not name.endswith('.html'):
            dst = os.path.join(out, name)
            if os.path.isdir(path):
                shutil.copytree(path, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(path, dst)
            continue
        html = open(path, encoding='utf-8').read()
        a = html.index('</helmet>') + len('</helmet>')
        b = html.index('</x-dc>')
        tpl, loops, warnings = annotate(html[a:b], name)
        all_warnings += warnings
        with open(os.path.join(out, name), 'w', encoding='utf-8', newline='') as f:
            f.write(html[:a] + tpl + html[b:])
        with open(os.path.join(out, name[:-5] + '.loops.json'), 'w', encoding='utf-8') as f:
            json.dump(loops, f, indent=1)
        print(f'{name}: {len(loops)} loops')
    for w in all_warnings:
        print('WARN', w)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
