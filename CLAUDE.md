# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TryllEngine is a static marketing website for a gaming AI product. The site promotes an AI engine that enables intelligent NPCs in games, running locally without cloud dependencies.

## Project Structure

```
TryllEngine/
├── index.html              # Main landing page with embedded JavaScript
├── privacy-policy.html     # Privacy policy page
├── style.css              # Basic styles (mostly unused as site uses Tailwind CSS)
├── robots.txt             # Search engine crawling rules
├── sitemap.xml            # XML sitemap for search engines
├── CNAME                  # GitHub Pages custom domain
├── assets/
│   ├── favicon/           # Favicon files in various formats
│   ├── logo/              # Logo assets (SVG)
│   └── team_photos/       # Team member photos (unused)
└── everything-you-need-section.html  # HTML snippet (backup/reference)
```

## Key Technologies

- **HTML5** - Single page website structure
- **Tailwind CSS** - Utility-first CSS framework loaded via CDN
- **Font Awesome** - Icon library loaded via CDN
- **Vanilla JavaScript** - For interactive elements (particles, animations, form handling)

## Development Commands

Since this is a static website with no build process:

```bash
# Open in browser directly
open index.html

# Or serve with any static server
python -m http.server 8000
# Then visit http://localhost:8000
```

## Architecture Notes

The website is a single-page marketing site with:

1. **index.html** - Contains all content, structured in sections:
   - Hero section with branding and key messaging
   - Demo section with YouTube embed and action cards
   - "The Old Way is Dead" comparison section
   - Interactive features showcase with clickable demo cards
   - Feature grid with detailed explanations
   - Cost comparison and value proposition
   - Target audience breakdown (Studios, Solo Developers, Modders)
   - FAQ section with collapsible answers
   - Pricing tiers and final call-to-action
   - Contact form (redirects to homepage on submission)

2. **privacy-policy.html** - Privacy policy page with legal information

3. **Styling approach**:
   - Primarily uses Tailwind CSS via CDN
   - Custom Tailwind config embedded in `<script>` tag
   - Custom CSS for animations, glass effects, and particles
   - The separate style.css file appears to be legacy/unused

4. **JavaScript functionality**:
   - Intersection Observer for fade-in animations
   - Ripple effects on buttons
   - Interactive feature showcase with smooth transitions
   - FAQ accordion with expand/collapse functionality
   - Form submission handlers with null checks
   - Fallback content system for missing video assets

## Important Patterns

- **Glass morphism design** - `.glass-card` class for translucent card effects
- **Gradient text** - `.gradient-text` class for colored headings
- **Neon glow effects** - `.neon-glow` classes for button hover states
- **Grid pattern backgrounds** - CSS-based grid overlays
- **Responsive design** - Mobile-first approach using Tailwind breakpoints

## SEO Setup

- **Meta tags**: Description, keywords, Open Graph, Twitter cards
- **robots.txt**: Allows all crawlers, points to sitemap
- **sitemap.xml**: Lists main pages for search engine discovery
- **Canonical URLs**: Set for all pages

## Recent Improvements (2025-07-18)

### SEO Implementation
- Added comprehensive meta tags for search engine optimization
- Created robots.txt and sitemap.xml files
- Removed unused pages (team.html, thank-you.html, old-features-section-backup.html)
- Updated form submissions to redirect to homepage
- Cleaned up project structure by removing Node.js files

## Recent Improvements (2025-07-09)

### Fixed JavaScript Issues
- Added null checks for form event listeners to prevent console errors
- Improved error handling for missing DOM elements
- Enhanced feature showcase with proper fallback content

### Interactive Features
- **Feature Showcase**: Clickable feature items with smooth transitions and visual feedback
- **FAQ Accordion**: Fully functional collapsible FAQ items (collapsed by default)
- **Fallback System**: Rich placeholder content for missing video assets with icons and descriptions

### Content Updates
- Enhanced FAQ answers with comprehensive information
- Added proper visual indicators for interactive elements
- Improved user experience with meaningful placeholder content