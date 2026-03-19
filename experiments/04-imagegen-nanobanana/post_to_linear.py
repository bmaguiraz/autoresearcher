#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Post image generation experiment results to Linear issue as comments.
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


def format_cycle_comment(cycle_data: dict, prompt_config: str = None, image_paths: list = None) -> str:
    """Format a single cycle's results as a markdown comment."""
    cycle_num = cycle_data["cycle"]
    metrics = cycle_data["metrics"]
    score = cycle_data["aggregate_score"]
    prompt = cycle_data["prompt"]

    comment = f"""## 🔄 Cycle {cycle_num} Complete

**Aggregate Score:** `{score:.3f}`

### Metrics Table

| Metric | Score |
|--------|-------|
| Visual Quality | {metrics['visual_quality']:.3f} |
| Prompt Clarity | {metrics['prompt_clarity']:.3f} |
| Style Consistency | {metrics['style_consistency']:.3f} |
| Composition | {metrics['composition']:.3f} |
| **Aggregate** | **{score:.3f}** |

**Prompt:** "{prompt}"

**Timestamp:** {cycle_data['timestamp']}
"""

    # Add collapsible prompt.py config if provided
    if prompt_config:
        comment += f"""
<details>
<summary>📝 prompt.py Configuration</summary>

```python
{prompt_config}
```

</details>
"""

    # Add inline generated images if provided
    if image_paths:
        comment += "\n### Generated Images\n\n"
        for img_path in image_paths:
            # Create descriptive alt text for accessibility
            alt_text = f"AI-generated image for cycle {cycle_num} using prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}"
            comment += f"![{alt_text}]({img_path})\n\n"

    return comment


def format_summary_comment(summary: dict, cycles_completed: int, experiment_id: str) -> str:
    """Format the final summary as a markdown comment."""
    comment = f"""## ✅ Experiment Complete - {cycles_completed} Cycles

### Summary Statistics
- **Experiment ID:** {experiment_id}
- **Total Cycles:** {summary['total_cycles']}
- **Initial Score:** {summary['initial_score']:.3f}
- **Final Score:** {summary['final_score']:.3f}
- **Improvement:** +{summary['improvement']:.3f} ({summary['improvement_percentage']:.1f}%)
- **Best Score:** {summary['best_score']:.3f}
- **Average Score:** {summary['average_score']:.3f}

### Results
The experiment has completed successfully with a **{summary['improvement_percentage']:.1f}% improvement** in aggregate score across {summary['total_cycles']} optimization cycles.

Results are available in `experiments/04-imagegen-nanobanana/results/results_latest.json`
"""
    return comment


def main():
    # Get environment variables
    api_key = os.getenv("LINEAR_API_KEY")
    if not api_key:
        print("Error: LINEAR_API_KEY environment variable not set")
        return 1

    issue_id = os.getenv("LINEAR_ISSUE_ID")
    if not issue_id:
        print("Error: LINEAR_ISSUE_ID environment variable not set")
        return 1

    # Load results
    results_file = Path(__file__).parent / "results" / "results_latest.json"
    if not results_file.exists():
        print(f"Error: Results file not found at {results_file}")
        return 1

    with open(results_file, 'r') as f:
        data = json.load(f)

    # Load prompt.py config for collapsible section
    prompt_config = None
    prompt_file = Path(__file__).parent / "prompt.py"
    if prompt_file.exists():
        with open(prompt_file, 'r') as f:
            prompt_config = f.read()

    # Check for generated images in outputs directory
    outputs_dir = Path(__file__).parent / "outputs"

    print(f"Posting results to Linear issue {issue_id}...")

    # Post cycle comments
    for cycle_result in data["results"]:
        cycle_num = cycle_result['cycle']

        # Look for images for this cycle
        image_paths = []
        if outputs_dir.exists():
            cycle_images = sorted(outputs_dir.glob(f"cycle_{cycle_num}_*.png"))
            if not cycle_images:
                # Fallback to seed-based naming
                cycle_images = sorted(outputs_dir.glob("seed_*.png"))

            # Upload images or use relative paths (depending on your setup)
            for img_path in cycle_images:
                # For now, just include relative paths
                # In production, you might want to upload to an image host
                image_paths.append(str(img_path.relative_to(Path(__file__).parent)))

        comment_body = format_cycle_comment(cycle_result, prompt_config, image_paths if image_paths else None)
        try:
            comment = post_comment_to_issue(issue_id, comment_body, api_key)
            print(f"✓ Posted cycle {cycle_num} comment (ID: {comment['id']})")
        except Exception as e:
            print(f"✗ Failed to post cycle {cycle_num} comment: {e}")
            return 1

    # Post summary comment
    summary_body = format_summary_comment(
        data["summary"],
        data["cycles_completed"],
        data["experiment_id"]
    )
    try:
        comment = post_comment_to_issue(issue_id, summary_body, api_key)
        print(f"✓ Posted summary comment (ID: {comment['id']})")
    except Exception as e:
        print(f"✗ Failed to post summary comment: {e}")
        return 1

    print("\n✅ All comments posted successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
