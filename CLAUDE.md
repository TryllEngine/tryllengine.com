# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TryllEngine.com is the static marketing site for Tryll Engine: on-device AI middleware for game engines (Unity, Unreal Engine 5, proprietary engines). It is hosted on GitHub Pages from the `main` branch, with the custom domain in `CNAME`.

The main pages are designed in **Claude Design** and turned into static HTML by `scripts/site-build/`. Read `scripts/site-build/README.md` before changing any page.

## Project Structure

```
├── index.html, features.html, download.html,     # GENERATED from the design export
│   demo.html, about.html, blog.html               #   by scripts/site-build/build.py
├── blog/
│   ├── posts.json            # post index (source)
│   ├── content/{slug}.md     # post bodies (source)
│   └── posts/{slug}/index.html   # GENERATED
├── tryll-assistant.html, boscotryll.html,        # old-design pages, hand-written,
│   closed-beta.html, privacy-policy.html,         #   kept at their URLs until redesigned
│   tryll-plugin-alpha.html
├── scripts/site-build/       # annotate → bake → build pipeline, config.py, serve.py
├── assets/
│   ├── site/                 # images from the design export (hashed names)
│   ├── js/site.js            # runtime that runs the design logic on static HTML
│   ├── js/pages/*.js         # GENERATED: each page's design logic
│   ├── js/forms.js           # contact (Formspree) + newsletter (MailerLite)
│   ├── js/blog-list.js       # blog topic chips + pagination
│   ├── js/cookie-consent.js  # cookie banner + Google Consent Mode v2
│   ├── css/site.css          # styles the design doesn't cover
│   ├── blog/                 # post covers and inline images
│   └── favicon/, images/, logo/, docs/
├── sitemap.xml               # GENERATED
├── robots.txt, llms.txt, CNAME
```

## Development Commands

```bash
py -3 scripts/site-build/serve.py                 # preview at http://localhost:8000 (GitHub Pages URL rules)
py -3 scripts/site-build/build.py                 # rebuild pages, blog, sitemap
py -3 scripts/site-build/bake.py "<export dir>"   # bring in a new Claude Design export, then build
```

Don't use `python -m http.server` to preview: it doesn't resolve `/blog` or `/features` the way GitHub Pages does.

## Rules

- **Never hand-edit generated files** (listed above). Change the design export, `scripts/site-build/config.py`, the blog sources or the build scripts, then rebuild.
- **SEO copy, link targets and form endpoints** live in `scripts/site-build/config.py`.
- **Canonical URLs** have no `.html` (`https://tryllengine.com/features`); blog posts end in a slash (`/blog/posts/{slug}/`, the URL GitHub Pages serves without a redirect).
- **Analytics**: GTM container `GTM-K8MPGKVX` (holds GA4 `G-V0BH3P7R63`, plus "Form submission" and "Clicks Download" events). `cookie-consent.js` must load before GTM; all consent defaults to denied.
- **Forms** must stay real `<form>` elements so GTM's form-submission trigger fires.
- **Old blog URLs must keep working**: never rename a post slug.

## Brand

- **Design**: navy hero (`#161D29`), primary `#232E41`, white content sections, warm card `#F7F2EE`, text `#181716`
- **Font**: Space Grotesk (400/500)
- **Voice**: for game developers, technical but approachable; say "on-device" and "player's GPU", not "edge" or "client-side"
