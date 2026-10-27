# Blog — How to Add a New Post

Post pages, the blog listing and the sitemap are **generated** by `scripts/site-build/build.py`. You only write the markdown, add images and register the post in `posts.json`.

## File structure

```
blog/
├── posts.json              # Post index (source of the listing, the pages and the sitemap)
├── blog-readme.md          # This file
├── content/
│   └── {slug}.md           # Markdown body for each post
└── posts/
    └── {slug}/
        └── index.html      # GENERATED — don't edit

assets/blog/
├── {slug}-cover.jpg        # Cover illustration (listing card, social preview)
├── {slug}-inline-1.{ext}   # In-article image 1 (optional)
└── ...
```

## Steps

### 1. Write the markdown

Create `blog/content/{slug}.md`: plain markdown, no front matter, no title (the build adds it).

- Use absolute image paths: `/assets/blog/{slug}-inline-1.jpg`
- **A photo on the very first line becomes the big hero image** on the post page. Without one, the cover is used.
- Two or more images in a row (separated only by blank lines) become a side-by-side gallery.
- `> quote` lines become the design's quote card. End with a line `> — Name, Company` to add a caption.
- Supported: `##`/`###` headings, **bold**, *italic*, links, lists, `code`, and raw HTML blocks (e.g. `<div class="video-embed"><iframe …></iframe></div>` for YouTube).

### 2. Add images

Put them in `assets/blog/`, named after the slug:

- **Cover** (required): `{slug}-cover.jpg`, an abstract geometric illustration (see the `blog-cover-prompts` skill), shown 16:10 on the listing card
- **Inline** (optional): `{slug}-inline-1.jpg`, `{slug}-inline-2.png`, …

### 3. Register in posts.json

Add an entry (order doesn't matter, the build sorts by date):

```json
{
  "slug": "welcome-pierre-moisan",
  "title": "Welcome Pierre Moisan to Tryll Engine",
  "excerpt": "1–2 sentences, used for the meta description and social previews.",
  "category": "news",
  "date": "2026-03-06",
  "readTime": 2,
  "image": "/assets/blog/welcome-pierre-moisan-cover.jpg",
  "icon": "fa-handshake",
  "author": "Tryll Engine Team",
  "linkedinUrl": "https://www.linkedin.com/feed/update/urn:li:activity:..."
}
```

`category` is one of `news`, `engineering`, `tutorial`, `case-study` (shown as News / Engineering / Tutorials / Case Studies).

### 4. Build and preview

```bash
py -3 scripts/site-build/build.py
py -3 scripts/site-build/serve.py      # then open http://localhost:8000/blog/posts/{slug}/
```

The post's canonical URL is `https://tryllengine.com/blog/posts/{slug}/`.
