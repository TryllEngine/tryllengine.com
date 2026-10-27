"""Markdown -> HTML for blog/content/*.md, in the blog-post design's markup.

Covers what the posts use: paragraphs, ## / ### headings, bold, italic,
inline code, links, images, bullet and numbered lists, blockquotes, and raw
HTML blocks (video embeds). Consecutive images become a gallery.
"""
import html
import re

IMG_RE = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)\s]+)(?:\s+"[^"]*")?\)')


def inline(text):
    keep = []

    def stash(s):
        keep.append(s)
        return f'\x00{len(keep) - 1}\x00'

    text = re.sub(r'`([^`]+)`', lambda m: stash(f'<code>{html.escape(m.group(1))}</code>'), text)
    text = IMG_RE.sub(lambda m: stash(
        f'<img src="{html.escape(m.group(2))}" alt="{html.escape(m.group(1))}" loading="lazy">'), text)

    def link(m):
        url = m.group(2)
        ext = ' target="_blank" rel="noopener"' if url.startswith('http') else ''
        return stash(f'<a href="{html.escape(url)}"{ext}>') + m.group(1) + stash('</a>')

    text = LINK_RE.sub(link, text)
    text = re.sub(r'https?://[^\s<>"\x00]*[^\s<>"\x00.,;:!?)]', lambda m: stash(
        f'<a href="{html.escape(m.group(0))}" target="_blank" rel="noopener">{html.escape(m.group(0))}</a>'), text)
    text = html.escape(text, quote=False)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<![*\w])\*(?![*\s])(.+?)(?<![*\s])\*(?![*\w])', r'<em>\1</em>', text)
    text = re.sub(r'(?<![\w])_(?![_\s])(.+?)(?<![_\s])_(?![\w])', r'<em>\1</em>', text)
    text = re.sub(r'  \n', '<br>', text)
    text = text.replace('\n', ' ')
    return re.sub(r'\x00(\d+)\x00', lambda m: keep[int(m.group(1))], text)


def md_to_html(md, quote_icon=''):
    out = []
    blocks = re.split(r'\n[ \t]*\n', md.replace('\r\n', '\n').strip())
    for block in blocks:
        lines = block.split('\n')
        # A heading line may be followed directly by paragraph lines.
        while lines and re.match(r'#{1,6} ', lines[0]):
            level = len(lines[0].split(' ', 1)[0])
            tag = 'h2' if level <= 2 else 'h3'
            out.append(f'<{tag}>{inline(lines[0][level + 1:].strip())}</{tag}>')
            lines = lines[1:]
        if not lines:
            continue
        block = '\n'.join(lines)
        if block.lstrip().startswith('<'):
            out.append(block)
        elif all(l.startswith('>') for l in lines):
            text = '\n'.join(re.sub(r'^> ?', '', l) for l in lines)
            cite = ''
            m = re.search(r'\n\s*(?:—|--|-)\s*([^\n]+)$', text)
            if m:
                cite, text = f'<cite>{inline(m.group(1))}</cite>', text[:m.start()]
            out.append(f'<blockquote><i>{quote_icon}</i><p>{inline(text)}</p>{cite}</blockquote>')
        elif re.match(r'\s*[-*+] ', lines[0]) or re.match(r'\s*\d+[.)] ', lines[0]):
            tag = 'ol' if re.match(r'\s*\d', lines[0]) else 'ul'
            items = []
            for l in lines:
                m = re.match(r'\s*(?:[-*+]|\d+[.)]) (.*)', l)
                if m:
                    items.append(m.group(1))
                elif items:
                    items[-1] += '\n' + l.strip()
            out.append(f'<{tag}>' + ''.join(f'<li>{inline(i)}</li>' for i in items) + f'</{tag}>')
        elif IMG_RE.fullmatch(block.strip()) or all(IMG_RE.fullmatch(l.strip()) for l in lines if l.strip()):
            imgs = [inline(l.strip()) for l in lines if l.strip()]
            cls = 'gal' if len(imgs) > 1 else 'fig'
            out.append(f'<div class="{cls}">' + ''.join(imgs) + '</div>')
        else:
            out.append(f'<p>{inline(block)}</p>')
    # Single images separated only by blank lines also read better as a gallery.
    merged = []
    for chunk in out:
        if chunk.startswith('<div class="fig">') and merged and merged[-1].startswith('<div class="fig">'):
            merged[-1] = '<div class="gal">' + merged[-1][17:-6] + chunk[17:-6] + '</div>'
        elif chunk.startswith('<div class="fig">') and merged and merged[-1].startswith('<div class="gal">'):
            merged[-1] = merged[-1][:-6] + chunk[17:-6] + '</div>'
        else:
            merged.append(chunk)
    return '\n'.join(merged)
