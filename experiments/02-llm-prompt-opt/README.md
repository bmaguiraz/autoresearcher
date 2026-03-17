# Experiment 02: LLM Prompt Optimization

## Overview

This experiment explores iterative prompt optimization for Large Language Models (LLMs). The goal is to systematically improve prompt effectiveness through multiple refinement cycles.

## Methodology

The experiment follows an iterative optimization approach:

1. **Baseline Evaluation**: Start with a basic prompt
2. **Metric Collection**: Evaluate prompt against key criteria:
   - Clarity: How clear and understandable is the prompt?
   - Specificity: How well does it target the desired behavior?
   - Response Quality: Quality of responses generated
   - Task Completion: Success rate for completing tasks

3. **Optimization**: Generate improved prompt based on metrics
4. **Iteration**: Repeat for specified number of cycles

## Running the Experiment

### Prerequisites

- Python 3.7+
- No external dependencies required (uses standard library)

### Execution

```bash
# From the experiment directory
cd experiments/02-llm-prompt-opt
python runner.py

# Or from project root
python experiments/02-llm-prompt-opt/runner.py
```

### Configuration

Edit `config.json` to adjust:
- Number of cycles
- Model parameters
- Optimization criteria
- Baseline prompt

## Results

Results are saved to the `results/` directory:
- `results_latest.json`: Most recent experiment run
- `results_YYYYMMDD_HHMMSS.json`: Timestamped result files

### Result Structure

```json
{
  "experiment_id": "02-llm-prompt-opt",
  "cycles_completed": 5,
  "results": [
    {
      "cycle": 1,
      "prompt": "...",
      "metrics": {
        "clarity": 0.75,
        "specificity": 0.80,
        ...
      },
      "aggregate_score": 0.78,
      "timestamp": "2026-03-17T..."
    }
  ],
  "summary": {
    "initial_score": 0.70,
    "final_score": 0.85,
    "improvement": 0.15,
    "improvement_percentage": 21.43
  }
}
```

## Expected Outcomes

Through iterative refinement, we expect to see:
- Progressive improvement in aggregate scores
- Convergence toward optimal prompt structure
- Identification of key prompt elements that drive quality

## Future Enhancements

- Integration with real LLM APIs for evaluation
- A/B testing framework for prompt variants
- Multi-dimensional optimization strategies
- Automated prompt generation using meta-prompting
