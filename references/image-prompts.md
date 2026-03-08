# Hero Image Style Guide

## Core style

All Tryll Engine blog hero images follow a consistent editorial illustration style:

- **Format**: Square, 1:1 ratio
- **Background**: Deep navy blue with subtle paper grain texture
- **Elements**: 1-2 simple geometric shapes (no complex illustrations)
- **Colors**: Bright sky blue (#60A5FA), soft violet (#A78BFA), warm teal (#2DD4BF), warm amber-gold (#FBBF24)
- **Composition**: Sparse, centered or slightly off-center, lots of negative space
- **Finish**: Matte, no glow, no shine, no reflections
- **Aesthetic**: Modern graphic design poster

## Prompt template

```
Minimal flat editorial illustration, square format 1:1 ratio. Deep navy blue background with subtle paper grain texture. [DESCRIBE 1-2 GEOMETRIC ELEMENTS AND THEIR COLORS]. Sparse composition, lots of negative space. Matte finish, no glow, no shine, no reflections. Modern graphic design poster aesthetic.
```

## Reference prompts from existing posts

### Security/Engineering post (stripes.png)
```
Minimal flat editorial illustration, square format 1:1 ratio. Deep navy blue background with subtle paper grain texture. Three horizontal bands at slight angles, layered like filter stages, in bright sky blue, soft violet, and warm teal. Small abstract dots scattered between layers. Sparse composition, lots of negative space. Matte finish, no glow, no shine, no reflections. Modern graphic design poster aesthetic.
```

### Gaming/Product post (joysticj.png)
```
Minimal flat editorial illustration, square format 1:1 ratio. Deep navy blue background with subtle paper grain texture. A simple geometric game controller shape made of overlapping translucent rectangles in bright sky blue and soft violet. Sparse composition, lots of negative space. Matte finish, no glow, no shine, no reflections. Modern graphic design poster aesthetic.
```

### Award/Grant post (polygon.png)
```
Minimal flat editorial illustration, square format 1:1 ratio. Deep navy blue background with subtle paper grain texture. A single abstract hexagon shape with a subtle inner triangle, in warm amber-gold and bright sky blue. Sparse composition, centered, lots of negative space. Matte finish, no glow, no shine, no reflections. Modern graphic design poster aesthetic.
```

### Advisor/People post (circles.png)
```
Minimal flat editorial illustration, square format 1:1 ratio. Deep navy blue background with subtle paper grain texture. Two simple abstract semicircle shapes overlapping at the center like a Venn diagram, in bright sky blue and soft violet. Sparse composition, lots of negative space. Matte finish, no glow, no shine, no reflections. Modern graphic design poster aesthetic.
```

## Topic to geometric element mapping

Use these as inspiration when creating new prompts:

| Topic | Suggested geometric elements |
|-------|------------------------------|
| Team/people announcements | Overlapping circles, connected nodes |
| Technical/engineering | Layered bands, grid patterns, angular shapes |
| Product launches | Controller shapes, screen/window rectangles |
| Awards/milestones | Hexagons, stars, trophy-like triangles |
| Partnerships | Interlocking shapes, Venn diagrams |
| Updates/versions | Arrows, stacked layers, progression shapes |
| Hardware/GPU | Chip-like rectangles, circuit patterns |
| AI/models | Neural-net-like connected dots, concentric shapes |

## DALL-E 3 specifics

When generating with DALL-E 3:
- Model: `dall-e-3`
- Size: `1024x1024`
- Quality: `standard` (hd not needed for this minimal style)
- The prompt works well as-is — DALL-E 3 handles this editorial style reliably
