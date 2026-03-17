# Experiment 05: OOH Creative Optimization - Restaurant (1 Cycle)

**Date:** 2026-03-17
**Branch:** `autoresearch/mar17-ooh-creative-restaurant`
**Use Case:** Casa Bella Trattoria (Italian Restaurant)

## Overview

Ran 1 optimization cycle for OOH billboard creative optimization using the OOH Canvas scoring rubric (100 points total across 7 categories).

## Results Summary

| Cycle | Commit | Score | Tier | Status | Hypothesis |
|-------|--------|-------|------|--------|------------|
| 0 | d1f33c5 | 89.5 | minor-revisions | keep | Baseline - Casa Bella Trattoria |
| 1 | fde6696 | 88.5 | minor-revisions | discard | White headline/CTA for better contrast |

**Best Score:** 89.5 (baseline)
**Baseline:** 89.5
**Improvement:** 0.0 points (0%)
**Tier:** minor-revisions (80-89 range, needs 90+ for launch-ready)

## Detailed Scoring

### Baseline (Cycle 0) - Score: 89.5
- visual_hierarchy: 20.0 / 20 (perfect)
- color_contrast: 11.0 / 15 (needs improvement)
- brand_integration: 8.5 / 10 (good)
- message_effectiveness: 17.0 / 20 (good)
- format_optimization: 10.0 / 10 (perfect)
- industry_practices: 13.0 / 15 (needs improvement)
- regulatory_compliance: 10.0 / 10 (perfect)

**Configuration:**
- Headline: "Handmade Pasta Since 1987"
- Subheadline: "Farm-to-table Italian | Tue-Sun 11am-10pm | 247 Main St"
- CTA: "(555) BELLA-01"
- Format: bulletin (3.4:1 aspect ratio, 7 word max)
- Layout: hero-left
- Colors: Dark brown bg (#2D1B0E), warm tan headline (#C4956A), white subheadline, dark red CTA (#8B0000)

### Cycle 1 - Score: 88.5 (Discarded)
- visual_hierarchy: 18.0 / 20 (-2.0)
- color_contrast: 15.0 / 15 (+4.0)
- brand_integration: 5.5 / 10 (-3.0)
- message_effectiveness: 17.0 / 20 (no change)
- format_optimization: 10.0 / 10 (no change)
- industry_practices: 13.0 / 15 (no change)
- regulatory_compliance: 10.0 / 10 (no change)

**Net change:** -1.0 points

**Hypothesis:** Improve contrast by using white for headline and CTA
**Why it failed:** While color_contrast improved significantly (+4.0), the loss of brand color usage hurt brand_integration (-3.0) and visual hierarchy also decreased (-2.0). The brand colors are an important part of the scoring rubric.

## Key Insights

1. **Brand integration is critical:** Using brand colors (warm tan #C4956A) is heavily weighted in the scoring. Pure white headlines may improve contrast but lose brand identity points.

2. **Baseline is already strong:** 89.5 score is just 0.5 points away from launch-ready tier. Small optimizations are needed.

3. **Areas for improvement:**
   - color_contrast: 11.0/15 - Could gain 4 points
   - industry_practices: 13.0/15 - Could gain 2 points

4. **Trade-offs matter:** Improvements in one category can cause regressions in others. Need to find changes that improve multiple categories simultaneously.

## Technical Notes

- **Image generation:** Google Gemini API not available (GOOGLE_API_KEY not set), evaluations ran in text-only mode
- **LLM judge:** Used Bedrock Claude Haiku via inference profile (us.anthropic.claude-3-5-haiku-20241022-v1:0)
- **Evaluation time:** ~4 seconds per cycle (text-only mode)

## Branch Status

- **Branch:** `autoresearch/mar17-ooh-creative-restaurant`
- **Pushed to origin:** Yes
- **Commits:** 5 total (setup + baseline + model fix + cycle 1 + results)
- **Results file:** `results.tsv` committed and pushed

## Files Modified

- `experiments/05-ooh-creative/creative.py` - Baseline configuration for restaurant use case
- `experiments/05-ooh-creative/results.tsv` - Cycle results tracking
- `experiments/05-ooh-creative/eval.py` - Fixed Bedrock model ID to use inference profile

## Next Steps (If Continuing)

To reach launch-ready (90+), consider:
1. Adjust CTA color to improve contrast while maintaining brand integration
2. Optimize subheadline to boost industry_practices score
3. Try different formats (digital-landscape allows 10-word headlines vs bulletin's 7-word limit)
4. Test hero-right layout instead of hero-left
