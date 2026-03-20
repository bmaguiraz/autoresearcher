# Experiment 06: LLM Model Comparison

Compare Claude Sonnet vs GPT-4o response quality on research summarization tasks.

## Overview

This experiment evaluates two leading LLM models (Claude Sonnet 4 and GPT-4o) on their ability to summarize research topics. The goal is to understand relative strengths and weaknesses across key quality dimensions.

## Experiment Design

### Topics

Three diverse research topics spanning different domains:
1. Quantum computing advances in error correction and fault-tolerant quantum computing
2. mRNA vaccine mechanisms and their application beyond COVID-19
3. Ocean carbon sequestration techniques and their potential for climate change mitigation

### Scoring Dimensions

Each response is scored on a 1-5 scale across four dimensions:
- **Factual Accuracy**: Correctness and precision of scientific claims
- **Citation Quality**: References to authoritative sources
- **Readability**: Clarity, structure, and accessibility
- **Completeness**: Coverage of key concepts and implications

### Models

- **Claude Sonnet 4** (`claude-sonnet-4-20250514`)
- **GPT-4o** (`gpt-4o`)

## Setup

### Prerequisites

- Python 3.10+
- `ANTHROPIC_API_KEY` environment variable set
- `OPENAI_API_KEY` environment variable set

### Installation

```bash
cd experiments/06-llm-comparison
uv sync
```

## Running the Experiment

### Step 1: Generate Responses

```bash
python runner.py
```

This calls both APIs for each topic and saves raw responses to `results/raw_responses.json`.

### Step 2: Evaluate Responses

```bash
python eval.py
```

This scores the responses and generates `results/EVALUATION.md` with:
- Numeric scores for each model × topic × dimension
- Results table and summary analysis
- Brief writeup interpreting the findings

## Success Criteria

- ✓ All API calls complete without errors
- ✓ Results table generated with scores for each model × topic × dimension
- ✓ Brief writeup (2-3 paragraphs) interpreting the results

## Notes

This is a lightweight smoke test to exercise the research pipeline, not a rigorous benchmark. For production use:
- Increase sample size (10+ topics)
- Use multiple human evaluators
- Implement blind evaluation
- Add inter-rater reliability checks
- Test across multiple prompt variations
