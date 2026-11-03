# Tryll Engine website

The marketing site for [Tryll Engine](https://tryllengine.com): on-device AI middleware for game engines (Unity, Unreal Engine 5, proprietary engines). Static HTML on GitHub Pages, served from `main` with the custom domain in `CNAME`.

## How it's made

The main pages (home, For Developers, Get Tryll Engine, demo, about, blog, privacy) are designed in **Claude Design** and turned into crawlable static HTML by the scripts in [`scripts/site-build/`](scripts/site-build/README.md), which also add the SEO tags, analytics, real forms and links, and generate the blog from `blog/posts.json` and `blog/content/*.md`. Those pages are generated: change the design export, `scripts/site-build/config.py` or the blog sources, then rebuild.

`tryll-assistant.html` (Tryll Assistant on Steam) and `tryll-plugin-alpha.html` (the plugin alpha: invited partners' download links) are hand-written pages from the old design, kept at their URLs until they are redesigned. Retired pages forward to their successors (`REDIRECTS` in `scripts/site-build/config.py`).

[`CLAUDE.md`](CLAUDE.md) has the project map and the rules (generated files, URLs, analytics, forms, brand); `.claude/skills/` has the workflows for new posts, pages and checks.

## Working on it

Python 3 is all the build needs. On Windows:

```bash
py -3 scripts/site-build/serve.py      # preview at http://localhost:8000 (resolves /features, /blog like GitHub Pages)
py -3 scripts/site-build/build.py      # rebuild the pages, the blog and the sitemap
```

Pushing to `main` publishes the site.

## Legal

Tryll Engine is a trademark of Tryll Engine, Inc. Space Grotesk (in `assets/fonts/`) is licensed under the SIL Open Font License 1.1.

© Tryll Engine, Inc. All rights reserved.
