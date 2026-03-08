# Blog — How to Add a New Post

## File structure

```
blog/
├── posts.json              # Post index (drives the blog listing page)
├── _template.html          # HTML template for new post pages
├── blog-readme.md          # This file
├── content/
│   └── {slug}.md           # Markdown body for each post
└── {slug}.html             # HTML page for each post

assets/blog/
├── {slug}.{ext}            # Card/thumbnail image (used in posts.json + HTML hero)
└── {slug}-inline.{ext}     # In-article image (used in markdown body, optional)
```

## Steps to add a new post

### 1. Write the markdown content

Create `blog/content/{slug}.md`. The file is **pure markdown** — no front-matter. It gets fetched at runtime and rendered with `marked.js`.

- Use absolute paths for images: `/assets/blog/{slug}-inline.png`
- Add hyperlinks for people (`[Name](linkedin-url)`) and products (`[Tryll Assistant](steam-url)`)

### 2. Add images

Place images in `assets/blog/`. All filenames must start with the post slug:

- **Card/thumbnail** (required): `{slug}.{ext}` — shown on the blog grid and as the hero image in the post HTML
- **Inline content** (optional): `{slug}-inline.{ext}` — additional images embedded in the markdown body

Examples for a post with slug `welcome-pierre-moisan`:
- `assets/blog/welcome-pierre-moisan.png` — card image
- `assets/blog/welcome-pierre-moisan-inline.png` — in-article image (if different from card)

If the card and inline image are the same, just use `{slug}.{ext}` for both references.

### 3. Create the HTML page

Copy `blog/_template.html` to `blog/{slug}.html` and replace all `POST_*` placeholders:

| Placeholder | Example |
|---|---|
| `POST_SLUG` | `welcome-pierre-moisan` |
| `POST_TITLE` | `Welcome Pierre Moisan to Tryll Engine` |
| `POST_EXCERPT` | 1-2 sentence summary for social previews |
| `POST_DATE_ISO` | `2026-03-06` |
| `POST_DATE_FORMATTED` | `Mar 6, 2026` |
| `POST_CATEGORY` | CSS class: `news`, `tutorial`, `engineering`, `case-study` |
| `POST_CATEGORY_LABEL` | Display text: `News`, `Tutorial`, `Engineering`, `Case Study` |
| `POST_READ_TIME` | Number only, e.g. `2` |
| `POST_IMAGE` | Full path or URL to hero image |

### 4. Register in posts.json

Add a new entry **at the top** of the array in `blog/posts.json` (newest first):

```json
{
  "slug": "welcome-pierre-moisan",
  "title": "Welcome Pierre Moisan to Tryll Engine",
  "excerpt": "Short summary for the blog card.",
  "category": "news",
  "date": "2026-03-06",
  "readTime": 2,
  "image": "/assets/blog/welcome-pierre-moisan.png",
  "icon": "fa-handshake",
  "author": "Tryll Engine Team"
}
```

**Fields:**
- `slug` — must match the `.html` and `.md` filenames
- `category` — one of: `news`, `engineering`, `tutorial`, `case-study`
- `icon` — Font Awesome class, used as fallback when no image loads
- `date` — ISO format `YYYY-MM-DD`, determines sort order

### 5. Update sitemap.xml

Add a `<url>` entry for the new post in `sitemap.xml`.

## Categories

| Key | Label | Use for |
|---|---|---|
| `news` | News | Team announcements, product launches, milestones |
| `engineering` | Engineering | Technical deep-dives, architecture decisions |
| `tutorial` | Tutorial | How-to guides, integration walkthroughs |
| `case-study` | Case Study | User stories, game-specific implementations |

## Conventions

- **Slugs** are lowercase, hyphen-separated: `welcome-pierre-moisan`
- **Image naming** — all images use the slug as prefix: `{slug}.ext` for card, `{slug}-inline.ext` for in-article
- **No spaces or uppercase** in filenames — use hyphens
- **Posts are sorted by date** (newest first) in `posts.json` — keep this order
- **Markdown content** should not include the post title (it's in the HTML page header)
- **LinkedIn links** for team members should go on the first mention of their name
- **Product links** (Steam, Discord, etc.) should use bold markdown for CTAs
