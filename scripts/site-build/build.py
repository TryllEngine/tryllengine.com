"""Step 3 of the site build: turn baked design pages into the live site.

Reads the browser-rendered pages in scripts/site-build/baked/ (made by
bake.py) plus the blog content, and writes:

    index.html, features.html, download.html, about.html, demo.html, blog.html,
    privacy-policy.html
    blog/posts/<slug>/index.html   (one per entry in blog/posts.json)
    assets/js/pages/<page>.js      (the page's original design logic)
    sitemap.xml

Everything that is not in the design export lives in config.py: SEO
copy, real link targets for the design's placeholder links, form
endpoints. No third-party packages needed:  py -3 scripts/site-build/build.py

    --downloads-live   build as if config.DOWNLOADS_LIVE were True (preview.py)
    --prune            delete the files in assets/site/ that no page uses
"""
import glob
import hashlib
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402
from markdown_lite import md_to_html  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
BAKED = os.path.join(HERE, 'baked')
todos = []


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- baked page

class Baked:
    """One browser-rendered design page, split into styles, body and logic."""

    def __init__(self, name):
        self.name = name
        raw = read(os.path.join(BAKED, name + '.html'))
        head = raw[:raw.index('</head>')]
        # Design styles and font links carry data-dc-tpl; runtime styles don't.
        self.head_links = re.findall(r'<link\b[^>]*data-dc-tpl[^>]*>', head)
        self.styles = re.findall(r'<style data-dc-tpl="\d+">(.*?)</style>', head, re.S)
        start = raw.index('<div id="dc-root">')
        end = raw.index('<script type="text/x-dc"')
        body = raw[start:end].strip()
        body = re.sub(r'^<div id="dc-root"><div class="sc-host"[^>]*>', '', body)
        body = re.sub(r'</div></div>$', '', body)
        self.body = body
        m = re.search(r'<script type="text/x-dc"[^>]*data-props="([^"]*)"[^>]*>(.*?)</script>', raw[end:], re.S)
        self.props = json.loads(html.unescape(m.group(1)))
        self.props.pop('$preview', None)
        self.logic = m.group(2).strip()
        self.loops = json.loads(read(os.path.join(BAKED, name + '.loops.json')))

    def clean(self):
        b = re.sub(r' data-dc-tpl="\d+"', '', self.body)
        b = re.sub(r'<span class="sc-interp">([^<]*)</span>', r'\1', b)
        self.body = fix_copy(fix_assets(b))
        self.styles = [fix_assets(s) for s in self.styles]
        self.styles += [s for s in [tablet_menu(self.styles)] if s]
        self.logic = fix_copy(fix_assets(self.logic))
        for loop in self.loops.values():
            loop['tpl'] = fix_assets(loop['tpl'])
        return self


def tablet_menu(styles):
    """The design has its menu button and panel only up to 640px and hides the header links
    from 900px down, so 641-1100px had either no navigation or links wrapping onto two
    lines. Repeat the design's own phone menu rules there (site.css hides the links)."""
    rules, stack = [], []
    for css in styles:
        for m in re.finditer(r'(@media[^{]*)\{|([^{}]+)\{([^{}]*)\}|\}', css):
            if m.group(1):
                stack.append(re.sub(r'\s+', '', m.group(1)))
            elif m.group(2) is not None:
                if stack and stack[-1] == '@media(max-width:640px)' and re.search(r'\.mnav|\.nav \.mb\b', m.group(2)):
                    rules.append(m.group(2).strip() + '{' + m.group(3) + '}')
            elif stack:
                stack.pop()
    return '@media (min-width:641px) and (max-width:1100px){' + ''.join(rules) + '}' if rules else ''


def fix_assets(s):
    return re.sub(r'(?<![\w/.])(?:\./)?assets/([0-9a-f]{32}\.(?:jpg|jpeg|png|svg|webp|gif))', r'/assets/site/\1', s)


# --------------------------------------------------------------------- links

INTERNAL = {
    'index.html': '/', 'features.html': '/features', 'download.html': '/download',
    'about.html': '/about', 'demo.html': '/demo', 'blog.html': '/blog',
    'privacy.html': '/privacy-policy',
}


def link_text(inner):
    t = re.sub(r'<svg\b.*?</svg>', ' ', inner, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()


def rewrite_links(page, body):
    def internal(m):
        href = m.group(1)
        base, _, frag = href.partition('#')
        if base in INTERNAL:
            url = INTERNAL[base]
            if frag:
                url = ('/' if url == '/' else url) + '#' + frag
            return f'href="{url}"'
        return m.group(0)

    body = re.sub(r'href="([\w-]+\.html(?:#[\w-]*)?)"', internal, body)
    counts = {}

    def placeholder(m):
        tag, inner = m.group(1), m.group(2)
        aria = re.search(r'aria-label="([^"]*)"', tag)
        key = aria.group(1) if aria and not link_text(inner) else link_text(inner)
        n = counts[key] = counts.get(key, 0) + 1
        url = C.placeholder_link(page, key, n)
        if url is None:
            return m.group(0)
        if url.startswith('TODO:'):
            todos.append(f'{page}: "{key}" -> {url[5:]}')
            tag = tag.replace('href="#"', f'href="#" data-todo="{esc(url[5:])}"')
            return tag + inner + '</a>'
        tag = tag.replace('href="#"', f'href="{esc(url)}"')
        if url.startswith('http') and 'target=' not in tag:
            tag = tag[:-1] + ' target="_blank" rel="noopener">'
        return tag + inner + '</a>'

    return re.sub(r'(<a\b[^>]*href="#"[^>]*>)(.*?)</a>', placeholder, body, flags=re.S)


def thumb(video_id):
    """The video's YouTube thumbnail, saved under assets/images/videos/ the first time."""
    url = f'/assets/images/videos/{video_id}.jpg'
    path = os.path.join(ROOT, url.lstrip('/'))
    if not os.path.exists(path):
        for size in ('sddefault', 'hqdefault'):   # 640x480 when the upload has it
            try:
                with urllib.request.urlopen(f'https://i.ytimg.com/vi/{video_id}/{size}.jpg', timeout=30) as r:
                    data = r.read()
                break
            except urllib.error.HTTPError:
                continue
        else:
            raise SystemExit(f'no YouTube thumbnail for video {video_id}')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)
    return url


