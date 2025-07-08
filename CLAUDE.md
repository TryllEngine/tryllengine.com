# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TryllEngine is a static marketing website for a gaming AI product. The site promotes an AI engine that enables intelligent NPCs in games, running locally without cloud dependencies.

## Project Structure

```
TryllEngine/
├── index.html  # Main landing page with embedded JavaScript
└── style.css   # Basic styles (mostly unused as site uses Tailwind CSS)
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
   - Hero section with animated particles
   - Value proposition
   - Demo section
   - Features list
   - Target audience
   - Social proof
   - Call-to-action forms

2. **Styling approach**:
   - Primarily uses Tailwind CSS via CDN
   - Custom Tailwind config embedded in `<script>` tag
   - Custom CSS for animations, glass effects, and particles
   - The separate style.css file appears to be legacy/unused

3. **JavaScript functionality**:
   - Particle animation system
   - Intersection Observer for fade-in animations
   - Ripple effects on buttons
   - Form submission handlers (currently just alerts)

## Important Patterns

- **Glass morphism design** - `.glass-card` class for translucent card effects
- **Gradient text** - `.gradient-text` class for colored headings
- **Neon glow effects** - `.neon-glow` classes for button hover states
- **Grid pattern backgrounds** - CSS-based grid overlays
- **Responsive design** - Mobile-first approach using Tailwind breakpoints