# Tryll Engine website

The marketing site for [Tryll Engine](https://tryllengine.com): on-device AI middleware that gives game characters realistic minds and runs on the player's GPU. It works with Unity, Unreal Engine 5 and proprietary engines.

## How the site is made

The main pages are designed in **Claude Design**. The scripts in [`scripts/site-build/`](scripts/site-build/README.md) turn the design export into plain static HTML. The build keeps the design's animations and adds what the design doesn't have: SEO tags, analytics, real forms, link targets and the blog.

Most HTML files in this repo are generated, for example `index.html`, `features.html`, `blog/posts/*/index.html` and `sitemap.xml`. Don't edit them by hand. Change the design export, `scripts/site-build/config.py` or the blog sources instead, then rebuild. The [site-build README](scripts/site-build/README.md) lists the generated files and where each setting lives.

## Working on the site

You only need Python 3, with no extra packages. Baking a new design export also needs Chrome or Edge, and re-cutting the trailer clips needs ffmpeg.

```bash
py -3 scripts/site-build/serve.py                 # preview at http://localhost:8000
py -3 scripts/site-build/build.py                 # rebuild pages, blog, sitemap
py -3 scripts/site-build/bake.py "<export dir>"   # bring in a new Claude Design export, then build
py -3 scripts/site-build/preview.py --publish     # publish the team preview
```

`serve.py` resolves URLs the way the live site does: `/features` → `features.html` and `/blog/posts/x` → `/blog/posts/x/`. `python -m http.server` doesn't.

Blog posts are Markdown files in `blog/content/`, listed in `blog/posts.json`.

## Hosting

- **Site:** Cloudflare Pages, connected to this repository. Every push to `main` is published. The pages are built locally with `build.py` and committed. Cloudflare's build only runs `scripts/site-build/publish.py`, which copies the site's own files into `dist/` (leaving out the build scripts, notes and sources), and publishes that folder. Each commit's "Cloudflare Pages" check shows its deploy and links to the build log.
- **DNS:** Cloudflare. `www.tryllengine.com` redirects to `tryllengine.com`.
- **Docs:** [docs.tryllengine.com](https://docs.tryllengine.com) is a separate Cloudflare Pages project, published from [TryllEngine/docs.tryllengine.com](https://github.com/TryllEngine/docs.tryllengine.com).
- **Team preview:** a password-protected copy on GitHub Pages at [tryllengine.github.io/site-preview](https://tryllengine.github.io/site-preview/), hidden from search engines. `preview.py --publish` updates it.

## Legal

Tryll Engine is a trademark of Tryll Engine, Inc. Deep Rock Galactic and Bosco are trademarks of Ghost Ship Games ApS. BoscoTryll is an unofficial mod and is not affiliated with Ghost Ship Games.

© 2026 Tryll Engine, Inc. All rights reserved.

## Contact

Join the [Discord](https://discord.gg/DTKycjPpzs) or use the contact form on [tryllengine.com](https://tryllengine.com/#contact).