def video_lists(body):
    """The design's "How to build" lists are placeholders; fill them from config.VIDEO_LISTS."""
    def block(m):
        head, title, grid, cards = m.groups()
        title = html.unescape(title)
        if title not in C.VIDEO_LISTS:
            print(f'WARN no VIDEO_LISTS entry for the "{title}" video list')
            return m.group(0)
        playlist, videos = C.VIDEO_LISTS[title]
        head = head.replace('<a class="lk2" href="#">',
                            f'<a class="lk2" href="https://www.youtube.com/playlist?list={playlist}" '
                            'target="_blank" rel="noopener">')
        card = re.match(r'<a class="vt" href="#">(.*?)</a>', cards, re.S).group(1)
        out = []
        for vid, length, name in videos:
            c = re.sub(r'url\(&quot;.*?&quot;\)', f'url(&quot;{thumb(vid)}&quot;)', card, count=1)
            c = re.sub(r'<span>[^<]*</span></div>', f'<span>{length}</span></div>', c, count=1)
            c = re.sub(r'<b>.*?</b>', f'<b>{esc(name)}</b>', c, count=1, flags=re.S)
            out.append(f'<a class="vt" href="https://www.youtube.com/watch?v={vid}&amp;list={playlist}" '
                       f'target="_blank" rel="noopener">{c}</a>')
        return head + grid + ''.join(out) + '</div>'

    return re.sub(r'(<div class="lbr"><div><h4>([^<]*)</h4>(?:<a class="lk2" href="#">.*?</a>)?</div>)'
                  r'(<div class="lg[^"]*">)((?:<a class="vt" href="#">.*?</a>)+)</div>', block, body, flags=re.S)


DOWNLOAD_BUTTONS = ('Get Tryll Engine', 'Download for Unity 6+', 'Download for UE 5.7+', 'Direct download')
STORE_BUTTONS = ('Steam', 'Itch.io')
# Envelope from the blog's Subscribe card, instead of the download arrow.
MAIL_ICON = ('<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3.5" y="5.5" width="17" '
             'height="13" rx="2"></rect><path d="M4 7l8 6 8-6"></path></svg>')


def coming_soon(body):
    """Downloads aren't open yet (config.DOWNLOADS_LIVE): download and "Get Tryll
    Engine" buttons say "Coming soon" and lead to the newsletter signup."""
    def button(m):
        tag, inner = m.group(1), m.group(2)
        text = link_text(inner)
        if text in STORE_BUTTONS:
            return ''
        if text not in DOWNLOAD_BUTTONS:
            return m.group(0)
        label = C.COMING_SOON['nav' if re.search(r'class="(?:nb|mcta)"', tag) else 'cta']
        tag = re.sub(r' data-todo="[^"]*"', '', tag)
        tag = re.sub(r'href="[^"]*"', f'href="{C.COMING_SOON["href"]}"', tag)
        if text.startswith('Download for'):
            inner = re.sub(r'(<span class="dt">)<svg\b.*?</svg>', r'\1' + MAIL_ICON, inner, count=1, flags=re.S)
        return tag + inner.replace(text, esc(label), 1) + '</a>'

    body = re.sub(r'(<a\b[^>]*>)(.*?)</a>', button, body, flags=re.S)
    return body.replace('<span class="dmb">Demo available</span>', '<span class="dmb">Coming soon</span>')


# ---------------------------------------------------------------------- head

GTM_HEAD = """<script src="/assets/js/cookie-consent.js"></script>
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','%s');</script>""" % C.GTM_ID

GTM_BODY = ('<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=%s" '
            'height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>' % C.GTM_ID)

FAVICONS = """<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/assets/favicon/apple-touch-icon.png">
<link rel="manifest" href="/assets/favicon/site.webmanifest">
<meta name="theme-color" content="#161D29">"""


def load_json(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except OSError:
        return default


# The design's Google Fonts, served from assets/fonts/ (fonts.py): {Google stylesheet URL: its CSS}.
FONTS = load_json(os.path.join(ROOT, 'assets', 'fonts', 'fonts.json'), {})
fonts_missing = set()


def font_links(links):
    """The design's font links. A Google Fonts stylesheet that fonts.py has copied goes into
    the page as it is, pointing at assets/fonts/, with its latin files preloaded: nothing
    loads from Google (visitors' IP addresses stay with us, and two connections fewer).
    One it hasn't stays a link to Google, with its preconnects."""
    out, google = [], False
    for link in links:
        m = re.search(r'href="(https://fonts\.googleapis\.com/[^"]+)"', link)
        css = m and FONTS.get(html.unescape(m.group(1)))
        if css:
            latin = re.findall(r'/\* latin \*/\s*@font-face\s*\{[^}]*?url\((/assets/fonts/[^)]+)\)', css)
            out += [f'<link rel="preload" href="{f}" as="font" type="font/woff2" crossorigin>' for f in dict.fromkeys(latin)]
            out.append('<style>' + re.sub(r'\s*\n\s*', ' ', css).strip() + '</style>')
            continue
        if m:
            google = True
            fonts_missing.add(html.unescape(m.group(1)))
        out.append(link)
    if google:
        out[:0] = ['<link rel="preconnect" href="https://fonts.googleapis.com">',
                   '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>']
    return out


def head(meta, baked, extra_ld=()):
    url = C.SITE + meta['path']
    image = meta.get('image') or C.OG_IMAGE
    if image.startswith('/'):
        image = C.SITE + image
    title = meta['title']
    desc = meta['description']
    ld = [json.dumps(x, ensure_ascii=False, indent=1) for x in extra_ld]
    parts = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        GTM_HEAD,
        f'<title>{esc(title)}</title>',
        f'<meta name="description" content="{esc(desc)}">',
        '<meta name="robots" content="index, follow, max-image-preview:large">',
        f'<link rel="canonical" href="{url}">',
        f'<meta property="og:type" content="{meta.get("og_type", "website")}">',
        '<meta property="og:site_name" content="Tryll Engine">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:title" content="{esc(meta.get("og_title", title))}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:image" content="{esc(image)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(meta.get("og_title", title))}">',
        f'<meta name="twitter:description" content="{esc(desc)}">',
        f'<meta name="twitter:image" content="{esc(image)}">',
    ]
    parts += meta.get('head_extra', [])
    parts.append(FAVICONS)
    parts += font_links(baked.head_links)
    parts += [f'<style>{s}</style>' for s in baked.styles]
    parts.append('<link rel="stylesheet" href="/assets/css/site.css">')
    parts += [f'<script type="application/ld+json">\n{x}\n</script>' for x in ld]
    return '\n'.join(parts)


def page_html(meta, baked, body, page_js, extra_ld=(), scripts=()):
    tail = []
    if baked.loops:
        tail.append(f'<script type="application/json" id="dc-loops">{json.dumps(baked.loops)}</script>')
    tail.append('<script src="/assets/js/site.js" defer></script>')
    tail.append(f'<script src="/assets/js/pages/{page_js}.js" defer></script>')
    tail += [f'<script src="{s}" defer></script>' for s in scripts]
    return docs_latest('<!doctype html>\n<html lang="en">\n<head>\n' + head(meta, baked, extra_ld) +
                       '\n</head>\n<body>\n' + GTM_BODY + '\n' + body + '\n' + '\n'.join(tail) + '\n</body>\n</html>\n')


# Docs links follow "latest" (config.DOCS_V): a version that a design export or a post
# pins is swapped for it, and the build checks that every docs page linked still opens.
DOCS_PINNED = re.compile(r'https://docs\.tryllengine\.com/v\d+(?:\.\d+)*/')
docs_links = set()


