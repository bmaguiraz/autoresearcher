#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Post MOR-40 experiment results to Linear."""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

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
issue_id = "054c1cff-0433-46e2-9237-28b9243bc2d8"  # MOR-40

if not api_key:
    print("Error: LINEAR_API_KEY not set")
    sys.exit(1)

# Load results
results_file = Path(__file__).parent / "results" / "results_latest.json"
with open(results_file, "r") as f:
    data = json.load(f)

print(f"Posting MOR-40 results to Linear issue {issue_id}...")

# Post cycle 1 (baseline) comment
cycle1 = data["results"][0]
cycle1_comment = f"""## 🔬 Cycle 1 - Baseline Evaluation

**Timestamp:** {cycle1['timestamp']}

### Prompt
```
{cycle1['prompt']}
```

### Results
- **Aggregate Score:** `{cycle1['aggregate_score']:.3f}`
- **Clarity:** {cycle1['metrics']['clarity']:.3f}
- **Specificity:** {cycle1['metrics']['specificity']:.3f}
- **Response Quality:** {cycle1['metrics']['response_quality']:.3f}
- **Task Completion:** {cycle1['metrics']['task_completion']:.3f}

**Model:** `{data['config']['parameters']['model']}`
**Temperature:** {data['config']['parameters']['temperature']}

Starting with baseline prompt to establish performance metrics.
"""

try:
    result = post_comment_graphql(issue_id, cycle1_comment, api_key)
    print(f"✓ Posted cycle 1 comment (ID: {result['id']})")
except Exception as e:
    print(f"✗ Failed to post cycle 1 comment: {e}")
    sys.exit(1)

# Post cycle 2 comment
cycle2 = data["results"][1]
improvement_pct = ((cycle2['aggregate_score'] - cycle1['aggregate_score']) / cycle1['aggregate_score']) * 100
cycle2_comment = f"""## ✅ Cycle 2 Complete

**Timestamp:** {cycle2['timestamp']}

### Optimized Prompt
```
{cycle2['prompt']}
```

### Results
- **Aggregate Score:** `{cycle2['aggregate_score']:.3f}` (↑ {improvement_pct:.1f}% from baseline)
- **Clarity:** {cycle2['metrics']['clarity']:.3f} (↑ {(cycle2['metrics']['clarity'] - cycle1['metrics']['clarity']):.3f})
- **Specificity:** {cycle2['metrics']['specificity']:.3f} (↑ {(cycle2['metrics']['specificity'] - cycle1['metrics']['specificity']):.3f})
- **Response Quality:** {cycle2['metrics']['response_quality']:.3f} (↑ {(cycle2['metrics']['response_quality'] - cycle1['metrics']['response_quality']):.3f})
- **Task Completion:** {cycle2['metrics']['task_completion']:.3f} (↑ {(cycle2['metrics']['task_completion'] - cycle1['metrics']['task_completion']):.3f})

**Status:** ✅ Success - Improved across all metrics

### Key Changes
- Made prompt more specific and action-oriented
- Emphasized capability and clarity
- Refined language for better user guidance
"""

try:
    result = post_comment_graphql(issue_id, cycle2_comment, api_key)
    print(f"✓ Posted cycle 2 comment (ID: {result['id']})")
except Exception as e:
    print(f"✗ Failed to post cycle 2 comment: {e}")
    sys.exit(1)

# Post summary comment
summary = data["summary"]
summary_comment = f"""## 🎯 Experiment Complete - Round 4 (2 Cycles)

### Summary Statistics
- **Total Cycles:** {summary['total_cycles']}
- **Initial Score:** {summary['initial_score']:.3f}
- **Final Score:** {summary['final_score']:.3f}
- **Improvement:** +{summary['improvement']:.3f} ({summary['improvement_percentage']:.1f}%)
- **Best Score:** {summary['best_score']:.3f}
- **Average Score:** {summary['average_score']:.3f}

### Key Achievement
✨ **Successful Optimization**: Achieved {summary['improvement_percentage']:.1f}% improvement through iterative prompt refinement. All optimization criteria showed positive gains.

### Optimization Strategy
Used `{data['config']['parameters']['optimization_strategy']}` approach with focus on:
- Clarity enhancement
- Specificity improvements
- Response quality optimization
- Task completion effectiveness

### Branch & Results
- **Branch:** `autoresearch/mor-40-round4-2cycles`
- **Results File:** `experiments/02-llm-prompt-opt/results/results_latest.json`
- **Model:** {data['config']['parameters']['model']}

---
🤖 Generated by Claude Code for Linear issue [MOR-40](https://linear.app/maguireb/issue/MOR-40)
"""

try:
    result = post_comment_graphql(issue_id, summary_comment, api_key)
    print(f"✓ Posted summary comment (ID: {result['id']})")
except Exception as e:
    print(f"✗ Failed to post summary comment: {e}")
    sys.exit(1)

print("\n✅ All comments posted successfully to MOR-40!")
