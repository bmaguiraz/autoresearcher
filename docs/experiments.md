# Running Experiments

## Overview

Experiments are self-contained optimization workflows. Each experiment directory includes everything needed to run and evaluate the experiment.

## Experiment Structure

Every experiment follows this standard layout:

```
experiments/<id>-<name>/
  program.md       # Instructions and methodology
  config.json      # Experiment parameters
  runner.py        # Main experiment runner
  eval.py          # Evaluation script (frozen, do not modify)
  prompt.py        # Prompt configuration (editable)
  data/            # Input datasets
  results/         # Output results
  pyproject.toml   # Python dependencies
```

## Running an Experiment

### 1. Set Up the Environment

```bash
cd experiments/<experiment-dir>
uv sync  # or: pip install -e .
```

### 2. Configure API Keys

Ensure required API keys are set:

```bash
export ANTHROPIC_API_KEY=your-key-here
```

### 3. Run the Evaluator

```bash
python eval.py
```

### 4. Review Results

Results are saved to the `results/` directory as JSON files. The evaluator also prints a summary:

```
accuracy:        0.720
correct:         36
total:           50
cost_cents:      1.2
eval_seconds:    45.3
```

## Creating a New Experiment

1. Create a new directory: `experiments/<id>-<name>/`
2. Add a `program.md` describing the experiment methodology
3. Add a `config.json` with experiment parameters
4. Implement `runner.py` and/or `eval.py`
5. Add a `pyproject.toml` listing dependencies
6. Document the experiment in the project README

## Experiment Conventions

- Experiment IDs are zero-padded numbers (01, 02, 03, ...)
- Evaluation scripts are frozen and must not be modified during experimentation
- Results should be committed to version control for reproducibility
- Each experiment manages its own virtual environment
