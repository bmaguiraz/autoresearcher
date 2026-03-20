# Experiment 07: Chain-of-Thought Prompting Evaluation

Evaluate how chain-of-thought (CoT) prompting affects factual accuracy in research summarization.

## Overview

This experiment measures the impact of chain-of-thought prompting on factual accuracy by comparing direct answers against answers generated with explicit "think step by step" instructions.

## Hypothesis

Chain-of-thought prompting will improve:
1. Factual correctness by encouraging verification of reasoning
2. Answer quality by exposing the reasoning process
3. Completeness by prompting systematic coverage of concepts

## Experiment Design

### Questions

Five factual questions spanning diverse domains:
1. **History**: Treaty of Versailles causes and consequences
2. **Science**: Photosynthesis process and carbon cycle role
3. **Economics**: Quantitative easing mechanisms and impacts
4. **Geography**: South Asian monsoon causes and effects
5. **Medicine**: mRNA vaccine mechanisms and differences from traditional vaccines

### Prompting Methods

1. **Direct**: "Answer the following question concisely and accurately: [question]"
2. **Chain-of-Thought**: "Let's think step by step to answer the following question: [question]"

### Evaluation Metrics

Each response is scored on three dimensions:

1. **Factual Correctness** (binary: 0 or 1)
   - Are the claims factually accurate?
   - Are there any errors or misconceptions?

2. **Reasoning Quality** (1-5 scale)
   - Is the explanation logical and well-structured?
   - Does it show clear reasoning steps?
   - Is the logic sound?

3. **Answer Completeness** (1-5 scale)
   - Does it cover all key aspects of the question?
   - Are important details included?
   - Is the scope appropriate?

### Scoring Methodology

This experiment uses automated heuristic scoring based on:
- Response structure and organization
- Keyword coverage for domain-specific concepts
- Word count and detail level
- Presence of specific examples and explanations

**Note**: This is a lightweight pipeline verification test. Production use would require:
- Human evaluation by domain experts
- Reference-based accuracy validation
- Inter-rater reliability assessment
- Larger sample sizes

## Setup

### Prerequisites

- Python 3.10+
- `ANTHROPIC_API_KEY` environment variable set

### Installation

```bash
cd experiments/07-cot-evaluation
uv sync
```

## Running the Experiment

```bash
python runner.py
```

This will:
1. Call Claude API with both prompting methods for each question (10 total API calls)
2. Evaluate each response using automated heuristics
3. Generate a markdown report with results table and analysis
4. Save detailed results to `results/` directory

## Output

- `results/results_YYYYMMDD_HHMMSS.json` - Raw JSON data with all responses and scores
- `results/report_YYYYMMDD_HHMMSS.md` - Markdown report with:
  - Results table (question × method × metrics)
  - Aggregate scores for each method
  - 1-paragraph summary of whether CoT improved accuracy

## Success Criteria

- ✓ All 10 API calls complete successfully (5 questions × 2 methods)
- ✓ Results table with scores for each question × prompting style
- ✓ 1-paragraph summary of whether CoT improved accuracy and by how much

## Cost

Approximate cost per run: $0.05-0.10 (depends on response lengths)

## Limitations

This is a smoke test for pipeline verification, not a rigorous scientific benchmark:
- Automated heuristic scoring (not human evaluation)
- Small sample size (5 questions)
- Single model tested
- No reference answers for validation
- Domain expertise not incorporated in scoring

For production deployment, implement:
- Human evaluation by domain experts
- Larger and more diverse question sets
- Multiple models and prompt variations
- Reference-based accuracy scoring
- Blind evaluation protocols
