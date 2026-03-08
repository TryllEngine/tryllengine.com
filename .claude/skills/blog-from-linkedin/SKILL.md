---
name: blog-from-linkedin
description: Create blog posts for tryllengine.com from LinkedIn post content. Use this skill whenever the user wants to create a new blog post, convert a LinkedIn post to a blog post, add a post to the Tryll Engine blog, or mentions creating content for tryllengine.com/blog. Also trigger when the user shares a LinkedIn URL and wants it turned into a blog post, or pastes LinkedIn post text for blog conversion. This skill handles the full pipeline — content adaptation, hero image generation, HTML page creation, and posts.json registration.
---

# Blog from LinkedIn

Create blog posts for tryllengine.com/blog from LinkedIn post content. Handles the full pipeline: LinkedIn scraping — content adaptation — hero image generation — HTML page — JSON registration — sitemap update.

## Overview

The Tryll Engine blog uses a static file structure:
- `blog/content/{slug}.md` — Markdown body (no front-matter, no title)
- `blog/posts/{slug}.html` — HTML page built from `blog/posts/_template.html`
- `blog/posts.json` — Post index (newest first)
- `assets/blog/` — Images (hero + content images)
- `sitemap.xml` — SEO sitemap

## Workflow

### Step 1: Extract LinkedIn content with Playwright

Use the Playwright MCP tools to scrape the LinkedIn post automatically.

#### 1a. Navigate to the URL

```
mcp__playwright__browser_navigate → LinkedIn post URL
```

#### 1b. Handle cookie consent

After navigation, take a `browser_snapshot`. If you see a cookie consent dialog (buttons like "Accept" / "Reject"), click **Accept** using `browser_click` with the appropriate ref.

#### 1c. Handle login walls

LinkedIn shows public company posts without login, but may show a "Sign in to view more content" modal overlay. If you see this:
- The post content is usually still visible in the page snapshot beneath the modal
- Extract the text from the `<article>` or `<paragraph>` elements in the snapshot
- You do NOT need to log in for public posts

If the post is truly private (no content visible), ask the user to copy-paste the post text instead.

#### 1d. Extract the content

From the `browser_snapshot`, extract:
- **Post text** — the main paragraph content
- **Linked profiles** — people and companies mentioned with their LinkedIn URLs
- **Post images** — note if there are embedded images (photos, screenshots)

**Important: Clean up LinkedIn tracking URLs.** Playwright extracts URLs with `?trk=public_post-text` suffixes. Strip these tracking parameters to get clean URLs:
- `https://ca.linkedin.com/in/pierre-moisan-2431272?trk=public_post-text` → `https://www.linkedin.com/in/pierre-moisan-2431272/`
- `https://ca.linkedin.com/company/behaviour-interactive?trk=public_post-text` → `https://www.linkedin.com/company/behaviour-interactive/`
- Also normalize `ca.linkedin.com` or `fr.linkedin.com` to `www.linkedin.com`

#### 1e. Save post images (if any)

If the LinkedIn post contains images (photos of people, screenshots, diagrams):

1. Use Playwright to extract the image's `src` URL from the page. Use `browser_evaluate` with JavaScript like:
   ```js
   document.querySelector('article img[src*="media.licdn.com"]')?.src
   ```
   Or find the image element in the snapshot and use its ref to get the source URL.

2. **Download the full-resolution image** using `curl`:
   ```bash
   curl -L -o "assets/blog/{slug}-inline.jpg" "IMAGE_URL"
   ```
   LinkedIn image URLs from `media.licdn.com` are publicly accessible and don't require authentication.

3. Check the actual file type with `file` command and use the correct extension (`.jpg`, `.png`, etc.).

4. **Compress inline images** to keep them under ~300 KB. Use Python/Pillow:
   ```python
   from PIL import Image
   img = Image.open("assets/blog/{slug}-inline-1.jpg")
   # Resize if wider than 800px (preserving aspect ratio)
   if img.width > 800:
       ratio = 800 / img.width
       img = img.resize((800, int(img.height * ratio)), Image.LANCZOS)
   img.save("assets/blog/{slug}-inline-1.jpg", optimize=True, quality=85)
   ```