def docs_latest(text):
    text = DOCS_PINNED.sub(C.DOCS_V, text)
    docs_links.update(u.split('#')[0] for u in re.findall(r'https://docs\.tryllengine\.com/[^"\'\s<>)]*', text))
    return text


def url_status(url):
    req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'tryll-site-build'})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except OSError:
        return None


DOCS_FALLBACKS = os.path.join(HERE, 'docs-fallbacks.json')


def check_docs_links(files):
    """Every docs page the site links to opens. "latest" on the docs site is a set of pages
    that forward to the newest version, and a docs release can leave some out: such links
    go to the version behind "latest" (the docs' versions.json) until "latest" has them.
    Those fallbacks are kept in docs-fallbacks.json, so a build without a connection to the
    docs site (another machine, CI) keeps them instead of linking pages "latest" lacks."""
    urls = sorted(docs_links)
    with ThreadPoolExecutor(8) as pool:
        status = dict(zip(urls, pool.map(url_status, urls)))
    if all(s is None for s in status.values()):
        swaps = {u: alt for u, alt in load_json(DOCS_FALLBACKS, {}).items() if u in docs_links}
        print('docs links not checked: no connection to docs.tryllengine.com' +
              (f'; kept the {len(swaps)} fallback(s) from the last check' if swaps else ''))
        swap_docs_links(files, swaps)
        return
    broken = [u for u in urls if status[u] != 200]
    current = None
    if any(u.startswith(C.DOCS_V) for u in broken):
        try:
            with urllib.request.urlopen(C.DOCS + 'versions.json', timeout=15) as r:
                current = next(v['version'] for v in json.load(r) if 'latest' in v.get('aliases', []))
        except (OSError, ValueError, StopIteration):
            pass
    swaps = {}
    for u in broken:
        alt = current and u.replace(C.DOCS_V, f'{C.DOCS}{current}/', 1)
        if alt and alt != u and url_status(alt) == 200:
            swaps[u] = alt
            print(f'NOTE docs "latest" has no {u[len(C.DOCS_V):]}: linked to {current} until it does')
        else:
            print(f'WARN docs link {u} answers {status[u] or "nothing"}: fix it in config.py or the page')
    write(DOCS_FALLBACKS, json.dumps(dict(sorted(swaps.items())), indent=1) + '\n')
    swap_docs_links(files, swaps)


def swap_docs_links(files, swaps):
    for path in files if swaps else ():
        text = read(path)
        for u, alt in swaps.items():
            text = re.sub(re.escape(u) + r'(?=["#])', alt, text)
        write(path, text)


# Browsers keep a file from GitHub Pages for 10 minutes, so right after a deploy a new page
# could meet the old stylesheet, script or clip. Every file the pages load carries a hash of
# its content (?v=…), which changes only when the file does. The design export's images
# (assets/site/) are named by their content already.
ASSET_URL = re.compile(r'''(?<=["'(;])/assets/(?!site/)[^"'?#()\s\\&]+(?=["')\\&\s])''')
# Text files are hashed with \n line ends: a Windows checkout has \r\n in them, and the same
# file must get the same stamp on every machine that builds the site.
TEXT_FILES = ('.js', '.css', '.html', '.svg', '.json', '.txt', '.xml', '.webmanifest')


def digest(path):
    with open(path, 'rb') as f:
        data = f.read()
    if path.endswith(TEXT_FILES):
        data = data.replace(b'\r\n', b'\n')
    return hashlib.sha1(data).hexdigest()[:8]


def stamp_assets(files):
    """?v=<hash> on the files the pages and their logic (assets/js/pages/*.js) load. The
    logic goes first: a page loads it by the hash of its stamped text."""
    digests = {}

    def stamped(m):
        path = os.path.join(ROOT, m.group(0)[1:])
        if not os.path.isfile(path):
            return m.group(0)
        if path not in digests:
            digests[path] = digest(path)
        return f'{m.group(0)}?v={digests[path]}'

    for path in logic_files() + files:
        text = read(path)
        new = ASSET_URL.sub(stamped, text)
        if new != text:
            write(path, new)


def logic_files():
    return sorted(glob.glob(os.path.join(ROOT, 'assets', 'js', 'pages', '*.js')))


# Pictures the pages show from assets/, as they write them (root-relative). Link previews and
# structured data use absolute URLs, so they always keep the original.
RASTER_URL = re.compile(r'''(?<=["'(;])/assets/(?!favicon/)[^"'?#()\s\\&]+\.(?:jpe?g|png)(?=["')\\&\s])''')


def use_webp(files):
    """A picture images.py has a lighter WebP copy of is loaded as that copy (config.WEBP),
    unless the original changed after the copy was made. Notes the pictures images.py
    hasn't looked at yet."""
    record = load_json(os.path.join(HERE, 'images.json'), {})
    copies, unseen = {}, set()
    for path, r in record.items():
        src, webp = os.path.join(ROOT, path), r.get('webp') and os.path.join(ROOT, r['webp'])
        if not webp or not os.path.isfile(src) or not os.path.isfile(webp):
            continue
        with open(src, 'rb') as f:
            if hashlib.sha1(f.read()).hexdigest() == r['sha1']:
                copies['/' + path] = '/' + r['webp']
            else:
                print(f'WARN {path} changed after images.py made its WebP copy: pages show the original until it runs again')

    def swap(m):
        if m.group(0)[1:] not in record:
            unseen.add(m.group(0)[1:])
        return copies.get(m.group(0), m.group(0)) if C.WEBP else m.group(0)

    for path in logic_files() + files:
        text = read(path)
        new = RASTER_URL.sub(swap, text)
        if new != text:
            write(path, new)
    if unseen:
        print(f'NOTE {len(unseen)} picture(s) on the pages not checked by images.py yet (it makes lighter '
              f'copies where nothing visible changes): ' + ', '.join(sorted(unseen)[:5]) + (' …' if len(unseen) > 5 else ''))


def check_assets(files, prune):
    """Warns about an /assets/ file the pages link to that isn't there, and lists the files in
    assets/site/ no page uses: a design export brings pictures the build replaces (video
    thumbnails, gallery and quote placeholders). --prune deletes those."""
    used, missing = set(), set()
    for path in logic_files() + files + [os.path.join(ROOT, 'assets', 'css', 'site.css')]:
        for u in re.findall(r'''(?<=["'(;])/assets/[^"'?#()\s\\&]+''', read(path)):
            if u.endswith('/'):   # a folder the logic builds a name in
                continue
            f = os.path.normpath(os.path.join(ROOT, urllib.parse.unquote(u).lstrip('/')))
            used.add(f)
            if f.endswith('.webp'):   # a WebP copy: its original stays (link previews, images.py)
                used.update(f[:-5] + e for e in ('.jpg', '.jpeg', '.png'))
            if not os.path.isfile(f):
                missing.add(u)
    for u in sorted(missing):
        print(f'WARN {u} is linked from the pages but missing')
    site = os.path.join(ROOT, 'assets', 'site')
    unused = [n for n in sorted(os.listdir(site)) if os.path.normpath(os.path.join(site, n)) not in used]
    if not unused:
        return
    size = sum(os.path.getsize(os.path.join(site, n)) for n in unused) // 1024
    if prune:
        for n in unused:
            os.remove(os.path.join(site, n))
        print(f'pruned {len(unused)} file(s) no page uses from assets/site/ ({size} KB)')
    else:
        print(f'NOTE {len(unused)} file(s) in assets/site/ no page uses ({size} KB): run build.py --prune to delete them')


