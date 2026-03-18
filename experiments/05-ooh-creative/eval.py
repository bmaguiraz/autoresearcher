# -*- coding: utf-8 -*-
"""OOH Creative Scorer — implements the OOH Canvas rubric.

Scores a creative config against 7 categories (100 points total):
  1. visual-hierarchy      (20 pts)
  2. color-contrast        (15 pts)
  3. brand-integration     (10 pts)
  4. message-effectiveness (20 pts)
  5. format-optimization   (10 pts)
  6. industry-practices    (15 pts)
  7. regulatory-compliance (10 pts)

Tier thresholds:
  90-100: launch-ready
  80-89:  minor-revisions
  65-79:  significant-revisions
  50-64:  major-rework
  0-49:   do-not-launch

Uses programmatic checks (word count, WCAG contrast, required info) plus
LLM-as-judge (Claude Haiku) for subjective criteria.

DO NOT MODIFY this file — it is the frozen evaluation harness.
"""

import json
import math
import os
import pathlib
import re
import time

import anthropic

# ---------------------------------------------------------------------------
# Format specifications
# ---------------------------------------------------------------------------

FORMAT_SPECS = {
    "bulletin": {"max_words": 7, "aspect_ratio": "3.4:1", "width": 1400, "height": 412},
    "poster": {"max_words": 7, "aspect_ratio": "2:1", "width": 1200, "height": 600},
    "digital-landscape": {"max_words": 10, "aspect_ratio": "16:9", "width": 1920, "height": 1080},
    "transit-shelter": {"max_words": 10, "aspect_ratio": "2:3", "width": 800, "height": 1200},
}

# ---------------------------------------------------------------------------
# Color utilities — WCAG 2.1 contrast ratio
# ---------------------------------------------------------------------------


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert #RRGGBB to (R, G, B) ints."""
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def relative_luminance(r: int, g: int, b: int) -> float:
    """WCAG 2.1 relative luminance from sRGB values 0-255."""

    def linearize(c: int) -> float:
        s = c / 255.0
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4

    rl, gl, bl = linearize(r), linearize(g), linearize(b)
    return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl


def contrast_ratio(hex1: str, hex2: str) -> float:
    """WCAG contrast ratio between two hex colors."""
    l1 = relative_luminance(*hex_to_rgb(hex1))
    l2 = relative_luminance(*hex_to_rgb(hex2))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def color_distance(hex1: str, hex2: str) -> float:
    """Euclidean distance in RGB space (0-441.67)."""
    r1, g1, b1 = hex_to_rgb(hex1)
    r2, g2, b2 = hex_to_rgb(hex2)
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------


def word_count(text: str) -> int:
    """Count words in a string."""
    return len(text.split())


def total_copy_words(headline: str, subheadline: str, cta: str) -> int:
    """Total word count across all copy elements."""
    return word_count(headline) + word_count(subheadline) + word_count(cta)


# ---------------------------------------------------------------------------
# Load brand config
# ---------------------------------------------------------------------------

CONFIG_DIR = pathlib.Path(__file__).parent / "config"


def load_brand_config(use_case: str) -> dict:
    """Load the brand config JSON for the given use case."""
    path = CONFIG_DIR / f"{use_case}.json"
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Category scorers
# ---------------------------------------------------------------------------


def score_visual_hierarchy(headline: str, subheadline: str, cta: str, fmt: str) -> tuple[float, list[str]]:
    """Score visual hierarchy (max 20 points)."""
    score = 0.0
    notes = []
    spec = FORMAT_SPECS.get(fmt, FORMAT_SPECS["bulletin"])
    max_words = spec["max_words"]

    hw = word_count(headline)
    if hw <= max_words:
        score += 6.0
        notes.append(f"headline {hw} words <= {max_words} max")
    elif hw <= max_words + 2:
        score += 3.0
        notes.append(f"headline {hw} words, slightly over {max_words} max")
    else:
        score += 0.0
        notes.append(f"headline {hw} words, well over {max_words} max")

    total = total_copy_words(headline, subheadline, cta)
    if total <= max_words + 8:
        score += 4.0
    elif total <= max_words + 14:
        score += 2.0
        notes.append(f"total copy {total} words is moderate")
    else:
        notes.append(f"total copy {total} words is too long")

    if headline.strip():
        score += 4.0
    else:
        notes.append("missing headline")

    if cta.strip():
        score += 3.0
    else:
        notes.append("missing CTA")

    if subheadline.strip():
        score += 3.0
    else:
        notes.append("missing subheadline")

    return score, notes


