# Chain-of-Thought Prompting Evaluation

**Experiment 07**: Evaluate the impact of chain-of-thought (CoT) prompting on factual accuracy in research summarization.

## Overview

This experiment compares two prompting strategies:
- **Direct prompting**: Simple question with no CoT instruction
- **Chain-of-thought prompting**: Question prefixed with "Think step by step and show your reasoning"

The experiment measures:
1. **Factual correctness** (binary: 0 or 1)
2. **Reasoning quality** (scale: 1-5)
3. **Answer completeness** (scale: 1-5)

## Test Questions

5 factual questions spanning diverse domains:
- **History**: Berlin Wall fall date and Soviet leader
- **Science**: Mitochondria role and ATP production
- **Economics**: Quantitative easing definition and origin
- **Geography**: South America's longest river
- **Medicine**: Beta-blocker mechanism and uses

## Usage

### Option 1: Run with live API calls (requires API key)

```bash
export ANTHROPIC_API_KEY="your-key-here"
python3 runner.py
```

### Option 2: Run demo with pre-generated responses (no API key)

```bash
python3 runner_demo.py
```

### Output

Results are saved to `results/`:
- `results_<timestamp>.json` - Full structured results
- `report_<timestamp>.md` - Markdown report with analysis

## Evaluation Criteria

**Factual Correctness**: Domain-specific keyword checks for key facts
**Reasoning Quality**: Presence of structure, explanation depth, reasoning markers
**Answer Completeness**: Coverage of all question parts, response length

## Success Criteria

- ✅ All 10 API calls complete (5 questions × 2 styles)
- ✅ Results table with scores per question and prompting style
- ✅ Summary paragraph analyzing CoT impact on accuracy
