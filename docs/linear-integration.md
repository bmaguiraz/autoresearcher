# Linear Webhook Integration

## Overview

This project is integrated with Linear for automated issue tracking and development workflows. When new issues are created in Linear, webhooks trigger automated processing.

## How It Works

1. **Issue Creation**: When a new Linear issue is created in the autoresearcher project
2. **Webhook Delivery**: Linear sends a webhook payload to the configured endpoint
3. **Project Matching**: The webhook processor maps the Linear project ID to this repository
4. **Automated Implementation**: An AI agent clones/updates the repo and implements the issue
5. **Pull Request**: Changes are committed and a PR is automatically opened

## Configuration

The project configuration is stored in `.linear-worker.json`:

```json
{
  "projectId": "62c20541-6d2a-4f57-a071-6c6625e7718e",
  "projectName": "autoresearcher",
  "teamId": "ba745c5b-3dee-421d-9d31-fe5707aff2ca"
}
```

## Webhook Payload

Linear webhooks include:
- Issue ID and identifier (e.g., MOR-18)
- Title and description
- State (Backlog, In Progress, Done)
- Priority and labels
- Team and project IDs

## Testing

This integration can be tested by creating issues in Linear with the prefix "Test Issue" - these will trigger the webhook workflow and verify end-to-end functionality.

## Session Tracking

Each webhook session is assigned a unique session ID (format: `ac:sid:<session-id>`) which can be used to track work across commits and PRs.

## Benefits

- **Automated Development**: Issues are automatically picked up and implemented
- **Consistency**: Standardized workflow for all Linear issues
- **Traceability**: Direct link from Linear issue to PR to deployment
- **Efficiency**: Reduces manual context switching and setup time
