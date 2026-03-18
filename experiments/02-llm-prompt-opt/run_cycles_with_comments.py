#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run multi-cycle experiment with Linear comment posting after each cycle.

This script:
1. Runs eval.py for each cycle
2. Posts results to Linear with full metrics table and collapsible prompt.py config
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
import requests


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


def read_prompt_config() -> str:
    """Read the current prompt.py configuration."""
    prompt_path = Path(__file__).parent / "prompt.py"
    with open(prompt_path, 'r') as f:
        return f.read()


def run_eval() -> dict:
    """Run eval.py and parse results."""
    print("Running eval.py...")

    # Run eval.py
    result = subprocess.run(
        [sys.executable, "eval.py"],
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True,
        timeout=300  # 5 minute timeout
    )

    if result.returncode != 0:
        print(f"Error running eval.py:")
        print(result.stderr)
        raise RuntimeError(f"eval.py failed with code {result.returncode}")

    output = result.stdout
    print(output)

    # Parse metrics from output
    metrics = {}
    for line in output.split('\n'):
        if line.startswith('accuracy:'):
            metrics['accuracy'] = float(line.split(':')[1].strip())
        elif line.startswith('correct:'):
            metrics['correct'] = int(line.split(':')[1].strip())
        elif line.startswith('total:'):
            metrics['total'] = int(line.split(':')[1].strip())
        elif line.startswith('cost_cents:'):
            metrics['cost_cents'] = float(line.split(':')[1].strip())
        elif line.startswith('eval_seconds:'):
            metrics['eval_seconds'] = float(line.split(':')[1].strip())

    if not metrics:
        raise ValueError("Could not parse metrics from eval.py output")

    return metrics


def format_cycle_comment(cycle_num: int, metrics: dict, prompt_config: str, commit_sha: str) -> str:
    """Format a cycle's results as a markdown comment with collapsible prompt config."""

    accuracy_pct = metrics['accuracy'] * 100

    comment = f"""## 🔄 Cycle {cycle_num} Complete

### Metrics

| Metric | Value |
|--------|-------|
| **Accuracy** | `{accuracy_pct:.1f}%` ({metrics['correct']}/{metrics['total']}) |
| **Cost** | `{metrics['cost_cents']:.1f}¢` |
| **Eval Time** | `{metrics['eval_seconds']:.1f}s` |
| **Commit** | `{commit_sha[:7]}` |

<details>
<summary><b>📝 prompt.py Configuration</b></summary>

```python
{prompt_config}
```

</details>

---
_Posted automatically after cycle {cycle_num}_
"""
    return comment


def main():
    # Get environment variables
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        print("Error: LINEAR_API_KEY environment variable not set")
        return 1

    issue_id = os.getenv("LINEAR_ISSUE_ID", "e8e7a6fd-1177-4684-b429-7f3a893c5f35")
    cycles = int(os.getenv("CYCLES", "2"))

    print(f"Running {cycles} cycle(s) for 02-llm-prompt-opt")
    print(f"Linear issue: {issue_id}")
    print("=" * 60)

    # Change to experiment directory
    os.chdir(Path(__file__).parent)

    # Get initial commit
    initial_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True
    ).stdout.strip()

    for cycle in range(1, cycles + 1):
        print(f"\n{'='*60}")
        print(f"CYCLE {cycle}/{cycles}")
        print(f"{'='*60}\n")

        try:
            # Run evaluation
            metrics = run_eval()

            # Read current prompt configuration
            prompt_config = read_prompt_config()

            # Get current commit
            commit_sha = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()

            # Format and post comment
            comment_body = format_cycle_comment(cycle, metrics, prompt_config, commit_sha)

            print(f"\nPosting results to Linear issue {issue_id}...")
            comment = post_comment_to_issue(issue_id, comment_body, api_key)
            print(f"✓ Posted cycle {cycle} comment (ID: {comment['id']})")

            # If not the last cycle, simulate optimization
            # (in a real experiment, an AI agent would modify prompt.py here)
            if cycle < cycles:
                print(f"\n⏸  Pausing before next cycle (in real experiment, prompt.py would be modified here)")
                time.sleep(2)

        except Exception as e:
            print(f"\n✗ Error in cycle {cycle}: {e}")
            import traceback
            traceback.print_exc()
            return 1

    print(f"\n{'='*60}")
    print(f"✅ All {cycles} cycles completed successfully!")
    print(f"{'='*60}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