**Important**: Do NOT use `browser_take_screenshot` on image elements — this produces a low-resolution capture of what's rendered on screen. Always download the original image from its source URL for full quality.

If you cannot extract the image URL automatically, ask the user to right-click the image on LinkedIn, copy the image URL, and provide it.

#### Fallback: Manual content

If Playwright fails or the post is behind a login wall:
1. Ask the user to copy-paste the post text
2. Ask them to save and provide any images from the post

### Step 2: Determine post metadata

From the extracted content, determine:

| Field | How to determine |
|-------|-----------------|
| `slug` | Derive from title, lowercase hyphenated (e.g., `welcome-pierre-moisan`) |
| `title` | Extract the main announcement/topic from the LinkedIn post |
| `excerpt` | Write a 1-2 sentence summary for social previews and blog cards |
| `category` | One of: `news`, `engineering`, `tutorial`, `case-study` |
| `date` | Today's date or ask the user |
| `readTime` | Estimate based on word count (~200 words/minute) |
| `icon` | Font Awesome class that fits the topic (e.g., `fa-handshake`, `fa-award`, `fa-microchip`) |

Present the metadata to the user for confirmation before proceeding.

### Step 3: Generate the cover image with DALL-E

**This is the FIRST thing to do after determining metadata.** Every blog post needs a cover image generated by DALL-E. This is a geometric abstract illustration — NEVER a photo. Photos of people, screenshots, etc. are separate "inline" images that go inside the markdown body (Step 4).

The cover image is used in two places:
- **Blog post page**: shown as a 168x168px hero image in the HTML header
- **Blog listing page**: shown as the card thumbnail

**Cover image style:**
- Square format, 1:1 ratio
- Deep navy blue background with subtle paper grain texture
- 1-2 minimal geometric shapes in sky blue, violet, teal, or amber-gold
- Matte finish, no glow/shine/reflections
- Modern graphic design poster aesthetic

Read `references/image-prompts.md` for the full style guide and topic-to-geometric-element mapping.

**Prompt template:**
```
Minimal flat editorial illustration, square format 1:1 ratio. Deep navy blue background with subtle paper grain texture. [DESCRIBE 1-2 GEOMETRIC ELEMENTS AND THEIR COLORS]. Sparse composition, lots of negative space. Matte finish, no glow, no shine, no reflections. Modern graphic design poster aesthetic.
```

**Reference prompts (follow this level of detail and tone):**

Award/Grant post:
```
Minimal flat editorial illustration, square format 1:1 ratio. Deep navy blue background with subtle paper grain texture. A single abstract hexagon shape with a subtle inner triangle, in warm amber-gold and bright sky blue. Sparse composition, centered, lots of negative space. Matte finish, no glow, no shine, no reflections. Modern graphic design poster aesthetic.
```

Advisor/People post:
```
Minimal flat editorial illustration, square format 1:1 ratio. Deep navy blue background with subtle paper grain texture. Two simple abstract semicircle shapes overlapping at the center like a Venn diagram, in bright sky blue and soft violet. Sparse composition, lots of negative space. Matte finish, no glow, no shine, no reflections. Modern graphic design poster aesthetic.
```

**Always generate with DALL-E:**

1. Craft a prompt following the template above and referencing `references/image-prompts.md`
2. Run the generation script (API key is in `.env`):

```bash
python scripts/generate_hero_image.py --prompt "YOUR_PROMPT" --output "assets/blog/{slug}-cover.png"
```

The script generates a 1024x1024 image via DALL-E 3, resizes it to 512x512, and saves it to `assets/blog/{slug}-cover.png` (~300-400 KB).

If the script fails (API error, missing key), inform the user and provide the prompt so they can generate manually.

**Important distinction — two types of images:**
| Type | What it is | How it's made | Filename | Where it appears |
|------|-----------|---------------|----------|-----------------|
| **Cover** | Abstract geometric illustration | Generated by DALL-E (always) | `{slug}-cover.png` | HTML hero (168x168), blog listing card, posts.json `image` field, og:image |
| **Inline** | Photos of people, screenshots, diagrams | Provided by user or captured from LinkedIn | `{slug}-inline-1.{ext}`, `{slug}-inline-2.{ext}`, etc. | Inside the markdown body only |

