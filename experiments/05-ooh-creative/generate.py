# -*- coding: utf-8 -*-
"""Image generation via Nano Banana (Gemini Flash Image Generation).

Generates a hero image from the creative config and saves to outputs/hero.png.
Uses the google.genai SDK with gemini-3.1-flash-image-preview.

Environment: GOOGLE_API_KEY must be set.
"""

import os
import pathlib
from io import BytesIO

from google import genai
from google.genai import types
from PIL import Image

OUTPUT_DIR = pathlib.Path(__file__).parent / "outputs"


def generate_hero_image(prompt: str, style: str, width: int, height: int) -> pathlib.Path:
    """Generate a hero image and save to outputs/hero.png.

    Returns the path to the saved image.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "hero.png"

    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    full_prompt = f"Generate an image: {prompt}, {style}. Aspect ratio approximately {width}:{height}."

    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=full_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        ),
    )

    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                img = Image.open(BytesIO(part.inline_data.data))
                img.save(output_path)
                print(f"Hero image saved to {output_path}")
                return output_path

    raise RuntimeError("Image generation returned no images")


if __name__ == "__main__":
    from creative import IMAGE_PROMPT, IMAGE_STYLE, FORMAT

    FORMAT_SPECS = {
        "bulletin": {"width": 1400, "height": 412},
        "poster": {"width": 1200, "height": 600},
        "digital-landscape": {"width": 1920, "height": 1080},
        "transit-shelter": {"width": 800, "height": 1200},
    }
    spec = FORMAT_SPECS[FORMAT]
    generate_hero_image(IMAGE_PROMPT, IMAGE_STYLE, spec["width"], spec["height"])
