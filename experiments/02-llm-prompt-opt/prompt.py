"""Mutable prompt configuration for sentiment classification.

The agent edits this file to optimize classification accuracy.
"""

# Model to use for classification (Bedrock model ID)
MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# Classification labels
CLASSIFICATION_LABELS = ["positive", "negative", "neutral"]

# System prompt for the classifier
SYSTEM_PROMPT = """You are a sentiment classifier. Classify text as: positive, negative, or neutral.

Labels:
- Positive: approval, satisfaction, praise, favorable outcome
- Negative: disapproval, dissatisfaction, criticism, unfavorable outcome (including hedged negativity)
- Neutral: factual with no evaluative stance, or mixed/ambiguous sentiment

For mixed sentiment or sarcasm, classify based on the actual intended meaning and dominant sentiment.

Respond with only the label."""

# Few-shot examples: list of (text, label) tuples
FEW_SHOT_EXAMPLES = [
    ("I absolutely loved this product, it exceeded all my expectations!", "positive"),
    ("This was the worst experience I've ever had. Complete waste of money.", "negative"),
    ("The package arrived on Tuesday as scheduled.", "neutral"),
    ("Not what I expected, pretty disappointed.", "negative"),
]
