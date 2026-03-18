# Test Issues in Linear

## Overview

The integration test suite in `tests/integration/test_linear_integration.py` creates **real Linear issues** when run against the production Linear workspace. This is by design for E2E testing but can result in test data appearing in the actual backlog.

## Known Test Issues

### MOR-26: Bug in authentication flow

- **Created by**: `test_telegram_webhook_simulation` test (line 133)
- **Description**: "Users are unable to login after password reset"
- **Status**: Test artifact - not a real bug
- **Reason**: Autoresearcher is a research automation platform with no authentication system
- **Webhook Events Tracked**:
  - Session 3ae17842: Issue creation webhook
  - Session 1b3ea2e1: State changed to "In Progress"
  - Session 7373cf1a: Issue update webhook
  - Session 5eb1e44e (current): Issue update webhook - tracking state progression

### How to Identify Test Issues

Test issues typically have:
- Generic descriptions like "Bug in authentication flow"
- Created from Telegram by @testuser
- Match the hardcoded test data in `test_linear_integration.py`

### Recommendations

1. **Close test issues** - They represent test data, not real work
2. **Use test workspace** - Run integration tests against a test Linear workspace
3. **Add cleanup** - Consider adding test cleanup to delete created issues after test completes
