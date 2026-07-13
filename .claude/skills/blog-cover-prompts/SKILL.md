---
name: blog-cover-prompts
description: Generate DALL-E prompts for Tryll Engine blog cover images. Use this skill whenever the user asks for a blog cover prompt, wants image ideas for a new post, needs prompts for DALL-E / Midjourney / Nano Banana, or asks for "the picture for this post." Also trigger when the user pastes blog/LinkedIn post text and says "give me the prompt" or "several prompts." Produces multiple diverse, concrete, recognizable options per post — never pure abstract geometric shapes.
---

# Blog Cover Prompts

Generate multiple varied DALL-E prompts for Tryll Engine blog cover images. Every prompt uses the same visual baseline (style, palette, format) but varies the **central object/metaphor** to fit the post's topic. Output must be **concrete and recognizable at a glance** — never abstract-shapes-only ("hexagons offset" was the anti-pattern that got rejected as "круче Кандинского").

## When to use

Trigger this skill when the user:
- Pastes post text and asks for a cover prompt / picture / obloszka
- Says "дай промпт", "give me the prompt", "пару разных", "варианты для картинки"
- Is writing a new blog post and hasn't specified imagery yet
- Wants to regenerate a rejected cover

## Style baseline (fixed across ALL prompts)

Always include these exact fragments — they lock the visual consistency of the blog series:

```
Editorial magazine illustration, square 1:1 ratio.
Deep navy blue background with subtle paper grain texture.
Semi-flat vector illustration style, clean outlines with light tonal shading.
Sparse composition, centered, lots of negative space.
Modern editorial poster aesthetic, reads instantly.
```

**Palette (pick 1–2 per prompt, never all four):**
- `warm amber-gold` — for milestones, momentum, human warmth
- `bright sky blue` — Tryll brand color, dominant option
- `soft violet` — for people, relationships, human/AI interaction
- `teal` — for contrast accent (use sparingly)

**Always avoid** (these break the series or DALL-E chokes on them):
- Text or labels on the illustration (DALL-E garbles typography)
- Photorealism, 3D renders, glossy surfaces
- More than 4 elements in the composition
- Human faces
- Words like "abstract", "geometric shapes", "minimal shapes" as the SOLE description — leads to Kandinsky-tier ambiguity
- Colors outside the palette (no red, no green, no yellow-yellow — amber-gold is fine)

## How to generate prompts for a post

### Step 1 — Extract 2–4 metaphors from the post text

Read the post and identify what the post is fundamentally about. Then draft 2–4 **different metaphor angles**, so the user has real choice. Never repeat the SAME metaphor already used in previous posts (check `assets/blog/*-cover.png` history in the project or `blog/posts.json`).

Typical metaphor axes:
| Post type | Recognizable icons that read instantly |
|-----------|--------------------------------------|
| Launch / alpha / milestone | rocket, hexagon+arrow, flag, upward staircase, sprouting shape |
| Funding / investment | seed, plant/sprout, tree, coin stack, upward arrow with base |
| Press / media coverage | radiating rings, newspaper stack, megaphone, quotation marks, spotlight cone |
| Partnership / advisor / hire | Venn overlap, handshake outline, two puzzle pieces, two chairs facing |
| Comparison / rival tech | two chips side-by-side, two arenas, two flags planted, split screen |
| Technical deep-dive | iceberg cross-section, layered stack (building floors), open cutaway of a box, wireframe cube |
| Missing pieces / gaps in a system | pipeline with a broken/dashed box, half-built stack, puzzle with hole |
| Detection / catching a lie / investigation | magnifying glass, keyhole, thread being pulled, contradiction (crossed lines) |
| Off-switch / kill / termination | power symbol, unplugged cord, switch, cliff edge |
| AI / on-device | brain outline, chip, small mesh network, GPU silhouette |
| Voice / TTS / chat | microphone, waveform, speaker, speech bubble |
| Roadmap / release | milestone markers on a line, checkpoints, ladder |

### Step 2 — Build each prompt with the fill-in template

```
Editorial magazine illustration, square 1:1 ratio.
Deep navy blue background with subtle paper grain texture.
[ONE OR TWO SENTENCES describing the concrete object(s), their positions, and colors from the palette. Include enough visual detail to make the object unambiguous — e.g. "a stylized microprocessor chip shown from above with visible pins along the edges", not just "a chip."]
Semi-flat vector illustration style, clean outlines with light tonal shading.
Sparse composition, centered, lots of negative space.
Modern editorial poster aesthetic, reads instantly.
```

The `[…]` slot is the ONLY variable part per prompt. Everything else is copy-paste.

### Step 3 — Present 3–4 variants to the user

Format:

