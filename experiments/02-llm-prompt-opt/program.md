# autoresearch — Experiment 02: LLM Prompt Optimization Loop

You are an autonomous AI researcher optimizing an LLM prompt for sentiment classification. No GPU needed — this experiment uses Claude API calls.

## Setup

To set up a new experiment, work with the user to:

1. **Agree on a run tag**: propose a tag based on today's date (e.g. `mar16`). The branch `autoresearch/<tag>` must not already exist.
2. **Create the branch**: `git checkout -b autoresearch/<tag>` from current HEAD.
3. **Read the in-scope files**: Read these files for full context:
   - This file (`program.md`) — your instructions.
   - `eval.py` — frozen evaluator. **Do not modify.**
   - `data/eval_set.json` — frozen eval set. **Do not modify.**
   - `prompt.py` — the file you modify. Prompt config for the classifier.
4. **Verify setup**: Check that `ANTHROPIC_API_KEY` is set and `anthropic` package is installed. Run `python eval.py` to verify.
5. **Initialize results.tsv**: Create `results.tsv` with just the header row.
6. **Confirm and go**.

## Experimentation

Each eval cycle takes ~60 seconds and calls the Claude API. Cost is minimal (a few cents per cycle using Haiku).

**What you CAN do:**
- Modify `prompt.py` — this is the only file you edit. Everything is fair game: system prompt wording, few-shot examples, number of examples, output format instructions, chain-of-thought reasoning, label definitions, classification strategy.

**What you CANNOT do:**
- Modify `eval.py`. It is read-only.
- Modify `data/eval_set.json`. It is read-only.
- Change the model to something more expensive.
- Install new packages or add dependencies.

**The goal: get the highest accuracy.**

### Hypothesis Space (suggestions, not exhaustive)
- System prompt wording: be more specific about what each label means
- Few-shot example selection: more examples, harder examples, edge cases
- Number of few-shot examples: find the sweet spot (too few = underspecified, too many = expensive and slow)
- Output format instructions: force exact label output, discourage hedging
- Chain-of-thought: ask the model to reason before labeling (extract label from reasoning)
- Label definitions: define what counts as positive, negative, neutral explicitly
- Edge case handling: instruct how to handle mixed sentiment, sarcasm, backhanded compliments
- Decision boundary guidance: "if sentiment is mixed, classify based on the overall takeaway"
- Structured output: ask for JSON, or a specific format

### Simplicity Criterion
All else being equal, simpler is better. A small accuracy gain from a much more complex prompt is not worth it. Weigh complexity cost against improvement magnitude.

## Output Format

The evaluator prints a summary:
```
---
accuracy:        0.720
correct:         36
total:           50
cost_cents:      1.2
eval_seconds:    45.3
```

Extract: `grep "^accuracy:\|^cost_cents:" run.log`

## Logging Results

Log to `results.tsv` (tab-separated):
```
commit	accuracy	cost_cents	status	description
a1b2c3d	0.720	1.2	keep	baseline
```

Columns: commit (7 chars), accuracy, cost_cents, status (keep/discard/crash), description.

## The Experiment Loop

LOOP FOREVER:

1. Check git state
2. Edit `prompt.py` with an experimental idea
3. `git commit`
4. Run: `python eval.py > run.log 2>&1`
5. Read results: `grep "^accuracy:\|^cost_cents:" run.log`
6. If grep is empty → crash. Run `tail -n 50 run.log` for stack trace.
7. Record in results.tsv
8. If accuracy improved (higher) → keep the commit
9. If accuracy is equal or worse → `git reset` back

**First run**: Always establish baseline by running `prompt.py` as-is.

**Timeout**: Kill runs exceeding 5 minutes. Treat as failure.

**NEVER STOP**: Once the loop begins, do NOT pause to ask the human. You are autonomous. If you run out of ideas, think harder — try combining previous near-misses, try more radical changes. The loop runs until manually stopped.
