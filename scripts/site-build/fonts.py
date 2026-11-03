"""Serve the design's fonts from the site itself instead of Google Fonts.

    py -3 scripts/site-build/fonts.py

The design links its fonts (Space Grotesk) from fonts.googleapis.com. Loaded
from there, every visitor's IP address goes to Google before they have agreed
to anything, and the text waits on two more connections. This downloads the
stylesheet each of the design's font links points to, as a current browser
gets it (woff2), and the font files it names: the files go to assets/fonts/,
the stylesheet, now pointing at them, to assets/fonts/fonts.json. build.py
writes that stylesheet into each page in place of the link, and preloads the
latin files. Run it again when the design asks for another font or weight:
build.py warns about a font link it can't serve and keeps that one as it is.
Then run build.py.
"""
import json
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'assets', 'fonts')
MANIFEST = os.path.join(OUT, 'fonts.json')
# Google sends woff2 (and unicode-range subsets) only to browsers it knows can use them.
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
FONT_LINK = re.compile(r'<link\b[^>]*href="(https://fonts\.googleapis\.com/[^"]+)"[^>]*rel="stylesheet"'
                       r'|<link\b[^>]*rel="stylesheet"[^>]*href="(https://fonts\.googleapis\.com/[^"]+)"')


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def design_font_links():
    import html
    links = set()
    baked = os.path.join(HERE, 'baked')
    for name in os.listdir(baked):
        if name.endswith('.html'):
            with open(os.path.join(baked, name), encoding='utf-8') as f:
                head = f.read().split('</head>', 1)[0]
            links.update(html.unescape(a or b) for a, b in FONT_LINK.findall(head))
    return sorted(links)


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = {}
    for link in design_font_links():
        css = fetch(link).decode('utf-8')
        blocks = re.findall(r'/\* ([\w-]+) \*/\s*(@font-face\s*\{[^}]*\})', css)
        if not blocks:
            raise SystemExit(f'no @font-face in {link}')
        # One file per family and subset (a variable font serves every weight); weights
        # that come as files of their own get the weight in the name.
        files = {}
        for subset, block in blocks:
            family = re.search(r"font-family:\s*'([^']+)'", block).group(1)
            url = re.search(r'src:\s*url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)', block).group(1)
            files.setdefault((family, subset), set()).add(url)
        names, out = {}, []
        for subset, block in blocks:
            family = re.search(r"font-family:\s*'([^']+)'", block).group(1)
            url = re.search(r'src:\s*url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)', block).group(1)
            if url not in names:
                name = f'{slug(family)}-{subset}'
                if len(files[(family, subset)]) > 1:
                    weight = re.search(r'font-weight:\s*(\d+)', block).group(1)
                    style = re.search(r'font-style:\s*(\w+)', block).group(1)
                    name += f'-{weight}' + ('i' if style == 'italic' else '')
                names[url] = name + '.woff2'
                data = fetch(url)
                with open(os.path.join(OUT, names[url]), 'wb') as f:
                    f.write(data)
                print(f'{names[url]}  {len(data) // 1024} KB')
            out.append(f'/* {subset} */\n' + block.replace(url, '/assets/fonts/' + names[url]))
        manifest[link] = '\n'.join(out)
    with open(MANIFEST, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifest, f, indent=1)
        f.write('\n')
    print(f'{len(manifest)} font link(s) -> {os.path.relpath(MANIFEST, ROOT)}; now run build.py')


if __name__ == '__main__':
    main()
