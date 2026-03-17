"""Mutable prompt configuration for sentiment classification.

The agent edits this file to optimize classification accuracy.
"""

# Model to use for classification (Bedrock model ID)
MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# Classification labels
CLASSIFICATION_LABELS = ["positive", "negative", "neutral"]

# System prompt for the classifier
SYSTEM_PROMPT = """You are a sentiment classifier. Classify the text as: positive, negative, or neutral.

Guidelines:
- Positive: expresses satisfaction, approval, or praise
- Negative: expresses dissatisfaction, disapproval, or criticism (including subtle forms like "wouldn't recommend")
- Neutral: factual statements with no clear emotional valence

Reply with only one word: the label."""

# Few-shot examples: list of (text, label) tuples
FEW_SHOT_EXAMPLES = [
    ("I absolutely loved this product, it exceeded all my expectations!", "positive"),
    ("This was the worst experience I've ever had. Complete waste of money.", "negative"),
    ("The package arrived on Tuesday as scheduled.", "neutral"),
    ("Not what I hoped for, pretty disappointed.", "negative"),
]
