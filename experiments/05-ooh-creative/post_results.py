#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Post OOH Creative experiment results to Linear issue as comments.
"""
import json
import os
import sys
import requests
from pathlib import Path


def post_comment_to_issue(issue_id: str, comment_body: str, api_key: str) -> dict:
    """Post a comment to a Linear issue."""
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
                url
            }
        }
    }
    """

    variables = {
        "issueId": issue_id,
        "body": comment_body
    }

    response = requests.post(
        "https://api.linear.app/graphql",
        json={"query": mutation, "variables": variables},
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json"
        },
        timeout=10
    )

    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise ValueError(f"GraphQL errors: {data['errors']}")

    if not data["data"]["commentCreate"]["success"]:
        raise ValueError("Comment creation failed")

    return data["data"]["commentCreate"]["comment"]


def format_results_comment(results_data: dict, session_id: str) -> str:
    """Format experiment results as a markdown comment."""
    use_case = results_data['use_case']
    cycles = results_data['cycles']
    elapsed = results_data['elapsed_seconds']
    best_variant = results_data['best_variant']
    best_score = results_data['best_score']

    # Build results table
    table_rows = []
    for result in results_data['results']:
        variant = result['variant']
        score = result['final_score']
        if result['success']:
            table_rows.append(f"| {variant.title():<15} | {score:.2f}/100 | ✅ Success |")
        else:
            table_rows.append(f"| {variant.title():<15} | N/A | ❌ Failed |")

    comment = f"""## ✅ Autoresearch Complete - MOR-39 (Round 3)

### Experiment: OOH Creative WriteFit (1 cycle)

**Session ID:** `{session_id}` (ac:sid label)

**Configuration:**
- **Use Case:** {use_case.title()}
- **Cycles:** {cycles}
- **Execution Time:** {elapsed:.2f}s
- **Parallel Execution:** {"Yes" if results_data['parallel_execution'] else "No"}

### Results Summary

| Variant | Score | Status |
|---------|-------|--------|
{chr(10).join(table_rows)}

**🏆 Best Performing Variant:** {best_variant.upper()}
**📊 Best Score:** {best_score:.2f}/100

### Analysis

The experiment evaluated 4 creative variants for the {use_case.title()} use case:

1. **Baseline** - Direct, feature-focused messaging
2. **Emotional** - Appeals to customer pain points and desires
3. **Urgency** - Time-sensitive offers and scarcity messaging
4. **Social Proof** - Trust signals and testimonials

The **{best_variant}** variant achieved the highest aggregate score across all OOH metrics (attention, clarity, relevance, conversion potential).

### Files Updated

- `experiments/05-ooh-creative/results/comparative_results_20260318_001733.json` - Comparative analysis
- `experiments/05-ooh-creative/results/results_20260318_001733.json` - Detailed results
- `experiments/05-ooh-creative/config.json` - Updated configuration
- `experiments/05-ooh-creative/experiment.log` - Execution logs

---

🤖 Generated with [Autoresearcher](https://github.com/bmaguiraz/autoresearcher) | Session: {session_id}
"""
    return comment


def main():
    # Get environment variables
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        print("Error: LINEAR_API_KEY environment variable not set")
        return 1

    # Issue ID from webhook payload
    issue_id = "9776871d-0025-4c4c-a878-761bf4d451dc"
    session_id = "d98919a8"

    # Load results
    script_dir = Path(__file__).parent

    # Try to find the latest comparative results file
    results_dir = script_dir / "results"
    comparative_files = sorted(results_dir.glob("comparative_results_*.json"), reverse=True)

    if not comparative_files:
        print("Error: No comparative results files found")
        return 1

    results_file = comparative_files[0]
    print(f"Using results file: {results_file}")

    with open(results_file, 'r') as f:
        data = json.load(f)

    print(f"Posting results to Linear issue {issue_id}...")

    # Post results comment
    comment_body = format_results_comment(data, session_id)
    try:
        comment = post_comment_to_issue(issue_id, comment_body, api_key)
        print(f"✓ Posted results comment")
        print(f"  Comment ID: {comment['id']}")
        print(f"  URL: {comment.get('url', 'N/A')}")
    except Exception as e:
        print(f"✗ Failed to post comment: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n✅ Results posted successfully to Linear!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
