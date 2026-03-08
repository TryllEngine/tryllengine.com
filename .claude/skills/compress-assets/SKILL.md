---
name: compress-assets
description: Scan and compress oversized images in the assets directory. Use this skill when the user wants to optimize images, reduce file sizes, check for large assets, compress blog images, find unused images, or optimize the site for performance. Also trigger when the user mentions slow page loads, large images, or asset optimization.
---

# Compress Assets

Scan `assets/` for oversized images, report file sizes, and compress images that exceed thresholds.

## Overview

Images in `assets/` are served directly via GitHub Pages with no CDN compression. Large images slow down page loads. This skill scans, reports, and compresses oversized files.

## Thresholds

| Image type | Max size | Pattern |
|-----------|----------|---------|
| Blog cover images | 400 KB | `assets/blog/*-cover.png` |
| Blog inline images | 300 KB | `assets/blog/*-inline-*.*` |
| Other images | 500 KB | Everything else in `assets/` |

## Workflow

### Step 1: Scan all images

Use Python to scan and report:

```python
import os, glob

for pattern in ['assets/**/*.png', 'assets/**/*.jpg', 'assets/**/*.jpeg', 'assets/**/*.gif', 'assets/**/*.webp']:
    for f in glob.glob(pattern, recursive=True):
        size_kb = os.path.getsize(f) / 1024
        print(f'{size_kb:8.0f} KB  {f}')
```

Skip SVG files (vector, already optimized) and favicon files (`assets/favicon/`).

### Step 2: Generate size report

```
# Image Asset Report

## Blog Cover Images (threshold: 400 KB)
  403 KB  assets/blog/example-cover.png  [OVER]
  334 KB  assets/blog/other-cover.png    [OK]

## Blog Inline Images (threshold: 300 KB)
   58 KB  assets/blog/example-inline-1.jpeg  [OK]

## Other Images (threshold: 500 KB)
  238 KB  assets/images/feature.png  [OK]

Total images: {count}
Total size: {total} MB
Over threshold: {count} images
```

### Step 3: Ask user for confirmation

Present oversized images and offer:
- **Compress all** — compress everything over threshold
- **Compress selected** — let user pick
- **Report only** — just the report, no changes

### Step 4: Compress oversized images

**PNG cover images (must stay square):**
```python
from PIL import Image
img = Image.open(path)
if img.width > 512 or img.height > 512:
    img = img.resize((512, 512), Image.LANCZOS)
img.save(path, "PNG", optimize=True)
```

**JPEG inline images:**
```python
from PIL import Image
img = Image.open(path)
if img.width > 1200:
    ratio = 1200 / img.width
    img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
img.save(path, optimize=True, quality=85)
```

**PNG inline images (non-cover):**
```python
from PIL import Image
img = Image.open(path)
if img.width > 1200:
    ratio = 1200 / img.width
    img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
img.save(path, "PNG", optimize=True)
```

### Step 5: Report results

```
# Compression Results

| File | Before | After | Saved |
|------|--------|-------|-------|
| assets/blog/example-cover.png | 450 KB | 380 KB | 70 KB (16%) |

Total saved: {total} KB
```

### Step 6: Check for unused images (optional)

If the user requests it:

1. List all image files in `assets/`
2. For each, search all `.html` and `.md` files for the filename
3. Also check `blog/posts.json` image fields (blog covers are referenced there)
4. Flag images with zero references as potentially unused

**Warning**: Some images may be referenced dynamically — present results but don't auto-delete.

## Important conventions

- **Never delete images** without explicit user confirmation
- **Blog covers must stay square** — do not change aspect ratio
- **Skip SVGs** — vector files, already optimized
- **Skip favicon files** — strict format requirements
- **Verify visually** after compression — take a Playwright screenshot of a page using the image
