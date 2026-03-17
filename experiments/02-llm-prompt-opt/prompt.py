"""Mutable prompt configuration for sentiment classification.

The agent edits this file to optimize classification accuracy.
"""

# Model to use for classification (Bedrock model ID)
MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# Classification labels
CLASSIFICATION_LABELS = ["positive", "negative", "neutral"]

# System prompt for the classifier
SYSTEM_PROMPT = """Classify sentiment as exactly one of: positive, negative, neutral.

- Positive: approval, satisfaction, praise, favorable outcome.
- Negative: disapproval, dissatisfaction, criticism, unfavorable outcome. Hedged negativity ("wouldn't do it again", "expected more") and cases where negatives outweigh positives are negative.
- Neutral: purely factual with no evaluative stance, or genuinely ambiguous ("it's fine").

For mixed sentiment, classify by the dominant feeling. For sarcasm, classify the intended meaning.

Respond with only the label."""

# Few-shot examples: list of (text, label) tuples
FEW_SHOT_EXAMPLES = [
    ("I absolutely loved this product, it exceeded all my expectations!", "positive"),
    ("This was the worst experience I've ever had. Complete waste of money.", "negative"),
    ("The package arrived on Tuesday as scheduled.", "neutral"),
]
