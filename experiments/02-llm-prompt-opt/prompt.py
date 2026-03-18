"""Mutable prompt configuration for sentiment classification.

The agent edits this file to optimize classification accuracy.
"""

# Model to use for classification (Bedrock model ID)
MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# Classification labels
CLASSIFICATION_LABELS = ["positive", "negative", "neutral"]

# System prompt for the classifier
SYSTEM_PROMPT = """You are a sentiment classifier. Classify text as exactly one of: positive, negative, or neutral.

Labels:
- Positive: approval, satisfaction, praise, favorable outcome, recommendations ("highly recommend", "will definitely"), accomplishments, exceeded expectations, expressions of gratitude or joy
- Negative: disapproval, dissatisfaction, criticism, unfavorable outcome (includes hedged negativity like "wouldn't do it again" or "wasn't great")
- Neutral: purely factual with no evaluative stance, or mixed/ambiguous sentiment

For mixed sentiment, sarcasm, or backhanded compliments: classify based on the actual meaning or dominant sentiment.

Respond with only the label."""

# Few-shot examples: list of (text, label) tuples
FEW_SHOT_EXAMPLES = [
    ("I absolutely loved this product, it exceeded all my expectations!", "positive"),
    ("This was the worst experience I've ever had. Complete waste of money.", "negative"),
    ("The shipping was on time and the package was intact.", "neutral"),
]
