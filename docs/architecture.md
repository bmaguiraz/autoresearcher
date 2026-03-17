# Architecture Overview

## System Design

Autoresearcher is organized around three core concepts:

### 1. Experiments

Self-contained optimization workflows that live in `experiments/`. Each experiment:

- Has its own directory, dependencies, and configuration
- Follows a standard structure (config, runner, evaluator, results)
- Can be run independently without affecting other experiments

### 2. Core Library (`src/`)

Shared utilities and base classes used across experiments:

- **Experiment base classes** -- Common interfaces for running experiments
- **Metrics tracking** -- Standardized result recording and comparison
- **Configuration management** -- Shared config loading and validation

### 3. Evaluation

Each experiment includes an evaluator that:

- Runs the current configuration against a test dataset
- Produces quantitative metrics (accuracy, cost, latency)
- Outputs results in a consistent format for comparison

## Data Flow

```
Config --> Runner --> LLM API --> Evaluator --> Results
  ^                                              |
  |______________ Optimization Loop ____________|
```

## Key Design Decisions

- **Experiment isolation**: Each experiment manages its own virtual environment and dependencies to avoid conflicts.
- **Frozen evaluators**: Evaluation scripts are read-only to ensure fair comparison across iterations.
- **Result persistence**: All results are saved to disk for reproducibility and audit trails.
