#!/usr/bin/env python3
import os
import requests
import sys

def post_comment(issue_id, body, api_key):
    mutation = """
    mutation CreateComment($issueId: String!, $body: String!) {
        commentCreate(input: {issueId: $issueId, body: $body}) {
            success
            comment { id }
        }
    }
    """
    response = requests.post(
        "https://api.linear.app/graphql",
        json={"query": mutation, "variables": {"issueId": issue_id, "body": body}},
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        timeout=10
    )
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        raise ValueError(f"GraphQL errors: {data['errors']}")
    return data["data"]["commentCreate"]["comment"]

summary = """## ✅ Experiment Complete - 2 Cycles

### Summary

**Branch:** `autoresearch/mar18-7d80796b-02-llm-prompt-opt`  
**Total Cycles:** 2 (+ baseline)

| Cycle | Commit | Accuracy | Cost | Status | Description |
|-------|--------|----------|------|--------|-------------|
| 0 (Baseline) | `6dcf42d7` | 1.000 (50/50) | 1.0¢ | ✅ keep | Current prompt config |
| 1 | `1e4c5d84` | 0.960 (48/50) | 0.9¢ | ❌ discard | Removed neutral example - accuracy dropped |
| 2 | `cc545b2b` | 1.000 (50/50) | 0.9¢ | ✅ keep | Streamlined system prompt |

### Results

- **Initial:** 1.000 accuracy @ 1.0¢
- **Final:** 1.000 accuracy @ 0.9¢
- **Improvement:** Maintained 100% accuracy with 10% cost reduction

### Key Findings

1. **Few-shot examples matter**: Removing the neutral example caused accuracy to drop from 100% to 96%
2. **System prompt optimization**: Streamlining verbose label definitions into comma-separated lists reduced cost by 10% while maintaining perfect accuracy
3. **Verification**: Both cycle comments included full metrics tables and collapsible prompt.py configs as expected

### Next Steps

Ready for PR and merge.
"""

issue_id = os.getenv("LINEAR_ISSUE_ID", "e8e7a6fd-1177-4684-b429-7f3a893c5f35")
api_key = os.getenv("LINEAR_API_KEY")
if not api_key:
    print("Error: LINEAR_API_KEY not set")
    sys.exit(1)

comment = post_comment(issue_id, summary, api_key)
print(f"✓ Posted summary comment (ID: {comment['id']})")
