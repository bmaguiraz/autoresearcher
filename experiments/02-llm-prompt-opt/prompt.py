# -*- coding: utf-8 -*-
"""Mutable prompt configuration for sentiment classification.

The agent edits this file to optimize classification accuracy.
"""

# Model to use for classification (Bedrock model ID)
MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# Classification labels
CLASSIFICATION_LABELS = ["positive", "negative", "neutral"]

# System prompt for the classifier
SYSTEM_PROMPT = """You are a sentiment classifier. Classify text as exactly one of: positive, negative, or neutral.

- Positive: approval, praise, satisfaction, recommendations, accomplishments, joy, gratitude, exceeded expectations
- Negative: disapproval, criticism, dissatisfaction, unfavorable outcome (includes hedged negativity like "wouldn't do it again")
- Neutral: factual with no evaluative stance, or mixed/ambiguous sentiment

For mixed sentiment or sarcasm: classify based on actual meaning or dominant sentiment.

Respond with only the label."""

# Few-shot examples: list of (text, label) tuples
FEW_SHOT_EXAMPLES = [
    ("I absolutely loved this product, it exceeded all my expectations!", "positive"),
    ("This was the worst experience I've ever had. Complete waste of money.", "negative"),
    ("The shipping was on time and the package was intact.", "neutral"),
]
