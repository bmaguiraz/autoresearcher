# Integration Test Issues Guide

## Overview

The autoresearcher integration test suite creates **real Linear issues** to verify the end-to-end workflow from Telegram → Linear → Agent. This document explains why these test issues exist and how to identify them.

## Why Real Issues?

The integration tests at `tests/integration/test_linear_integration.py` validate that:

1. Telegram bot can receive `/create_issue` commands
2. Linear issues are correctly created via API
3. Linear webhooks trigger the agent workflow
4. Agent receives and processes the issue correctly

Creating real Linear issues (rather than mocking) ensures the entire webhook chain works in production.

## Identifying Test Issues

As of this fix (MOR-24), test issues are clearly marked:

### Title Prefix
All test issues now have `[TEST]` prefix:
- ✅ `[TEST] Bug in authentication flow`
- ❌ `Bug in authentication flow` (old format)

### Description Markers
Test issue descriptions include:
- 🧪 emoji and "TEST ISSUE - Integration Test Suite" header
- Source file reference: `tests/integration/test_linear_integration.py`
- Clear statement: "This is NOT a real bug"
- Test purpose explanation

### Example Test Issue

```
Title: [TEST] Bug in authentication flow

Description:
**🧪 TEST ISSUE - Integration Test Suite**

Created from Telegram by @testuser

Users are unable to login after password reset. This is a test issue from integration suite.

---
*This issue was created by the automated integration test suite...*
```

## Historical Context

Before this fix, test issues were indistinguishable from real work items, leading to:
- MOR-20: Investigation and documentation
- MOR-22: Attempted authentication implementation
- MOR-24: Multiple fix attempts (this issue)
- MOR-26: Documentation improvements

All of these were actually the same test issue being created repeatedly by the integration test.

## What This Project Actually Is

**autoresearcher** is:
- ✅ Python AI/ML experimentation framework
- ✅ LLM prompt optimization platform
- ✅ Autonomous research automation tool

**autoresearcher** is NOT:
- ❌ A web application
- ❌ A system with user authentication
- ❌ A service with login/password functionality

Therefore, issues about "authentication bugs" are always test data from the integration suite, not real bugs.

## Recommendations for Future

1. **Filter test issues**: Consider creating a Linear label `test:integration` or workspace filter to hide test issues from the main backlog

2. **Cleanup after tests**: If test issues should be temporary, enhance the test suite to archive or delete them after successful runs

3. **Separate test workspace**: Consider using a dedicated Linear team/project for integration testing

## Related Files

- `tests/integration/test_linear_integration.py` - Integration test suite
- `.linear-worker.json` - Linear project configuration
- `docs/test-issues-guide.md` - This file

## References

- MOR-24: https://linear.app/maguireb/issue/MOR-24/bug-in-authentication-flow
- PR #87: Documentation approach
- PR #88: Authentication implementation (not needed)