def score_color_contrast(color_scheme: dict) -> tuple[float, list[str]]:
    """Score color contrast (max 15 points)."""
    score = 0.0
    notes = []
    bg = color_scheme["background"]

    h_ratio = contrast_ratio(color_scheme["headline"], bg)
    if h_ratio >= 4.5:
        score += 6.0
        notes.append(f"headline contrast {h_ratio:.1f}:1 (WCAG AA)")
    elif h_ratio >= 3.0:
        score += 3.0
        notes.append(f"headline contrast {h_ratio:.1f}:1 (below AA)")
    else:
        notes.append(f"headline contrast {h_ratio:.1f}:1 (poor)")

    cta_ratio = contrast_ratio(color_scheme["cta"], bg)
    if cta_ratio >= 4.5:
        score += 4.0
        notes.append(f"CTA contrast {cta_ratio:.1f}:1 (WCAG AA)")
    elif cta_ratio >= 3.0:
        score += 2.0
        notes.append(f"CTA contrast {cta_ratio:.1f}:1 (below AA)")
    else:
        notes.append(f"CTA contrast {cta_ratio:.1f}:1 (poor)")

    sub_ratio = contrast_ratio(color_scheme["subheadline"], bg)
    if sub_ratio >= 4.5:
        score += 3.0
    elif sub_ratio >= 3.0:
        score += 1.5
        notes.append(f"subheadline contrast {sub_ratio:.1f}:1 (below AA)")
    else:
        notes.append(f"subheadline contrast {sub_ratio:.1f}:1 (poor)")

    colors = [bg, color_scheme["headline"], color_scheme["subheadline"], color_scheme["cta"]]
    unique_pairs = [(colors[i], colors[j]) for i in range(len(colors)) for j in range(i + 1, len(colors))]
    avg_dist = sum(color_distance(a, b) for a, b in unique_pairs) / len(unique_pairs)
    if avg_dist > 100:
        score += 2.0
    elif avg_dist > 50:
        score += 1.0
        notes.append("limited color diversity")
    else:
        notes.append("very low color diversity")

    return score, notes


def score_brand_integration(color_scheme: dict, brand_config: dict) -> tuple[float, list[str]]:
    """Score brand integration (max 10 points)."""
    score = 0.0
    notes = []
    brand_colors = brand_config["brand_colors"]
    used_colors = list(color_scheme.values())

    primary = brand_colors["primary"]
    if primary in used_colors:
        score += 4.0
        notes.append("brand primary color present")
    else:
        min_dist = min(color_distance(primary, c) for c in used_colors)
        if min_dist < 50:
            score += 2.0
            notes.append(f"near-match to brand primary (dist={min_dist:.0f})")
        else:
            notes.append("brand primary color not used")

    secondary = brand_colors["secondary"]
    accent = brand_colors["accent"]
    sec_used = secondary in used_colors or any(color_distance(secondary, c) < 50 for c in used_colors)
    acc_used = accent in used_colors or any(color_distance(accent, c) < 50 for c in used_colors)
    if sec_used and acc_used:
        score += 3.0
    elif sec_used or acc_used:
        score += 1.5
        notes.append("only one of secondary/accent brand colors used")
    else:
        notes.append("brand secondary/accent colors not used")

    all_brand = [primary, secondary, accent]
    creative_colors = [color_scheme["headline"], color_scheme["subheadline"], color_scheme["cta"]]
    avg_min_dist = sum(
        min(color_distance(cc, bc) for bc in all_brand) for cc in creative_colors
    ) / len(creative_colors)
    if avg_min_dist < 30:
        score += 3.0
    elif avg_min_dist < 80:
        score += 1.5
        notes.append("moderate brand color alignment")
    else:
        notes.append("creative colors diverge from brand palette")

    return score, notes


def score_format_optimization(fmt: str, layout: str) -> tuple[float, list[str]]:
    """Score format optimization (max 10 points)."""
    score = 0.0
    notes = []

    if fmt in FORMAT_SPECS:
        score += 4.0
    else:
        notes.append(f"unknown format: {fmt}")
        return score, notes

    valid_layouts = ["hero-left", "hero-right", "centered", "split"]
    if layout in valid_layouts:
        score += 3.0
    else:
        notes.append(f"unknown layout: {layout}")

    good_combos = {
        "bulletin": ["hero-left", "hero-right"],
        "poster": ["hero-left", "hero-right", "centered"],
        "digital-landscape": ["hero-left", "hero-right", "centered", "split"],
        "transit-shelter": ["centered", "split"],
    }
    if layout in good_combos.get(fmt, []):
        score += 3.0
    else:
        score += 1.0
        notes.append(f"layout '{layout}' is suboptimal for format '{fmt}'")

    return score, notes


