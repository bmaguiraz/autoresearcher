# -*- coding: utf-8 -*-
"""Tests for concurrent execution utilities."""

import json
import logging
import time
from pathlib import Path

import pytest

from autoresearcher.concurrent import (
    ConcurrentExperimentRunner,
    ConcurrentEvaluator,
    ConcurrentExperimentResult,
)
from autoresearcher.experiment import BaseExperiment


class MockExperiment(BaseExperiment):
    """Mock experiment for testing concurrency."""

    def __init__(self, config_path, sleep_time=0.1):
        super().__init__(config_path)
        self.sleep_time = sleep_time
        self._score = 0.5

    def evaluate(self, cycle):
        time.sleep(self.sleep_time)
        self._score += 0.1
        return {"accuracy": min(self._score, 1.0)}

    def optimize(self, result):
        pass


class FailingExperiment(BaseExperiment):
    """Mock experiment that always fails."""

    def __init__(self, config_path):
        super().__init__(config_path)

    def evaluate(self, cycle):
        raise ValueError("Intentional test failure")

    def optimize(self, result):
        pass


def _make_config(tmp_path, experiment_id, cycles=2):
    """Helper to create a test config file."""
    config = {"experiment_id": experiment_id, "cycles": cycles}
    config_path = tmp_path / f"{experiment_id}_config.json"
    config_path.write_text(json.dumps(config))
    return config_path


class TestConcurrentExperimentRunner:
    def test_run_single_experiment(self, tmp_path):
        """Test running a single experiment works correctly."""
        config_path = _make_config(tmp_path, "exp-1")
        exp = MockExperiment(config_path)

        runner = ConcurrentExperimentRunner(max_workers=1)
        results = runner.run_experiments([exp])

        assert len(results) == 1
        assert results[0].experiment_id == "exp-1"
        assert results[0].success is True
        assert results[0].error is None
        assert results[0].summary.total_cycles == 2

    def test_run_multiple_experiments(self, tmp_path):
        """Test running multiple experiments concurrently."""
        experiments = []
        for i in range(3):
            config_path = _make_config(tmp_path, f"exp-{i}")
            experiments.append(MockExperiment(config_path))

        runner = ConcurrentExperimentRunner(max_workers=3)
        results = runner.run_experiments(experiments)

        assert len(results) == 3
        exp_ids = {r.experiment_id for r in results}
        assert exp_ids == {"exp-0", "exp-1", "exp-2"}
        assert all(r.success for r in results)

    def test_concurrent_execution_faster_than_sequential(self, tmp_path):
        """Test that concurrent execution is faster than sequential."""
        sleep_time = 0.2
        num_experiments = 3

        experiments = []
        for i in range(num_experiments):
            config_path = _make_config(tmp_path, f"exp-{i}", cycles=1)
            experiments.append(MockExperiment(config_path, sleep_time=sleep_time))

        # Run concurrently
        runner = ConcurrentExperimentRunner(max_workers=num_experiments)
        start = time.time()
        results = runner.run_experiments(experiments)
        concurrent_time = time.time() - start

        # Sequential would take at least: sleep_time * num_experiments * cycles
        # Concurrent should be significantly faster
        expected_sequential_time = sleep_time * num_experiments * 1
        assert concurrent_time < expected_sequential_time * 0.8  # Allow some overhead

    def test_handles_experiment_failure(self, tmp_path):
        """Test that failures in one experiment don't affect others."""
        config_path_1 = _make_config(tmp_path, "exp-success")
        config_path_2 = _make_config(tmp_path, "exp-fail")

        exp_success = MockExperiment(config_path_1)
        exp_fail = FailingExperiment(config_path_2)

        runner = ConcurrentExperimentRunner(max_workers=2)
        results = runner.run_experiments([exp_success, exp_fail])

        assert len(results) == 2

        success_result = next(r for r in results if r.experiment_id == "exp-success")
        fail_result = next(r for r in results if r.experiment_id == "exp-fail")

        assert success_result.success is True
        assert fail_result.success is False
        assert "Intentional test failure" in fail_result.error

    def test_empty_experiment_list(self):
        """Test handling of empty experiment list."""
        runner = ConcurrentExperimentRunner()
        results = runner.run_experiments([])
        assert results == []

    def test_max_workers_parameter(self, tmp_path):
        """Test that max_workers parameter is respected."""
        experiments = []
        for i in range(5):
            config_path = _make_config(tmp_path, f"exp-{i}", cycles=1)
            experiments.append(MockExperiment(config_path, sleep_time=0.05))

        # Test with limited workers
        runner = ConcurrentExperimentRunner(max_workers=2)
        results = runner.run_experiments(experiments)

        assert len(results) == 5
        assert all(r.success for r in results)


