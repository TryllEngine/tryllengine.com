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
"""
import html
import json
import os
import re
import sys
import urllib.error
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
    parts.append('<link rel="preconnect" href="https://fonts.googleapis.com">')
    parts.append('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    parts += baked.head_links
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


def check_docs_links(files):
    """Every docs page the site links to opens. "latest" on the docs site is a set of pages
    that forward to the newest version, and a docs release can leave some out: such links
    go to the version behind "latest" (the docs' versions.json) until "latest" has them."""
    urls = sorted(docs_links)
    with ThreadPoolExecutor(8) as pool:
        status = dict(zip(urls, pool.map(url_status, urls)))
    if all(s is None for s in status.values()):
        print('docs links not checked: no connection to docs.tryllengine.com')
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
    for path in files if swaps else ():
        text = read(path)
        for u, alt in swaps.items():
            text = re.sub(re.escape(u) + r'(?=["#])', alt, text)
        write(path, text)


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
    return (f'<video class="clip" muted loop playsinline preload="none" poster="/assets/video/{name}.jpg" '
            f'data-src="/assets/video/{name}.mp4"{small} data-start="{start}"{label}></video>')


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
    """Use-case cards get their picture from config.CARD_PICTURES instead of the design."""
    def card(m):
        h = re.search(r'<h3>(.*?)</h3>', m.group(0))
        pic = h and C.CARD_PICTURES.get(html.unescape(h.group(1)))
        if not pic:
            return m.group(0)
        url, alt = pic
        tag = f'<div class="ugv" style="background-image: url(&quot;{url}&quot;);" role="img" aria-label="{esc(alt)}"></div>'
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
        return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(text)}</a>'

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
    return body


def features_logic(logic):
    """/features opens in its compact view on phones; the design always opened the full view."""
    logic, n = re.subn(r'\bcol = !!st\.col\b',
                       "col = st.col != null ? !!st.col : matchMedia('(max-width: 640px)').matches", logic, count=1)
    assert n == 1, 'compact view flag (col) not found in the features logic'
    return logic


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


def blog_listing(body, posts):
    cards = []
    for p in posts:
        cat = CATS.get(p['category'], p['category'].title())
        cards.append(
            f'<a class="pc" href="/blog/posts/{p["slug"]}/" data-cat="{esc(cat)}">'
            f'<div class="cv ph" style="background-image:url(\'{esc(p["image"])}\')" role="img" '
            f'aria-label="{esc(p["title"])}"></div>'
            f'<p class="mt">{esc(cat)} · {fmt_date(p["date"])}</p><h3>{esc(p["title"])}</h3></a>')
    body, n = re.subn(r'<div class="grid">.*?</div><p class="emp"[^>]*>',
                      '<div class="grid">' + ''.join(cards) + '</div><p class="emp" style="display:none">',
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
            body = speech_row(body)
            baked.logic = features_logic(baked.logic)
        if name == 'demo':
            body = demo_page(body)
            baked.logic = demo_logic(baked.logic)
        if not downloads:
            body = coming_soon(body)
        write_logic(name, baked)
        html_files.append(os.path.join(ROOT, meta['out']))
        write(html_files[-1], page_html(meta, baked, body, name, ld, scripts))
        out_pages.append((meta['path'], date.today().isoformat(), meta.get('priority', '0.8')))

    # Blog posts share the blog-post design page.
    baked = Baked('blog-post').clean()
    tpl_body = rewrite_links('blog-post', baked.body)
    if not downloads:
        tpl_body = coming_soon(tpl_body)
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

    # Sitemap: new pages, kept legacy pages, then posts (newest first).
    urls = out_pages[:len(C.PAGES)] + [(p, d, pr) for p, d, pr in C.LEGACY_PAGES] + out_pages[len(C.PAGES):]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, mod, pr in urls:
        sm.append(f'  <url><loc>{C.SITE}{path}</loc><lastmod>{mod}</lastmod><priority>{pr}</priority></url>')
    sm.append('</urlset>')
    write(os.path.join(ROOT, 'sitemap.xml'), '\n'.join(sm) + '\n')

    print(f'built {len(C.PAGES)} pages, {len(posts)} posts, sitemap with {len(urls)} urls')
    for old, _ in C.COPY:
        if old not in copy_used:
            print(f'WARN COPY: "{old}" is no longer in the design; remove it from config.py')
    if not downloads:
        print(f'downloads not live: download buttons say "Coming soon" and lead to {C.COMING_SOON["href"]}')
    if not C.HUBSPOT['form']:
        print("contact form posts to Formspree until config.HUBSPOT['form'] is set")
    check_docs_links(html_files)
    if todos:
        print('\nLinks still waiting for a real URL (left as href="#" with data-todo):')
        for t in sorted(set(todos)):
            print('  -', t)


if __name__ == '__main__':
    main()
