# Program: Image Gen Prompt Optimization with Nano Banana

## Objective

Maximize the composite image generation score (0-100) by iteratively refining
the prompt configuration in `prompt.py`. The score combines CLIP similarity,
aesthetic quality, and cross-seed consistency.

## Rules

1. **Edit only `prompt.py`** — `eval.py` is frozen.
2. **Loop forever** — NEVER STOP.
3. **Keep or revert** — after each eval, keep the change if score improved,
   otherwise `git checkout prompt.py` to revert.

## Cycle

```
1. Form a hypothesis about what prompt change will improve the score.
2. Edit prompt.py (one focused change per cycle).
3. git add prompt.py && git commit -m "<hypothesis>"
4. python eval.py   → read the score block from stdout.
5. If score >= best score so far → KEEP. Record in results.tsv.
   If score < best score        → REVERT: git checkout HEAD~1 -- prompt.py && git commit -m "revert: <hypothesis>"
6. Append row to results.tsv.
7. Go to 1.
```

## What You Can Change

- `POSITIVE_PROMPT` — the main generation prompt
- `NEGATIVE_PROMPT` — things to avoid
- `STYLE_TOKENS` — artistic style modifiers
- `TARGET_DESCRIPTION` — the subject matter (explore different scenes)
- `ASPECT_RATIO` — "1:1", "16:9", "9:16", "4:3", "3:4"
- `NUM_SEEDS` — how many images to generate (more = slower but more reliable consistency score)

## What You Must NOT Change

- `SEEDS` — fixed for reproducibility across runs.

## Hypothesis Space

- Prompt specificity: generic vs highly detailed descriptions
- Lighting terms: golden hour, soft diffused, dramatic, rim lighting
- Material descriptions: weathered oak, brushed copper, hand-thrown ceramic
- Composition: rule of thirds, leading lines, centered subject
- Artistic style: photorealistic vs painterly vs cinematic
- Negative prompt refinement: what artifacts to suppress
- Subject matter: try different scenes to find what the model excels at
- Color palette: warm vs cool, monochrome, complementary colors
- Texture emphasis: fabric, wood grain, metal patina, glass reflections
- Atmosphere: fog, dust motes, rain, steam, bokeh

## Timing

Each cycle takes ~60-90 seconds (API calls + scoring). Plan accordingly.

## Logging

Maintain `results.tsv` with columns:

```
commit	score	clip_score	aesthetic_score	consistency	status	description
```

- `status`: "keep" or "revert"
- `description`: brief note on what was tried

## Scoring Breakdown

- **Composite** = 0.4 * CLIP + 0.3 * Aesthetic + 0.3 * Consistency
- **CLIP score**: how well the image matches the prompt text (0-100)
- **Aesthetic score**: sharpness, color richness, contrast (0-100)
- **Consistency**: visual similarity across seeds (0-100, higher = more consistent)
