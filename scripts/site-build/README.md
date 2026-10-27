# Site build

The site is designed in **Claude Design** and published as plain static HTML on GitHub Pages. These scripts turn a design export into the live pages without losing the design's animations, and add everything the design doesn't have: SEO tags, analytics, real forms, link targets and the blog.

Only Python 3 is needed (no packages). Baking also needs Chrome or Edge.

## Everyday tasks

| Task | Command |
|---|---|
| Preview the site locally | `py -3 scripts/site-build/serve.py` → http://localhost:8000/ |
| Rebuild after editing `config.py`, a blog post or `posts.json` | `py -3 scripts/site-build/build.py` |
| Bring in a new design export | `py -3 scripts/site-build/bake.py "C:/path/to/export"` then `build.py` |

`serve.py` resolves URLs the way GitHub Pages does (`/features` → `features.html`, `/blog/posts/x` → `/blog/posts/x/`), so links behave like production. `python -m http.server` does not.

## How it works

1. **annotate.py**: copies the export and marks every template binding (`{{…}}`, `<sc-for>` loops, `onClick` handlers) with `data-*` attributes.
2. **bake.py**: loads each annotated page in headless Chrome, lets the design runtime render it once, and saves the DOM to `baked/`. Design images go to `assets/site/`.
3. **build.py**: turns the baked pages into the site.
   - Writes the page head: `<title>`, description, canonical, Open Graph/Twitter, favicons, JSON-LD, GTM + cookie consent.
   - Swaps the design's placeholder `href="#"` links for real ones from `config.py`.
   - Turns the drawn contact and newsletter forms into real `<form>`s.
   - Writes each page's original design logic to `assets/js/pages/<page>.js`.
   - Generates `blog.html` and every `blog/posts/<slug>/index.html` from `blog/posts.json` and `blog/content/*.md`, then rewrites `sitemap.xml`.
4. In the browser, **assets/js/site.js** (~8 KB) runs that design logic against the static markup. Animations, carousels, menus and toggles behave as in Claude Design, but the HTML is crawlable and there's no React download or page-wide re-render loop.

## Where things live

| What | Where |
|---|---|
| SEO titles/descriptions, link targets, redirects, form endpoints, GTM ID | `config.py` |
| Contact form → Formspree, newsletter → MailerLite | `assets/js/forms.js` |
| Blog topic chips + pagination | `assets/js/blog-list.js` |
| Cookie banner + Google Consent Mode v2 | `assets/js/cookie-consent.js` |
| CSS the design doesn't cover (inputs, article headings, lists, video) | `assets/css/site.css` |
| Markdown → HTML for posts | `markdown_lite.py` |

## Generated files: don't edit by hand

`index.html`, `features.html`, `download.html`, `demo.html`, `about.html`, `blog.html`, `blog/posts/*/index.html`, `assets/js/pages/*.js` and `sitemap.xml` are rewritten by `build.py`. Change the design, `config.py` or the blog sources instead.

Hand-written pages from the old design still live at their URLs and are untouched by the build: `tryll-assistant.html`, `boscotryll.html`, `privacy-policy.html` and `tryll-plugin-alpha.html`.

Retired URLs go in `REDIRECTS` in `config.py`. GitHub Pages can't do server redirects, so the build writes a small page that forwards instantly with a canonical to the new URL, which Google treats as a permanent move. `/closed-beta` → `/download` works this way.

## Open links

`build.py` ends by listing every placeholder link that still has no real URL (`TODO:` entries in `config.py`). On the page these stay as `href="#" data-todo="…"`, so they are easy to find.
