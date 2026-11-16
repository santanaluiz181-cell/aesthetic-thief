---
name: aesthetic-thief
description: Captures real web aesthetics via Playwright/CDP (screenshots, motion curves, computed CSS tokens) and remixes multiple styles by architectural layer into a new non-Frankenstein repository using human-craft-frontend and antislop.
---

# Aesthetic Thief (REA + Human-Craft-Frontend)

Combines headless browser reverse-engineering with layered aesthetic composition. Never blindly copy HTML or interpolate conflicting styles on the same element.

## Mandatory 4-Step Workflow

### Step 1: Target Hunt & Capture (STOP AND SHOW)
1. Locate 1 to 4 target URLs (user-supplied or searched by vibe).
2. Run the local extractor to capture desktop (`1440x900`) and mobile (`375x812`) screenshots, computed styles, palette frequencies, font stacks, and `document.getAnimations()` motion data:
   ```bash
   python tools/extract_aesthetic.py <url1> [<url2> ...] --out ./captured
   ```
3. **Show the screenshots and `AESTHETIC_REPORT.md` to the user** before remixing or writing UI code.

### Step 2: Layer-Based Aesthetic Mixing (Anti-Frankenstein)
Never average conflicting properties (e.g. `0px` CLI corners + `9999px` pill corners) on the same component. Assign each aesthetic to a dedicated **architectural layer**:
1. **Structure & Rhythm:** Grid proportions, max-width, whitespace cadence.
2. **Surface & Palette:** Primary background, ink/text contrast, accent color.
3. **Typography & Voice:** Display serif/sans + body font + mono/handwritten margin accents.
4. **Micro-Components & Borders:** Radius, stroke style, CLI/pixel badges, or hand-drawn SVG dividers.
5. **Motion & Tactility:** Easing curves, draw-on SVG strokes, or snappy terminal transitions.

Run the blender to generate a canonical `DESIGN_SPEC.md`:
```bash
python tools/blend_layers.py --structure claude-editorial --surface antigravity --accent handmade-ink --micro cli-pixel --out DESIGN_SPEC.md
```
Or pass extracted `--tokens ./captured/<site>/tokens.json` to map real captured tokens into any layer.

### Step 3: Gate 3 Hand Sketch / Map (STOP AND CONFIRM)
Present the layered `DESIGN_SPEC.md` + a bespoke ASCII layout map to the user. Wait for `"OK"` or adjustments before scaffolding the new repository.

### Step 4: Build & Anti-Slop Verification
1. Generate the new repository respecting `DESIGN_SPEC.md` and `antislop` rules (WCAG AA contrast, zero dead buttons, zero em-dashes, zero horizontal overflow).
2. Verify in headless browser (`1440px` and `375px`) with zero console errors before publishing.
