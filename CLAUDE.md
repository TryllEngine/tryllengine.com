# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TryllEngine is a static marketing website for a gaming AI product. The site promotes an AI engine that enables intelligent NPCs in games, running locally without cloud dependencies. The site includes a showcase mod demonstration (BoscoTryll) for Deep Rock Galactic.

## Project Structure

```
TryllEngine.com/
├── index.html              # Main landing page with embedded JavaScript
├── boscotryll.html         # BoscoTryll mod showcase page
├── tryll-assistant.html    # Tryll Assistant product page
├── privacy-policy.html     # Privacy policy page
├── blog.html               # Blog listing page
├── blog/                   # Blog posts and templates
├── STYLE_GUIDE.md         # Design system documentation
├── robots.txt             # Search engine crawling rules
├── sitemap.xml            # XML sitemap for search engines
├── llms.txt               # LLM-readable site description
├── CNAME                  # GitHub Pages custom domain
└── assets/
    ├── blog/              # Blog post images
    ├── docs/              # Legal documents
    ├── favicon/           # Favicon files in various formats
    ├── images/            # Feature showcase images
    └── logo/              # Logo assets (SVG)
```

## Key Technologies

- **HTML5** - Static website structure
- **Tailwind CSS** - Utility-first CSS framework loaded via CDN
- **Font Awesome** - Icon library loaded via CDN (v6.4.0)
- **Vanilla JavaScript** - For interactive elements (animations, form handling, feature showcase)
- **GitHub Pages** - Static hosting

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

### Main Landing Page (index.html)
1. **Navigation**: Fixed header with unified menu across all pages (Product, Integrate, Pricing, Blog, Showcase + Get Early Access button)
2. **Hero Section**: "Drag-Drop AI Into Your Game Engine" — DirectX analogy, Unreal screenshot + code snippet
3. **Numbers Bar**: Trust metrics strip (~8¢, 0 servers, 100% on-device, <50ms latency)
4. **Proof — Already Running**: BoscoTryll video + Tryll Assistant card — shipping proof on Steam
5. **Integration — Three Steps**: Step-by-step with Unreal Editor screenshots (component, tools, blueprint)
6. **Capabilities**: 5-modality icon grid (LLM, STT, TTS, VLM, Agents) + 2×2 use case cards
7. **Why On-Device**: "Cloud AI Breaks Games" — cost, compliance, dependency (moved from position 2 to 7)
6. **Pricing**: Revenue-based calculator
7. **Tryll Assistant — See It Working**: Proof of concept section — on-device AI app on Steam, RAG, end-to-end pipeline, privacy
8. **FAQ Section**: Collapsible accordion with Developer and Player tabs
9. **Contact Form**: Book a Demo / Get in Touch

### BoscoTryll Showcase (boscotryll.html)
1. **Hero Section**: Mod introduction with download CTA
2. **Disclaimer**: Trademark notices for Ghost Ship Games
3. **Feature Showcase**: Interactive demo of mod capabilities
4. **Installation Guide**: Step-by-step instructions
5. **Customization**: Personality examples and configuration
6. **System Requirements**: Hardware specifications
7. **Roadmap**: Planned features and improvements
8. **Community Integration**: Discord links and feedback prompts

### JavaScript Functionality
- **Feature Showcase**: Dynamic content switching with position tracking
- **Mobile Menu**: Toggle with close button functionality
- **Animations**: Intersection Observer for fade-in effects
- **FAQ Accordion**: Expand/collapse functionality
- **Form Handling**: Validation and submission with privacy checkbox
- **Ripple Effects**: Button click animations

## Important Patterns

### CSS Classes
- **Glass morphism**: `.glass-card` for translucent card effects
- **Navigation glass**: `.nav-glass-card` with enhanced frost effects
- **Gradient text**: `.gradient-text` for branded headings
- **Primary button**: `.btn-primary` for main CTAs
- **Text hierarchy**: `.heading-primary`, `.text-secondary`
- **Animations**: `.fade-in`, `.animate-slide-up`, `.animate-scale-in`

### Design System
- **Dark theme only**: Pure black (#000000) background
- **Mobile-first**: All components responsive by default
- **Consistent spacing**: Using Tailwind's spacing scale
- **Typography**: Inter for UI, JetBrains Mono for code

## Brand Guidelines

### Colors
- **Primary**: #232E41 (dark blue-gray)
- **Primary Blue**: #3B82F6 (Tailwind blue-500)
- **Secondary**: #F6F0EB (light cream)
- **Text Colors**:
  - Primary headings: rgba(255, 255, 255, 0.9)
  - Body text: rgba(255, 255, 255, 0.65)
  - Muted text: rgba(255, 255, 255, 0.4)

### Voice & Tone
- **Audience**: Game developers (technical but approachable)
- **Style**: Professional yet conversational
- **Focus**: Benefits over features, local-first messaging

## SEO & Analytics

- **Meta Tags**: Comprehensive Open Graph and Twitter cards
- **Structured Data**: JSON-LD for better search visibility
- **Sitemap**: XML sitemap for all pages
- **Canonical URLs**: Properly set for all pages
- **Robots.txt**: Configured for optimal crawling

## Recent Improvements (2025-07-25)

### Major Additions
- Added BoscoTryll showcase page demonstrating Tryll Engine capabilities
- Created STYLE_GUIDE.md for design system documentation
- Implemented trademark disclaimers for Ghost Ship Games

### UX Improvements
- Rewrote feature descriptions to target developers instead of players
- Updated navigation CTAs ("Try in Action", "Add AI to Your Game")
- Added icons to navigation buttons for visual clarity
- Simplified mobile navigation to single primary CTA
- Added close buttons to mobile menu overlays

### Technical Fixes
- Fixed animation opacity issues with `animation-fill-mode: both`
- Implemented proper height matching for feature showcase columns
- Added container IDs for JavaScript functionality
- Fixed text disappearing after animations
- Improved contrast for secondary buttons

### Content Updates
- Renamed roadmap items for clarity (e.g., "Voice & Text Chat" instead of "NLP")
- Added personality examples (Veteran Miner, Annoyed Old-Timer, Lazy Little Bot)
- Updated tagline to position as showcase mod
- Added "tell us what you think" messaging for alpha feedback

## Best Practices

### When Making Changes
1. **Always use existing patterns** - Check STYLE_GUIDE.md first
2. **Test on mobile** - Mobile-first approach is critical
3. **Maintain consistency** - Use established color and spacing systems
4. **Preserve animations** - Keep smooth transitions and effects
5. **Update sitemap.xml** - When adding new pages

### Code Style
- Use semantic HTML5 elements
- Follow Tailwind utility patterns
- Keep JavaScript vanilla (no frameworks)
- Comment complex animations or interactions
- Use descriptive class names for custom styles

### Git Workflow
- Stage only relevant files (exclude test files, temp files)
- Write clear commit messages
- Update this file when making architectural changes
- Test locally before pushing