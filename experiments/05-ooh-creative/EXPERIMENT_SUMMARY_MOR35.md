# Experiment 05: OOH Creative Optimization - Restaurant (1 Cycle, Round 3)

**Date:** 2026-03-17
**Branch:** `autoresearch/mor35-restaurant-r3`
**Use Case:** Casa Bella Trattoria (Italian Restaurant)
**Linear Issue:** [MOR-35](https://linear.app/maguireb/issue/MOR-35/autoresearch-ooh-creative-restaurant-1-cycle-round-3)

## Overview

Ran 1 optimization cycle for OOH billboard creative optimization using the OOH Canvas scoring rubric (100 points total across 7 categories).

## Results Summary

| Cycle | Commit | Score | Tier | Status | Hypothesis |
|-------|--------|-------|------|--------|------------|
| 0 | 016c6a7 | 90.0 | launch-ready | keep | Baseline - Restaurant creative |
| 1 | 16e1e0b | 88.5 | minor-revisions | discard | Accent color for CTA |

**Best Score:** 90.0 (baseline)
**Baseline:** 90.0
**Improvement:** 0.0 points (0%)
**Tier:** launch-ready (90-100 range, ready for deployment)

## Detailed Scoring

### Baseline (Cycle 0) - Score: 90.0 ✅
- visual_hierarchy: 18.0 / 20
- color_contrast: 15.0 / 15 (perfect)
- brand_integration: 7.0 / 10
- message_effectiveness: 17.0 / 20
- format_optimization: 10.0 / 10 (perfect)
- industry_practices: 13.0 / 15
- regulatory_compliance: 10.0 / 10 (perfect)

**Configuration:**
- Headline: "Taste Real Italy Downtown"
- Subheadline: "Handmade pasta daily, family recipes since 1987 | Tue-Sun 11am-10pm"
- CTA: "247 Main St | (555) BELLA-01"
- Format: bulletin (3.4:1 aspect ratio, 7 word max)
- Layout: hero-left
- Colors: Dark brown bg (#2D1B0E), white headline (#FFFFFF), warm tan subheadline/CTA (#C4956A)

### Cycle 1 - Score: 88.5 (Discarded)
- visual_hierarchy: 18.0 / 20 (no change)
- color_contrast: 11.0 / 15 (-4.0) ⚠️
- brand_integration: 8.5 / 10 (+1.5) ✓
- message_effectiveness: 17.0 / 20 (no change)
- format_optimization: 10.0 / 10 (no change)
- industry_practices: 14.0 / 15 (+1.0) ✓
- regulatory_compliance: 10.0 / 10 (no change)

**Net change:** -1.5 points

**Hypothesis:** Improve brand_integration by using all 3 brand colors (added accent #8B0000 dark red for CTA) and emphasize heritage in headline.

**Why it failed:** While brand_integration improved (+1.5) and industry_practices improved (+1.0), the dark red CTA significantly hurt color_contrast (-4.0). The net result was a loss of 1.5 points.

**Key insight:** Color contrast is heavily weighted. Dark red (#8B0000) on dark brown (#2D1B0E) has poor contrast. The baseline's warm tan (#C4956A) provides much better contrast while still using brand colors.

## Key Insights

1. **Baseline is already launch-ready:** 90.0 score achieves the launch-ready tier threshold. The creative is production-ready as-is.

2. **Color contrast vs brand integration trade-off:** Using the dark red accent color improved brand_integration but severely hurt color_contrast. The 4-point contrast loss outweighed the 1.5-point brand gain.

3. **Warm tan is optimal for OOH:** The #C4956A warm tan achieves both good contrast (15.0/15) and brand alignment (secondary brand color).

4. **Perfect scores achieved:**
   - color_contrast: 15.0/15
   - format_optimization: 10.0/10
   - regulatory_compliance: 10.0/10

5. **Remaining opportunities (10 points):**
   - brand_integration: 7.0/10 (+3 possible)
   - message_effectiveness: 17.0/20 (+3 possible)
   - visual_hierarchy: 18.0/20 (+2 possible)
   - industry_practices: 13.0/15 (+2 possible)

## Technical Notes

- **Image generation:** Google Gemini API not available (GOOGLE_API_KEY not set), evaluations ran in text-only mode
- **LLM judge:** Used Bedrock Claude Haiku via inference profile (us.anthropic.claude-3-5-haiku-20241022-v1:0)
- **Evaluation time:** ~4.5 seconds per cycle (text-only mode)

## Branch Status

- **Branch:** `autoresearch/mor35-restaurant-r3`
- **Ready to push:** Yes
- **Commits:** 3 total (init + baseline + cycle 1 results)
- **Results file:** `results.tsv` committed

## Files Modified

- `experiments/05-ooh-creative/creative.py` - Restaurant baseline configuration
- `experiments/05-ooh-creative/results.tsv` - Cycle results tracking
- `experiments/05-ooh-creative/EXPERIMENT_SUMMARY_MOR35.md` - This summary

## Recommendation

The baseline creative (90.0, launch-ready tier) is ready for deployment. The creative achieves:
- Perfect color contrast for outdoor visibility
- Complete regulatory compliance
- Optimal format configuration
- Strong message effectiveness and visual hierarchy

Further optimization would require multi-cycle experiments to explore combinations of:
1. Different headline phrasing to boost message_effectiveness
2. Alternative color schemes that maintain contrast while improving brand_integration
3. Subheadline optimization for industry_practices improvements
