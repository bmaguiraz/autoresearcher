# Experiment 05: OOH Creative Optimization - WriteFit (1 Cycle, Round 3)

**Date:** 2026-03-18
**Branch:** `MOR-39-ooh-creative-writefit-round3`
**Use Case:** WriteFit.ai (EdTech - Writing Practice Platform)
**Linear Issue:** [MOR-39](https://linear.app/maguireb/issue/MOR-39/autoresearch-ooh-creative-writefit-1-cycle-round-3)

## Overview

Ran 1 optimization cycle for OOH billboard creative optimization using the OOH Canvas scoring rubric (100 points total across 7 categories).

## Results Summary

| Cycle | Commit | Score | Tier | Status | Hypothesis |
|-------|--------|-------|------|--------|------------|
| 0 | 52692dd | 87.0 | minor-revisions | keep | Baseline - WriteFit creative |
| 1 | 68459d3 | 91.5 | launch-ready | keep | All-white text for maximum contrast |

**Best Score:** 91.5 (cycle 1) ✅
**Baseline:** 87.0
**Improvement:** +4.5 points (5.2%)
**Tier:** launch-ready (90-100 range, ready for deployment)

## Detailed Scoring

### Baseline (Cycle 0) - Score: 87.0
- visual_hierarchy: 18.0 / 20
- color_contrast: 11.0 / 15 (needs improvement)
- brand_integration: 10.0 / 10 (perfect)
- message_effectiveness: 16.0 / 20
- format_optimization: 10.0 / 10 (perfect)
- industry_practices: 12.0 / 15
- regulatory_compliance: 10.0 / 10 (perfect)

**Configuration:**
- Headline: "Practice Writing That Matters" (5 words)
- Subheadline: "AI-powered exercises from your essay | Never writes for you | writefit.ai"
- CTA: "Try Free | writefit.ai"
- Format: digital-landscape (16:9, 10 word max)
- Layout: centered
- Colors: Dark purple-gray bg (#5B5670), white headline (#FFFFFF), off-white subheadline (#FAFAF8), purple CTA (#6B47DC)

### Cycle 1 - Score: 91.5 (KEPT) ✅
- visual_hierarchy: 20.0 / 20 (+2.0) ✓ PERFECT
- color_contrast: 15.0 / 15 (+4.0) ✓ PERFECT
- brand_integration: 8.5 / 10 (-1.5) ⚠️
- message_effectiveness: 16.0 / 20 (no change)
- format_optimization: 10.0 / 10 (no change) PERFECT
- industry_practices: 12.0 / 15 (no change)
- regulatory_compliance: 10.0 / 10 (no change) PERFECT

**Net change:** +4.5 points

**Hypothesis:** Improve color_contrast by using white for all text elements instead of off-white and purple.

**Why it succeeded:**
- color_contrast improved to perfect score (+4.0) by using pure white (#FFFFFF) for all text on dark background
- visual_hierarchy also improved to perfect (+2.0) with cleaner, more uniform text treatment
- brand_integration decreased slightly (-1.5) due to not using secondary purple (#6B47DC) color
- Net gain of 4.5 points pushed creative into launch-ready tier

**Key insight:** High contrast is critical for OOH visibility. The 4-point gain in contrast and 2-point gain in visual hierarchy outweighed the 1.5-point loss in brand integration. Pure white text on dark background maximizes readability for billboards.

## Key Insights

1. **Launch-ready achieved:** 91.5 score exceeds the 90-point threshold for launch-ready tier. The creative is production-ready.

2. **Contrast is king for OOH:** Moving from mixed colors (off-white, purple) to all-white text delivered the largest single improvement. Outdoor visibility demands maximum contrast.

3. **Perfect scores achieved (4 out of 7 categories):**
   - visual_hierarchy: 20.0/20
   - color_contrast: 15.0/15
   - format_optimization: 10.0/10
   - regulatory_compliance: 10.0/10

4. **Trade-offs were worth it:** Losing 1.5 points on brand_integration by not using the purple accent color was acceptable given the 6.5-point gain in visual_hierarchy + color_contrast.

5. **Remaining opportunities (8.5 points):**
   - message_effectiveness: 16.0/20 (+4 possible)
   - industry_practices: 12.0/15 (+3 possible)
   - brand_integration: 8.5/10 (+1.5 possible)

## Technical Notes

- **Image generation:** Google Gemini API not available (GOOGLE_API_KEY not set), evaluations ran in text-only mode
- **LLM judge:** Used Bedrock Claude Haiku via inference profile (us.anthropic.claude-3-5-haiku-20241022-v1:0)
- **Evaluation time:** ~4.3 seconds per cycle (text-only mode)

## Branch Status

- **Branch:** `MOR-39-ooh-creative-writefit-round3`
- **Ready to push:** Yes
- **Commits:** 3 total (init baseline + cycle 1 + results)
- **Results file:** `results.tsv` committed

## Files Modified

- `experiments/05-ooh-creative/creative.py` - WriteFit baseline + cycle 1 optimization
- `experiments/05-ooh-creative/results.tsv` - Cycle results tracking
- `experiments/05-ooh-creative/EXPERIMENT_SUMMARY_MOR39.md` - This summary

## Recommendation

**The cycle 1 creative (91.5, launch-ready tier) is ready for deployment.** The creative achieves:
- Perfect color contrast for outdoor visibility (15.0/15)
- Perfect visual hierarchy (20.0/20)
- Perfect format configuration (10.0/10)
- Perfect regulatory compliance (10.0/10)
- Strong messaging and brand integration

Further optimization would require multi-cycle experiments to explore:
1. Message effectiveness improvements through headline/subheadline refinement
2. Industry best practices enhancements (trust signals, social proof)
3. Balance between brand color usage and contrast requirements

## Comparison to Previous WriteFit Experiments

Previous WriteFit baseline (from results.tsv history):
- Commit 2f53866: 86.0 score (minor-revisions)
- Commit 0bfae0f: 88.0 score (improved with white text)

**This round (MOR-39):**
- Baseline: 87.0 (similar starting point)
- Final: 91.5 (achieved launch-ready tier)

The all-white text optimization proved successful, gaining 4.5 points and reaching production-ready status in just 1 cycle.
