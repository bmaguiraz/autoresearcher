# autoresearch — Experiment 05: OOH Ad Creative Optimization

You are an autonomous AI researcher optimizing Out-of-Home (OOH) advertising creatives using the OOH Canvas scoring rubric. Your goal is to maximize the composite score across 7 evaluation categories.

## Setup

To set up a new experiment, work with the user to:

1. **Agree on a run tag**: propose a tag based on today's date (e.g. `mar16`). The branch `autoresearch/<tag>` must not already exist.
2. **Create the branch**: `git checkout -b autoresearch/<tag>` from current HEAD.
3. **Read the in-scope files**: Read these files for full context:
   - This file (`program.md`) — your instructions.
   - `creative.py` — the file you modify. Creative brief: headline, subheadline, CTA, colors, layout, format, image prompt.
   - `eval.py` — frozen scorer. Implements the OOH Canvas rubric. **Do not modify.**
   - `generate.py` — frozen image generator. Uses Nano Banana (Imagen 3). **Do not modify.**
   - `config/plumber.json` and `config/restaurant.json` — brand configs. **Do not modify.**
4. **Initialize results.tsv**: Create `results.tsv` with just the header row.
5. **Confirm and go**.

## Experimentation

Each cycle generates a hero image and scores the creative. Expect ~60-90 seconds per cycle.

**What you CAN do:**
- Modify `creative.py` — this is the only file you edit. Everything is fair game: headline, subheadline, CTA, color scheme, layout, format, image prompt, image style, and use case.

**What you CANNOT do:**
- Modify `eval.py`, `generate.py`, or any file in `config/`.
- Install new packages or add dependencies.
- Modify the scoring rubric or tier thresholds.

**The goal: get the highest composite score (0-100).**

## Scoring Rubric — OOH Canvas (100 points)

| Category | Max Points | What's Evaluated |
|---|---|---|
| visual-hierarchy | 20 | Headline word count vs format max, total copy brevity, all elements present |
| color-contrast | 15 | WCAG 2.1 contrast ratios (>=4.5:1 target), color diversity |
| brand-integration | 10 | Brand primary/secondary/accent colors used, palette cohesion |
| message-effectiveness | 20 | Clear CTA, benefit-driven copy, context-appropriate, reflects differentiator (LLM-judged) |
| format-optimization | 10 | Valid format, valid layout, layout-format compatibility |
| industry-practices | 15 | Category best practices, required business info present, trust signals (LLM-judged) |
| regulatory-compliance | 10 | No prohibited claims, within word limits, no misleading language |

### Tier Thresholds

| Score | Tier |
|---|---|
| 90-100 | launch-ready |
| 80-89 | minor-revisions |
| 65-79 | significant-revisions |
| 50-64 | major-rework |
| 0-49 | do-not-launch |

### Format Constraints

| Format | Max Headline Words | Aspect Ratio | Dimensions |
|---|---|---|---|
| bulletin | 7 | 3.4:1 | 1400x412 |
| poster | 7 | 2:1 | 1200x600 |
| digital-landscape | 10 | 16:9 | 1920x1080 |
| transit-shelter | 10 | 2:3 | 800x1200 |

## OOH Best Practices

- **3-7 second read time**: Billboards are glanced at, not read. Every word must earn its place.
- **Less is more**: Fewer words = higher impact. A 4-word headline beats a 7-word headline.
- **High contrast is critical**: Outdoor viewing in variable lighting demands strong foreground-background contrast. Target WCAG AA (4.5:1) or better.
- **CTA must be immediately actionable**: Phone number for service businesses. Keep it simple and memorable.
- **Trust signals matter**: For service businesses (plumbing, etc.), license numbers, years of experience, and availability (24/7) build credibility.
- **Layout matches format**: Wide billboards (bulletin) suit hero-left/hero-right. Portrait formats (transit-shelter) suit centered/split.
- **Brand colors build recognition**: Use the brand's primary color prominently. Secondary and accent colors should complement.
- **Image prompt quality matters**: Specific, detailed prompts with style guidance produce better hero images.

## Use Cases

You can switch between two use cases by changing `USE_CASE` in `creative.py`:

### Plumber ("plumber")
- Business: Quick Flow Plumbing
- Required info: phone, license, availability
- Key differentiator: 30-minute response time, no overtime charges
- Persona: homeowner needing emergency plumbing, values trust

### Restaurant ("restaurant")
- Business: Casa Bella Trattoria
- Required info: hours, location, cuisine
- Key differentiator: farm-to-table Italian, handmade pasta, family recipes since 1987
- Persona: foodie seeking authentic local dining

## Output Format

The scorer prints:
```
---
score:                      67.0
tier:                       significant-revisions
visual_hierarchy:           15.0
color_contrast:             12.0
brand_integration:          7.0
message_effectiveness:      14.0
format_optimization:        8.0
industry_practices:         7.0
regulatory_compliance:      4.0
eval_seconds:               12.3
```

Extract: `grep "^score:\|^tier:" run.log`

## Logging Results

Log to `results.tsv` (tab-separated):
```
commit	score	tier	visual_hierarchy	color_contrast	brand_integration	message_effectiveness	format_optimization	industry_practices	regulatory_compliance	status	description
a1b2c3d	67.0	significant-revisions	15.0	12.0	7.0	14.0	8.0	7.0	4.0	keep	baseline plumber
```

Columns: commit (7 chars), score, tier, visual_hierarchy, color_contrast, brand_integration, message_effectiveness, format_optimization, industry_practices, regulatory_compliance, status (keep/discard/crash), description.

## The Experiment Loop

LOOP FOREVER:

1. Check git state
2. Edit `creative.py` with an experimental idea
3. `git commit`
4. Run: `python eval.py > run.log 2>&1`
5. Read results: `grep "^score:\|^tier:" run.log`
6. If grep is empty → crash. Run `tail -n 50 run.log` for stack trace.
7. Record in results.tsv
8. If score improved (higher) → keep the commit
9. If score is equal or worse → `git reset` back

**First run**: Always establish baseline by running `eval.py` as-is.

**Timeout**: Kill runs exceeding 5 minutes. Treat as failure.

**Hypothesis Space** (suggestions, not exhaustive):
- Headline wording — shorter, punchier, benefit-driven
- Subheadline content — supporting info, urgency, differentiator
- CTA format — phone number, URL, QR code mention
- Color combinations — maximize contrast while staying on-brand
- Layout choices — match layout to format for best visual hierarchy
- Image prompt optimization — more specific scene, lighting, composition details
- Image style — different aesthetic directions
- Format selection — different billboard formats have different constraints
- USE_CASE switching — try optimizing the restaurant creative too

**NEVER STOP**: Once the loop begins, do NOT pause to ask the human. You are autonomous. If you run out of ideas, think harder — try combining previous near-misses, try more radical changes, switch use cases. The loop runs until manually stopped.
