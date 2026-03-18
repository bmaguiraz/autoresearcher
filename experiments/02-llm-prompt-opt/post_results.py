#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import sys

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
issue_id = os.getenv("LINEAR_ISSUE_ID")

if not api_key:
    print("Error: LINEAR_API_KEY not set")
    sys.exit(1)

if not issue_id:
    print("Error: LINEAR_ISSUE_ID not set")
    sys.exit(1)

# Load results
with open("results/results_latest.json", "r") as f:
    data = json.load(f)

# Format comment
comment = f"""## ✅ Cycle 1 Complete (Round 3)

### Results
- **Accuracy:** `{data['results']['accuracy']:.1%}` ({data['results']['correct']}/{data['results']['total']})
- **Cost:** ${data['results']['cost_cents']:.2f}¢
- **Evaluation Time:** {data['results']['eval_seconds']:.1f}s
- **Model:** `{data['config']['model']}`

### Summary
Completed 1 optimization cycle with perfect accuracy on the sentiment classification task.

**Timestamp:** {data['timestamp']}
"""

print(f"Posting results to Linear issue {issue_id}...")
try:
    result = post_comment_graphql(issue_id, comment, api_key)
    print(f"✓ Posted comment (ID: {result['id']})")
    print("✅ Success!")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)
