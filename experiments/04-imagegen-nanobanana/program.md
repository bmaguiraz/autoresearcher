# autoresearch — Experiment 04: Image Gen Prompt Optimization (Nano)

A minimal experiment to test per-issue parallelism alongside other experiments.

## Purpose

This is a short test experiment designed to:
- Validate parallel experiment execution
- Test the autoresearch framework with a different domain (image generation)
- Run quickly (1 optimization cycle: baseline + 1 hypothesis)

## Configuration

- **Cycles**: 2 (baseline evaluation + 1 optimized hypothesis)
- **Domain**: Image generation prompts
- **Optimization Target**: Improve prompt quality metrics

## Metrics

The experiment evaluates prompts on four dimensions:
- **visual_quality**: Simulated quality of generated images
- **prompt_clarity**: How clear and specific the prompt is
- **style_consistency**: Consistency of artistic style
- **composition**: Quality of image composition

## Experiment Flow

1. **Cycle 1 (Baseline)**: Evaluate the baseline prompt
2. **Cycle 2 (Optimized)**: Evaluate an improved prompt variant

## Running the Experiment

```bash
cd experiments/04-imagegen-nanobanana
python runner.py
```

## Notes

- This is a "nano" experiment with simulated metrics for testing purposes
- Designed to run quickly (~1-2 seconds) to test parallelism
- Does not make actual API calls or generate real images
