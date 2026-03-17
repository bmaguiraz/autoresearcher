# Experiment 05: OOH Creative Optimization

## Overview

This experiment optimizes Out-of-Home (OOH) advertising creative for various use cases. OOH includes billboards, transit ads, and other outdoor advertising where brevity and impact are critical.

## Methodology

The experiment tests concurrent optimization by running multiple creative variants in parallel. Each variant is evaluated on:

- **Attention** (0-25): Eye-catching, memorable, stands out
- **Clarity** (0-25): Clear message, obvious call-to-action
- **Relevance** (0-25): Resonates with target audience
- **Conversion Potential** (0-25): Likelihood to drive desired action

**Composite Score**: Sum of all dimensions (0-100)

## Parallel Execution Strategy

To test 4-way per-issue parallelism, the experiment runs 4 creative variants concurrently:

1. **Baseline**: Direct, feature-focused messaging
2. **Emotional**: Appeal to customer pain points and desires
3. **Urgency**: Time-sensitive offers and scarcity
4. **Social Proof**: Trust signals and testimonials

Each variant is evaluated independently, then results are compared.

## Use Cases

### Plumber
- **Target**: Homeowners with emergency plumbing needs
- **Key Messages**: 24/7 availability, licensed/insured, fast response
- **Pain Points**: Burst pipes, clogged drains, water damage
- **Call-to-Action**: Phone number, "Call Now"

### Future Use Cases
- HVAC contractor
- Pest control
- Auto repair
- Restaurant/dining
- Real estate

## Constraints

- **Headline**: Max 50 characters
- **Body**: Max 100 characters
- **Style**: Professional, trustworthy
- **Format**: High-contrast, readable at distance

## Expected Outcomes

- Validate concurrent execution framework
- Identify which creative strategy performs best for plumber use case
- Establish baseline metrics for future optimization cycles
- Test scalability of parallel evaluation

## Running the Experiment

```bash
cd experiments/05-ooh-creative
python runner.py --use-case plumber --cycles 1
```

Or from project root:
```bash
python experiments/05-ooh-creative/runner.py --use-case plumber --cycles 1
```

## Results Format

Results are saved to `results/` directory with:
- Individual variant scores
- Comparative analysis
- Best performing variant
- Execution time and parallelism metrics
