---
name: changelog-from-steam
description: Create blog posts for tryllengine.com from Steam update changelogs. Use this skill when the user wants to create a changelog blog post, write a release notes post, document a new version of Tryll Assistant or BoscoTryll, or mentions creating a blog post from Steam update notes. Also trigger when the user provides a version number and list of changes for a product update.
---

# Changelog from Steam

Create blog posts for tryllengine.com/blog from Steam product update changelogs. Handles the full pipeline: content gathering — markdown creation — hero image generation — HTML page — JSON registration — sitemap update.

## Overview

This skill creates blog posts for product releases and updates. It follows the same blog file structure as `blog-from-linkedin`:
- `blog/content/{slug}.md` — Markdown body (no front-matter, no title)
- `blog/posts/{slug}.html` — HTML page built from `blog/posts/_template.html`
- `blog/posts.json` — Post index (newest first)
- `assets/blog/` — Images (hero + content images)
- `sitemap.xml` — SEO sitemap

## Reference

Use `blog/content/tryll-assistant-v0-0-8-cuda-hip-support.md` as the structural template for changelog posts.

## Steam App IDs

- **Tryll Assistant**: `3442530` → `https://store.steampowered.com/app/3442530/Tryll_Assistant/`
- **BoscoTryll**: `4193780` → `https://store.steampowered.com/app/4193780/`

## Workflow

### Step 1: Gather update information

Ask the user for or extract from their message:

| Field | How to determine |
|-------|-----------------|
| Product name | Tryll Assistant or BoscoTryll |
| Version number | e.g., `v0.0.9` |
| Change list | Bullet points of what changed — new features, fixes, improvements |
| Screenshot/image | Optional — ask if they have a screenshot of the new feature |

If the user provides a Steam update URL, use Playwright to navigate and extract the update text:
```
mcp__playwright__browser_navigate → Steam update URL
mcp__playwright__browser_snapshot
```

### Step 2: Determine post metadata

| Field | How to determine |
|-------|-----------------|
| `slug` | `{product}-v{version-hyphenated}-{key-feature}` e.g., `tryll-assistant-v0-0-9-multi-monitor` |
| `title` | `{Product} v{version} — {Key Feature}` e.g., `Tryll Assistant v0.0.9 — Multi-Monitor Support` |
| `excerpt` | 1-2 sentence summary of the most important changes |
| `category` | `news` |
| `date` | Today's date or the actual release date |
| `readTime` | Estimate based on word count (~200 words/minute), typically 2-3 min |
| `icon` | `fa-rocket` for major releases, `fa-code-branch` for minor updates, `fa-microchip` for hardware/backend changes |

Present the metadata to the user for confirmation before proceeding.

### Step 3: Generate the cover image with DALL-E

Use the "Updates/versions" mapping from `references/image-prompts.md`: arrows, stacked layers, progression shapes.

**Prompt template for changelogs:**
```
Minimal flat editorial illustration, square format 1:1 ratio. Deep navy blue background with subtle paper grain texture. [GEOMETRIC ELEMENTS]. Sparse composition, lots of negative space. Matte finish, no glow, no shine, no reflections. Modern graphic design poster aesthetic.
```

Adjust geometric elements based on the update topic:
- GPU/hardware changes → chip-like rectangles, circuit patterns
- UI/feature additions → window rectangles, overlapping panels
- Performance improvements → streamlined arrows, angular shapes
- General updates → stacked layers, progression shapes

**Reference prompt (version/update post):**
```
Minimal flat editorial illustration, square format 1:1 ratio. Deep navy blue background with subtle paper grain texture. Three stacked horizontal rectangles with rounded corners, slightly offset like version layers, in bright sky blue, warm teal, and soft violet. Sparse composition, lots of negative space. Matte finish, no glow, no shine, no reflections. Modern graphic design poster aesthetic.
```

Generate with:
```bash
python scripts/generate_hero_image.py --prompt "YOUR_PROMPT" --output "assets/blog/{slug}-cover.png"
```

The script auto-resizes to 512x512 (~300-400 KB).

### Step 4: Create the markdown content

Create `blog/content/{slug}.md` following this structure:

