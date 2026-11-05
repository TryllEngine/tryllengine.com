# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TryllEngine.com is the static marketing site for Tryll Engine: on-device AI middleware for game engines (Unity, Unreal Engine 5, proprietary engines). It is hosted on Cloudflare Pages, and every push to `main` is published (see Hosting below).

The main pages are designed in **Claude Design** and turned into static HTML by `scripts/site-build/`. Read `scripts/site-build/README.md` before changing any page.

## Project Structure

```
├── index.html, features.html, download.html,     # GENERATED from the design export
│   demo.html, about.html, blog.html,              #   by scripts/site-build/build.py
│   privacy-policy.html, 404.html
├── blog/
│   ├── posts.json            # post index (source)
│   ├── content/{slug}.md     # post bodies (source)
│   └── posts/{slug}/index.html   # GENERATED
├── tryll-assistant.html, boscotryll.html,        # old-design pages, hand-written,
│   tryll-plugin-alpha.html                        #   kept at their URLs until redesigned
├── closed-beta.html          # GENERATED redirect to /download (see REDIRECTS in config.py)
├── scripts/site-build/       # annotate → bake → build pipeline, config.py, serve.py, publish.py (what Cloudflare publishes)
├── scripts/lead-alerts/      # Cloudflare Worker: accepted contact messages → Slack (config.LEAD_ALERTS)
├── assets/
│   ├── site/                 # images and scripts (three.js) from the design export (hashed names)
│   ├── js/site.js            # runtime that runs the design logic on static HTML
│   ├── js/pages/*.js         # GENERATED: each page's design logic
│   ├── js/forms.js           # contact (HubSpot, or Formspree until config.HUBSPOT is set) + newsletter (MailerLite)
│   ├── js/clips.js           # trailer clips: lazy load, pause off screen, sound buttons
│   ├── js/marquee.js         # media logos highlight (the row scrolls via CSS)
│   ├── video/                # trailer clips + posters, cut by scripts/site-build/clips.py
│   ├── js/blog-list.js       # blog topic chips + pagination
│   ├── js/cookie-consent.js  # cookie banner + Google Consent Mode v2
│   ├── css/site.css          # styles the design doesn't cover
│   ├── blog/                 # post covers and inline images
│   └── favicon/, images/, logo/, docs/
├── sitemap.xml               # GENERATED
├── robots.txt, llms.txt
```

## Development Commands

```bash
py -3 scripts/site-build/serve.py                 # preview at http://localhost:8000 (the live site's URL rules)
py -3 scripts/site-build/build.py                 # rebuild pages, blog, sitemap
py -3 scripts/site-build/bake.py "<export dir>"   # bring in a new Claude Design export, then build
py -3 scripts/site-build/bake.py "<export dir>" index 404   # ...or only some of its pages (a "parts" export, see the README)
py -3 scripts/site-build/preview.py --publish     # team preview at tryllengine.github.io/site-preview
py -3 scripts/site-build/clips.py "<trailer without subtitles>.mp4"   # re-cut the hero / Smart NPCs clips (config.CLIPS), then build
```

Don't use `python -m http.server` to preview: it doesn't resolve `/blog` or `/features` the way the live site does.

## Hosting

- **Site**: Cloudflare Pages project `tryllengine-com`, connected to this repo. Every push to `main` is published. Cloudflare's build command, `python3 scripts/site-build/publish.py`, copies into `dist/` everything git tracks except `scripts/`, `.claude/`, `.github/`, `blog/content/`, `references/`, `blog/posts.json` and Markdown files. Cloudflare then publishes `dist/`. publish.py also writes `dist/_redirects`, which sends every left-out path to the home page. Without that, Cloudflare keeps serving a removed file for up to a week to anyone who requested it before ("asset preservation"), and a cache purge doesn't clear it. The pages themselves are built locally and committed. The "Cloudflare Pages" check on each commit shows its deploy and links to the build log. Claude can't open the Cloudflare dashboard, so if a deploy gets stuck, the user has to click Retry deployment there.
- **Docs**: docs.tryllengine.com is a separate Cloudflare Pages project, published from the `TryllEngine/docs.tryllengine.com` repo.
- **DNS** is also on Cloudflare. The `www` → root redirect is a Cloudflare redirect rule, and HTTP/3 is on.
- **Caching**: browsers revalidate HTML on every visit but keep CSS, scripts and pictures for 4 hours. That's why the build stamps those files with `?v=<content hash>`.
- **Unknown URLs** get `404.html` (the design's "This page rolled a zero") with status 404: Cloudflare Pages serves the site's top-level `404.html` for any path it doesn't have. Paths publish.py leaves out still go to the home page (`_redirects`).
- **The team preview** is still a GitHub Pages site (tryllengine.github.io/site-preview), published by `preview.py`.

## Rules

- **Never hand-edit generated files** (listed above). Change the design export, `scripts/site-build/config.py`, the blog sources or the build scripts, then rebuild.
- **SEO copy, link targets and form endpoints** live in `scripts/site-build/config.py`.
- **Downloads aren't public yet**: `DOWNLOADS_LIVE = False` in `config.py` turns every download and "Get Tryll Engine" button into "Coming soon" (→ newsletter signup). The team preview always shows downloads as designed.
- **Canonical URLs** have no `.html` (`https://tryllengine.com/features`; Cloudflare Pages redirects `/features.html` there with a 308). Blog posts end in a slash (`/blog/posts/{slug}/`), the URL that is served without a redirect.
- **Analytics**: GTM container `GTM-K8MPGKVX` (holds GA4 `G-V0BH3P7R63`, plus "Form submission" and "Clicks Download" events). `cookie-consent.js` must load before GTM; all consent defaults to denied.
- **Forms** must stay real `<form>` elements so GTM's form-submission trigger fires.
- **Old URLs must keep working**: never rename a post slug; when a page is retired, add it to `REDIRECTS` in `config.py` instead of deleting it.

## Brand

- **Design**: navy hero (`#161D29`), primary `#232E41`, white content sections, warm card `#F7F2EE`, text `#181716`
- **Font**: Space Grotesk (400/500)
- **Voice**: for game developers, technical but approachable; say "on-device" and "player's GPU", not "edge" or "client-side"
