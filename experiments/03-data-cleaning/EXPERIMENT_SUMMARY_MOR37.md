# Experiment 03: Data Cleaning Pipeline - MOR-37 (2 Cycles, Round 3)

**Date:** 2026-03-18
**Branch:** `autoresearch/MOR-37-d61511d1`
**Session ID:** d61511d1
**Linear Issue:** [MOR-37](https://linear.app/maguireb/issue/MOR-37/autoresearch-data-cleaning-pipeline-2-cycles-round-3)

## Overview

Ran 2 optimization cycles for the data cleaning pipeline, focusing on code quality improvements while maintaining the perfect 100/100 score.

## Results Summary

| Cycle | Commit | Score | Type | Null | Dedup | Outlier | Status | Description |
|-------|--------|-------|------|------|-------|---------|--------|-------------|
| Baseline | b2484c1 | 100.0 | 25.0 | 25.0 | 25.0 | 25.0 | keep | Baseline - Round 3 |
| 1 | 4dd339c | 100.0 | 25.0 | 25.0 | 25.0 | 25.0 | keep | Consolidate outlier filtering and numeric conversion |
| 2 | 469be26 | 100.0 | 25.0 | 25.0 | 25.0 | 25.0 | keep | Simplify phone normalization logic |

**Best Score:** 100.0/100.0 (maintained across all cycles)
**Improvement:** 0.0 points (maintained perfect score)
**Result:** Code quality improvements with no score regression

## Detailed Analysis

### Baseline (Commit: b2484c1) - Score: 100.0
- **type_correctness**: 25.0/25.0 (perfect)
- **null_handling**: 25.0/25.0 (perfect)
- **dedup**: 25.0/25.0 (perfect)
- **outlier_treatment**: 25.0/25.0 (perfect)

The baseline already achieved a perfect score across all metrics:
- All data types correctly formatted (names in Title Case, emails lowercase, phones as (XXX) XXX-XXXX, dates as YYYY-MM-DD, states as 2-letter codes)
- Sentinel values ("N/A", "null", "None") properly converted to empty strings using regex pattern
- Duplicate rows removed (unique on name+email)
- Invalid ages (<0 or >120) and salaries (<0 or >1,000,000) properly filtered

### Cycle 1 (Commit: 4dd339c) - Score: 100.0 (KEEP)

**Hypothesis:** Consolidate outlier filtering and numeric conversion to reduce dataframe operations

**Change:**
```python
# Before (lines 103-111):
# Outlier filtering
df["age"] = pd.to_numeric(df["age"], errors="coerce")
df["salary"] = pd.to_numeric(df["salary"], errors="coerce")
df = df[df["age"].isna() | df["age"].between(0, 120)]
df = df[df["salary"].isna() | df["salary"].between(0, 1_000_000)]

# Convert numeric fields back to strings
for col in ["age", "salary"]:
    df[col] = df[col].apply(lambda x: str(int(x)) if pd.notna(x) else "")

# After:
# Outlier filtering with conversion to strings
for col in ["age", "salary"]:
    numeric_vals = pd.to_numeric(df[col], errors="coerce")
    if col == "age":
        valid = numeric_vals.isna() | numeric_vals.between(0, 120)
    else:  # salary
        valid = numeric_vals.isna() | numeric_vals.between(0, 1_000_000)
    df = df[valid]
    df[col] = numeric_vals[valid].apply(lambda x: str(int(x)) if pd.notna(x) else "")
```

**Results:**
- **Score**: 100.0/100.0 (maintained perfect score)
- **type_correctness**: 25.0/25.0 (no change)
- **null_handling**: 25.0/25.0 (no change)
- **dedup**: 25.0/25.0 (no change)
- **outlier_treatment**: 25.0/25.0 (no change)

**Why it succeeded:** The refactored code keeps related logic together:
- Single loop for both age and salary processing
- Outlier filtering and string conversion happen in the same iteration
- Clearer separation of concerns between columns
- No performance degradation

### Cycle 2 (Commit: 469be26) - Score: 100.0 (KEEP)

**Hypothesis:** Simplify phone normalization with more concise conditional expressions

**Change:**
```python
# Before (lines 32-40):
def normalize_phone(phone):
    if pd.isna(phone) or phone == "":
        return ""
    digits = re.sub(r"\D", "", str(phone))
    if digits.startswith("1") and len(digits) == 11:
        digits = digits[1:]
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return ""

# After:
def normalize_phone(phone):
    if pd.isna(phone) or phone == "":
        return ""
    digits = re.sub(r"\D", "", str(phone))
    # Strip leading 1 from 11-digit numbers
    digits = digits[1:] if len(digits) == 11 and digits[0] == "1" else digits
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}" if len(digits) == 10 else ""
```

**Results:**
- **Score**: 100.0/100.0 (maintained perfect score)
- **type_correctness**: 25.0/25.0 (no change)
- **null_handling**: 25.0/25.0 (no change)
- **dedup**: 25.0/25.0 (no change)
- **outlier_treatment**: 25.0/25.0 (no change)

**Why it succeeded:** The simplified code is more Pythonic:
- Ternary operator for leading '1' removal is more concise
- Single-line conditional return reduces boilerplate
- More readable and maintainable
- Identical functionality with fewer lines

## Key Insights

1. **Code already optimized**: The baseline was already at 100/100, indicating the data cleaning logic is fully optimized for the scoring rubric.

2. **Focus on code quality**: With perfect scores, the optimization focused on making the code more maintainable and readable through:
   - Consolidating related operations
   - Using more concise conditional expressions
   - Improving code organization

3. **Successful refactoring patterns**:
   - **Cycle 1**: Grouping related logic (outlier filtering + conversion) improved clarity
   - **Cycle 2**: Using ternary operators reduced boilerplate while maintaining readability

4. **No performance regression**: All optimizations maintained the perfect 100/100 score while improving code quality.

## Technical Details

- **Evaluation time**: ~0.5 seconds per cycle
- **Dataset**: messy.csv with multiple data quality issues (sentinel values, duplicates, outliers, format inconsistencies)
- **Scoring dimensions**: 4 categories (type_correctness, null_handling, dedup, outlier_treatment), each worth 25 points
- **Python version**: 3.10+
- **Dependencies**: pandas (stdlib + pandas only, no additional packages)

## Branch Status

- **Branch:** `autoresearch/MOR-37-d61511d1`
- **Commits:** 6 total
  1. `b2484c1` - Initialize experiment branch
  2. `7e53320` - Record baseline
  3. `4dd339c` - Cycle 1 improvement
  4. `a431064` - Record Cycle 1 results
  5. `469be26` - Cycle 2 improvement
  6. `733564b` - Record Cycle 2 results
- **Results file:** `results.tsv` updated and committed

## Files Modified

- `experiments/03-data-cleaning/clean.py` - Two code quality improvements:
  - Lines 103-111: Consolidated outlier filtering and numeric conversion
  - Lines 32-37: Simplified phone normalization with ternary operators
- `experiments/03-data-cleaning/results.tsv` - Added baseline and 2 cycle results

## Conclusion

This 2-cycle experiment successfully maintained the perfect 100/100 score while improving code quality and maintainability. Both optimizations focused on making the code more Pythonic and easier to understand:

1. **Cycle 1** consolidated related operations, reducing the number of separate dataframe operations
2. **Cycle 2** simplified conditional logic using ternary operators for better readability

The results demonstrate that optimization isn't always about improving scores—sometimes it's about making great code even better through cleaner abstractions and more maintainable patterns.
