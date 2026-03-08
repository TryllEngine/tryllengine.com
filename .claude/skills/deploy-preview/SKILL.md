---
name: deploy-preview
description: Take screenshots of all site pages locally and compare with the live site before pushing. Use this skill when the user wants to preview changes before deploying, do a visual diff, check if pages look correct, compare local vs production, or do a pre-push visual check. Also trigger when the user says "preview", "check before push", or "visual diff".
---

# Deploy Preview

Visual pre-push check. Screenshots all pages locally and on the live site, then presents side-by-side comparisons to catch visual regressions before deploying.

## Overview

This skill helps catch visual issues before pushing to GitHub Pages:
1. Starts a local dev server
2. Gets all page URLs from `sitemap.xml`
3. Takes Playwright screenshots at desktop and mobile widths
4. Takes matching screenshots from the live site for comparison
5. Presents findings for review

**Important**: This skill does NOT push. The user decides whether to push after reviewing.

## Workflow

### Step 1: Start local server

```bash
python -m http.server 8000 &
```

### Step 2: Collect page URLs

Read `sitemap.xml` and extract all `<loc>` URLs. Build two lists:
- **Local**: Replace `https://tryllengine.com` with `http://localhost:8000`
- **Live**: Keep as-is

Also check for modified HTML files not yet in sitemap:
```bash
git diff --name-only HEAD | grep '\.html$'
```

**Processing order**: Homepage first, then product pages, then blog listing, then blog posts (newest 3 only to keep it manageable).

### Step 3: Screenshot local pages

For each local URL:

**Desktop (1440x900):**
```
mcp__playwright__browser_resize → width: 1440, height: 900
mcp__playwright__browser_navigate → {local_url}
mcp__playwright__browser_take_screenshot
```

**Mobile (375x812):**
```
mcp__playwright__browser_resize → width: 375, height: 812
mcp__playwright__browser_navigate → {local_url}
mcp__playwright__browser_take_screenshot
```

### Step 4: Screenshot live pages

Navigate to each live URL (`https://tryllengine.com/...`) and take matching screenshots at the same viewport sizes.

If the live site is down or a page doesn't exist on live (new page), skip the comparison and note it.

### Step 5: Present comparisons

For each page show:
1. Page name and URL
2. Desktop: local vs live screenshot
3. Mobile: local vs live screenshot
4. Status: **Matches**, **Changed**, or **New page**

Flag anything that looks broken:
- Blank/empty pages
- Missing images (broken icons)
- Layout shifts or overflow
- Missing nav or footer

### Step 6: Summary

```
# Deploy Preview Summary

Pages checked: {count}
New pages: {list}
Changed pages: {list}
Unchanged pages: {list}
Issues found: {list or "None"}
```

Ask the user if they want to proceed with pushing.

## Important conventions

- **Do NOT push** — only preview
- **Blog posts**: Include only the newest 2-3 to keep previews fast
- **Pages in .gitignore** (WIP): Screenshot locally but skip live comparison
- **Live site differences are expected** if changes haven't been pushed yet — highlight but don't treat as errors
