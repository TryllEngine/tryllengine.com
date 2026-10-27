"""Step 3 of the site build: turn baked design pages into the live site.

Reads the browser-rendered pages in scripts/site-build/baked/ (made by
bake.py) plus the blog content, and writes:

    index.html, features.html, download.html, about.html, demo.html, blog.html
    blog/posts/<slug>/index.html   (one per entry in blog/posts.json)
    assets/js/pages/<page>.js      (the page's original design logic)
    sitemap.xml

Everything that is not in the design export lives in config.py: SEO
copy, real link targets for the design's placeholder links, form
endpoints. No third-party packages needed:  py -3 scripts/site-build/build.py
"""
import html
import json
import os
import re
import sys
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
        self.body = fix_assets(b)
        self.styles = [fix_assets(s) for s in self.styles]
        self.logic = fix_assets(self.logic)
        for loop in self.loops.values():
            loop['tpl'] = fix_assets(loop['tpl'])
        return self


def fix_assets(s):
    return re.sub(r'(?<![\w/.])(?:\./)?assets/([0-9a-f]{32}\.(?:jpg|jpeg|png|svg|webp|gif))', r'/assets/site/\1', s)


# --------------------------------------------------------------------- links

INTERNAL = {
    'index.html': '/', 'features.html': '/features', 'download.html': '/download',
    'about.html': '/about', 'demo.html': '/demo', 'blog.html': '/blog',
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
    return ('<!doctype html>\n<html lang="en">\n<head>\n' + head(meta, baked, extra_ld) +
            '\n</head>\n<body>\n' + GTM_BODY + '\n' + body + '\n' + '\n'.join(tail) + '\n</body>\n</html>\n')


def write_logic(name, baked):
    js = ('/* Generated by scripts/site-build/build.py from the Claude Design export. Do not edit by hand. */\n'
          '(function () {\n' + baked.logic + '\n\nwindow.tryllBoot(Component, ' +
          json.dumps(baked.props, ensure_ascii=False) + ');\n})();\n')
    write(os.path.join(ROOT, 'assets', 'js', 'pages', name + '.js'), js)


# --------------------------------------------------------------------- forms

def contact_form(body):
    """The design's contact card is a picture of a form; make it a real one."""
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
    form = (
        f'<form class="fcard" id="contact-form" action="{C.FORMS["contact"]}" method="POST" '
        f'data-form="contact" novalidate>{tab}'
        '<input type="hidden" name="_subject" value="New Tryll Engine contact form submission">'
        '<input type="hidden" name="source" value="tryllengine.com/#contact">'
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
    return body.replace('By subscribing, you agree to our <a href="#">Privacy Policy</a>',
                        'By subscribing, you agree to our <a href="/privacy-policy">Privacy Policy</a>')


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
               lambda m: f'<article class="pb"><p class="pub"><span>Published</span> {when}</p>{article}' + m.group(1),
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
    posts = load_posts()
    out_pages = []

    for name, meta in C.PAGES.items():
        baked = Baked(name).clean()
        body = rewrite_links(name, baked.body)
        scripts = ['/assets/js/forms.js']
        ld = []
        if name == 'index':
            body = contact_form(body)
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
        write_logic(name, baked)
        write(os.path.join(ROOT, meta['out']), page_html(meta, baked, body, name, ld, scripts))
        out_pages.append((meta['path'], date.today().isoformat(), meta.get('priority', '0.8')))

    # Blog posts share the blog-post design page.
    baked = Baked('blog-post').clean()
    tpl_body = rewrite_links('blog-post', baked.body)
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
        write(os.path.join(ROOT, 'blog', 'posts', p['slug'], 'index.html'),
              page_html(meta, baked, body, 'blog-post', ld))
        out_pages.append((path, p['date'], '0.6'))

    # Retired URLs: an instant meta refresh, which Google treats as a permanent
    # redirect, plus a canonical to the new page. Not listed in the sitemap.
    for old, new in C.REDIRECTS.items():
        write(os.path.join(ROOT, old.strip('/') + '.html'), (
            '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<title>Moved — Tryll Engine</title>\n'
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
    if todos:
        print('\nLinks still waiting for a real URL (left as href="#" with data-todo):')
        for t in sorted(set(todos)):
            print('  -', t)


if __name__ == '__main__':
    main()