> **Вариант A — [short metaphor name]** (one-line rationale linking metaphor to post's thesis)
> ```
> [full prompt]
> ```

Add a one-line recommendation at the end pointing to your favorite and why.

## Concrete iconography — how to describe objects unambiguously

DALL-E treats short descriptions as room for interpretation and often fails. Give it enough detail to lock the shape.

Bad → Good rewrites:

| Bad (too abstract) | Good (concrete, readable) |
|---|---|
| "an abstract hexagon" | "a stylized hexagon shape with a thin inner outline echoing the perimeter" |
| "a chip" | "a stylized computer microchip shown from above with visible pins along four edges and a small square die in the center" |
| "an iceberg" | "an iceberg shown in cross-section: a small pointed peak above a wavy horizontal water line, and a much larger jagged mass below the waterline" |
| "a microphone" | "a small stylized studio microphone with a rounded capsule head and thin stem" |
| "some rings" | "three concentric circular outlines radiating outward from a single small solid dot at the center" |
| "a pipeline" | "a horizontal row of small icons connected by thin arrow lines from left to right" |
| "a stack" | "four horizontal slab shapes of equal width arranged like architectural floors of a small building, with thin visible gaps between them" |

Rule of thumb: if you can imagine 5 different objects matching your description, add more detail until only 1 fits.

## Example — full 4-variant output for a real post

Post topic: "We attended an NVIDIA webinar about their on-device AI. Nice demos, but they showed a shallow pipeline. Real production needs RAG, guardrails, tool-calling, evals."

**Вариант A — Два чипа рядом** (Tryll и NVIDIA в одном поле, разные подходы)
```
Editorial magazine illustration, square 1:1 ratio. Deep navy blue background with subtle paper grain texture. Two stylized computer microchips shown from above, side by side with a small gap between them, both clearly recognizable as microprocessors with visible pins along the edges and a small square die in the center. One chip filled in warm amber-gold, the other in bright sky blue. Semi-flat vector illustration style, clean outlines with light tonal shading. Sparse composition, centered horizontally, lots of negative space. Modern editorial poster aesthetic, reads instantly.
```

**Вариант B — Айсберг в разрезе** (демо на поверхности, продакшн под водой)
```
Editorial magazine illustration, square 1:1 ratio. Deep navy blue background with subtle paper grain texture. A stylized iceberg shown in cross-section: a small pointed peak above a clearly drawn wavy horizontal water line in the upper third of the composition, and a much larger jagged mass extending below the waterline toward the bottom. The tip above water in warm amber-gold, the submerged mass in bright sky blue with soft depth shading. A few small hidden dots inside the submerged mass hint at complexity beneath the surface. Semi-flat vector illustration style, clean outlines. Sparse composition, centered vertically. Modern editorial poster aesthetic, reads instantly.
```

**Вариант C — NPC-pipeline с пропуском** (в демо не было того, что нужно в проде)
```
Editorial magazine illustration, square 1:1 ratio. Deep navy blue background with subtle paper grain texture. A horizontal row of four icons connected by thin arrow lines from left to right: a small stylized microphone, a small microchip shape, then an empty dashed-outline square where a fourth icon should be but is missing, and finally a small speaker icon on the right. The three drawn icons in bright sky blue, the empty missing-piece outlined in warm amber-gold. Semi-flat vector illustration, clean thin linework. Sparse composition, horizontally centered, lots of negative space above and below. Modern editorial poster aesthetic, reads instantly.
```

**Вариант D — Стек как здание** (глубокий стек Tryll: RAG, guardrails, evals)
```
Editorial magazine illustration, square 1:1 ratio. Deep navy blue background with subtle paper grain texture. A vertical stack of four horizontal slab shapes of equal width arranged like architectural floors of a small building, with thin visible gaps between them. Each slab has a subtle inner pattern: the top slab shows small sound-wave lines, the second small circuit dots, the third a tiny grid pattern, the fourth a small shield curve. Slabs alternate between bright sky blue and warm amber-gold. Semi-flat vector illustration style, clean outlines with light shading suggesting depth. Sparse composition, centered vertically. Modern editorial poster aesthetic, reads instantly.
```

**Рекомендация — Вариант B (айсберг)**. Максимально бьёт по тезису "media showcase vs production-ready", читается моментально даже в маленькой карточке.

## Common mistakes checklist (self-review before delivering)

- [ ] Did I use ONLY the fixed palette (amber-gold / sky blue / violet / teal)?
- [ ] Did every variant name a **concrete object** (chip, iceberg, microphone…), not just geometry?
- [ ] Are objects described in enough detail that only 1 shape fits?
- [ ] Did I include ALL five style-baseline fragments in each prompt?
- [ ] Are variants **actually different metaphors**, or three renamings of the same idea?
- [ ] Zero mentions of text/labels/typography in the illustration?
- [ ] 2–4 elements max per composition?
- [ ] Recommended a favorite at the end with one-line rationale?

## After the user picks a variant

- If they generate via DALL-E manually (no `.env` API key in the project): they'll paste the image path back. Process it into `assets/blog/{slug}-cover.png` at 512×512 via Pillow.
- If a `scripts/generate_hero_image.py` exists and `.env` has an API key, offer to run it directly with the chosen prompt.
- Never generate the cover image before the user confirms which variant to use.