# Sitemap: a page's lastmod moves only when the page itself changed (its ?v= stamps aside), so
# rebuilding on another day doesn't date every page anew. lastmod.json keeps a fingerprint of
# each page as the live site has it; the --downloads-live build for the preview leaves it alone.
LASTMOD = os.path.join(HERE, 'lastmod.json')
UNSTAMPED = re.compile(r'\?v=[0-9a-f]{8}')


def page_lastmods(pages, save):
    """{path: lastmod} for the design pages written, as [(path, file)]."""
    known = load_json(LASTMOD, None)
    if known is None:   # first run: start from the dates the sitemap has
        try:
            sm = read(os.path.join(ROOT, 'sitemap.xml'))
        except OSError:
            sm = ''
        known = {loc[len(C.SITE):]: {'sha1': None, 'lastmod': mod}
                 for loc, mod in re.findall(r'<loc>([^<]*)</loc><lastmod>([^<]*)</lastmod>', sm)}
        first = True
    else:
        first = False
    today, out, record = date.today().isoformat(), {}, {}
    for path, f in pages:
        h = hashlib.sha1(UNSTAMPED.sub('', read(f)).encode('utf-8')).hexdigest()
        k = known.get(path) or {}
        same = k.get('lastmod') and (k.get('sha1') == h or (first and k.get('sha1') is None))
        out[path] = k['lastmod'] if same else today
        record[path] = {'sha1': h, 'lastmod': out[path]}
    if save:
        write(LASTMOD, json.dumps(record, indent=1) + '\n')
    return out


# The design logic's clock steps 25 times a second (setInterval, 40 ms), which shows on
# the dice; site.js's tryllClock advances it on animation frames instead. With a site.js
# cached from before tryllClock (browsers keep it 10 minutes), the old clock still runs.
DESIGN_CLOCK = 'setInterval(() => this.setState({ T: ((this.state && this.state.T) || 0) + 0.04 }), 40)'
SMOOTH_CLOCK = ('(window.tryllClock || (f => setInterval(() => f(0.04), 40)))'
                '(dt => this.setState({ T: ((this.state && this.state.T) || 0) + dt }))')


def write_logic(name, baked):
    logic = baked.logic.replace(DESIGN_CLOCK, SMOOTH_CLOCK)
    if 'setInterval(' in logic.replace(SMOOTH_CLOCK, ''):
        print(f'WARN {name}: a setInterval in the design logic was not swapped for the smooth clock')
    js = ('/* Generated by scripts/site-build/build.py from the Claude Design export. Do not edit by hand. */\n'
          '(function () {\n' + logic + '\n\nwindow.tryllBoot(Component, ' +
          json.dumps(baked.props, ensure_ascii=False) + ');\n})();\n')
    write(os.path.join(ROOT, 'assets', 'js', 'pages', name + '.js'), js)


# --------------------------------------------------------------------- forms

def contact_form(body):
    """The design's contact card is a picture of a form; make it a real one. It posts to
    HubSpot once config.HUBSPOT has a form, to Formspree until then (assets/js/forms.js)."""
    def field(label, name, ph, kind='input', required=False, auto=''):
        fid = 'cf-' + name
        req = ' required' if required else ''
        ac = f' autocomplete="{auto}"' if auto else ''
        if kind == 'textarea':
            ctl = f'<textarea class="in ta" id="{fid}" name="{name}" rows="4" placeholder="{ph}"{req}></textarea>'
        else:
            t = 'email' if name == 'email' else 'text'
            ctl = f'<input class="in" id="{fid}" type="{t}" name="{name}" placeholder="{ph}"{req}{ac}>'
        return f'<div class="f"><label for="{fid}">{label}</label>{ctl}</div>'

    m = re.search(r'<div class="fcard">(<div class="tab">.*?</div>)<div class="two">.*?<div class="ft">'
                  r'(<button type="button" class="ok"[^>]*>)(.*?)</button>'
                  r'<button type="button" class="cta">(.*?)</button></div></div>', body, re.S)
    if not m:
        raise SystemExit('contact form markup not found in index')
    tab, ok_tag, ok_inner, cta_inner = m.groups()
    ok_inner = ok_inner.replace('<u>privacy policy</u>',
                                '<u><a href="/privacy-policy" target="_blank">privacy policy</a></u>')
    ok_tag = ok_tag.replace('<button', '<button role="checkbox" aria-checked="false" data-consent')
    if C.HUBSPOT['form']:
        action = f'{C.HUBSPOT["api"]}/submissions/v3/integration/submit/{C.HUBSPOT["portal"]}/{C.HUBSPOT["form"]}'
        extra, hidden = ' data-provider="hubspot"', ''
    else:
        action, extra = C.FORMS['contact'], ''
        hidden = ('<input type="hidden" name="_subject" value="New Tryll Engine contact form submission">'
                  '<input type="hidden" name="source" value="tryllengine.com/#contact">')
    if C.LEAD_ALERTS:   # forms.js sends accepted messages on to Slack (scripts/lead-alerts)
        extra += f' data-alerts="{esc(C.LEAD_ALERTS)}"'
    form = (
        f'<form class="fcard" id="contact-form" action="{action}" method="POST" '
        f'data-form="contact"{extra} novalidate>{tab}{hidden}'
        '<input type="text" name="_gotcha" tabindex="-1" autocomplete="off" class="hp" aria-hidden="true">'
        '<div class="two">' + field('Name*', 'name', 'Your name', required=True, auto='name') +
        field('Studio (optional)', 'company', 'Studio or company', auto='organization') + '</div>' +
        field('Email*', 'email', 'you@studio.com', required=True, auto='email') +
        field('Message', 'message', 'Tell us how we can help', kind='textarea') +
        f'<div class="ft">{ok_tag}{ok_inner}</button>'
        f'<button type="submit" class="cta">{cta_inner}</button></div>'
        '<p class="fmsg" role="status" aria-live="polite"></p></form>'
    )
    return body[:m.start()] + form + body[m.end():]


SOUND_ICON = ('<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 9.5h3.5L12 6v12l-4.5-3.5H4z">'
              '</path><path class="off" d="M16 9.5l5 5M21 9.5l-5 5"></path>'
              '<path class="on" d="M15.5 9a4 4 0 0 1 0 6M18 6.5a7.5 7.5 0 0 1 0 11"></path></svg>')


