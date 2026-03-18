# -*- coding: utf-8 -*-
"""Compose the final OOH ad by rendering copy text onto the hero image.

Takes the hero image and overlays headline, subheadline, and CTA using
the specified color scheme and layout. Produces the final ad creative
that gets evaluated.

DO NOT MODIFY this file — it is part of the frozen evaluation harness.
"""

import pathlib
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = pathlib.Path(__file__).parent / "outputs"

# Try to use a clean sans-serif font, fall back to default
def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/System/Library/Fonts/SFCompact.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def compose_ad(
    hero_path: str,
    headline: str,
    subheadline: str,
    cta: str,
    color_scheme: dict,
    layout: str,
    width: int,
    height: int,
) -> pathlib.Path:
    """Render ad copy onto the hero image and save as outputs/ad_final.png.

    Layout options:
    - hero-left: image on left, text on right
    - hero-right: image on right, text on left
    - centered: image as full background, text centered with semi-transparent overlay
    - split: image top half, text bottom half
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "ad_final.png"

    # Load and resize hero image
    hero = Image.open(hero_path).convert("RGBA")

    # Create the canvas at the target format size
    canvas = Image.new("RGBA", (width, height), hex_to_rgb(color_scheme["background"]) + (255,))

    bg_rgb = hex_to_rgb(color_scheme["background"])
    headline_rgb = hex_to_rgb(color_scheme["headline"])
    sub_rgb = hex_to_rgb(color_scheme["subheadline"])
    cta_rgb = hex_to_rgb(color_scheme["cta"])

    # Scale font sizes relative to canvas height
    headline_size = max(24, int(height * 0.12))
    sub_size = max(16, int(height * 0.06))
    cta_size = max(18, int(height * 0.07))

    headline_font = _get_font(headline_size)
    sub_font = _get_font(sub_size)
    cta_font = _get_font(cta_size)

    if layout == "hero-left":
        # Hero takes left 45%, text on right 55%
        hero_w = int(width * 0.45)
        hero_resized = hero.resize((hero_w, height), Image.LANCZOS)
        canvas.paste(hero_resized, (0, 0))

        text_x = hero_w + int(width * 0.03)
        text_w = width - text_x - int(width * 0.03)
        _draw_text_block(canvas, text_x, text_w, height, headline, subheadline, cta,
                         headline_font, sub_font, cta_font,
                         headline_rgb, sub_rgb, cta_rgb)

    elif layout == "hero-right":
        # Text on left 55%, hero on right 45%
        hero_w = int(width * 0.45)
        hero_resized = hero.resize((hero_w, height), Image.LANCZOS)
        canvas.paste(hero_resized, (width - hero_w, 0))

        text_x = int(width * 0.03)
        text_w = width - hero_w - int(width * 0.06)
        _draw_text_block(canvas, text_x, text_w, height, headline, subheadline, cta,
                         headline_font, sub_font, cta_font,
                         headline_rgb, sub_rgb, cta_rgb)

    elif layout == "centered":
        # Hero as full background with semi-transparent overlay
        hero_resized = hero.resize((width, height), Image.LANCZOS)
        canvas.paste(hero_resized, (0, 0))

        # Dark overlay for text readability
        overlay = Image.new("RGBA", (width, height), bg_rgb + (160,))
        canvas = Image.alpha_composite(canvas, overlay)

        text_x = int(width * 0.1)
        text_w = int(width * 0.8)
        _draw_text_block(canvas, text_x, text_w, height, headline, subheadline, cta,
                         headline_font, sub_font, cta_font,
                         headline_rgb, sub_rgb, cta_rgb, center=True)

    elif layout == "split":
        # Hero top half, text bottom half
        hero_h = int(height * 0.5)
        hero_resized = hero.resize((width, hero_h), Image.LANCZOS)
        canvas.paste(hero_resized, (0, 0))

        text_x = int(width * 0.05)
        text_w = int(width * 0.9)
        text_area_top = hero_h + int(height * 0.03)
        text_area_height = height - text_area_top
        _draw_text_block_at(canvas, text_x, text_area_top, text_w, text_area_height,
                            headline, subheadline, cta,
                            headline_font, sub_font, cta_font,
                            headline_rgb, sub_rgb, cta_rgb)
    else:
        # Fallback to hero-left
        return compose_ad(hero_path, headline, subheadline, cta, color_scheme,
                          "hero-left", width, height)

    # Save as RGB PNG
    final = canvas.convert("RGB")
    final.save(output_path, "PNG")
    print(f"Final ad saved to {output_path}")
    return output_path


def _draw_text_block(canvas, text_x, text_w, canvas_h,
                     headline, subheadline, cta,
                     h_font, s_font, c_font,
                     h_color, s_color, c_color, center=False):
    """Draw headline, subheadline, CTA vertically centered in the text area."""
    draw = ImageDraw.Draw(canvas)
    anchor = "mm" if center else "lm"

    # Vertical spacing
    total_text_h = h_font.size + s_font.size + c_font.size + 40
    y_start = (canvas_h - total_text_h) // 2

    x = text_x + text_w // 2 if center else text_x

    # Headline
    draw.text((x, y_start + h_font.size // 2), headline, font=h_font, fill=h_color, anchor=anchor)
    y_start += h_font.size + 15

    # Subheadline
    draw.text((x, y_start + s_font.size // 2), subheadline, font=s_font, fill=s_color, anchor=anchor)
    y_start += s_font.size + 20

    # CTA
    draw.text((x, y_start + c_font.size // 2), cta, font=c_font, fill=c_color, anchor=anchor)


def _draw_text_block_at(canvas, text_x, text_y, text_w, text_h,
                        headline, subheadline, cta,
                        h_font, s_font, c_font,
                        h_color, s_color, c_color):
    """Draw text block at a specific y position (for split layout)."""
    draw = ImageDraw.Draw(canvas)
    cx = text_x + text_w // 2

    total_text_h = h_font.size + s_font.size + c_font.size + 40
    y_start = text_y + (text_h - total_text_h) // 2

    draw.text((cx, y_start + h_font.size // 2), headline, font=h_font, fill=h_color, anchor="mm")
    y_start += h_font.size + 15
    draw.text((cx, y_start + s_font.size // 2), subheadline, font=s_font, fill=s_color, anchor="mm")
    y_start += s_font.size + 20
    draw.text((cx, y_start + c_font.size // 2), cta, font=c_font, fill=c_color, anchor="mm")
