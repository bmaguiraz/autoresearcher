# Experiment 05: OOH Creative Optimization

## Overview

Autonomous AI researcher experiment for optimizing Out-of-Home (OOH) advertising creative using iterative testing and the OOH Canvas scoring rubric.

**Experiment Type**: Autoresearch autonomous optimization
**Goal**: Maximize composite score (0-100) across 7 evaluation categories

## Scoring - OOH Canvas (100 points)

| Category | Max Points | What's Evaluated |
|---|---|---|
| visual-hierarchy | 20 | Headline word count vs format max, total copy brevity, all elements present |
| color-contrast | 15 | WCAG 2.1 contrast ratios (>=4.5:1 target), color diversity |
| brand-integration | 10 | Brand primary/secondary/accent colors used, palette cohesion |
| message-effectiveness | 20 | Clear CTA, benefit-driven copy, context-appropriate, reflects differentiator (LLM-judged) |
| format-optimization | 10 | Valid format, valid layout, layout-format compatibility |
| industry-practices | 15 | Category best practices, required business info present, trust signals (LLM-judged) |
| regulatory-compliance | 10 | No prohibited claims, within word limits, no misleading language |

## Usage

### Run via Autoresearch

```bash
# From project root
/autoresearch run 05-ooh-creative --cycles 1 --use-case plumber
```

### Run Directly

```bash
cd experiments/05-ooh-creative
python eval.py
```

### Available Use Cases

- `plumber` - Quick Flow Plumbing (emergency services)
- `restaurant` - Casa Bella Trattoria (Italian dining)

Switch use cases by editing `USE_CASE` in `creative.py`.

## Files

- `creative.py` - Creative brief configuration (edit this to optimize)
- `eval.py` - Scorer implementing OOH Canvas rubric (frozen, do not edit)
- `generate.py` - Image generator using Imagen 3 (frozen, do not edit)
- `program.md` - Full autoresearch instructions for autonomous AI agent
- `config/*.json` - Brand configurations (frozen, do not edit)
- `results.tsv` - Experiment results log

## Results

Results are logged to `results.tsv` with columns:
- commit (7 chars)
- score, tier
- Individual category scores
- status (keep/discard/crash)
- description

## Architecture

This is an **autoresearch experiment** designed for autonomous AI optimization:

1. AI agent reads `program.md` for instructions
2. Agent iteratively modifies `creative.py` to test hypotheses
3. Each change is committed and evaluated via `eval.py`
4. Results are logged and the agent continues optimization
5. Process runs autonomously until manually stopped

See `program.md` for complete methodology and instructions.
