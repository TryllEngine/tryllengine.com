# Tryll Engine Website

Official marketing website for Tryll Engine - the AI engine that brings NPCs to life in games without cloud dependencies.

## 🚀 Overview

Tryll Engine enables game developers to integrate intelligent NPCs powered by local language models. This repository contains the marketing website and BoscoTryll showcase mod demonstration.

## 🎮 Live Demo

Visit [tryllengine.com](https://tryllengine.com) to see:
- Product features and capabilities
- BoscoTryll showcase mod for Deep Rock Galactic
- Pricing and early access information

## 📁 Project Structure

```
TryllEngine.com/
├── index.html              # Main landing page
├── boscotryll.html         # BoscoTryll mod showcase page
├── privacy-policy.html     # Privacy policy
├── style.css              # Legacy styles (site uses Tailwind CSS)
├── STYLE_GUIDE.md         # Design system documentation
├── robots.txt             # SEO crawler rules
├── sitemap.xml            # Search engine sitemap
├── CNAME                  # GitHub Pages custom domain
└── assets/
    ├── favicon/           # Favicon files
    ├── logo/              # Brand assets (SVG)
    └── team_photos/       # Team photos (unused)
```

## 🛠️ Technology Stack

- **Frontend**: HTML5, Tailwind CSS (via CDN), Vanilla JavaScript
- **Design**: Glass morphism, dark theme, responsive mobile-first
- **Hosting**: GitHub Pages
- **Icons**: Font Awesome 6.4.0
- **Fonts**: Inter, JetBrains Mono

## 🎨 Key Features

### Marketing Site (index.html)
- Interactive feature showcase with smooth animations
- Developer-focused messaging
- Pricing tiers (Free & Commercial)
- FAQ section with collapsible items
- Contact form for early access

### BoscoTryll Showcase (boscotryll.html)
- Demonstrates Tryll Engine capabilities
- Installation and customization guides
- Personality examples for AI companions
- System requirements and roadmap
- Alpha community integration

## 🚦 Development

### Local Development

Since this is a static website, simply open files in a browser:

```bash
# Direct browser
open index.html

# Or use any static server
python -m http.server 8000
# Visit http://localhost:8000
```

### Making Changes

1. Follow the design patterns in `STYLE_GUIDE.md`
2. Use existing Tailwind classes and custom components
3. Test on mobile devices (mobile-first approach)
4. Ensure all animations use the established patterns

### Git Workflow

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Your change description"

# Push to GitHub
git push origin main
```

Changes are automatically deployed via GitHub Pages.

## 📝 Content Guidelines

### Brand Voice
- **Tone**: Professional yet approachable
- **Audience**: Game developers (studios, indies, modders)
- **Focus**: Technical capabilities without jargon

### SEO Optimization
- All pages include meta descriptions and Open Graph tags
- Structured data for better search visibility
- Sitemap.xml for search engine discovery

## ⚖️ Legal

### Trademarks
- Tryll Engine is a trademark of Tryll Engine, Inc.
- Deep Rock Galactic and Bosco are trademarks of Ghost Ship Games ApS
- BoscoTryll is an unofficial mod not affiliated with Ghost Ship Games

### License
© 2025 Tryll Engine, Inc. All rights reserved.

## 🤝 Contributing

This is the official Tryll Engine website. For questions or suggestions:
- Join our [Discord](https://discord.gg/XCBBGUMzUM)
- Email: Contact through the website form

## 🔗 Links

- **Website**: [tryllengine.com](https://tryllengine.com)
- **Discord**: [Join Community](https://discord.gg/XCBBGUMzUM)
- **BoscoTryll Mod**: [View Showcase](https://tryllengine.com/boscotryll.html)

---

Built with ❤️ by the Tryll Engine team