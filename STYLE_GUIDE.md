# Tryll Engine Style Guide

This guide outlines the visual design system and coding patterns for creating new pages that match the existing Tryll Engine website style.

## Core Design Principles

1. **Dark Theme Only** - The site uses a pure black background with light text
2. **Glass Morphism** - Translucent cards with backdrop blur effects
3. **Subtle Animations** - Fade-in effects and smooth transitions
4. **Mobile-First Responsive** - All components must work on mobile devices

## Color Palette

### Primary Colors
- **Brand Primary**: `#232E41` (dark blue-gray) - Used for accents and highlights
- **Primary Blue**: `#3B82F6` (Tailwind blue-500) - Used for buttons and CTAs
- **Primary Hover**: `#2563EB` (Tailwind blue-600) - Button hover states

### Secondary Colors  
- **Secondary**: `#F6F0EB` (light cream) - Used for body text
- **White**: `rgba(255, 255, 255, 0.9)` - Primary headings
- **White/80**: `rgba(255, 255, 255, 0.75)` - Subheadings
- **White/60**: `rgba(255, 255, 255, 0.6)` - Secondary text

### Background Colors
- **Page Background**: `#000000` (pure black)
- **Dark Shades**:
  - `dark-900`: `#0a0d12`
  - `dark-800`: `#0f1419`
  - `dark-700`: `#141a20`

## Typography

### Font Families
- **Primary Font**: Inter (with system font fallbacks)
  ```css
  font-family: 'Inter', BlinkMacSystemFont, -apple-system, 'SF Pro Display', sans-serif;
  ```
- **Monospace Font**: JetBrains Mono (for code/technical content)
  ```css
  font-family: 'JetBrains Mono', monospace;
  ```

### Heading Styles
- **H1**: `text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold heading-primary`
- **H2**: `text-3xl sm:text-4xl md:text-5xl font-bold heading-primary`
- **H3**: `text-xl md:text-2xl font-bold`

### Text Classes
- **Body Large**: `text-lg md:text-xl text-secondary leading-relaxed`
- **Body Regular**: `text-base text-secondary`
- **Small Text**: `text-sm text-secondary`

## Component Patterns

### Glass Cards
```html
<div class="glass-card p-6 md:p-8">
  <!-- Content -->
</div>
```
Glass card CSS:
```css
background: rgba(35, 46, 65, 0.08);
border: 1px solid rgba(35, 46, 65, 0.15);
border-radius: 12px;
backdrop-filter: blur(10px);
```

### Primary Button
```html
<button class="btn-primary px-6 py-3 rounded-lg text-base inline-flex items-center justify-center">
  Button Text
</button>
```

### Feature Cards
```html
<div class="feature-card p-6 rounded-xl">
  <!-- Content -->
</div>
```
Feature card CSS:
```css
background: rgba(35, 46, 65, 0.06);
border: 1px solid rgba(35, 46, 65, 0.12);
backdrop-filter: blur(20px);
```

## Layout Structure

### Standard Page Template
```html
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <!-- Meta tags, favicon, Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#232E41',
                        secondary: '#F6F0EB',
                        // ... other colors
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-black text-white">
    <!-- Navigation (fixed) -->
    <nav class="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-black/70">
        <!-- Nav content -->
    </nav>
    
    <!-- Main Content -->
    <main>
        <!-- Hero Section -->
        <section class="relative min-h-screen flex items-center justify-center">
            <!-- Background effects -->
            <div class="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent"></div>
            <!-- Content -->
        </section>
        
        <!-- Additional Sections -->
    </main>
    
    <!-- Footer -->
    <footer class="border-t border-white/10 py-12">
        <!-- Footer content -->
    </footer>
</body>
</html>
```

## Animations

### Fade-in Effect
Add `fade-in` class to elements:
```html
<div class="fade-in">
  <!-- Content appears on scroll -->
</div>
```

### Hover Effects
- Buttons: `hover:bg-primary-600 transition-all duration-300`
- Links: `hover:text-white transition-colors duration-200`
- Cards: Add subtle transform on hover

## Responsive Breakpoints

Use Tailwind's responsive prefixes:
- `sm:` - 640px and up
- `md:` - 768px and up  
- `lg:` - 1024px and up
- `xl:` - 1280px and up

## Background Effects

### Gradient Overlays
```html
<div class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
```

### Grid Pattern (CSS)
```css
background-image: 
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(59, 130, 246, 0.15), transparent),
    radial-gradient(circle at 1px 1px, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
background-size: 100% 100%, 50px 50px;
```

## Best Practices

1. **Always use semantic HTML** - Use appropriate heading levels and ARIA labels
2. **Mobile-first development** - Design for mobile, then enhance for desktop
3. **Consistent spacing** - Use Tailwind's spacing scale (p-4, p-6, p-8, etc.)
4. **Accessibility** - Ensure sufficient color contrast and keyboard navigation
5. **Performance** - Lazy load images and minimize JavaScript
6. **SEO** - Include proper meta tags and structured data

## Common Utility Classes

### Spacing
- Sections: `py-16 md:py-24`
- Containers: `max-w-7xl mx-auto px-4 md:px-8`
- Cards: `p-6 md:p-8`

### Text Alignment
- Center: `text-center`
- Left (default): `text-left`

### Flexbox Utilities
- Center content: `flex items-center justify-center`
- Space between: `flex items-center justify-between`
- Column on mobile: `flex flex-col md:flex-row`

### Grid Layouts
- Feature grid: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6`
- Two column: `grid grid-cols-1 lg:grid-cols-2 gap-8`

## Icon Usage

Use Font Awesome icons (loaded via CDN):
```html
<i class="fas fa-rocket text-primary-500"></i>
```

Common icons:
- `fa-rocket` - Innovation/launch
- `fa-brain` - AI/intelligence  
- `fa-gamepad` - Gaming
- `fa-check` - Success/features
- `fa-shield-alt` - Security/privacy

## Form Styling

```html
<input type="text" 
       class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 
              text-white placeholder-white/40 focus:outline-none focus:border-primary-500 
              transition-colors duration-200">
              
<textarea class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 
                 text-white placeholder-white/40 focus:outline-none focus:border-primary-500 
                 transition-colors duration-200 resize-none">
</textarea>
```

## Example Section

```html
<section class="py-16 md:py-24 relative overflow-hidden">
    <div class="max-w-7xl mx-auto px-4 md:px-8">
        <div class="text-center mb-12 md:mb-16 fade-in">
            <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4 md:mb-6 heading-primary">
                Section Title
            </h2>
            <p class="text-lg md:text-xl text-secondary max-w-3xl mx-auto leading-relaxed">
                Section description text goes here
            </p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
            <!-- Card items -->
            <div class="glass-card p-6 md:p-8 fade-in">
                <div class="text-primary-500 mb-4">
                    <i class="fas fa-rocket text-3xl"></i>
                </div>
                <h3 class="text-xl font-bold text-white mb-3">Card Title</h3>
                <p class="text-secondary">Card description text</p>
            </div>
        </div>
    </div>
</section>
```

This style guide ensures consistency across all Tryll Engine pages while maintaining the established dark, modern gaming aesthetic.