### Step 4: Adapt content to markdown

Create `blog/content/{slug}.md` following these rules:

1. **Do NOT include the post title** — it's in the HTML page header
2. **Start with a bold intro line** that links the person/product and summarizes the announcement. Example:
   ```
   **We're excited to welcome [Pierre Moisan](https://www.linkedin.com/in/pierre-moisan-2431272/) to Tryll Engine!**
   ```
3. **Optionally include the hero image** in the markdown body if it adds value — but this is NOT required since the hero image is already shown in the HTML page header at 168x168px
4. **Use bold for emphasis** on key phrases: `**on-device AI**`, `**30 years**`, `**Senior Advisor**`
5. **Adapt LinkedIn tone to blog tone**: Remove LinkedIn-specific language ("I'm excited to share...", hashtags, emoji spam, bold Unicode text). Keep it direct and professional, matching Tryll's voice.
6. **Include content images** from the LinkedIn post with proper paths: `/assets/blog/{slug}-inline-1.{ext}`
7. **Add hyperlinks** for:
   - People — their LinkedIn profiles (clean URLs, no tracking params)
   - Products — relevant URLs (Steam, website, etc.)
   - Companies — their LinkedIn company pages or websites
8. **Use bold markdown** for CTAs: `**[Install on Steam](url)**`
9. **Keep it concise** — blog posts are typically short announcements, not essays
10. **Use structured content** where appropriate — bullet lists for backgrounds, `##` headings for sections

**Content image sizing note**: Images from LinkedIn (photos of people, screenshots) go inside the markdown content at full width. The hero image in the HTML template is already sized to 168x168px — you don't need to handle that in markdown.

**Image naming convention**:
- `{slug}-cover.png` — hero/card image (geometric, generated by DALL-E)
- `{slug}-inline-1.{ext}` — in-article content images (photos, screenshots from LinkedIn)

### Step 5: Create the HTML page

Copy the template and replace all placeholders:

```bash
cp blog/posts/_template.html blog/posts/{slug}.html
```

Then replace these placeholders in the new file:

| Placeholder | Replace with |
|-------------|-------------|
| `POST_SLUG` | The slug (used in canonical URL, og:url, twitter:url, fetch script) |
| `POST_TITLE` | Full post title (used in `<title>`, `<h1>`, og:title, twitter:title, alt text) |
| `POST_EXCERPT` | 1-2 sentence summary (used in meta description, og:description, twitter:description) |
| `POST_DATE_ISO` | ISO date like `2026-03-15` (used in article:published_time) |
| `POST_DATE_FORMATTED` | Display date like `Mar 15, 2026` |
| `POST_CATEGORY` | CSS class: `news`, `tutorial`, `engineering`, or `case-study` |
| `POST_CATEGORY_LABEL` | Display text: `News`, `Tutorial`, `Engineering`, or `Case Study` |
| `POST_READ_TIME` | Number only, e.g., `2` |
| `POST_IMAGE` | Path to hero image, e.g., `/assets/blog/{slug}-cover.png` |
| `POST_LINKEDIN_URL` | LinkedIn post URL (e.g., `https://www.linkedin.com/feed/update/urn:li:activity:...`) |

**Important**: `POST_CATEGORY` and `POST_CATEGORY_LABEL` appear together in a single HTML element:
```html
<span class="category-badge POST_CATEGORY">POST_CATEGORY_LABEL</span>
```
Replace them carefully — `POST_CATEGORY` becomes the CSS class (e.g., `news`), `POST_CATEGORY_LABEL` becomes the display text (e.g., `News`).

