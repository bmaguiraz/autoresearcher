"""Mutable prompt configuration for sentiment classification.

The agent edits this file to optimize classification accuracy.
"""

# Model to use for classification (Bedrock model ID)
MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# Classification labels
CLASSIFICATION_LABELS = ["positive", "negative", "neutral"]

# System prompt for the classifier
SYSTEM_PROMPT = """You are a sentiment classifier. Given a piece of text, classify its sentiment as exactly one of: positive, negative, or neutral.

Guidelines:
- Positive: the text expresses approval, satisfaction, praise, or a favorable outcome.
- Negative: the text expresses disapproval, dissatisfaction, criticism, or an unfavorable outcome. This includes hedged negativity like "I wouldn't do it again" or "it wasn't great." Backhanded compliments or lukewarm statements like "it's fine" should be considered neutral unless there's clear dissatisfaction.
- Neutral: the text is purely factual with no evaluative stance, or expresses mixed/ambiguous sentiment.

Respond with only the label, nothing else."""

# Few-shot examples: list of (text, label) tuples
FEW_SHOT_EXAMPLES = [
    ("I absolutely loved this product, it exceeded all my expectations!", "positive"),
    ("This was the worst experience I've ever had. Complete waste of money.", "negative"),
    ("The package arrived on Tuesday as scheduled.", "neutral"),
    ("Not what I expected, pretty disappointed.", "negative"),
    ("Amazing quality! Highly recommend.", "positive"),
    ("The item is blue and weighs 2 pounds.", "neutral"),
]
