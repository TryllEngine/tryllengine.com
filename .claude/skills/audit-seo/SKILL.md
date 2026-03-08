---
name: audit-seo
description: Run an SEO audit on tryllengine.com by crawling all pages with Playwright. Use this skill when the user wants to check SEO, audit meta tags, find broken links, verify sitemap consistency, check for missing alt text, or validate the site's search engine optimization. Also trigger when the user asks to check the site health, validate meta tags, or find SEO issues.
---

# Audit SEO

Crawl tryllengine.com locally with Playwright, check every page for SEO issues, and produce a structured report with severity levels.

## Overview

This is a **read-only** operation — no files are modified. It starts a local dev server, reads all pages from `sitemap.xml`, navigates to each with Playwright, and checks for common SEO issues.

## Workflow

### Step 1: Start local server

```bash
python -m http.server 8000 &
```

### Step 2: Parse sitemap.xml

Read `sitemap.xml` and extract all `<loc>` URLs. Convert `https://tryllengine.com/...` to `http://localhost:8000/...` for local testing.

Also scan for HTML files not in the sitemap:
```bash
ls *.html blog/posts/*.html
```

Compare against sitemap entries. Exclude from flagging:
- Files listed in `.gitignore` (WIP pages)
- `blog/posts/_template.html`
- `design-experiments.html`

### Step 3: Crawl each page

For each page URL, navigate with Playwright:
```
mcp__playwright__browser_navigate → {local_url}
```

Then run a single `browser_evaluate` to collect all SEO data:

```javascript
({
  url: location.href,
  title: document.title,
  titleLength: document.title.length,
  metaDescription: document.querySelector('meta[name="description"]')?.content || null,
  metaDescLength: (document.querySelector('meta[name="description"]')?.content || '').length,
  canonical: document.querySelector('link[rel="canonical"]')?.href || null,
  robots: document.querySelector('meta[name="robots"]')?.content || null,
  ogTitle: document.querySelector('meta[property="og:title"]')?.content || null,
  ogDescription: document.querySelector('meta[property="og:description"]')?.content || null,
  ogImage: document.querySelector('meta[property="og:image"]')?.content || null,
  twitterCard: document.querySelector('meta[property="twitter:card"]')?.content || null,
  twitterTitle: document.querySelector('meta[property="twitter:title"]')?.content || null,
  twitterImage: document.querySelector('meta[property="twitter:image"]')?.content || null,
  h1Count: document.querySelectorAll('h1').length,
  h1Text: document.querySelector('h1')?.textContent?.trim() || null,
  imgsWithoutAlt: Array.from(document.querySelectorAll('img:not([alt]), img[alt=""]')).map(i => i.src),
  internalLinks: [...new Set(Array.from(document.querySelectorAll('a[href]')).map(a => a.href).filter(h => h.startsWith(location.origin)))],
})
```

### Step 4: Evaluate each page

| Check | Severity | Rule |
|-------|----------|------|
| Title exists | Critical | `<title>` must not be empty |
| Title length | Warning | 30-60 characters recommended |
| Meta description exists | Critical | Must exist and not be empty |
| Meta description length | Warning | 120-160 characters recommended |
| Canonical URL exists | High | `<link rel="canonical">` must be present |
| og:title exists | Medium | Required for social sharing |
| og:description exists | Medium | Required for social sharing |
| og:image exists | Medium | Required for social previews |
| twitter:card exists | Low | Twitter Card meta tag |
| H1 exists | High | Every page needs exactly one `<h1>` |
| Multiple H1s | Medium | Only one `<h1>` per page |
| Images without alt text | Medium | All `<img>` need `alt` attributes |
| robots meta exists | Low | Should have `<meta name="robots">` |

### Step 5: Check internal links

Collect all unique internal links from all pages. For each:
1. Convert to local URL
2. Navigate with Playwright
3. Check if the page loads (no error state)

Report any broken links with the source page and broken href.

### Step 6: Sitemap consistency

**Pages in sitemap but missing as files:**
- For each `<loc>`, verify the file exists on disk

**HTML files not in sitemap:**
- List all `.html` files in root and `blog/posts/`
- Exclude `.gitignore`'d files, `_template.html`, `design-experiments.html`
- Flag any missing from sitemap

**Format check:**
- All URLs use `https://tryllengine.com/` prefix
- `<lastmod>` dates are valid ISO format
- `<priority>` values between 0.0 and 1.0

### Step 7: Check robots.txt

Read `robots.txt` and verify:
- `User-agent: *` directive exists
- `Sitemap:` URL declared
- No important pages accidentally disallowed

### Step 8: Generate report

```
# SEO Audit Report — tryllengine.com
Generated: {date}
Pages crawled: {count}

## Critical Issues
- [page.html] Missing meta description
- ...

## High Priority
- [page.html] Missing canonical URL
- ...

## Medium Priority
- [page.html] Missing og:image
- [page.html] 3 images without alt text
- ...

## Low Priority / Warnings
- [page.html] Title is 72 characters (recommended: 30-60)
- ...

## Sitemap Issues
- {file}.html on disk but not in sitemap.xml
- ...

## Broken Links
- [source.html] → /broken-path (404)
- ...

## Summary
Total issues: {count}
Critical: {n} | High: {n} | Medium: {n} | Low: {n}
```

## Important conventions

- **Do NOT modify any files** — this is read-only
- **Check .gitignore** before flagging missing sitemap entries — WIP pages are intentionally excluded
- **Include blog/posts/** in the crawl
- **Exclude `_template.html`** from all checks
