# Test Issues and Integration Testing

## Overview

This document explains test issues that may appear in the Linear backlog as a result of integration testing.

## MOR-22: Bug in authentication flow

**Status**: Test Issue - Should be closed

**Origin**: This issue was created by the integration test `test_telegram_webhook_simulation` in `tests/integration/test_linear_integration.py` (line 133).

**Context**:
- The issue description "Users are unable to login after password reset" is example text used to demonstrate the Linear-Telegram integration
- Autoresearcher is a Python-based AI research automation platform with **no web application or authentication system**
- There is no authentication flow to fix - this project focuses on running AI optimization experiments

**Resolution**: This issue should be closed as it was created for testing purposes and does not represent a real bug or feature request.

## Identifying Test Issues

Test issues created by integration tests typically have:
- Description starting with "Created from Telegram by @testuser"
- Content that matches test case data in `tests/integration/`
- References to features that don't exist in the autoresearcher codebase

## Recommendations

1. Mark integration test issues with a specific label (e.g., "test-issue") when created
2. Automatically close or archive test issues after verification
3. Use a dedicated test team/project for integration testing to avoid polluting the main backlog
