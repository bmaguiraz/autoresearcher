# Linear Integration Tests

This directory contains integration tests for the Linear + Telegram integration (MOR-1).

## Overview

The integration allows creating Linear issues from Telegram messages, enabling seamless issue tracking from chat.

## Files

- `test_linear_integration.py` - Pytest-based integration tests
- `verify_linear_telegram_e2e.py` - Standalone E2E verification script

## Prerequisites

1. **Linear API Key**: Get your API key from [Linear Settings → API](https://linear.app/settings/api)
2. **Team ID**: Find your team ID in Linear (optional, defaults to autoresearcher team)

## ⚠️ Important Note

**These tests create REAL Linear issues in your workspace!**

When you run `test_telegram_webhook_simulation()` or the verification script, they will create actual Linear issues with titles like:
- "Bug in authentication flow" (MOR-26)
- "Test Linear integration from Telegram"

These are **NOT real bugs** - they are test data used to verify the integration works end-to-end. If you see these issues in your Linear backlog, you can safely close them or use them to verify your webhook integration is working.

## Running the E2E Verification

The quickest way to verify the integration is using the standalone script:

```bash
# Set your Linear API key
export LINEAR_API_KEY="lin_api_xxxxx"

# Optional: Set your team ID
export LINEAR_TEAM_ID="your-team-id"

# Run the verification
python tests/integration/verify_linear_telegram_e2e.py
```

This script will:
1. Verify connection to Linear API
2. Simulate a Telegram message
3. Parse the message command
4. Create a real Linear issue
5. Report the results

## Running Pytest Tests

For more comprehensive testing:

```bash
# Install test dependencies
pip install pytest requests

# Run all integration tests
pytest tests/integration/test_linear_integration.py -v

# Run specific test
pytest tests/integration/test_linear_integration.py::TestLinearIntegration::test_linear_api_connection -v
```

## Test Coverage

The tests verify:

- ✅ Connection to Linear API
- ✅ Authentication with API key
- ✅ Creating Linear issues via GraphQL API
- ✅ Parsing Telegram message format
- ✅ E2E flow: Telegram message → Linear issue

## Telegram Message Format

To create a Linear issue from Telegram, send a message like:

```
/create_issue Issue title here
Description: Detailed description of the issue
```

The integration will:
1. Extract the title from the first line
2. Extract the description from subsequent lines
3. Add attribution showing who created the issue
4. Create the issue in Linear

## Expected Output

Successful verification output:

```
======================================================================
  Linear + Telegram Integration E2E Verification
======================================================================

[Step 1] Checking environment variables
✓ LINEAR_API_KEY found: lin_api_xxxxx...
✓ Team ID: ba745c5b-3dee-421d-9d31-fe5707aff2ca

[Step 2] Verifying Linear API connection
✓ Connected as: Your Name (your.email@example.com)
✓ Organization: Your Org

[Step 3] Simulating Telegram message
  Message from: @testuser
  Message text: /create_issue Test Linear integration from Telegram...

[Step 4] Parsing Telegram command
✓ Title: Test Linear integration from Telegram
✓ Description length: 123 chars

[Step 5] Creating Linear issue
✓ Issue created: MOR-123
  Title: Test Linear integration from Telegram
  Team: autoresearcher
  State: Backlog
  URL: https://linear.app/yourorg/issue/MOR-123

======================================================================
  E2E Verification Complete!
======================================================================
✓ All steps completed successfully

📋 Created Issue: MOR-123
🔗 URL: https://linear.app/yourorg/issue/MOR-123

The Linear + Telegram integration is working correctly!
```

## Troubleshooting

### Error: LINEAR_API_KEY not set

Set your Linear API key:
```bash
export LINEAR_API_KEY="your_key_here"
```

### Error: GraphQL errors

Check that:
- Your API key is valid
- Your team ID is correct
- You have permissions to create issues in the team

### Error: Connection failed

Verify:
- You have internet connectivity
- Linear API is accessible
- No firewall blocking the connection

## Next Steps

After verification succeeds:

1. ✅ E2E flow is working
2. Implement actual Telegram bot webhook handler
3. Deploy bot to production
4. Configure webhook URL in Telegram
5. Test with real Telegram messages

## Related Issues

- MOR-1: Test Linear integration - verify E2E issue creation from Telegram
- MOR-26: Example test issue created by `test_telegram_webhook_simulation()` (not a real bug)