class TestConcurrentEvaluator:
    def test_evaluate_batch_single_item(self):
        """Test evaluating a single item."""
        evaluator = ConcurrentEvaluator()

        def eval_fn(x):
            return {"score": x * 2}

        results = evaluator.evaluate_batch(eval_fn, [5])

        assert len(results) == 1
        assert results[0] == {"score": 10}

    def test_evaluate_batch_multiple_items(self):
        """Test evaluating multiple items."""
        evaluator = ConcurrentEvaluator(max_workers=3)

        def eval_fn(x):
            time.sleep(0.05)  # Simulate work
            return {"value": x ** 2}

        items = [1, 2, 3, 4]
        results = evaluator.evaluate_batch(eval_fn, items)

        assert len(results) == 4
        assert results[0] == {"value": 1}
        assert results[1] == {"value": 4}
        assert results[2] == {"value": 9}
        assert results[3] == {"value": 16}

    def test_evaluate_batch_preserves_order(self):
        """Test that results maintain the same order as inputs."""
        evaluator = ConcurrentEvaluator(max_workers=4)

        def eval_fn(x):
            # Add variable sleep to ensure different completion times
            time.sleep(0.01 * (5 - x))
            return {"id": x}

        items = [1, 2, 3, 4, 5]
        results = evaluator.evaluate_batch(eval_fn, items)

        assert len(results) == 5
        for i, result in enumerate(results):
            assert result["id"] == items[i]

    def test_evaluate_batch_empty_list(self):
        """Test handling of empty input list."""
        evaluator = ConcurrentEvaluator()

        def eval_fn(x):
            return {"value": x}

        results = evaluator.evaluate_batch(eval_fn, [])
        assert results == []

    def test_concurrent_evaluation_faster_than_sequential(self):
        """Test that concurrent evaluation is faster."""
        sleep_time = 0.1
        num_items = 4

        evaluator = ConcurrentEvaluator(max_workers=num_items)

        def eval_fn(x):
            time.sleep(sleep_time)
            return {"result": x}

        items = list(range(num_items))

        start = time.time()
        results = evaluator.evaluate_batch(eval_fn, items)
        concurrent_time = time.time() - start

        expected_sequential_time = sleep_time * num_items
        assert concurrent_time < expected_sequential_time * 0.8

    def test_evaluate_batch_with_complex_results(self):
        """Test evaluation with complex result structures."""
        evaluator = ConcurrentEvaluator()

        def eval_fn(item):
            return {
                "accuracy": item["value"] * 0.1,
                "precision": item["value"] * 0.15,
                "recall": item["value"] * 0.12,
            }

        items = [{"value": i} for i in range(1, 4)]
        results = evaluator.evaluate_batch(eval_fn, items)

        assert len(results) == 3
        assert results[0]["accuracy"] == pytest.approx(0.1)
        assert results[1]["precision"] == pytest.approx(0.3)
        assert results[2]["recall"] == pytest.approx(0.36)


class TestConcurrentExperimentResult:
    def test_result_dataclass_structure(self):
        """Test that ConcurrentExperimentResult has correct structure."""
        result = ConcurrentExperimentResult(
            experiment_id="test-exp",
            summary=None,  # type: ignore
            success=False,
            error="Test error",
        )

        assert result.experiment_id == "test-exp"
        assert result.success is False
        assert result.error == "Test error"


class TestConcurrentLogging:
    def test_run_experiments_logs_start_and_finish(self, tmp_path, caplog):
        """Test that running experiments logs start and finish messages."""
        config_path = _make_config(tmp_path, "exp-log", cycles=1)
        exp = MockExperiment(config_path, sleep_time=0.01)
        runner = ConcurrentExperimentRunner(max_workers=1)
        with caplog.at_level(logging.INFO, logger="autoresearcher.concurrent"):
            runner.run_experiments([exp])
        messages = [r.message for r in caplog.records]
        assert any("Starting concurrent run" in m for m in messages)
        assert any("Concurrent run finished" in m for m in messages)

    def test_successful_experiment_logs_info(self, tmp_path, caplog):
        """Test that a successful experiment logs an info message."""
        config_path = _make_config(tmp_path, "exp-ok", cycles=1)
        exp = MockExperiment(config_path, sleep_time=0.01)
        runner = ConcurrentExperimentRunner(max_workers=1)
        with caplog.at_level(logging.INFO, logger="autoresearcher.concurrent"):
            runner.run_experiments([exp])
        assert any("completed successfully" in r.message for r in caplog.records)

    def test_failed_experiment_logs_warning(self, tmp_path, caplog):
        """Test that a failed experiment logs a warning."""
        config_path = _make_config(tmp_path, "exp-bad", cycles=1)
        exp = FailingExperiment(config_path)
        runner = ConcurrentExperimentRunner(max_workers=1)
        with caplog.at_level(logging.WARNING, logger="autoresearcher.concurrent"):
            runner.run_experiments([exp])
        assert any(r.levelno == logging.WARNING for r in caplog.records)
        assert any("failed" in r.message for r in caplog.records)

    def test_failed_experiment_logs_error_in_runner(self, tmp_path, caplog):
        """Test that the internal runner logs an error for exceptions."""
        config_path = _make_config(tmp_path, "exp-err", cycles=1)
        exp = FailingExperiment(config_path)
        runner = ConcurrentExperimentRunner(max_workers=1)
        with caplog.at_level(logging.ERROR, logger="autoresearcher.concurrent"):
            runner.run_experiments([exp])
        assert any(r.levelno == logging.ERROR for r in caplog.records)

    def test_batch_evaluation_logs_info(self, caplog):
        """Test that batch evaluation logs start and completion."""
        evaluator = ConcurrentEvaluator()
        with caplog.at_level(logging.INFO, logger="autoresearcher.concurrent"):
            evaluator.evaluate_batch(lambda x: {"v": x}, [1, 2, 3])
        messages = [r.message for r in caplog.records]
        assert any("Starting batch evaluation" in m for m in messages)
        assert any("Batch evaluation complete" in m for m in messages)