def clip_tag(name, start):
    """<video> for a clip made by clips.py; assets/js/clips.js loads and plays it."""
    c = C.CLIPS[name]
    small = f' data-src-small="/assets/video/{name}-small.mp4"' if c.get('small') else ''
    label = f' aria-label="{esc(c["label"])}"' if c.get('label') else ' aria-hidden="true"'
    # A clip cut without its subtitles carries its lines; clips.js shows them in the .cap.
    caps = f' data-captions="{esc(json.dumps(c["captions"], ensure_ascii=False))}"' if c.get('captions') else ''
    caps += f' data-loop-end="{c["loop_end"]}"' if c.get('loop_end') else ''   # muted, it loops here
    return (f'<video class="clip" muted loop playsinline preload="none" poster="/assets/video/{name}.jpg" '
            f'data-src="/assets/video/{name}.mp4"{small} data-start="{start}"{label}{caps}></video>' +
            ('<span class="cap" aria-hidden="true"><span></span></span>' if caps else ''))


def trailer_clips(body):
    """The hero picture and the Smart NPCs "Before / With Tryll" pictures become
    trailer clips (config.CLIPS), each with a button to hear the NPC."""
    body, n = re.subn(r'<div class="hv-vid" role="img" aria-label="[^"]*">',
                      lambda m: '<div class="hv-vid has-clip">' + clip_tag('hero', 'load'), body, count=1)
    assert n == 1, 'hero picture not found in index'
    snd = f'<button type="button" class="snd" aria-label="Play with sound" aria-pressed="false">{SOUND_ICON}</button>'
    body, n = re.subn(r'<div class="ugv pair"><i style="[^"]*">(<span class="bdg">[^<]*</span>)</i>'
                      r'<i style="[^"]*">(<span class="bdg t">[^<]*</span>)</i></div>',
                      lambda m: ('<div class="ugv pair">'
                                 f'<i class="has-clip">{clip_tag("npc-before", "view")}{m.group(1)}{snd}</i>'
                                 f'<i class="has-clip">{clip_tag("npc-after", "view")}{m.group(2)}{snd}</i></div>'),
                      body, count=1)
    assert n == 1, 'Smart NPCs pictures not found in index'
    if not C.TRAILER_URL:   # no trailer link yet: the hero has no "Watch on YouTube"
        body, n = re.subn(r'<a\b[^>]*class="hv-yt"[^>]*>.*?</a>', '', body, count=1, flags=re.S)
        assert n == 1, 'hero "Watch on YouTube" not found in index'
    return body


copy_used = set()


def fix_copy(text):
    """Wording changed since the design export (config.COPY)."""
    for old, new in C.COPY:
        if old in text:
            copy_used.add(old)
            text = text.replace(old, new)
    return text


def media_links(body):
    """Each media logo links to its article (config.MEDIA_LINKS). The row repeats the
    logos so it can loop; only the first set is reachable by keyboard and screen readers."""
    seen = {}

    def logo(m):
        attrs, inner = m.groups()
        key = re.search(r'alt="([^"]*)"', inner) or re.search(r'<b>([^<]*)</b>', inner)
        url = C.MEDIA_LINKS.get(html.unescape(key.group(1)))
        if not url:
            print(f'WARN no MEDIA_LINKS entry for the "{key.group(1)}" media logo')
            return m.group(0)
        seen[url] = seen.get(url, 0) + 1
        hidden = '' if seen[url] == 1 else ' tabindex="-1" aria-hidden="true"'
        return f'<a{attrs} href="{esc(url)}" target="_blank" rel="noopener"{hidden}>{inner}</a>'

    return re.sub(r'<div( class="logo(?: on)?")>(<img [^>]*>|<b>[^<]*</b>)</div>', logo, body)


def smooth_logos(body):
    """The design scrolls the media logos from its 25 fps logic tick, which stutters.
    Unbind the row: site.css scrolls it with a CSS animation and marquee.js keeps the
    design's "on" highlight in step with it."""
    body, n = re.subn(r' data-b-style="L\.tr"', '', body)
    assert n == 1, 'media logos row not found in index'
    return re.sub(r' data-b-class="L\.k\d+"', '', body)


def card_pictures(body):
    """Use-case cards get their picture from config.CARD_PICTURES instead of the design,
    or a clip from config.CARD_CLIPS (with a sound button when the clip has sound)."""
    def card(m):
        h = re.search(r'<h3>(.*?)</h3>', m.group(0))
        key = h and html.unescape(h.group(1))
        clip, pic = C.CARD_CLIPS.get(key), C.CARD_PICTURES.get(key)
        if clip:
            snd = (f'<button type="button" class="snd" aria-label="Play with sound" aria-pressed="false">{SOUND_ICON}'
                   '</button>') if C.CLIPS[clip].get('audio') else ''
            tag = f'<div class="ugv has-clip">{clip_tag(clip, "view")}{snd}</div>'
        elif pic:
            url, alt = pic
            tag = f'<div class="ugv" style="background-image: url(&quot;{url}&quot;);" role="img" aria-label="{esc(alt)}"></div>'
        else:
            return m.group(0)
        new, n = re.subn(r'<div class="ugv(?: ph)?"(?: style="[^"]*")?>(?:<span>[^<]*</span>)?</div>',
                         lambda _: tag, m.group(0), count=1)
        if not n:
            print(f'WARN no picture in the "{h.group(1)}" use-case card')
        return new

    return re.sub(r'<article class="ugc">.*?</article>', card, body, flags=re.S)


def client_quotes(body):
    """"What clients are saying" shows config.CLIENT_QUOTES, one card each, with its own
    picture or the design's in its place. With none, its heading and carousel are left out
    and "Media about us" after it stays."""
    if not C.CLIENT_QUOTES:
        body, n = re.subn(r'<div class="th"><h2>What clients are saying</h2></div>.*?(?=<div class="media">)',
                          '', body, count=1, flags=re.S)
        assert n == 1, '"What clients are saying" not found in index'
        return body
    a = body.find('<section class="sec cls">')
    b = body.find('</section>', a)
    assert a >= 0 and b > a, '"What clients are saying" not found in index'
    sec = body[a:b]
    shots = re.findall(r'<article class="card">(<div class="shot[^>]*></div>)', sec)

    def ext(url, text):
        return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(text)}</a>' if url else esc(text)

    cards = []
    for i, q in enumerate(C.CLIENT_QUOTES):
        if q.get('picture'):
            src, alt = q['picture']
            shot = f'<div class="shot pic"><img src="{esc(src)}" alt="{esc(alt)}" loading="lazy"></div>'
        else:
            shot = shots[i] if i < len(shots) else '<div class="shot"></div>'
        who = ext(q['linkedin'], q['name']) + (f' · {esc(q["role"])}' if q['role'] else '')
        cards.append(f'<article class="card">{shot}<h3>{ext(q["site"], q["studio"])}</h3><p class="m">{who}</p>'
                     f'<p class="q">“{esc(q["quote"])}”</p></article>')
    sec, n = re.subn(r'(?:<article class="card">.*?</article>)+', lambda _: ''.join(cards), sec, count=1, flags=re.S)
    assert n == 1, 'client quote cards not found in index'
    return body[:a] + sec + body[b:]


