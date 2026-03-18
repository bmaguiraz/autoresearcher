# autoresearch — Experiment 03: Data Cleaning Pipeline Optimization

You are an autonomous AI researcher optimizing a data cleaning pipeline for maximum data quality.

## Setup

To set up a new experiment:

1. **Create the branch**: `git checkout -b autoresearch/<tag>` from current HEAD.
2. **Read the in-scope files**: Read these files for full context:
   - This file (`program.md`) — your instructions.
   - `runner.py` — experiment orchestrator.
   - `config.json` — configuration parameters.
3. **Verify setup**: Run `python runner.py` to verify.
4. **Initialize results**: Results are automatically tracked in `results/` directory.

## Experimentation

Each cycle evaluates different data cleaning strategies against quality metrics.

**What you CAN do:**
- Modify cleaning strategies
- Adjust quality thresholds
- Change optimization targets
- Experiment with different cleaning sequences

**What you CANNOT do:**
- Modify the evaluation metrics
- Change the core data structure
- Install new packages

**The goal: achieve the highest aggregate data quality score.**

### Strategy Space

- Null handling: remove vs. impute
- Format standardization: strict vs. flexible
- Validation rules: comprehensive vs. permissive
- Deduplication: exact match vs. fuzzy matching
- Sequencing: order of cleaning operations

### Simplicity Criterion

All else being equal, simpler is better. A small quality gain from a much more complex pipeline is not worth it.

## Output Format

The runner prints a summary after each cycle:
```
---
Cycle: 1
Strategy: baseline
Aggregate Score: 0.875
Completeness: 0.85
Consistency: 0.90
Accuracy: 0.88
Deduplication: 0.95
---
```

## The Experiment Loop

For each cycle:

1. Apply cleaning strategy to sample dataset
2. Calculate quality metrics
3. Compute aggregate score
4. Log results
5. Generate improved strategy for next cycle

The loop runs for the configured number of cycles.