def score_regulatory_compliance(headline: str, subheadline: str, cta: str, fmt: str) -> tuple[float, list[str]]:
    """Score regulatory compliance (max 10 points)."""
    score = 0.0
    notes = []
    all_text = f"{headline} {subheadline} {cta}".lower()

    prohibited = ["guaranteed", "free*", "#1 rated", "best in the world", "miracle", "unlimited"]
    found = [p for p in prohibited if p.lower() in all_text]
    if not found:
        score += 4.0
    else:
        score += max(0, 4.0 - len(found) * 2)
        notes.append(f"prohibited terms: {', '.join(found)}")

    spec = FORMAT_SPECS.get(fmt, FORMAT_SPECS["bulletin"])
    hw = word_count(headline)
    if hw <= spec["max_words"]:
        score += 3.0
    else:
        score += 1.0
        notes.append(f"headline exceeds {fmt} word limit ({hw} > {spec['max_words']})")

    misleading = ["always", "never fails", "100%", "guaranteed", "permanent"]
    found_misleading = [m for m in misleading if m.lower() in all_text]
    if not found_misleading:
        score += 3.0
    else:
        score += 1.0
        notes.append(f"potentially misleading: {', '.join(found_misleading)}")

    return score, notes


# ---------------------------------------------------------------------------
# LLM-as-judge scoring (Claude Haiku)
# ---------------------------------------------------------------------------


def llm_judge(
    headline: str,
    subheadline: str,
    cta: str,
    color_scheme: dict,
    layout: str,
    fmt: str,
    brand_config: dict,
    image_path: str | None = None,
) -> dict:
    """Use Claude Haiku to score message-effectiveness and industry-practices."""
    client = anthropic.AnthropicBedrock()

    spec = FORMAT_SPECS.get(fmt, FORMAT_SPECS["bulletin"])
    category = brand_config.get("business_category", "general")
    differentiator = brand_config.get("differentiator", "")
    persona = brand_config.get("persona", "")
    required_info = brand_config.get("required_info", [])

    all_text = f"{headline} {subheadline} {cta}".lower()
    info_present = {}
    for key in required_info:
        value = brand_config.get(key, "")
        if isinstance(value, str) and value:
            parts = re.split(r"[^a-zA-Z0-9]+", value.lower())
            significant = [p for p in parts if len(p) > 2]
            info_present[key] = any(p in all_text for p in significant) if significant else False
        else:
            info_present[key] = False

    prompt = f"""You are an OOH (Out-of-Home) advertising expert scoring a billboard creative.

## Creative Under Review
- Headline: "{headline}"
- Subheadline: "{subheadline}"
- CTA: "{cta}"
- Layout: {layout}
- Format: {fmt} ({spec['aspect_ratio']}, max {spec['max_words']} words for headline)
- Color scheme: background={color_scheme['background']}, headline={color_scheme['headline']}, subheadline={color_scheme['subheadline']}, cta={color_scheme['cta']}

## Brand Context
- Business: {brand_config['business_name']}
- Category: {category}
- Differentiator: {differentiator}
- Target persona: {persona}
- Required info presence: {json.dumps(info_present)}

## Score Two Categories

### 1. Message Effectiveness (0-20 points)
- Clear, actionable CTA (0-5 pts)
- Benefit-driven copy that resonates with persona (0-5 pts)
- Context-appropriate messaging for {category} (0-5 pts)
- Reflects the differentiator: "{differentiator}" (0-5 pts)

### 2. Industry Practices (0-15 points)
- Category-specific best practices for {category} (0-5 pts)
- Key business info present (required: {', '.join(required_info)}) (0-5 pts)
- Trust signals and credibility markers (0-5 pts)

## OOH Best Practices to Consider
- Billboards are read in 3-7 seconds
- Less is more — fewer words = higher impact
- Phone numbers should be prominent for service businesses
- Trust signals (licenses, years in business) matter for service industries
- Food businesses benefit from sensory language and appetite appeal

Respond with ONLY valid JSON (no markdown, no code fences):
{{
  "message_effectiveness": <number 0-20>,
  "industry_practices": <number 0-15>,
  "message_notes": ["<note1>", "<note2>"],
  "industry_notes": ["<note1>", "<note2>"]
}}"""

    content_blocks = [{"type": "text", "text": prompt}]

    if image_path and os.path.exists(image_path):
        import base64

        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")
        content_blocks.insert(
            0,
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": image_data,
                },
            },
        )
        content_blocks[1]["text"] += "\n\nThe FINAL RENDERED AD is attached — this is the actual billboard with headline, subheadline, and CTA text composited onto the hero image. Evaluate the complete ad as it would appear to viewers: text readability, visual hierarchy, color contrast against the actual background, layout effectiveness, and overall professional quality. This is the real creative, not a mockup."

    response = client.messages.create(
        model="us.anthropic.claude-3-5-haiku-20241022-v1:0",
        max_tokens=512,
        messages=[{"role": "user", "content": content_blocks}],
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)

    result = json.loads(text)

    result["message_effectiveness"] = max(0, min(20, float(result["message_effectiveness"])))
    result["industry_practices"] = max(0, min(15, float(result["industry_practices"])))

    return result