def badge_links(body):
    """The hero's Epic MegaGrants and Early Game Ventures badges, and the footer's "Epic
    MegaGrants recipient", link out (config.EPIC_MEGAGRANT, EGV_SITE, EGV_NEWS). A badge's
    logo and text become two links, so EGV's logo can go to their site."""
    epic = esc(C.EPIC_MEGAGRANT)
    body = re.sub(r'<span>(<img [^>]*>)(Epic MegaGrants<br>recipient)</span>',
                  lambda m: f'<span><a class="hbl" href="{epic}" tabindex="-1" aria-hidden="true">{m.group(1)}</a>'
                            f'<a href="{epic}">{m.group(2)}</a></span>', body)
    body = re.sub(r'<span>(<img [^>]*?)alt=""([^>]*>)(Funded by<br>Early Game Ventures)</span>',
                  lambda m: f'<span><a class="hbl" href="{esc(C.EGV_SITE)}" target="_blank" rel="noopener">'
                            f'{m.group(1)}alt="Early Game Ventures"{m.group(2)}</a>'
                            f'<a href="{esc(C.EGV_NEWS)}" target="_blank" rel="noopener">{m.group(3)}</a></span>', body)
    return body.replace('<span class="cp">Epic MegaGrants recipient</span>',
                        f'<a class="cp" href="{epic}">Epic MegaGrants recipient</a>')


def topic_titles(body):
    """/features: each topic title's text goes in one <span>. The heading lays out its
    children in a row with space between, which spread "Talking <em>is</em> the gameplay"
    across the full width."""
    return re.sub(r'(<h3 data-on-click="h\d+">)(.*?)(<i class="pm"></i></h3>)', r'\1<span>\2</span>\3', body)


def speech_row(body):
    """/features: "Faster than speech" ends with a row for how fast people talk, and its
    footnote says where that number comes from (config.SPEECH_ROW)."""
    num, label, note = C.SPEECH_ROW
    row = f'<div class="vr ref"><b>{esc(num)}</b><span>{esc(label)}</span></div>'
    body, n = re.subn(r'(>Faster than speech<.*?<div class="tv viz vs">.*?)(<small>)(.*?)</small>',
                      lambda m: f'{m.group(1)}{row}{m.group(2)}{m.group(3).rstrip(".")}. {esc(note)}</small>',
                      body, count=1, flags=re.S)
    assert n == 1, '"Faster than speech" rows not found in features'
    return body


def demo_page(body):
    """/demo: the gallery shows config.DEMO_SHOTS, the tags in config.DEMO_DROP_TAGS are left
    out, and "About this game" (config.DEMO_ABOUT, Markdown) comes before the system
    requirements, which get an anchor for its link."""
    shots = C.DEMO_SHOTS
    first, alt = shots[0]
    body, n = re.subn(r'(<img class="gim" src=")[^"]*(" alt=")[^"]*"',
                      lambda m: f'{m.group(1)}/assets/images/demo/{first}.jpg{m.group(2)}{esc(alt)}"',
                      body, count=1)
    assert n == 1, 'demo gallery picture not found'
    thumbs = ''.join(f'<button type="button" class="gtb{" on" if i == 0 else ""}" aria-label="Show slide {i + 1}" '
                     f'data-b-class="t{i}" data-on-click="g{i}"><img src="/assets/images/demo/{name}-thumb.jpg" alt="">'
                     '</button>' for i, (name, _) in enumerate(shots))
    body, n = re.subn(r'<div class="gth">.*?</div>',
                      lambda _: f'<div class="gth" style="grid-template-columns:repeat({len(shots)},minmax(0,1fr))">'
                                f'{thumbs}</div>', body, count=1, flags=re.S)
    assert n == 1, 'demo gallery thumbnails not found'
    body = re.sub(r'(<span class="gct" data-t="cnt">)1 / \d+', rf'\g<1>1 / {len(shots)}', body, count=1)
    for tag in C.DEMO_DROP_TAGS:
        body, n = re.subn(rf'<span>{re.escape(tag)}</span>', '', body, count=1)
        assert n == 1, f'demo tag "{tag}" not found'
    about = md_to_html(read(os.path.join(HERE, C.DEMO_ABOUT)))
    body, n = re.subn(r'<section class="ab greq">',
                      lambda _: '<section class="ab gai gabt" id="about"><div class="gsh"><h2>About this game</h2></div>'
                                f'<div class="gab">{about}</div></section><section class="ab greq" id="requirements">',
                      body, count=1)
    assert n == 1, 'demo system requirements not found'
    return demo_requirements(body)


def demo_requirements(body):
    """/demo: the design's two cards (minimum, recommended) become one, from
    config.DEMO_REQUIREMENTS. A value both share shows once, across both columns; on phones
    the two values of a row stack, each labelled."""
    def cell(v):   # "i5-10400" never breaks at its hyphen
        return esc(re.sub(r'(?<=\w)-(?=\d)', chr(0x2011), v))

    rows = ['<div class="row rqh" aria-hidden="true"><b></b><span>Minimum</span><span>Recommended</span></div>']
    for name, *values in C.DEMO_REQUIREMENTS:
        if len(values) == 1:
            rows.append(f'<div class="row"><b>{esc(name)}</b><span class="all">{cell(values[0])}</span></div>')
        else:
            rows.append(f'<div class="row two"><b>{esc(name)}</b>'
                        f'<span><i>Minimum</i>{cell(values[0])}</span><span><i>Recommended</i>{cell(values[1])}</span></div>')
    card = '<div class="rqx"><div class="rqp">' + ''.join(rows) + '</div></div>'
    body, n = re.subn(r'<div class="rqg">.*?(?=</section>)', lambda _: card, body, count=1, flags=re.S)
    assert n == 1, 'demo requirement cards not found'
    return body


def features_logic(logic):
    """/features opens in its compact view; the design always opened the full view. A topic's
    picture lines up with the top of a taller text ("top", measured by _m after the page
    opens and on resize); switching the view or opening a topic measures again, since the
    compact view hides the pictures."""
    logic, n = re.subn(r'\bcol = !!st\.col\b', 'col = st.col != null ? !!st.col : true', logic, count=1)
    assert n == 1, 'compact view flag (col) not found in the features logic'
    for old, new in (('out.ca = () => this.setState({ col: !col, op: {} });',
                      'out.ca = () => { this.setState({ col: !col, op: {} }); requestAnimationFrame(this._m); };'),
                     ('this.setState({ op: n }); };', 'this.setState({ op: n }); requestAnimationFrame(this._m); };')):
        assert logic.count(old) == 1, f'features logic changed: {old}'
        logic = logic.replace(old, new)
    return logic


