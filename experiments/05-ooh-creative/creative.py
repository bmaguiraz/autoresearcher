# OOH Creative Config — agent edits this file
# Switch between use cases by changing USE_CASE
USE_CASE = "restaurant"  # "plumber", "restaurant", or "writefit"

# Creative elements (agent optimizes these)
HEADLINE = "Handmade Pasta Since 1987"
SUBHEADLINE = "Farm-to-table Italian | Tue-Sun 11am-10pm | 247 Main St"
CTA = "(555) BELLA-01"
COLOR_SCHEME = {
    "background": "#2D1B0E",  # dark brown (brand primary)
    "headline": "#D4A87A",    # slightly lighter tan - better contrast, stays on-brand
    "subheadline": "#FFFFFF", # white for readability
    "cta": "#C41E1E",         # brighter red - more visible, still brand-appropriate
}
LAYOUT = "hero-left"  # hero-left, hero-right, centered, split
FORMAT = "bulletin"  # bulletin: 3.4:1, 7 word max

# Image generation prompt for the hero image
IMAGE_PROMPT = "close-up of fresh handmade pappardelle pasta being lifted from a rustic wooden board, flour dusted surface, warm golden hour lighting, authentic Italian trattoria kitchen, rich textures"
IMAGE_STYLE = "food photography, warm natural lighting, shallow depth of field, appetizing and authentic mood, rustic Italian aesthetic"
