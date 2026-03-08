---
name: new-page
description: Scaffold a new static HTML page for tryllengine.com with all required boilerplate. Use this skill when the user wants to create a new page, add a new HTML page to the site, scaffold a page, or mentions needing a new landing page, product page, or content page. Handles boilerplate setup — GTM, meta tags, OG tags, favicon, Tailwind config, nav, footer — sitemap registration, and .gitignore cleanup.
---

# New Page

Scaffold a new static HTML page for tryllengine.com with all required boilerplate.

## Overview

All pages on tryllengine.com share identical boilerplate:
- Google Tag Manager (GTM-K8MPGKVX)
- SEO meta tags + Open Graph + Twitter Cards
- Favicon block (6 links + manifest)
- Tailwind CSS CDN + brand color config
- Font Awesome 6.4.0 CDN
- Google Fonts (Inter + JetBrains Mono)
- Navigation bar (desktop + mobile with overlay menu)
- Footer with social links
- Mobile menu JavaScript

**Reference pages for boilerplate:**
- `blog/posts/_template.html` — cleanest minimal boilerplate (nav, footer, mobile JS)
- `tryll-assistant.html` — product page pattern with feature sections
- `STYLE_GUIDE.md` — design system documentation

## Workflow

### Step 1: Gather page information

Ask the user for:

| Field | Required | Example |
|-------|----------|---------|
| Page slug | Yes | `sdk-docs` → creates `sdk-docs.html` |
| Page title | Yes | `SDK Documentation` |
| Meta description | Yes | 1-2 sentence description for SEO |
| Page type | Yes | `product`, `content`, or `simple` |
| OG image | No | Defaults to site logo |

**Page types:**

| Type | Layout | Use for |
|------|--------|---------|
| `product` | Hero + feature cards + CTAs, max-w-7xl | Product pages like tryll-assistant.html |
| `content` | Prose layout, max-w-3xl | Documentation, guides, long-form content |
| `simple` | Centered single section, max-w-4xl | Legal pages, announcements |

### Step 2: Create the HTML file

Create `{slug}.html` in the project root.

**Critical**: Copy the nav, footer, and mobile menu JS **exactly** from `blog/posts/_template.html`. These must be character-for-character identical across all pages. Do not rewrite them.

#### Structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Google Tag Manager — copy exact snippet from blog/posts/_template.html -->

    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{PAGE_TITLE} | Tryll Engine</title>

    <!-- SEO Meta Tags -->
    <meta name="description" content="{META_DESCRIPTION}">
    <meta name="author" content="Tryll Engine">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="https://tryllengine.com/{slug}">

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://tryllengine.com/{slug}.html">
    <meta property="og:title" content="{PAGE_TITLE}">
    <meta property="og:description" content="{META_DESCRIPTION}">
    <meta property="og:image" content="{OG_IMAGE or /assets/logo/logo-mark/blue.svg}">

    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://tryllengine.com/{slug}.html">
    <meta property="twitter:title" content="{PAGE_TITLE}">
    <meta property="twitter:description" content="{META_DESCRIPTION}">
    <meta property="twitter:image" content="{OG_IMAGE or /assets/logo/logo-mark/blue.svg}">

    <!-- Favicon — copy exact block from blog/posts/_template.html -->
    <!-- Tailwind CDN + config — copy from blog/posts/_template.html -->
    <!-- Font Awesome CDN — copy from blog/posts/_template.html -->
    <!-- Styles — copy base styles from blog/posts/_template.html, add page-specific styles -->
</head>
<body>
    <!-- GTM noscript — copy from blog/posts/_template.html -->
    <!-- Navigation — copy exactly from blog/posts/_template.html -->

    <main class="pt-32 md:pt-40 pb-20 px-4">
        <!-- Content scaffolding based on page type (see below) -->
    </main>

    <!-- Footer — copy exactly from blog/posts/_template.html -->
    <!-- Mobile menu JS — copy from blog/posts/_template.html -->
</body>
</html>
```

#### Content scaffolding by page type:

**Product page** (`product`):
```html
<main class="pt-32 md:pt-40 pb-20 px-4">
    <section class="max-w-7xl mx-auto text-center mb-20">
        <h1 class="text-4xl sm:text-5xl md:text-6xl heading-primary mb-6">{PAGE_TITLE}</h1>
        <p class="text-lg md:text-xl text-secondary max-w-2xl mx-auto mb-8">{META_DESCRIPTION}</p>
        <a href="#" class="btn-primary px-8 py-4 rounded-lg text-lg inline-flex items-center gap-2">
            Get Started
        </a>
    </section>
    <!-- Feature sections go here -->
</main>
```

**Content page** (`content`):
```html
<main class="pt-32 md:pt-40 pb-20 px-4">
    <div class="max-w-3xl mx-auto">
        <h1 class="text-3xl md:text-4xl lg:text-5xl heading-primary mb-6">{PAGE_TITLE}</h1>
        <div class="prose">
            <!-- Content goes here -->
        </div>
    </div>
</main>
```

**Simple page** (`simple`):
```html
<main class="pt-32 md:pt-40 pb-20 px-4">
    <div class="max-w-4xl mx-auto text-center">
        <h1 class="text-3xl md:text-4xl heading-primary mb-6">{PAGE_TITLE}</h1>
        <p class="text-secondary text-lg">{META_DESCRIPTION}</p>
    </div>
</main>
```

### Step 3: Update sitemap.xml

Add after existing top-level pages, before blog post entries:

```xml
<url>
    <loc>https://tryllengine.com/{slug}.html</loc>
    <lastmod>{YYYY-MM-DD}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
</url>
```

### Step 4: Update .gitignore

Check if the slug appears in `.gitignore` under `# Pages not ready for upload`:
```bash
grep "{slug}" .gitignore
```
If found, **remove it** so the page gets tracked by git.

### Step 5: Preview in browser

1. Start local server: `python -m http.server 8000` (background)
2. Navigate with Playwright and screenshot at desktop width
3. Resize to 375x812 and screenshot mobile view
4. Show both to the user for review

### Step 6: Final checklist

- [ ] `{slug}.html` exists in project root
- [ ] GTM snippet in `<head>` and noscript in `<body>`
- [ ] Title, meta description, canonical, og:*, twitter:* all set
- [ ] Favicon block present
- [ ] Nav matches other pages exactly
- [ ] Footer matches other pages exactly
- [ ] Mobile menu JS present and working
- [ ] `sitemap.xml` updated
- [ ] `.gitignore` updated if needed
- [ ] Page renders at desktop and mobile widths

## Important conventions

- **Nav and footer must be identical** across all pages — always copy from `blog/posts/_template.html`
- **Canonical URLs**: `https://tryllengine.com/{slug}` (no `.html`)
- **OG URLs**: `https://tryllengine.com/{slug}.html` (with `.html`)
- **Tailwind config** must include brand colors: primary (#232E41), secondary (#F6F0EB)
- **Reference STYLE_GUIDE.md** for design patterns and component classes
- **Use absolute paths** for assets: `/assets/favicon/`, `/assets/logo/`
