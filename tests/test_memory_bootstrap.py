#!/usr/bin/env python3
"""Memory system bootstrap verification test.

This test verifies that the Bedrock AgentCore memory system is properly configured
and that S3 storage structure is accessible.

Test created for Linear issue MOR-150.
"""

import os
import sys
from datetime import datetime
from typing import Dict, List

import boto3
import pytest
from botocore.exceptions import ClientError


class TestMemoryBootstrap:
    """Test suite for verifying memory system bootstrap."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.memory_id = os.environ.get("BEDROCK_AGENTCORE_MEMORY_ID")
        self.region = os.environ.get("AWS_REGION", "us-east-1")

        if not self.memory_id:
            pytest.skip("BEDROCK_AGENTCORE_MEMORY_ID not set - skipping memory tests")

        self.control_client = boto3.client("bedrock-agentcore-control", region_name=self.region)
        self.runtime_client = boto3.client("bedrock-agentcore", region_name=self.region)

    def test_memory_exists_and_active(self):
        """Verify memory system exists and is in ACTIVE state."""
        try:
            response = self.control_client.get_memory(memoryId=self.memory_id)
            memory = response.get("memory", {})

            assert memory["id"] == self.memory_id, "Memory ID mismatch"
            assert memory["status"] == "ACTIVE", f"Memory status is {memory['status']}, expected ACTIVE"
            assert "memoryExecutionRoleArn" in memory, "Memory execution role ARN missing"

            print(f"✓ Memory {self.memory_id} is ACTIVE")
            print(f"  ARN: {memory['arn']}")
            print(f"  Role: {memory['memoryExecutionRoleArn']}")

        except ClientError as e:
            pytest.fail(f"Failed to get memory: {e}")

    def test_all_strategies_configured(self):
        """Verify all required memory strategies are configured and ACTIVE."""
        expected_strategies = {
            "SUMMARIZATION": "Conversation summaries",
            "SEMANTIC": "Semantic facts",
            "USER_PREFERENCE": "User preferences"
        }

        try:
            response = self.control_client.get_memory(memoryId=self.memory_id)
            strategies = response.get("memory", {}).get("strategies", [])

            assert len(strategies) >= 3, f"Expected at least 3 strategies, found {len(strategies)}"

            found_types = {}
            for strategy in strategies:
                strategy_type = strategy["type"]
                strategy_id = strategy["strategyId"]
                strategy_name = strategy["name"]
                strategy_status = strategy["status"]

                assert strategy_status == "ACTIVE", f"Strategy {strategy_name} is {strategy_status}, expected ACTIVE"

                found_types[strategy_type] = {
                    "id": strategy_id,
                    "name": strategy_name,
                    "namespaces": strategy.get("namespaces", [])
                }

                print(f"✓ Strategy {strategy_type} ({strategy_name}) is ACTIVE")
                print(f"  ID: {strategy_id}")
                print(f"  Namespaces: {strategy.get('namespaces', [])}")

            # Verify all expected strategy types are present
            for expected_type in expected_strategies:
                assert expected_type in found_types, f"Missing strategy type: {expected_type}"

        except ClientError as e:
            pytest.fail(f"Failed to verify strategies: {e}")

    def test_memory_write_operation(self):
        """Test writing a memory record to verify S3 storage is accessible."""
        try:
            # Get semantic strategy for testing
            response = self.control_client.get_memory(memoryId=self.memory_id)
            strategies = response.get("memory", {}).get("strategies", [])

            semantic_strategy = None
            for s in strategies:
                if s["type"] == "SEMANTIC":
                    semantic_strategy = s
                    break

            assert semantic_strategy is not None, "SEMANTIC strategy not found"

            strategy_id = semantic_strategy["strategyId"]
            namespace = f"/strategies/{strategy_id}/actors/test_bootstrap/"

            # Write a test memory record
            test_content = f"Memory bootstrap test record - {datetime.now().isoformat()}"
            timestamp = datetime.now()

            self.runtime_client.batch_create_memory_records(
                memoryId=self.memory_id,
                records=[{
                    "requestIdentifier": f"bootstrap-test-{int(timestamp.timestamp())}",
                    "namespaces": [namespace],
                    "content": {"text": test_content},
                    "memoryStrategyId": strategy_id,
                    "timestamp": timestamp,
                }]
            )

            print(f"✓ Successfully wrote test memory record")
            print(f"  Namespace: {namespace}")
            print(f"  Content: {test_content}")

        except ClientError as e:
            pytest.fail(f"Failed to write memory record: {e}")

    def test_memory_read_operation(self):
        """Test reading memory records to verify S3 storage is readable."""
        try:
            # Get semantic strategy for testing
            response = self.control_client.get_memory(memoryId=self.memory_id)
            strategies = response.get("memory", {}).get("strategies", [])

            semantic_strategy = None
            for s in strategies:
                if s["type"] == "SEMANTIC":
                    semantic_strategy = s
                    break

            assert semantic_strategy is not None, "SEMANTIC strategy not found"

            strategy_id = semantic_strategy["strategyId"]
            namespace = f"/strategies/{strategy_id}/actors/test_bootstrap/"

            # Try to retrieve memory records
            response = self.runtime_client.retrieve_memory_records(
                memoryId=self.memory_id,
                namespace=namespace,
                searchCriteria={
                    "searchQuery": "bootstrap test",
                    "memoryStrategyId": strategy_id,
                    "topK": 5
                },
                maxResults=5
            )

            records = response.get("memoryRecordSummaries", [])
            print(f"✓ Successfully retrieved memory records")
            print(f"  Found {len(records)} records in namespace")

            # Verify we can access the record content
            if records:
                for i, record in enumerate(records[:3], 1):
                    content = record.get("content", {}).get("text", "")
                    print(f"  [{i}] {content[:80]}...")

        except ClientError as e:
            pytest.fail(f"Failed to read memory records: {e}")

    def test_memory_namespace_structure(self):
        """Verify memory namespace structure matches expected patterns."""
        try:
            response = self.control_client.get_memory(memoryId=self.memory_id)
            strategies = response.get("memory", {}).get("strategies", [])

            expected_patterns = {
                "SUMMARIZATION": ["/strategies/{memoryStrategyId}/actors/{actorId}/sessions/{sessionId}/"],
                "SEMANTIC": ["/strategies/{memoryStrategyId}/actors/{actorId}/"],
                "USER_PREFERENCE": ["/strategies/{memoryStrategyId}/actors/{actorId}/"]
            }

            for strategy in strategies:
                strategy_type = strategy["type"]
                namespaces = strategy.get("namespaces", [])

                if strategy_type in expected_patterns:
                    expected_ns = expected_patterns[strategy_type]
                    assert namespaces == expected_ns, (
                        f"Namespace mismatch for {strategy_type}: "
                        f"expected {expected_ns}, got {namespaces}"
                    )
                    print(f"✓ {strategy_type} namespace structure verified")

        except ClientError as e:
            pytest.fail(f"Failed to verify namespace structure: {e}")


def main():
    """Run tests directly when executed as a script."""
    # Run with pytest
    sys.exit(pytest.main([__file__, "-v", "-s"]))


if __name__ == "__main__":
    main()
