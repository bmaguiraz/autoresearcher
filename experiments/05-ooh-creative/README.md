# Experiment 05: OOH Creative Optimization

## Overview

Out-of-Home (OOH) advertising creative optimization experiment that tests concurrent execution of multiple creative variants.

**Key Innovation**: 4-way parallelism testing - runs multiple creative strategies simultaneously to compare effectiveness.

## Metrics

Each creative is evaluated on four dimensions (0-25 points each):

- **Attention**: Eye-catching, memorable, stands out
- **Clarity**: Clear message and obvious call-to-action
- **Relevance**: Resonates with target audience
- **Conversion Potential**: Likelihood to drive desired action

**Total Score**: 0-100 (sum of all dimensions)

## Creative Variants

The experiment tests 4 different creative strategies:

1. **Baseline**: Direct, feature-focused messaging
2. **Emotional**: Appeals to customer pain points and desires
3. **Urgency**: Time-sensitive offers and scarcity messaging
4. **Social Proof**: Trust signals and testimonials

## Usage

### Quick Start

```bash
cd experiments/05-ooh-creative
python runner.py --use-case plumber --cycles 1
```

### Command Line Options

```bash
python runner.py --use-case <case> --cycles <n> [--sequential]
```

- `--use-case`: Target use case (default: `plumber`)
- `--cycles`: Number of optimization cycles (default: `1`)
- `--sequential`: Run variants sequentially instead of in parallel

### Supported Use Cases

- `plumber` - Plumbing services (emergency repairs, 24/7 service)
- `restaurant` - Restaurant dining (Casa Bella Trattoria, Italian cuisine)
- More use cases can be added to the `_generate_creatives()` method

## Example Output

```
==================================================================
OOH Creative Optimization Experiment
Use Case: Plumber
Cycles: 1
Parallel Variants: 4 (baseline, emotional, urgency, social_proof)
==================================================================

Running 4 variants concurrently...

==================================================================
EXPERIMENT RESULTS - Comparative Analysis
==================================================================

Variant         Score      Attention    Clarity    Relevance    Conversion
----------------------------------------------------------------------
baseline        72.0       15.0         22.0       18.0         17.0
emotional       82.0       20.0         19.0       22.0         21.0
urgency         84.0       22.0         20.0       19.0         23.0
social_proof    82.0       18.0         21.0       21.0         22.0

✓ Best Performing Variant: URGENCY
  Score: 84.0/100

Total Execution Time: 2.3s
Successful Variants: 4/4
```

## Results

Results are saved to the `results/` directory:

- Individual variant results in timestamped JSON files
- Comparative analysis across all variants
- Best performing variant identification
- Execution time and parallelism metrics

## Architecture

This experiment demonstrates the autoresearcher framework's concurrent execution capabilities:

- Uses `ConcurrentExperimentRunner` from the core library
- Runs multiple experiment instances in parallel using ThreadPoolExecutor
- Each variant is an independent `BaseExperiment` instance
- Results are collected and compared across variants

## Future Enhancements

- Add more use cases (HVAC, pest control, auto repair)
- Implement multi-cycle optimization
- A/B testing with real user feedback
- Integration with ad platforms for live testing
- Image/visual component optimization
