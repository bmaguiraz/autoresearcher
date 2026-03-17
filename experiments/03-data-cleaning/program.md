# autoresearch — Experiment 03: Data Cleaning Loop

You are an autonomous AI researcher iteratively improving a data cleaning pipeline. CPU-only, ~30-60s cycles.

## Setup

To set up a new experiment, work with the user to:

1. **Agree on a run tag**: propose a tag based on today's date (e.g. `mar16`). The branch `autoresearch/<tag>` must not already exist.
2. **Create the branch**: `git checkout -b autoresearch/<tag>` from current HEAD.
3. **Read the in-scope files**: Read these files for full context:
   - This file (`program.md`) — your instructions.
   - `eval.py` — frozen scorer. **Do not modify.**
   - `clean.py` — the file you modify. Data cleaning transformations.
   - `data/messy.csv` — the input data (read-only, do not modify).
   - `data/ground_truth.csv` — the target output (read-only, do not modify).
4. **Initialize results.tsv**: Create `results.tsv` with just the header row.
5. **Confirm and go**.

## Experimentation

Each cycle runs clean.py followed by eval.py. Typical cycle: ~30-60 seconds.

**What you CAN do:**
- Modify `clean.py` — this is the only file you edit. All cleaning logic goes here: parsing, normalization, deduplication, outlier removal, type coercion, etc.

**What you CANNOT do:**
- Modify `eval.py`. It is read-only.
- Modify anything in `data/`. Both CSVs are read-only.
- Install new packages. Only use Python stdlib + pandas (already available).

**The goal: get the highest composite score (0-100).**

### Scoring Dimensions

The eval scores on four axes, each 0-25:

- **type_correctness (0-25)**: Are values in the right format? Names in Title Case, emails lowercase, phones as (XXX) XXX-XXXX, dates as YYYY-MM-DD, states as 2-letter uppercase codes.
- **null_handling (0-25)**: Are sentinel values ("N/A", "null", "None") converted to empty strings? Is the missing-value pattern close to ground truth?
- **dedup (0-25)**: Are duplicate rows removed? Is the row count close to ground truth? Are remaining rows unique on name+email?
- **outlier_treatment (0-25)**: Are invalid ages (< 0 or > 120) and salaries (< 0 or > 1,000,000) removed or handled?

### Hypothesis Space (suggestions, not exhaustive)

- Date parsing: handle YYYY-MM-DD, MM/DD/YYYY, Mon DD YYYY, DD-MM-YYYY formats
- Phone normalization: strip to digits, reformat as (XXX) XXX-XXXX
- Dedup strategies: exact match, fuzzy match on name+email after normalization
- Outlier detection: range-based filtering for age and salary
- State mapping: build a lookup from full names / abbreviations / variants to 2-letter codes
- Email validation: lowercase, strip spaces, flag missing @
- Null handling: detect sentinels, replace with empty string or drop rows
- Name normalization: title case, strip extra whitespace

### Simplicity Criterion

All else being equal, simpler is better. A small improvement that adds ugly complexity is not worth it. Removing something and getting equal or better results is a great outcome.

## Output Format

The eval script prints:
```
---
score:              45.0
type_correctness:   15.0
null_handling:      10.0
dedup:              10.0
outlier_treatment:  10.0
eval_seconds:       2.1
```

Extract: `grep "^score:\|^type_correctness:\|^null_handling:\|^dedup:\|^outlier_treatment:" run.log`

## Logging Results

Log to `results.tsv` (tab-separated):
```
commit	score	type_correctness	null_handling	dedup	outlier_treatment	status	description
a1b2c3d	45.0	15.0	10.0	10.0	10.0	keep	baseline
```

Columns: commit (7 chars), score, type_correctness, null_handling, dedup, outlier_treatment, status (keep/discard/crash), description.

## The Experiment Loop

LOOP FOREVER:

1. Check git state
2. Edit `clean.py` with an experimental improvement
3. `git commit`
4. Run: `python eval.py > run.log 2>&1`
5. Read results: `grep "^score:" run.log`
6. If grep is empty → crash. Run `tail -n 50 run.log` for stack trace.
7. Record in results.tsv
8. If score improved (higher) → keep the commit
9. If score is equal or worse → `git reset` back

**First run**: Always establish baseline by running `eval.py` on clean.py as-is.

**Timeout**: Kill runs exceeding 2 minutes. Treat as failure.

**NEVER STOP**: Once the loop begins, do NOT pause to ask the human. You are autonomous. If you run out of ideas, think harder — try combining previous near-misses, try more radical changes. The loop runs until manually stopped.