1. **Optional inline image** — if the user provided a screenshot:
   ```
   ![{Title}](/assets/blog/{slug}-inline-1.{ext})
   ```

2. **Intro paragraph** — one sentence stating the version and its headline change:
   ```
   Tryll Assistant v0.0.9 is out, adding **multi-monitor support** and several performance improvements.
   ```

3. **"What's New" section** with `##` heading — subsections for each major change using `###`

4. **Optional comparison table** — if comparing options (backends, settings, etc.)

5. **"How to Get It" or "How to Update" section**:
   ```
   ## How to Update

   Steam updates automatically. If you have auto-updates disabled:
   1. Right-click Tryll Assistant in your Steam library
   2. Select **Properties > Updates**
   3. Click **Update**
   ```

6. **Closing CTA** with Steam link:
   ```
   ---

   Download the update on [Steam](https://store.steampowered.com/app/{APP_ID}/{Product_Name}/) and let us know how it works on your setup.
   ```

**Content rules:**
- Do NOT include the post title as a heading
- Use **bold** for feature names and key terms
- Keep it concise — changelog posts are typically 2-3 min reads
- Match the tone of `tryll-assistant-v0-0-8-cuda-hip-support.md`

### Step 5: Save inline images (if any)

If the user provides screenshots:
1. Save to `assets/blog/{slug}-inline-1.{ext}`
2. Compress if larger than 300 KB:
   ```python
   from PIL import Image
   img = Image.open("assets/blog/{slug}-inline-1.jpg")
   if img.width > 1200:
       ratio = 1200 / img.width
       img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
   img.save("assets/blog/{slug}-inline-1.jpg", optimize=True, quality=85)
   ```

### Step 6: Create the HTML page

```bash
mkdir -p blog/posts/{slug}
cp blog/posts/_template.html blog/posts/{slug}/index.html
```

Replace all `POST_*` placeholders. For changelog posts:
- `POST_CATEGORY` → `news`
- `POST_CATEGORY_LABEL` → `News`
- `POST_LINKEDIN_URL` → If no LinkedIn post exists, use the Steam store page URL

Verify: `grep -c "POST_" blog/posts/{slug}/index.html` should return 0.

### Step 7: Update posts.json

Add a new entry **at the top** of the array:

```json
{
  "slug": "{slug}",
  "title": "{title}",
  "excerpt": "{excerpt}",
  "category": "news",
  "date": "{YYYY-MM-DD}",
  "readTime": {number},
  "image": "/assets/blog/{slug}-cover.png",
  "icon": "fa-{icon}",
  "author": "Tryll Engine Team",
  "linkedinUrl": "{steam-or-linkedin-url}"
}
```

### Step 8: Update sitemap.xml

Add before existing blog post entries:

```xml
<url>
    <loc>https://tryllengine.com/blog/posts/{slug}</loc>
    <lastmod>{YYYY-MM-DD}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
</url>
```

### Step 9: Preview in browser

1. Start local server: `python -m http.server 8000` (background)
2. Navigate with Playwright to the new post and take a screenshot
3. Also screenshot `http://localhost:8000/blog.html` to verify the blog card
4. Show both to the user for approval

### Step 10: Final checklist

- [ ] `blog/content/{slug}.md` exists, no `POST_*` placeholders, no title heading
- [ ] `blog/posts/{slug}/index.html` exists, zero `POST_*` placeholders
- [ ] `blog/posts.json` has the new entry at the top, valid JSON
- [ ] Cover image exists at `assets/blog/{slug}-cover.png`
- [ ] Any inline images compressed and in `assets/blog/`
- [ ] `sitemap.xml` has the new URL entry
- [ ] Steam links use the correct app ID
- [ ] User has reviewed the post preview

## Important conventions

- **Changelog posts are short**: 2-3 minute reads, not essays
- **Use the v0.0.8 post as reference**: `blog/content/tryll-assistant-v0-0-8-cuda-hip-support.md`
- **Hero images are abstract**: Never use screenshots as hero. Always DALL-E geometric style.
- **Tone**: Direct, technically grounded. Describe what changed and why it matters. No marketing fluff.