def compact_view(body):
    """The /features markup starts in the compact view too (features_logic), so the page
    doesn't show the full view first and fold it up once the logic runs."""
    for old, new in (('<div class="cats" data-b-class="cc">', '<div class="cats cl" data-b-class="cc">'),
                     ('<i class="x" data-b-class="cai">', '<i class="" data-b-class="cai">'),
                     ('<span data-t="cal">Compact view</span>', '<span data-t="cal">Full view</span>')):
        assert body.count(old) == 1, f'compact view markup not found in features: {old}'
        body = body.replace(old, new)
    # Folded, with no "top": the logic measures that only for topics shown open.
    body, n = re.subn(r'(<article id="tp\d+" class="tp)(?: top)?(" data-b-class="o\d+">)', r'\1 cl\2', body)
    assert n, 'features topics (data-b-class="oN") not found'
    return body


def demo_logic(logic):
    """The gallery's slides in the design logic (const GS) follow config.DEMO_SHOTS."""
    gs = [{'src': f'/assets/images/demo/{name}.jpg', 'alt': alt} for name, alt in C.DEMO_SHOTS]
    logic, n = re.subn(r'const GS = \[.*?\];', lambda _: f'const GS = {json.dumps(gs, ensure_ascii=False)};',
                       logic, count=1, flags=re.S)
    assert n == 1, 'demo gallery slides (const GS) not found in the design logic'
    return logic


def get_started_cta(body):
    """The design's "How to get started" steps end without a button: add the
    pricing card's "Get Tryll Engine" after them, with a still copy of its die."""
    sec = re.search(r'<section class="gsw">.*?</section>', body, re.S)
    if not sec or 'class="cta' in sec.group(0):
        return body   # section gone, or the design has its own button now
    die = re.search(r'<a class="cta" href="/download">Get Tryll Engine <span class="dt">(<svg\b.*?</svg>)</span></a>',
                    body, re.S)
    if not die:
        raise SystemExit('pricing "Get Tryll Engine" button not found in index')
    # The original die is animated by the page logic; the copy keeps only its drawing.
    icon = re.sub(r' data-(?:b-[\w-]+|loop|lk|t)="[^"]*"', '', die.group(1))
    icon = re.sub(r'<g data-loop-end="[^"]*"></g>', '', icon)
    end = sec.end() - len('</section>')
    return (body[:end] + f'<div class="gcta"><a class="cta" href="/download">Get Tryll Engine '
            f'<span class="dt">{icon}</span></a></div>' + body[end:])


def subscribe_form(body):
    m = re.search(r'<div class="ef"><span>([^<]*)</span><a class="cta" href="#">(.*?)</a></div>', body, re.S)
    if not m:
        raise SystemExit('subscribe markup not found in blog')
    form = (f'<form class="ef" data-form="newsletter" data-ml-form="{C.MAILERLITE_FORM}" '
            f'data-source="blog" novalidate>'
            f'<input type="email" name="email" required autocomplete="email" placeholder="{m.group(1)}" '
            f'aria-label="Email address">'
            '<input type="text" name="website" tabindex="-1" autocomplete="off" class="hp" aria-hidden="true">'
            f'<button type="submit" class="cta">{m.group(2)}</button></form>'
            '<p class="fmsg" role="status" aria-live="polite"></p>')
    body = body[:m.start()] + form + body[m.end():]
    # Target of the "Coming soon" buttons (config.COMING_SOON).
    body, n = re.subn(r'<div class="sub">', '<div class="sub" id="subscribe">', body, count=1)
    assert n == 1, 'subscribe block not found in blog'
    return body


# ---------------------------------------------------------------------- blog

CATS = {'news': 'News', 'engineering': 'Engineering', 'tutorial': 'Tutorials', 'case-study': 'Case Studies'}


def fmt_date(iso):
    d = date.fromisoformat(iso)
    return d.strftime('%b ') + str(d.day) + d.strftime(', %Y')


def load_posts():
    posts = json.loads(read(os.path.join(ROOT, 'blog', 'posts.json')))
    return sorted(posts, key=lambda p: p['date'], reverse=True)


BLOG_PER_PAGE = 12   # posts per page of the listing (assets/js/blog-list.js reads it from the grid)


def blog_listing(body, posts):
    """Every post's card is in the page, so crawlers see every link; blog-list.js shows one
    page at a time. Cards after the first page start hidden, so their covers (~300 KB each)
    load only when someone pages there."""
    cards = []
    for i, p in enumerate(posts):
        cat = CATS.get(p['category'], p['category'].title())
        hidden = ' style="display:none"' if i >= BLOG_PER_PAGE else ''
        cards.append(
            f'<a class="pc" href="/blog/posts/{p["slug"]}/" data-cat="{esc(cat)}"{hidden}>'
            f'<div class="cv ph" style="background-image:url(\'{esc(p["image"])}\')" role="img" '
            f'aria-label="{esc(p["title"])}"></div>'
            f'<p class="mt">{esc(cat)} · {fmt_date(p["date"])}</p><h3>{esc(p["title"])}</h3></a>')
    body, n = re.subn(r'<div class="grid">.*?</div><p class="emp"[^>]*>',
                      f'<div class="grid" data-per-page="{BLOG_PER_PAGE}">' + ''.join(cards) +
                      '</div><p class="emp" style="display:none">',
                      body, count=1, flags=re.S)
    assert n == 1, 'blog grid not found'
    body, n = re.subn(r'<div class="pgn">(.*?)</div>', r'<nav class="pgn" aria-label="Blog pages">\1</nav>', body,
                      count=1, flags=re.S)
    assert n == 1, 'blog pagination not found'
    return body


BLOCKQUOTE_ICON_RE = re.compile(r'<blockquote><i>(<svg\b.*?</svg>)</i>', re.S)


def blog_post(tpl_body, post, md, blockquote_icon):
    cat = CATS.get(post['category'], post['category'].title())
    when = fmt_date(post['date'])
    # A leading image in the markdown becomes the hero; otherwise use the cover.
    hero_src, hero_alt = post['image'], post['title']
    lead = re.match(r'\s*!\[([^\]]*)\]\(([^)\s]+)[^)]*\)\s*\n', md)
    if lead:
        hero_alt, hero_src = lead.group(1) or post['title'], lead.group(2)
        md = md[lead.end():]
    article = md_to_html(md, blockquote_icon)

    b = tpl_body
    b = re.sub(r'<p class="crumb">.*?</p>',
               f'<p class="crumb"><a href="/blog">Blog</a> <span>/</span> {esc(cat)}</p>', b, count=1, flags=re.S)
    b = re.sub(r'<h1>.*?</h1>', f'<h1>{esc(post["title"])}</h1>', b, count=1, flags=re.S)
    li = post.get('linkedinUrl') or C.LINKEDIN
    b = re.sub(r'<p class="meta"><span>[^<]*</span><span>[^<]*</span><span>[^<]*</span><a href="[^"]*"',
               f'<p class="meta"><span>{esc(cat)}</span><span>{post.get("readTime", 2)} min read</span>'
               f'<span><time datetime="{post["date"]}">{when}</time></span><a href="{esc(li)}"', b, count=1)
    b = re.sub(r'<div class="pimg"><img [^>]*></div>',
               f'<div class="pimg"><img src="{esc(hero_src)}" alt="{esc(hero_alt)}" fetchpriority="high"></div>',
               b, count=1)
    b = re.sub(r'<article class="pb">.*?(<div class="pfoot">)',
               lambda m: f'<article class="pb post"><p class="pub"><span>Published</span> {when}</p>{article}' + m.group(1),
               b, count=1, flags=re.S)
    return b


