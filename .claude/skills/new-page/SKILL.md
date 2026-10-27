---
name: new-page
description: Add a new page to tryllengine.com. Use this skill when the user wants to create a new page, add a new HTML page to the site, scaffold a page, or mentions needing a new landing page, product page, or content page. Pages are designed in Claude Design and baked into the site by scripts/site-build; this skill covers registering the page, its SEO copy, links, sitemap and preview.
---

# New Page

Pages on tryllengine.com are designed in **Claude Design** and turned into static HTML by `scripts/site-build/` (see `scripts/site-build/README.md`). Don't hand-write page HTML: the head (GTM + cookie consent, SEO/OG tags, favicons, JSON-LD), the runtime scripts and the sitemap are all generated.

## Workflow

### Step 1: Get the design

Ask the user for the updated Claude Design export folder (the one with `index.html`, `support.js`, `assets/`). The new page must be one of its `*.html` files and use the same nav and footer as the other pages.

### Step 2: Register the page

1. `scripts/site-build/bake.py` — add the page name (file name without `.html`) to `PAGES`.
2. `scripts/site-build/config.py` — add an entry to `PAGES`:

```python
'pricing': {
    'out': 'pricing.html', 'path': '/pricing', 'priority': '0.8',
    'title': 'Pricing — Tryll Engine',                 # 30–60 chars
    'description': '120–160 character summary for search results and link previews.',
},
```

3. `scripts/site-build/build.py` — add `'pricing.html': '/pricing'` to `INTERNAL` so other pages' links to it get the clean URL.
4. Any `href="#"` placeholder links on the page: add targets to `PAGE_LINKS['pricing']` in `config.py`, keyed by link text (or `aria-label` for icon links). Use `TODO + 'what is missing'` for URLs nobody has yet; the build lists them.

### Step 3: Bake and build

```bash
py -3 scripts/site-build/bake.py "C:/path/to/design-export"
py -3 scripts/site-build/build.py
```

The build prints any links still waiting for a URL.

### Step 4: Preview

1. `py -3 scripts/site-build/serve.py` (background) — resolves `/pricing` like GitHub Pages does
2. Screenshot `http://localhost:8000/pricing` at desktop (1440×900) and mobile (375×812)
3. Check the console for errors and click through the page's interactive parts
4. Show the screenshots to the user

### Step 5: Final checklist

- [ ] Page is in `PAGES` in both `bake.py` and `config.py`, and in `INTERNAL` in `build.py`
- [ ] Title and description written for search (not copied from another page)
- [ ] `sitemap.xml` lists the new URL (the build adds it)
- [ ] No `data-todo` links left, or the user knows which ones are open
- [ ] Desktop and mobile previews reviewed by the user

## Conventions

- **Canonical URLs have no `.html`**: `https://tryllengine.com/pricing`. Internal links use the same form.
- **Never edit generated files** (`index.html`, `features.html`, …, `blog/posts/*/index.html`, `assets/js/pages/*`, `sitemap.xml`) — change the design, `config.py` or the build and rebuild.
- **Old-design pages** (`tryll-assistant.html`, `boscotryll.html`, `closed-beta.html`, `privacy-policy.html`, `tryll-plugin-alpha.html`) are still hand-written HTML; when one is redesigned, remove it from `LEGACY_PAGES` in `config.py`.
