"""Playwright-based aesthetic extractor for capturing screenshots, computed CSS tokens, and animations."""

import argparse
import json
import os
import re
from collections import Counter
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

EXTRACTION_JS = """() => {
  const pick = (el) => {
    if (!el) return null;
    const cs = getComputedStyle(el);
    return {
      tag: el.tagName.toLowerCase(),
      color: cs.color,
      backgroundColor: cs.backgroundColor,
      fontFamily: cs.fontFamily,
      fontSize: cs.fontSize,
      fontWeight: cs.fontWeight,
      lineHeight: cs.lineHeight,
      borderRadius: cs.borderRadius,
      border: cs.border,
      boxShadow: cs.boxShadow,
      padding: cs.padding
    };
  };

  const sampleColors = [];
  const sampleFonts = [];
  const sampleRadii = [];

  const nodes = Array.from(document.querySelectorAll("body, header, nav, main, section, h1, h2, h3, p, a, button, article, code, pre"));
  for (const node of nodes.slice(0, 120)) {
    const cs = getComputedStyle(node);
    if (cs.backgroundColor && cs.backgroundColor !== "rgba(0, 0, 0, 0)") sampleColors.push(cs.backgroundColor);
    if (cs.color) sampleColors.push(cs.color);
    if (cs.fontFamily) sampleFonts.push(cs.fontFamily);
    if (cs.borderRadius && cs.borderRadius !== "0px") sampleRadii.push(cs.borderRadius);
  }

  const cssVars = {};
  for (const sheet of Array.from(document.styleSheets)) {
    try {
      for (const rule of Array.from(sheet.cssRules || [])) {
        if (rule.style) {
          for (const prop of Array.from(rule.style)) {
            if (prop.startsWith("--")) {
              cssVars[prop] = rule.style.getPropertyValue(prop).trim();
            }
          }
        }
      }
    } catch (_e) {
      // Cross-origin stylesheet skipped intentionally
    }
  }

  const animations = document.getAnimations().slice(0, 30).map((anim) => {
    const timing = anim.effect && anim.effect.getTiming ? anim.effect.getTiming() : {};
    return {
      id: anim.id || null,
      playState: anim.playState,
      duration: timing.duration ?? null,
      easing: timing.easing ?? null,
      iterations: timing.iterations ?? null
    };
  });

  return {
    title: document.title,
    url: window.location.href,
    body: pick(document.body),
    h1: pick(document.querySelector("h1")),
    button: pick(document.querySelector("button, a.btn, [role='button']")),
    colors: sampleColors,
    fonts: sampleFonts,
    radii: sampleRadii,
    cssVars,
    animations
  };
}"""


def slugify_url(url: str) -> str:
    """Convert a URL into a filesystem-safe directory slug."""
    parsed = urlparse(url)
    raw = f"{parsed.netloc}{parsed.path}".strip("/") or "local_target"
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", raw)[:64]


def launch_browser(playwright_instance):
    """Launch headless Chromium, preferring system Edge on Windows when available."""
    try:
        return playwright_instance.chromium.launch(headless=True, channel="msedge")
    except Exception:
        return playwright_instance.chromium.launch(headless=True)


def summarize_tokens(raw: dict) -> dict:
    """Aggregate frequency counts for colors, fonts, and border radii."""
    return {
        "title": raw.get("title", ""),
        "url": raw.get("url", ""),
        "body": raw.get("body"),
        "h1": raw.get("h1"),
        "button": raw.get("button"),
        "topColors": [c for c, _ in Counter(raw.get("colors", [])).most_common(8)],
        "topFonts": [f for f, _ in Counter(raw.get("fonts", [])).most_common(4)],
        "topRadii": [r for r, _ in Counter(raw.get("radii", [])).most_common(4)],
        "cssVars": raw.get("cssVars", {}),
        "animations": raw.get("animations", []),
    }


def extract_urls(urls: list[str], out_dir: str) -> list[dict]:
    """Capture desktop/mobile screenshots and computed CSS tokens for each target URL."""
    if not urls:
        raise ValueError("At least one target URL is required.")

    os.makedirs(out_dir, exist_ok=True)
    results = []

    with sync_playwright() as p:
        browser = launch_browser(p)
        try:
            for url in urls:
                slug = slugify_url(url)
                target_dir = os.path.join(out_dir, slug)
                os.makedirs(target_dir, exist_ok=True)

                desktop = browser.new_page(viewport={"width": 1440, "height": 900})
                desktop.goto(url, wait_until="networkidle", timeout=30000)
                desktop.screenshot(path=os.path.join(target_dir, "desktop.png"), full_page=False)
                raw = desktop.evaluate(EXTRACTION_JS)
                desktop.close()

                mobile = browser.new_page(viewport={"width": 375, "height": 812}, has_touch=True)
                mobile.goto(url, wait_until="networkidle", timeout=30000)
                mobile.screenshot(path=os.path.join(target_dir, "mobile.png"), full_page=False)
                mobile.close()

                summary = summarize_tokens(raw)
                summary["slug"] = slug
                summary["screenshots"] = {
                    "desktop": os.path.join(target_dir, "desktop.png"),
                    "mobile": os.path.join(target_dir, "mobile.png"),
                }

                with open(os.path.join(target_dir, "tokens.json"), "w", encoding="utf-8") as f:
                    json.dump(summary, f, indent=2, ensure_ascii=False)

                results.append(summary)
        finally:
            browser.close()

    report_path = os.path.join(out_dir, "AESTHETIC_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Aesthetic Extraction Report\n\n")
        for item in results:
            f.write(f"## {item['title'] or item['slug']}\n")
            f.write(f"- URL: `{item['url']}`\n")
            f.write(f"- Top Colors: `{', '.join(item['topColors'][:5])}`\n")
            f.write(f"- Top Fonts: `{', '.join(item['topFonts'][:3])}`\n")
            f.write(f"- Top Radii: `{', '.join(item['topRadii'][:3]) or '0px'}`\n")
            f.write(f"- Animations Captured: `{len(item['animations'])}`\n\n")

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture screenshots and computed CSS tokens from URLs.")
    parser.add_argument("urls", nargs="+", help="One or more URLs to inspect.")
    parser.add_argument("--out", default="./captured", help="Output directory for screenshots and tokens.")
    args = parser.parse_args()
    extracted = extract_urls(args.urls, args.out)
    print(f"Captured {len(extracted)} target(s) into {args.out}")


if __name__ == "__main__":
    main()