# ---------------------------------------------------------------------- main

def org_ld():
    return {
        '@context': 'https://schema.org', '@type': 'Organization', 'name': 'Tryll Engine',
        'legalName': 'Tryll Engine, Inc.', 'url': C.SITE + '/',
        'logo': C.SITE + '/assets/favicon/android-chrome-512x512.png',
        'sameAs': [C.LINKEDIN, C.DISCORD, C.YOUTUBE],
    }


def main():
    downloads = C.DOWNLOADS_LIVE or '--downloads-live' in sys.argv[1:]
    posts = load_posts()
    out_pages = []
    html_files = []   # pages and posts written, for the docs link check

    for name, meta in C.PAGES.items():
        if not downloads and 'description_soon' in meta:
            meta = dict(meta, description=meta['description_soon'])
        baked = Baked(name).clean()
        body = rewrite_links(name, video_lists(baked.body))
        scripts = ['/assets/js/forms.js']
        ld = []
        if name == 'index':
            body = contact_form(body)
            body = get_started_cta(body)
            body = trailer_clips(body)
            body = card_pictures(body)
            body = client_quotes(body)
            body = media_links(smooth_logos(body))
            scripts += ['/assets/js/clips.js', '/assets/js/marquee.js']
            ld = [org_ld(), C.SOFTWARE_LD,
                  {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Tryll Engine',
                   'url': C.SITE + '/'}]
        if name == 'blog':
            body = subscribe_form(body)
            body = blog_listing(body, posts)
            body = body.replace(' data-b-style="emp"', '')
            scripts.append('/assets/js/blog-list.js')
            ld = [{'@context': 'https://schema.org', '@type': 'Blog', 'name': 'Tryll Engine Blog',
                   'url': C.SITE + '/blog', 'publisher': org_ld()}]
        if name == 'features':
            body = compact_view(topic_titles(speech_row(body)))
            baked.logic = features_logic(baked.logic)
        if name == 'demo':
            body = demo_page(body)
            baked.logic = demo_logic(baked.logic)
        if not downloads:
            body = coming_soon(body)
        body = badge_links(body)
        write_logic(name, baked)
        html_files.append(os.path.join(ROOT, meta['out']))
        write(html_files[-1], page_html(meta, baked, body, name, ld, scripts))
        out_pages.append((meta['path'], html_files[-1], meta.get('priority', '0.8')))

    # Blog posts share the blog-post design page.
    baked = Baked('blog-post').clean()
    tpl_body = rewrite_links('blog-post', baked.body)
    if not downloads:
        tpl_body = coming_soon(tpl_body)
    tpl_body = badge_links(tpl_body)
    icon = BLOCKQUOTE_ICON_RE.search(tpl_body).group(1)
    write_logic('blog-post', baked)
    for p in posts:
        md = read(os.path.join(ROOT, 'blog', 'content', p['slug'] + '.md'))
        body = blog_post(tpl_body, p, md, icon)
        path = f'/blog/posts/{p["slug"]}/'
        meta = {'path': path, 'title': f'{p["title"]} | Tryll Engine Blog', 'og_title': p['title'],
                'description': p['excerpt'], 'image': p['image'], 'og_type': 'article',
                'head_extra': [f'<meta property="article:published_time" content="{p["date"]}">']}
        ld = [{
            '@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': p['title'],
            'description': p['excerpt'], 'image': C.SITE + p['image'], 'datePublished': p['date'],
            'author': {'@type': 'Organization', 'name': p.get('author') or 'Tryll Engine Team'},
            'publisher': org_ld(), 'mainEntityOfPage': C.SITE + path,
        }, {
            '@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Blog', 'item': C.SITE + '/blog'},
                {'@type': 'ListItem', 'position': 2, 'name': p['title'], 'item': C.SITE + path}],
        }]
        html_files.append(os.path.join(ROOT, 'blog', 'posts', p['slug'], 'index.html'))
        write(html_files[-1], page_html(meta, baked, body, 'blog-post', ld))
        out_pages.append((path, p['date'], '0.6'))

    # Retired URLs: an instant meta refresh, which Google treats as a permanent
    # redirect, plus a canonical to the new page. Noindex, not in the sitemap.
    for old, new in C.REDIRECTS.items():
        write(os.path.join(ROOT, old.strip('/') + '.html'), (
            '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<title>Moved — Tryll Engine</title>\n'
            '<meta name="robots" content="noindex">\n'
            f'<link rel="canonical" href="{C.SITE}{new}">\n'
            f'<meta http-equiv="refresh" content="0; url={new}">\n'
            f'<script>location.replace({json.dumps(new)} + location.hash)</script>\n'
            f'</head>\n<body>\n<p>This page has moved to <a href="{new}">{C.SITE}{new}</a>.</p>\n'
            '</body>\n</html>\n'))

    print(f'built {len(C.PAGES)} pages, {len(posts)} posts')
    for old, _ in C.COPY:
        if old not in copy_used:
            print(f'WARN COPY: "{old}" is no longer in the design; remove it from config.py')
    if not downloads:
        print(f'downloads not live: download buttons say "Coming soon" and lead to {C.COMING_SOON["href"]}')
    if not C.HUBSPOT['form']:
        print("contact form posts to Formspree until config.HUBSPOT['form'] is set")
    for link in sorted(fonts_missing):
        print(f'WARN font {link} loads from Google Fonts: run fonts.py to serve it from assets/fonts/')
    check_docs_links(html_files)
    use_webp(html_files)
    stamp_assets(html_files)

    # Sitemap: the pages (dated by their last change), then posts (newest first).
    mods = page_lastmods([(path, out) for path, out, _ in out_pages[:len(C.PAGES)]],
                         save='--downloads-live' not in sys.argv[1:])
    out_pages[:len(C.PAGES)] = [(path, mods[path], pr) for path, _, pr in out_pages[:len(C.PAGES)]]
    urls = out_pages
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, mod, pr in urls:
        sm.append(f'  <url><loc>{C.SITE}{path}</loc><lastmod>{mod}</lastmod><priority>{pr}</priority></url>')
    sm.append('</urlset>')
    write(os.path.join(ROOT, 'sitemap.xml'), '\n'.join(sm) + '\n')
    print(f'sitemap with {len(urls)} urls')
    check_assets(html_files, '--prune' in sys.argv[1:])
    if todos:
        print('\nLinks still waiting for a real URL (left as href="#" with data-todo):')
        for t in sorted(set(todos)):
            print('  -', t)


if __name__ == '__main__':
    main()
