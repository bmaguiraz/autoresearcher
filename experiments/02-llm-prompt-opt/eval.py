# -*- coding: utf-8 -*-
"""Frozen evaluator for sentiment classification.

DO NOT MODIFY THIS FILE. The agent edits only prompt.py.

Loads eval set, runs the configured prompt against Claude, reports accuracy.
"""

import json
import os
import time
import pathlib
import anthropic

from prompt import (
    MODEL,
    SYSTEM_PROMPT,
    FEW_SHOT_EXAMPLES,
    CLASSIFICATION_LABELS,
)

DATA_PATH = pathlib.Path(__file__).parent / "data" / "eval_set.json"
MAX_RETRIES = 5
RETRY_BASE_DELAY = 2.0  # seconds


def load_eval_set():
    with open(DATA_PATH) as f:
        data = json.load(f)
    return data


def build_messages(text: str) -> list[dict]:
    """Build the messages list from few-shot examples and the query text."""
    messages = []
    for example_text, example_label in FEW_SHOT_EXAMPLES:
        messages.append({"role": "user", "content": example_text})
        messages.append({"role": "assistant", "content": example_label})
    messages.append({"role": "user", "content": text})
    return messages


def classify(client: anthropic.AnthropicBedrock, text: str) -> tuple[str, float]:
    """Classify a single text. Returns (predicted_label, cost_cents).

    Retries on rate-limit and transient errors.
    """
    messages = build_messages(text)
    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=16,
                system=SYSTEM_PROMPT,
                messages=messages,
            )
            raw = response.content[0].text.strip().lower()
            # Map to closest valid label
            prediction = raw if raw in CLASSIFICATION_LABELS else _closest_label(raw)
            # Estimate cost: input + output tokens
            input_cost = response.usage.input_tokens * 0.80 / 1_000_000
            output_cost = response.usage.output_tokens * 4.00 / 1_000_000
            cost_cents = (input_cost + output_cost) * 100
            return prediction, cost_cents
        except anthropic.RateLimitError:
            delay = RETRY_BASE_DELAY * (2 ** attempt)
            print(f"  Rate limited, retrying in {delay:.0f}s...")
            time.sleep(delay)
        except anthropic.APIError as e:
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                print(f"  API error ({e}), retrying in {delay:.0f}s...")
                time.sleep(delay)
            else:
                raise
    raise RuntimeError("Max retries exceeded")


def _closest_label(raw: str) -> str:
    """Try to match a raw response to a valid label."""
    for label in CLASSIFICATION_LABELS:
        if label in raw:
            return label
    # Default fallback — treat as wrong answer
    return raw


def main():
    client = anthropic.AnthropicBedrock()
    eval_set = load_eval_set()
    total = len(eval_set)
    correct = 0
    total_cost = 0.0

    start = time.time()

    for i, example in enumerate(eval_set):
        text = example["text"]
        gold = example["label"]
        prediction, cost = classify(client, text)
        total_cost += cost
        if prediction == gold:
            correct += 1
        else:
            print(f"  [{i+1}/{total}] WRONG: expected={gold} got={prediction}")

    elapsed = time.time() - start
    accuracy = correct / total

    print("---")
    print(f"accuracy:        {accuracy:.3f}")
    print(f"correct:         {correct}")
    print(f"total:           {total}")
    print(f"cost_cents:      {total_cost:.1f}")
    print(f"eval_seconds:    {elapsed:.1f}")


if __name__ == "__main__":
    main()
