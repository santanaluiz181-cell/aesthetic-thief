"""Layer-based aesthetic mixer that composes distinct styles by architectural layer."""

import argparse
import json
import os

PRESETS = {
    "antigravity": {
        "label": "Antigravity Onyx",
        "surface": {"bg": "#0B0D10", "panel": "#13171D", "text": "#F2F4F8", "border": "#262C36"},
        "structure": {"maxWidth": "1160px", "gridGap": "1.5rem", "rhythm": "tight-modular"},
        "accent": {"color": "#7CE0C3", "style": "sharp-telemetry"},
        "micro": {"radius": "4px", "font": "'Google Sans', 'IBM Plex Sans', sans-serif", "badge": "1px solid #262C36"},
    },
    "claude-editorial": {
        "label": "Claude Editorial",
        "surface": {"bg": "#FAF9F5", "panel": "#F2EFE8", "text": "#1C1B18", "border": "#DFD9CC"},
        "structure": {"maxWidth": "1040px", "gridGap": "2.25rem", "rhythm": "editorial-generous"},
        "accent": {"color": "#C96442", "style": "warm-terracotta"},
        "micro": {"radius": "6px", "font": "'Newsreader', Georgia, serif", "badge": "1px solid #DFD9CC"},
    },
    "handmade-ink": {
        "label": "Handmade Ink & Paper",
        "surface": {"bg": "#F2EBDD", "panel": "#EDE4D1", "text": "#292821", "border": "#D8CBB3"},
        "structure": {"maxWidth": "1080px", "gridGap": "2rem", "rhythm": "notebook-margin"},
        "accent": {"color": "#A64B3C", "style": "hand-drawn-svg-strike"},
        "micro": {"radius": "0px", "font": "'Caveat', cursive", "badge": "1.5px dashed #A64B3C"},
    },
    "cli-pixel": {
        "label": "CLI Pixel Terminal",
        "surface": {"bg": "#0D100E", "panel": "#141A16", "text": "#E4EFE7", "border": "#2F3D33"},
        "structure": {"maxWidth": "1120px", "gridGap": "1.25rem", "rhythm": "grid-strict"},
        "accent": {"color": "#7CE08A", "style": "terminal-prompt"},
        "micro": {"radius": "0px", "font": "'VT323', 'IBM Plex Mono', monospace", "badge": "1px solid currentColor"},
    },
}


def load_source(spec: str) -> dict:
    """Resolve a preset name or a path to an extracted tokens.json file."""
    if spec in PRESETS:
        return PRESETS[spec]
    if os.path.isfile(spec):
        with open(spec, "r", encoding="utf-8") as f:
            data = json.load(f)
        body = data.get("body") or {}
        h1 = data.get("h1") or {}
        colors = data.get("topColors") or []
        radii = data.get("topRadii") or ["0px"]
        return {
            "label": data.get("title") or data.get("slug") or spec,
            "surface": {
                "bg": body.get("backgroundColor") or (colors[0] if colors else "#0B0D10"),
                "panel": colors[1] if len(colors) > 1 else "#161A20",
                "text": body.get("color") or "#F2F4F8",
                "border": colors[2] if len(colors) > 2 else "#2B313B",
            },
            "structure": {"maxWidth": "1120px", "gridGap": "1.75rem", "rhythm": "extracted-layout"},
            "accent": {"color": colors[-1] if colors else "#A64B3C", "style": "extracted-accent"},
            "micro": {
                "radius": radii[0],
                "font": h1.get("fontFamily") or body.get("fontFamily") or "monospace",
                "badge": f"1px solid {colors[2] if len(colors) > 2 else '#2B313B'}",
            },
        }
    raise ValueError(f"Unknown preset or missing tokens file: {spec}")


def blend_layers(structure_src: str, surface_src: str, accent_src: str, micro_src: str) -> dict:
    """Compose a unified non-Frankenstein spec by assigning each source to one layer."""
    s_struct = load_source(structure_src)
    s_surf = load_source(surface_src)
    s_acc = load_source(accent_src)
    s_mic = load_source(micro_src)

    return {
        "sources": {
            "structure": s_struct["label"],
            "surface": s_surf["label"],
            "accent": s_acc["label"],
            "micro": s_mic["label"],
        },
        "layers": {
            "structure": s_struct["structure"],
            "surface": s_surf["surface"],
            "accent": s_acc["accent"],
            "micro": s_mic["micro"],
        },
    }


def render_markdown(spec: dict) -> str:
    """Format the layered spec into a canonical DESIGN_SPEC.md document."""
    src = spec["sources"]
    lay = spec["layers"]
    return "\n".join([
        "# DESIGN_SPEC (Layered Aesthetic Mix)",
        "",
        "## Layer Assignment (25% / 25% / 25% / 25%)",
        f"- **Structure & Rhythm:** `{src['structure']}` (`maxWidth: {lay['structure']['maxWidth']}`, `gap: {lay['structure']['gridGap']}`)",
        f"- **Surface & Palette:** `{src['surface']}` (`bg: {lay['surface']['bg']}`, `panel: {lay['surface']['panel']}`, `text: {lay['surface']['text']}`)",
        f"- **Accent & Irregular Craft:** `{src['accent']}` (`accent: {lay['accent']['color']}`, `style: {lay['accent']['style']}`)",
        f"- **Micro-Components & CLI:** `{src['micro']}` (`radius: {lay['micro']['radius']}`, `font: {lay['micro']['font']}`)",
        "",
        "## Anti-Frankenstein Rule",
        "Each architectural layer owns its tokens exclusively. Do not mix radii or background palettes inside the same component.",
        "",
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description="Blend multiple aesthetics by architectural layer.")
    parser.add_argument("--structure", default="claude-editorial", help="Preset or tokens.json for layout rhythm.")
    parser.add_argument("--surface", default="antigravity", help="Preset or tokens.json for background/surface.")
    parser.add_argument("--accent", default="handmade-ink", help="Preset or tokens.json for irregular/accent craft.")
    parser.add_argument("--micro", default="cli-pixel", help="Preset or tokens.json for badges/CLI/pixel details.")
    parser.add_argument("--out", default="DESIGN_SPEC.md", help="Output markdown path.")
    args = parser.parse_args()

    spec = blend_layers(args.structure, args.surface, args.accent, args.micro)
    md = render_markdown(spec)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Wrote layered spec to {args.out}")


if __name__ == "__main__":
    main()
