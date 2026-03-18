# -*- coding: utf-8 -*-
"""Frozen evaluation script — scores the output of clean.py against ground truth."""

import subprocess
import sys
import time
import pandas as pd
import numpy as np

CLEANED_PATH = "data/cleaned.csv"
GROUND_TRUTH_PATH = "data/ground_truth.csv"
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0  # seconds


def run_clean():
    """Run clean.py as a subprocess with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            result = subprocess.run(
                [sys.executable, "clean.py"],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                return
            # Non-zero exit code
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                print(f"clean.py failed (attempt {attempt + 1}/{MAX_RETRIES}), retrying in {delay:.0f}s...", file=sys.stderr)
                print(f"Error: {result.stderr}", file=sys.stderr)
                time.sleep(delay)
            else:
                print(f"clean.py failed after {MAX_RETRIES} attempts:\n{result.stderr}", file=sys.stderr)
                sys.exit(1)
        except subprocess.TimeoutExpired:
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                print(f"clean.py timed out (attempt {attempt + 1}/{MAX_RETRIES}), retrying in {delay:.0f}s...", file=sys.stderr)
                time.sleep(delay)
            else:
                print(f"clean.py timed out after {MAX_RETRIES} attempts", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                print(f"clean.py error ({e}) (attempt {attempt + 1}/{MAX_RETRIES}), retrying in {delay:.0f}s...", file=sys.stderr)
                time.sleep(delay)
            else:
                print(f"clean.py error after {MAX_RETRIES} attempts: {e}", file=sys.stderr)
                sys.exit(1)


def load_csv(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def score_type_correctness(cleaned, truth):
    """0-25: Check that columns can be parsed to expected types."""
    score = 0.0
    max_per_check = 25.0 / 8  # 8 columns

    # For each column, check if values match expected patterns
    type_checks = {
        "name": lambda s: s.str.match(r"^[A-Z][a-z]+ [A-Z][a-z]+$", na=False),
        "email": lambda s: s.str.match(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", na=False),
        "phone": lambda s: s.str.match(r"^\(\d{3}\) \d{3}-\d{4}$", na=False),
        "age": lambda s: s.str.match(r"^\d{1,3}$", na=False),
        "salary": lambda s: s.str.match(r"^\d+$", na=False),
        "signup_date": lambda s: s.str.match(r"^\d{4}-\d{2}-\d{2}$", na=False),
        "city": lambda s: s.str.match(r"^[A-Za-z .'-]+$", na=False),
        "state": lambda s: s.str.match(r"^[A-Z]{2}$", na=False),
    }

    for col, check_fn in type_checks.items():
        if col not in cleaned.columns:
            continue
        # Only score non-empty rows
        non_empty = cleaned[col] != ""
        if non_empty.sum() == 0:
            score += max_per_check * 0.5  # partial credit for empty
            continue
        valid = check_fn(cleaned.loc[non_empty, col])
        frac = valid.sum() / non_empty.sum() if non_empty.sum() > 0 else 0
        score += max_per_check * frac

    return round(score, 1)


def score_null_handling(cleaned, truth):
    """0-25: Check that nulls/missing values are handled consistently."""
    score = 0.0

    # Check that sentinel values are removed
    sentinel_values = {"N/A", "null", "None", "n/a", "NULL", "none", "NA", "na"}
    sentinel_count = 0
    total_cells = 0

    for col in cleaned.columns:
        vals = cleaned[col]
        total_cells += len(vals)
        sentinel_count += vals.isin(sentinel_values).sum()

    if total_cells == 0:
        return 0.0

    # Score: no sentinels = full marks
    sentinel_frac = sentinel_count / total_cells
    sentinel_score = max(0, 1.0 - sentinel_frac * 50)  # harsh penalty
    score += 12.5 * sentinel_score

    # Compare missing pattern to ground truth
    cleaned_empty = (cleaned == "").sum().sum()
    truth_empty = (truth == "").sum().sum()

    # Reward being close to truth's missing count
    if truth_empty == 0:
        empty_score = 1.0 if cleaned_empty == 0 else max(0, 1.0 - cleaned_empty / (total_cells * 0.1))
    else:
        ratio = cleaned_empty / truth_empty if truth_empty > 0 else 0
        empty_score = max(0, 1.0 - abs(1.0 - ratio))

    score += 12.5 * empty_score

    return round(score, 1)


def score_dedup(cleaned, truth):
    """0-25: Check duplicate removal quality."""
    score = 0.0

    # Row count comparison
    truth_rows = len(truth)
    cleaned_rows = len(cleaned)

    # Penalize having too many or too few rows
    if truth_rows == 0:
        return 0.0

    row_ratio = cleaned_rows / truth_rows
    if row_ratio > 1.0:
        # Too many rows — likely didn't remove duplicates
        row_score = max(0, 1.0 - (row_ratio - 1.0) * 5)
    else:
        # Too few rows — removed too many
        row_score = max(0, row_ratio)

    score += 12.5 * row_score

    # Check for remaining duplicates in cleaned data
    if cleaned_rows > 0:
        # Check duplicates on name+email combo (should be unique after cleaning)
        if "name" in cleaned.columns and "email" in cleaned.columns:
            key_cols = ["name", "email"]
            avail = [c for c in key_cols if c in cleaned.columns]
            dupes = cleaned.duplicated(subset=avail, keep=False).sum()
            dupe_frac = dupes / cleaned_rows
            dupe_score = max(0, 1.0 - dupe_frac * 5)
        else:
            dupes = cleaned.duplicated(keep=False).sum()
            dupe_frac = dupes / cleaned_rows
            dupe_score = max(0, 1.0 - dupe_frac * 5)
    else:
        dupe_score = 0.0

    score += 12.5 * dupe_score

    return round(score, 1)


def score_outlier_treatment(cleaned, truth):
    """0-25: Check that outlier ages and salaries are handled."""
    score = 0.0

    # Age outliers: should have no ages < 0 or > 120
    if "age" in cleaned.columns:
        ages = pd.to_numeric(cleaned["age"], errors="coerce")
        valid_ages = ages.dropna()
        if len(valid_ages) > 0:
            bad_ages = ((valid_ages < 0) | (valid_ages > 120)).sum()
            age_score = max(0, 1.0 - bad_ages / len(valid_ages) * 10)
        else:
            age_score = 0.5
    else:
        age_score = 0.0
    score += 12.5 * age_score

    # Salary outliers: should have no salaries < 0 or > 1,000,000
    if "salary" in cleaned.columns:
        salaries = pd.to_numeric(cleaned["salary"], errors="coerce")
        valid_salaries = salaries.dropna()
        if len(valid_salaries) > 0:
            bad_salaries = ((valid_salaries < 0) | (valid_salaries > 1_000_000)).sum()
            salary_score = max(0, 1.0 - bad_salaries / len(valid_salaries) * 10)
        else:
            salary_score = 0.5
    else:
        salary_score = 0.0
    score += 12.5 * salary_score

    return round(score, 1)


def main():
    t0 = time.time()

    run_clean()

    try:
        cleaned = load_csv(CLEANED_PATH)
    except Exception as e:
        print(f"Failed to load {CLEANED_PATH}: {e}", file=sys.stderr)
        sys.exit(1)

    truth = load_csv(GROUND_TRUTH_PATH)

    tc = score_type_correctness(cleaned, truth)
    nh = score_null_handling(cleaned, truth)
    dd = score_dedup(cleaned, truth)
    ot = score_outlier_treatment(cleaned, truth)
    composite = round(tc + nh + dd + ot, 1)

    elapsed = round(time.time() - t0, 1)

    print("---")
    print(f"score:              {composite}")
    print(f"type_correctness:   {tc}")
    print(f"null_handling:      {nh}")
    print(f"dedup:              {dd}")
    print(f"outlier_treatment:  {ot}")
    print(f"eval_seconds:       {elapsed}")


if __name__ == "__main__":
    main()
