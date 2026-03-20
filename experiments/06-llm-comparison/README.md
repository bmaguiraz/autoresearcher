# Experiment 06: LLM Comparison (Claude vs GPT-4o)

Compare Claude Sonnet and GPT-4o response quality on research summarization tasks.

## Overview

This lightweight experiment compares two state-of-the-art LLMs across three diverse research topics:
1. Quantum Computing Advances
2. mRNA Vaccine Mechanisms
3. Ocean Carbon Sequestration

Each model receives identical prompts and responses are scored on:
- **Factual Accuracy** (1-5): Correctness of claims
- **Citation Quality** (1-5): Specific examples and research mentions
- **Readability** (1-5): Clarity and structure
- **Completeness** (1-5): Addresses all prompt aspects

## Prerequisites

- Python 3.10+
- `ANTHROPIC_API_KEY` environment variable
- `OPENAI_API_KEY` environment variable

## Setup

```bash
cd experiments/06-llm-comparison
uv sync
```

## Running the Experiment

```bash
python runner.py
```

This will:
1. Call both Claude Sonnet and GPT-4o APIs for each topic
2. Score responses using automated heuristics
3. Generate a markdown report with results table
4. Save detailed results to `results/` directory

## Output

- `results/report_YYYYMMDD_HHMMSS.md` - Full markdown report with analysis
- `results/results_YYYYMMDD_HHMMSS.json` - Raw JSON data

## Cost

Approximate cost per run: $0.10-0.20 (depends on response lengths)

## Note

This is a smoke test to verify the research pipeline, not a rigorous benchmark. Scoring uses automated heuristics rather than human evaluation.
