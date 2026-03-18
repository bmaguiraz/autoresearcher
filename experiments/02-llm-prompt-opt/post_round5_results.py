#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Post Round 5 experiment results to Linear issue MOR-44."""
import json
import os
import sys
from pathlib import Path

# Try to import requests, fall back to urllib if not available
try:
    import requests
    USE_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.parse
    USE_REQUESTS = False


def post_comment_graphql(issue_id, comment_body, api_key):
    """Post a comment to Linear using GraphQL."""
    mutation = """
    mutation CreateComment($issueId: String!, $body: String!) {
        commentCreate(input: {
            issueId: $issueId
            body: $body
        }) {
            success
            comment {
                id
                body
                createdAt
            }
        }
    }
    """

    variables = {
        "issueId": issue_id,
        "body": comment_body
    }

    payload = json.dumps({"query": mutation, "variables": variables})
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    if USE_REQUESTS:
        response = requests.post(
            "https://api.linear.app/graphql",
            data=payload,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
    else:
        req = urllib.request.Request(
            "https://api.linear.app/graphql",
            data=payload.encode('utf-8'),
            headers=headers
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

    if "errors" in data:
        raise ValueError(f"GraphQL errors: {data['errors']}")

    if not data["data"]["commentCreate"]["success"]:
        raise ValueError("Comment creation failed")

    return data["data"]["commentCreate"]["comment"]


# Load environment variables
api_key = os.getenv("LINEAR_API_KEY")
issue_id = "09cd60d2-a07a-4656-b002-8605c32d316f"  # MOR-44

if not api_key:
    print("Error: LINEAR_API_KEY not set")
    sys.exit(1)

# Load results
results_file = Path(__file__).parent / "results" / "results_round5.json"
with open(results_file, "r") as f:
    data = json.load(f)

print(f"Posting Round 5 results to Linear issue {issue_id} (MOR-44)...")

# Post baseline comment
baseline = data["cycles"][0]
baseline_comment = f"""## 🔬 Round 5 - Baseline Evaluation

**Commit:** `{baseline['commit']}`

### Results
- **Accuracy:** `{baseline['results']['accuracy']:.1%}` ({baseline['results']['correct']}/{baseline['results']['total']})
- **Cost:** {baseline['results']['cost_cents']:.1f}¢
- **Evaluation Time:** {baseline['results']['eval_seconds']:.1f}s
- **Model:** `{data['config']['model']}`
- **Few-shot Examples:** {baseline['prompt_config']['few_shot_examples']}

Starting from perfect baseline accuracy (100%) with 3 few-shot examples.
"""

try:
    result = post_comment_graphql(issue_id, baseline_comment, api_key)
    print(f"✓ Posted baseline comment (ID: {result['id']})")
except Exception as e:
    print(f"✗ Failed to post baseline comment: {e}")
    sys.exit(1)

# Post cycle 1 comment
cycle1 = data["cycles"][1]
cycle1_comment = f"""## ❌ Cycle 1 Complete - Regression

**Commit:** `{cycle1['commit']}`
**Hypothesis:** {cycle1['hypothesis']}

### Results
- **Accuracy:** `{cycle1['results']['accuracy']:.1%}` ({cycle1['results']['correct']}/{cycle1['results']['total']})
- **Cost:** {cycle1['results']['cost_cents']:.1f}¢
- **Evaluation Time:** {cycle1['results']['eval_seconds']:.1f}s
- **Few-shot Examples:** {cycle1['prompt_config']['few_shot_examples']} (reduced from {baseline['prompt_config']['few_shot_examples']})

**Status:** ❌ Regression - Accuracy dropped from 100% to 96%

### Errors
- Example 7: expected `positive`, got `neutral`
- Example 12: expected `positive`, got `neutral`

### Analysis
Removing the neutral example caused the model to misclassify some positive sentiments as neutral. The third example appears necessary for maintaining optimal accuracy.
"""

try:
    result = post_comment_graphql(issue_id, cycle1_comment, api_key)
    print(f"✓ Posted cycle 1 comment (ID: {result['id']})")
except Exception as e:
    print(f"✗ Failed to post cycle 1 comment: {e}")
    sys.exit(1)

# Post summary comment
summary = data["summary"]
summary_comment = f"""## 🎯 Experiment Complete - Round 5

### Summary Statistics
- **Total Cycles:** {summary['total_cycles']}
- **Baseline Accuracy:** {summary['baseline_accuracy']:.1%}
- **Final Accuracy:** {summary['final_accuracy']:.1%}
- **Change:** {summary['improvement']:+.1%}

### Key Finding
⚠️ **Simplification Limit Reached**: Reducing from 3 to 2 few-shot examples caused accuracy regression (100% → 96%). The neutral example is necessary for optimal performance.

### Recommendation
**Keep 3 few-shot examples** as the optimal configuration. Further simplification sacrifices accuracy.

### Branch & Results
- **Branch:** `autoresearch/mar18-round5`
- **Results File:** `experiments/02-llm-prompt-opt/results/results_round5.json`
- **Commits:** `91fd77b` (baseline) → `27ff8bc` (cycle 1) → `2f986ab` (results)

{summary['notes']}
"""

try:
    result = post_comment_graphql(issue_id, summary_comment, api_key)
    print(f"✓ Posted summary comment (ID: {result['id']})")
except Exception as e:
    print(f"✗ Failed to post summary comment: {e}")
    sys.exit(1)

print("\n✅ All comments posted successfully to MOR-44!")
