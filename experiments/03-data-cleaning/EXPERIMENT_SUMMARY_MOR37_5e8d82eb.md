# Autoresearch Experiment Summary: MOR-37

**Issue:** [MOR-37](https://linear.app/maguireb/issue/MOR-37/autoresearch-data-cleaning-pipeline-2-cycles-round-3)
**Title:** Data Cleaning Pipeline (2 cycles, round 3)
**Session ID:** 5e8d82eb
**Date:** 2026-03-18
**Branch:** autoresearch/MOR-37-5e8d82eb

## Objective

Run 2 optimization cycles on the data cleaning pipeline (baseline + 2 hypotheses) to maintain or improve the composite score.

## Results Summary

| Metric | Baseline | Final | Change |
|--------|----------|-------|--------|
| **Composite Score** | 100.0 | 100.0 | ✅ 0.0 |
| Type Correctness | 25.0 | 25.0 | 0.0 |
| Null Handling | 25.0 | 25.0 | 0.0 |
| Deduplication | 25.0 | 25.0 | 0.0 |
| Outlier Treatment | 25.0 | 25.0 | 0.0 |

**Status:** ✅ **SUCCESS** - Maintained perfect score with improved code quality

## Experiment Details

### Cycle Log

| Cycle | Commit | Score | Type | Null | Dedup | Outlier | Status | Description |
|-------|--------|-------|------|------|-------|---------|--------|-------------|
| Baseline | cab5f03 | 100.0 | 25.0 | 25.0 | 25.0 | 25.0 | keep | Baseline - MOR-37 Round 3 (session: 5e8d82eb) |
| Cycle 1a | 44824db | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | crash | FAILED - Vectorized string conversion (dtype assignment error) |
| Cycle 1 | a416af5 | 100.0 | 25.0 | 25.0 | 25.0 | 25.0 | keep | Simplify phone normalization with ternary expression |
| Cycle 2 | cde3060 | 100.0 | 25.0 | 25.0 | 25.0 | 25.0 | keep | Check length of upper variable in normalize_state |

### Cycle 1a: Vectorized String Conversion (FAILED)

**Hypothesis:** Replace lambda function with vectorized mask-based operations for better performance.

**Change:**
```python
# Before:
for col, min_val, max_val in [("age", 0, 120), ("salary", 0, 1_000_000)]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[df[col].isna() | df[col].between(min_val, max_val)]
    df[col] = df[col].apply(lambda x: str(int(x)) if pd.notna(x) else "")

# After (FAILED):
for col, min_val, max_val in [("age", 0, 120), ("salary", 0, 1_000_000)]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[df[col].isna() | df[col].between(min_val, max_val)]
    mask = df[col].notna()
    df.loc[mask, col] = df.loc[mask, col].astype(int).astype(str)
    df.loc[~mask, col] = ""
```

**Result:** ❌ **CRASH** - Pandas dtype assignment error. Cannot assign string array to float64 column using .loc indexer. Learned that vectorized assignment is not always straightforward with mixed dtypes.

### Cycle 1: Simplify Phone Normalization

**Hypothesis:** Consolidate if-statement into inline ternary expression for cleaner code.

**Change:**
```python
# Before:
def normalize_phone(phone):
    if pd.isna(phone) or phone == "":
        return ""
    digits = re.sub(r"\D", "", str(phone))
    if len(digits) == 11 and digits[0] == "1":
        digits = digits[1:]
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}" if len(digits) == 10 else ""

# After:
def normalize_phone(phone):
    if pd.isna(phone) or phone == "":
        return ""
    digits = re.sub(r"\D", "", str(phone))
    # Strip leading 1 from 11-digit numbers
    digits = digits[1:] if len(digits) == 11 and digits.startswith("1") else digits
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}" if len(digits) == 10 else ""
```

**Result:** ✅ Maintained perfect score (100.0) with more Pythonic code using ternary expression.

### Cycle 2: Check Length of Upper Variable

**Hypothesis:** Improve consistency by checking length of the variable we're actually using and returning.

**Change:**
```python
# Before:
def normalize_state(state):
    if pd.isna(state) or state == "":
        return ""
    s = str(state).lower()
    if mapped := STATE_MAP.get(s):
        return mapped
    upper = s.upper()
    return upper if len(s) == 2 and upper in VALID_STATES else ""

# After:
def normalize_state(state):
    if pd.isna(state) or state == "":
        return ""
    s = str(state).lower()
    if mapped := STATE_MAP.get(s):
        return mapped
    upper = s.upper()
    return upper if len(upper) == 2 and upper in VALID_STATES else ""
```

**Result:** ✅ Maintained perfect score (100.0) with improved variable consistency.

## Key Insights

1. **Vectorization Trade-offs:** While vectorized operations are generally faster, they can introduce complexity with pandas dtype handling. The lambda approach, while slightly slower, is more robust for mixed-type conversions.

2. **Code Quality Focus:** With perfect scores already achieved, optimization focused on code clarity and consistency rather than performance gains.

3. **Incremental Improvements:** Small refinements to conditional logic and variable naming improve code maintainability without risking functionality.

4. **Perfect Score Maintenance:** All successful cycles maintained the maximum score (100.0/100.0), demonstrating the pipeline's robustness.

## Files Modified

- `experiments/03-data-cleaning/clean.py` - Improved phone normalization and state validation logic
- `experiments/03-data-cleaning/results.tsv` - Added baseline and 2 cycle results

## Reproducibility

```bash
# Clone and checkout
git clone https://github.com/bmaguiraz/autoresearcher.git
cd autoresearcher
git checkout autoresearch/MOR-37-5e8d82eb

# Run experiment
cd experiments/03-data-cleaning
python eval.py
```

## Technical Details

- **Evaluation time:** ~0.5 seconds per cycle
- **Dataset:** messy.csv with multiple data quality issues
- **Scoring dimensions:** 4 categories (type_correctness, null_handling, dedup, outlier_treatment), each worth 25 points
- **Python version:** 3.10+
- **Dependencies:** pandas (stdlib + pandas only)

## Next Steps

1. Merge this PR to preserve the code quality improvements
2. Continue iterative refinement in future rounds
3. The pipeline maintains optimal performance (100.0/100.0)

---

**Session:** 5e8d82eb
**Generated:** 2026-03-18 11:22 UTC
🤖 Powered by Claude Code
