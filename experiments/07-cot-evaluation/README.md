# Experiment 07: Chain-of-Thought Prompting Evaluation

Evaluate the impact of chain-of-thought (CoT) prompting on factual accuracy in question-answering tasks.

## Overview

This experiment compares two prompting strategies for factual questions:
1. **Direct prompting**: Standard question-answer format
2. **Chain-of-thought prompting**: Explicit "think step by step" instruction

Questions span five domains:
- History (Treaty of Versailles)
- Science (Photosynthesis)
- Economics (Quantitative easing)
- Geography (Monsoons)
- Medicine (mRNA vaccines)

Each response is evaluated on:
- **Factual Correctness** (binary): Accuracy of claims
- **Reasoning Quality** (1-5): Logic and structure
- **Answer Completeness** (1-5): Coverage of key concepts

## Prerequisites

- Python 3.10+
- `ANTHROPIC_API_KEY` environment variable

## Setup

```bash
cd experiments/07-cot-evaluation
uv sync
```

## Running the Experiment

```bash
python runner.py
```

This will:
1. Call Claude Sonnet with both prompting methods for each question (10 API calls)
2. Score responses using automated heuristics
3. Generate a markdown report with results table
4. Save detailed results to `results/` directory

## Output

- `results/report_YYYYMMDD_HHMMSS.md` - Full markdown report with analysis
- `results/results_YYYYMMDD_HHMMSS.json` - Raw JSON data

## Cost

Approximate cost per run: $0.05-0.10

## Note

This is a lightweight smoke test to verify the research pipeline, not a rigorous benchmark. Scoring uses automated heuristics rather than human evaluation. For production use, implement domain expert evaluation and larger sample sizes.