# ---------------------------------------------------------------------------
# Main evaluation
# ---------------------------------------------------------------------------


def get_tier(score: float) -> str:
    """Map composite score to tier."""
    if score >= 90:
        return "launch-ready"
    elif score >= 80:
        return "minor-revisions"
    elif score >= 65:
        return "significant-revisions"
    elif score >= 50:
        return "major-rework"
    else:
        return "do-not-launch"


def evaluate() -> dict:
    """Run the full OOH Canvas evaluation. Returns a results dict."""
    t0 = time.time()

    from creative import (
        CTA,
        COLOR_SCHEME,
        FORMAT,
        HEADLINE,
        IMAGE_PROMPT,
        IMAGE_STYLE,
        LAYOUT,
        SUBHEADLINE,
        USE_CASE,
    )

    brand_config = load_brand_config(USE_CASE)
    spec = FORMAT_SPECS.get(FORMAT, FORMAT_SPECS["bulletin"])

    image_path = None
    try:
        from generate import generate_hero_image
        from compose import compose_ad

        hero_path = str(generate_hero_image(IMAGE_PROMPT, IMAGE_STYLE, spec["width"], spec["height"]))
        image_path = str(compose_ad(
            hero_path, HEADLINE, SUBHEADLINE, CTA, COLOR_SCHEME, LAYOUT,
            spec["width"], spec["height"],
        ))
    except Exception as e:
        print(f"Ad composition failed: {e}")
        print("Continuing with text-only evaluation...")

    vh_score, vh_notes = score_visual_hierarchy(HEADLINE, SUBHEADLINE, CTA, FORMAT)
    cc_score, cc_notes = score_color_contrast(COLOR_SCHEME)
    bi_score, bi_notes = score_brand_integration(COLOR_SCHEME, brand_config)

    llm_result = llm_judge(
        HEADLINE, SUBHEADLINE, CTA, COLOR_SCHEME, LAYOUT, FORMAT, brand_config, image_path,
    )
    me_score = llm_result["message_effectiveness"]
    ip_score = llm_result["industry_practices"]

    fo_score, fo_notes = score_format_optimization(FORMAT, LAYOUT)
    rc_score, rc_notes = score_regulatory_compliance(HEADLINE, SUBHEADLINE, CTA, FORMAT)

    composite = vh_score + cc_score + bi_score + me_score + fo_score + ip_score + rc_score
    tier = get_tier(composite)

    elapsed = time.time() - t0

    results = {
        "score": round(composite, 1),
        "tier": tier,
        "visual_hierarchy": round(vh_score, 1),
        "color_contrast": round(cc_score, 1),
        "brand_integration": round(bi_score, 1),
        "message_effectiveness": round(me_score, 1),
        "format_optimization": round(fo_score, 1),
        "industry_practices": round(ip_score, 1),
        "regulatory_compliance": round(rc_score, 1),
        "eval_seconds": round(elapsed, 1),
    }

    return results


def print_results(results: dict) -> None:
    """Print results in autoresearch format."""
    print("---")
    for key, value in results.items():
        print(f"{key + ':':27s}{value}")


if __name__ == "__main__":
    results = evaluate()
    print_results(results)
