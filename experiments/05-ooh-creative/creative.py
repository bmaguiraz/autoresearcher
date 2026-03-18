# OOH Creative Config — agent edits this file
# Switch between use cases by changing USE_CASE
USE_CASE = "writefit"  # "plumber", "restaurant", or "writefit"

# Creative elements (agent optimizes these)
HEADLINE = "Taste Real Italy Downtown"
SUBHEADLINE = "Handmade pasta daily, family recipes since 1987 | Tue-Sun 11am-10pm"
CTA = "247 Main St | (555) BELLA-01"
COLOR_SCHEME = {
    "background": "#2D1B0E",  # dark brown (brand primary — exact match)
    "headline": "#FFFFFF",    # white — max contrast on dark brown
    "subheadline": "#C4956A", # warm tan (brand secondary — exact match)
    "cta": "#C4956A",         # warm tan (brand secondary) — 6.16:1 contrast
}
LAYOUT = "hero-left"  # hero-left, hero-right, centered, split
FORMAT = "bulletin"  # bulletin: 3.4:1, 7 word max

# Image generation prompt for the hero image
IMAGE_PROMPT = "close-up of fresh handmade pappardelle pasta on rustic wooden board, flour dusted surface, warm golden hour lighting, authentic Italian trattoria kitchen, rich textures"
IMAGE_STYLE = "food photography, warm natural lighting, shallow depth of field, appetizing and authentic mood, rustic Italian aesthetic"