Also clean up the placeholder comment block at the top of the file (lines 15-26) after replacing — the comment still references `POST_*` names which will be replaced with actual values, making the comment look odd. Either remove the comment block entirely or leave it as-is (it's just an HTML comment, invisible to users).

Verify all placeholders are replaced:
```bash
grep -c "POST_" blog/posts/{slug}.html  # Should be 0
```

### Step 6: Update posts.json

Add a new entry **at the top** of the array in `blog/posts.json`:

```json
{
  "slug": "{slug}",
  "title": "{title}",
  "excerpt": "{excerpt}",
  "category": "{category}",
  "date": "{YYYY-MM-DD}",
  "readTime": {number},
  "image": "/assets/blog/{slug}-cover.png",
  "icon": "fa-{icon}",
  "author": "Tryll Engine Team",
  "linkedinUrl": "https://www.linkedin.com/feed/update/urn:li:activity:..."
}
```

Read the existing file, parse JSON, prepend the new entry, write back with proper formatting (2-space indent).

### Step 7: Update sitemap.xml

Add a `<url>` entry for the new post in `sitemap.xml`, before the first existing blog post entry:

```xml
<url>
    <loc>https://tryllengine.com/blog/posts/{slug}.html</loc>
    <lastmod>{YYYY-MM-DD}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
</url>
```

### Step 8: Preview in browser

Start a local dev server and open the new post for review:

1. Start the server (if not already running):
```bash
python -m http.server 8000
```
Run this in the background so it doesn't block.

2. Use Playwright to navigate to the new post:
```
mcp__playwright__browser_navigate → http://localhost:8000/blog/posts/{slug}.html
```

3. Take a screenshot of the post page with `browser_take_screenshot` and show it to the user.

4. Also navigate to `http://localhost:8000/blog.html` and take a screenshot to show how the card looks in the blog listing.

5. Ask the user to review both views and confirm the post looks good, or request changes.

If the user requests changes, make them and re-preview. Once approved, proceed to the final checklist.

### Step 9: Final checklist

Before finishing, verify:

- [ ] `blog/content/{slug}.md` exists and has no `POST_*` placeholders
- [ ] `blog/content/{slug}.md` does NOT include the post title as a heading
- [ ] `blog/posts/{slug}.html` exists and has zero `POST_*` placeholders remaining
- [ ] `blog/posts.json` has the new entry at the top, valid JSON
- [ ] Hero image file exists in `assets/blog/` (generated by DALL-E)
- [ ] Any content images are saved in `assets/blog/` with `{slug}-inline` naming
- [ ] `sitemap.xml` has the new URL entry
- [ ] All LinkedIn URLs are clean (no `?trk=` tracking params, normalized to `www.linkedin.com`)
- [ ] All image paths use `/assets/blog/` prefix
- [ ] No spaces or uppercase in filenames — use hyphens
- [ ] User has reviewed the post and blog listing previews

Present a summary to the user:
```
Blog post created: {title}
   - Page: blog/posts/{slug}.html
   - Content: blog/content/{slug}.md
   - Hero image: assets/blog/{slug}-cover.png
   - Added to posts.json (position: first)
   - Added to sitemap.xml
   - Preview: http://localhost:8000/blog/posts/{slug}.html
```

## Important conventions

- **Always preview with Playwright**: After creating the post, you MUST start a local server and use Playwright to screenshot both the post page and the blog listing. Never skip this step — always show the user what the post looks like before finishing.
- **Tryll positioning language**: Use "on-device" not "edge" or "local." Use "player's GPU" not "client-side."
- **Tone**: Direct, confident, technically grounded. No buzzwords. Match founder voice, not marketing press release.
- **Blog posts are short**: Most existing posts are 2-4 minute reads. Don't pad.
- **Hero images are abstract**: Never use photos as hero images. Always geometric/editorial style, generated by DALL-E.
- **Content images can be photos**: Photos of people, screenshots, etc. go inside the markdown body with `{slug}-inline-N` naming.
- **Image naming**: `{slug}-cover.png` for DALL-E cover, `{slug}-inline-1.{ext}`, `{slug}-inline-2.{ext}` for in-article images.
- **Bold for emphasis**: Use `**bold**` for key phrases, titles, and stats in the markdown body.
- **LinkedIn links**: Always use clean URLs without tracking parameters. Normalize country subdomains to `www.linkedin.com`.
- **Structured intros**: Start markdown with a bold intro paragraph linking the key person/product.
