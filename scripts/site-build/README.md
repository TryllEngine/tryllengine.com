# Site build

The site is designed in **Claude Design** and published as plain static HTML on GitHub Pages. These scripts turn a design export into the live pages without losing the design's animations, and add everything the design doesn't have: SEO tags, analytics, real forms, link targets and the blog.

Only Python 3 is needed (no packages). Baking also needs Chrome or Edge.

## Everyday tasks

| Task | Command |
|---|---|
| Preview the site locally | `py -3 scripts/site-build/serve.py` → http://localhost:8000/ |
| Rebuild after editing `config.py`, a blog post or `posts.json` | `py -3 scripts/site-build/build.py` |
| Bring in a new design export | `py -3 scripts/site-build/bake.py "C:/path/to/export"` then `build.py` |
| Publish the team preview | `py -3 scripts/site-build/preview.py --publish` → https://tryllengine.github.io/site-preview/ |
| Re-cut the trailer clips (hero, Smart NPCs) | edit `CLIPS` in `config.py`, then `py -3 scripts/site-build/clips.py "C:/path/to/trailer.mp4"` and `build.py` (needs ffmpeg) |

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
| Wording changed since the design export (e.g. the $200k pricing threshold) | `COPY` in `config.py`: applied to every design page; the build warns when an entry no longer matches |
| Media logos → coverage articles | `MEDIA_LINKS` in `config.py`, keyed by the logo's alt text |
| "What clients are saying" cards: studio, person, quote (an empty list hides the section) | `CLIENT_QUOTES` in `config.py` |
| /demo: gallery screenshots and the "About this game" text | `DEMO_SHOTS` in `config.py` (images in `assets/images/demo/`, 1600×900 plus a 400×225 `-thumb`), `demo-about.md` here |
| Docs links: deep links follow the docs' `latest`, so a docs release needs no change here | `DOCS_V` in `config.py`; the build checks every docs page opens, and links one that `latest` lacks to the version behind `latest` until it has it |
| /features "Faster than speech": the row for how fast people talk | `SPEECH_ROW` in `config.py` |
| Animation clock of the design logic (dice, dial): animation frames instead of the design's 25 steps a second | `tryllClock` in `assets/js/site.js`, swapped in by `write_logic` in `build.py` |
| "How to build" videos (YouTube playlists, titles, lengths) | `VIDEO_LISTS` in `config.py`; thumbnails are saved to `assets/images/videos/` |
| "Coming soon" instead of downloads | `DOWNLOADS_LIVE` and `COMING_SOON` in `config.py` (see below) |
| Trailer clips: which seconds, crops, sizes; the trailer's YouTube link (empty: no "Watch on YouTube" on the hero) | `CLIPS`, `TRAILER_URL` in `config.py`; `clips.py` writes `assets/video/` |
| Homepage use-case card pictures that replace the design's (Real Talk, Dynamic worlds, New genres) | `CARD_PICTURES` in `config.py`, images in `assets/images/` (16:10, 1152×720) |
| Clip playback: lazy loading, pause off screen, the sound buttons | `assets/js/clips.js` (posters only with reduced motion or Save-Data) |
| Media logos row: scrolls with a CSS animation (`tryll-logos` in `site.css`), not the design's 25 fps tick | `assets/js/marquee.js` keeps the "on" highlight in step |
| Contact form → HubSpot once `HUBSPOT['form']` is set in `config.py` (Formspree until then), newsletter → MailerLite | `assets/js/forms.js` |
| Accepted contact messages → the team's Slack channel | `LEAD_ALERTS` in `config.py` + the Cloudflare Worker in `scripts/lead-alerts/` (setup in its README) |
| Blog topic chips + pagination | `assets/js/blog-list.js` |
| Cookie banner + Google Consent Mode v2 | `assets/js/cookie-consent.js` |
| CSS the design doesn't cover (inputs, article headings, lists, video) | `assets/css/site.css` |
| Markdown → HTML for posts | `markdown_lite.py` |

## Generated files: don't edit by hand

`index.html`, `features.html`, `download.html`, `demo.html`, `about.html`, `blog.html`, `privacy-policy.html`, `closed-beta.html`, `blog/posts/*/index.html`, `assets/js/pages/*.js` and `sitemap.xml` are rewritten by `build.py`. Change the design, `config.py` or the blog sources instead.

Hand-written pages from the old design still live at their URLs and are untouched by the build: `tryll-assistant.html`, `boscotryll.html` and `tryll-plugin-alpha.html`.

Retired URLs go in `REDIRECTS` in `config.py`. GitHub Pages can't do server redirects, so the build writes a small noindex page that forwards instantly with a canonical to the new URL, which Google treats as a permanent move. `/closed-beta` → `/download` works this way.

## Coming soon

While `DOWNLOADS_LIVE = False` in `config.py`, the build replaces every "Get Tryll Engine" and download button with "Coming soon" linking to the blog's newsletter signup (`/blog#subscribe`), hides the demo's Steam and Itch.io buttons, and uses the `description_soon` SEO copy. `preview.py` always builds the team preview with downloads on, as designed, then rebuilds the repo's pages for the live site.

On launch day: fill in the download `TODO:` links in `config.py`, set `DOWNLOADS_LIVE = True`, run `build.py` and push.

## Open links

`build.py` ends by listing every placeholder link that still has no real URL (`TODO:` entries in `config.py`). On the page these stay as `href="#" data-todo="…"`, so they are easy to find.
