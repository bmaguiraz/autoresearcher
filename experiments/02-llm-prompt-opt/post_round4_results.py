#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Post Round 4 experiment results to Linear issue MOR-36."""
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
issue_id = "8308b625-a0d5-4535-995d-5976f0ef5311"  # MOR-36

if not api_key:
    print("Error: LINEAR_API_KEY not set")
    sys.exit(1)

# Load results
results_file = Path(__file__).parent / "results" / "results_round4.json"
with open(results_file, "r") as f:
    data = json.load(f)

print(f"Posting Round 4 results to Linear issue {issue_id} (MOR-36)...")

# Post baseline comment
baseline = data["cycles"][0]
baseline_comment = f"""## 🔬 Round 4 - Baseline Evaluation

**Commit:** `{baseline['commit']}`

### Results
- **Accuracy:** `{baseline['results']['accuracy']:.1%}` ({baseline['results']['correct']}/{baseline['results']['total']})
- **Cost:** {baseline['results']['cost_cents']:.1f}¢
- **Evaluation Time:** {baseline['results']['eval_seconds']:.1f}s
- **Model:** `{data['config']['model']}`
- **Few-shot Examples:** {baseline['prompt_config']['few_shot_examples']}

Starting from perfect baseline accuracy to test simplification hypothesis.
"""

try:
    result = post_comment_graphql(issue_id, baseline_comment, api_key)
    print(f"✓ Posted baseline comment (ID: {result['id']})")
except Exception as e:
    print(f"✗ Failed to post baseline comment: {e}")
    sys.exit(1)

# Post cycle 1 comment
cycle1 = data["cycles"][1]
cycle1_comment = f"""## ✅ Cycle 1 Complete

**Commit:** `{cycle1['commit']}`
**Hypothesis:** {cycle1['hypothesis']}

### Results
- **Accuracy:** `{cycle1['results']['accuracy']:.1%}` ({cycle1['results']['correct']}/{cycle1['results']['total']})
- **Cost:** {cycle1['results']['cost_cents']:.1f}¢
- **Evaluation Time:** {cycle1['results']['eval_seconds']:.1f}s
- **Few-shot Examples:** {cycle1['prompt_config']['few_shot_examples']} (reduced from {baseline['prompt_config']['few_shot_examples']})

**Status:** ✅ Success - Maintained perfect accuracy with simpler prompt

### Change
Removed redundant fourth example to simplify the prompt while preserving 100% accuracy.
"""

try:
    result = post_comment_graphql(issue_id, cycle1_comment, api_key)
    print(f"✓ Posted cycle 1 comment (ID: {result['id']})")
except Exception as e:
    print(f"✗ Failed to post cycle 1 comment: {e}")
    sys.exit(1)

# Post summary comment
summary = data["summary"]
summary_comment = f"""## 🎯 Experiment Complete - Round 4

### Summary Statistics
- **Total Cycles:** {summary['total_cycles']}
- **Baseline Accuracy:** {summary['baseline_accuracy']:.1%}
- **Final Accuracy:** {summary['final_accuracy']:.1%}
- **Improvement:** {summary['improvement']:+.1%}

### Key Achievement
✨ **Simplicity Improvement**: Maintained perfect accuracy (100%) while reducing prompt complexity from 4 to 3 few-shot examples.

### Branch & Results
- **Branch:** `autoresearch/mar18-round4`
- **Results File:** `experiments/02-llm-prompt-opt/results/results_round4.json`
- **Commits:** `2b9a089` (baseline) → `0e6e11f` (cycle 1)

{summary['notes']}
"""

try:
    result = post_comment_graphql(issue_id, summary_comment, api_key)
    print(f"✓ Posted summary comment (ID: {result['id']})")
except Exception as e:
    print(f"✗ Failed to post summary comment: {e}")
    sys.exit(1)

print("\n✅ All comments posted successfully to MOR-36!")
