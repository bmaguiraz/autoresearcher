# -*- coding: utf-8 -*-
"""Tests for the experiment base classes."""

import json
import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from autoresearcher.experiment import BaseExperiment, ExperimentResult, ExperimentSummary, RetryConfig


class SimpleExperiment(BaseExperiment):
    """Concrete implementation for testing."""

    def __init__(self, config_path, **kwargs):
        super().__init__(config_path, **kwargs)
        self._score = 0.5

    def evaluate(self, cycle):
        self._score += 0.1
        return {"accuracy": min(self._score, 1.0)}

    def optimize(self, result):
        pass


class FlakeyExperiment(BaseExperiment):
    """Experiment that fails a configurable number of times before succeeding."""

    def __init__(self, config_path, fail_times=2, **kwargs):
        super().__init__(config_path, **kwargs)
        self._fail_times = fail_times
        self._attempt = 0

    def evaluate(self, cycle):
        self._attempt += 1
        if self._attempt <= self._fail_times:
            raise RuntimeError(f"Transient failure (attempt {self._attempt})")
        return {"accuracy": 0.9}

    def optimize(self, result):
        pass


def _make_config(tmp_path, cycles=3):
    config = {"experiment_id": "test-exp", "cycles": cycles}
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    return config_path


class TestExperimentResult:
    def test_aggregate_score_single_metric(self):
        r = ExperimentResult(experiment_id="x", cycle=1, metrics={"a": 0.8})
        assert r.aggregate_score == 0.8

    def test_aggregate_score_multiple_metrics(self):
        r = ExperimentResult(experiment_id="x", cycle=1, metrics={"a": 0.6, "b": 1.0})
        assert r.aggregate_score == 0.8

    def test_aggregate_score_empty(self):
        r = ExperimentResult(experiment_id="x", cycle=1, metrics={})
        assert r.aggregate_score == 0.0

    def test_to_dict_contains_aggregate(self):
        r = ExperimentResult(experiment_id="x", cycle=1, metrics={"a": 0.5})
        d = r.to_dict()
        assert "aggregate_score" in d
        assert d["aggregate_score"] == 0.5


class TestExperimentSummary:
    def test_improvement(self):
        s = ExperimentSummary(
            total_cycles=3,
            initial_score=0.5,
            final_score=0.8,
            best_score=0.8,
            average_score=0.65,
            elapsed_seconds=10.0,
        )
        assert s.improvement == 0.3

    def test_improvement_percentage(self):
        s = ExperimentSummary(
            total_cycles=3,
            initial_score=0.5,
            final_score=0.75,
            best_score=0.75,
            average_score=0.625,
            elapsed_seconds=5.0,
        )
        assert s.improvement_percentage == 50.0

    def test_improvement_percentage_zero_initial(self):
        s = ExperimentSummary(
            total_cycles=1,
            initial_score=0.0,
            final_score=0.5,
            best_score=0.5,
            average_score=0.5,
            elapsed_seconds=1.0,
        )
        assert s.improvement_percentage == 0.0

    def test_to_dict(self):
        s = ExperimentSummary(
            total_cycles=2,
            initial_score=0.4,
            final_score=0.6,
            best_score=0.6,
            average_score=0.5,
            elapsed_seconds=3.0,
        )
        d = s.to_dict()
        # Verify all dataclass fields
        assert d["total_cycles"] == 2
        assert d["initial_score"] == 0.4
        assert d["final_score"] == 0.6
        assert d["best_score"] == 0.6
        assert d["average_score"] == 0.5
        assert d["elapsed_seconds"] == 3.0
        assert d["status_test_id"] == "experiment-status"
        # Verify computed properties are included
        assert "improvement" in d
        assert d["improvement"] == 0.2
        assert "improvement_percentage" in d
        assert d["improvement_percentage"] == 50.0


class TestBaseExperiment:
    def test_init_loads_config(self, tmp_path):
        config_path = _make_config(tmp_path)
        exp = SimpleExperiment(config_path)
        assert exp.experiment_id == "test-exp"
        assert exp.max_cycles == 3

    def test_run_cycle(self, tmp_path):
        config_path = _make_config(tmp_path, cycles=1)
        exp = SimpleExperiment(config_path)
        result = exp.run_cycle(1)
        assert result.cycle == 1
        assert "accuracy" in result.metrics
        assert len(exp.results) == 1

    def test_run_full(self, tmp_path):
        config_path = _make_config(tmp_path, cycles=2)
        exp = SimpleExperiment(config_path)
        summary = exp.run()
        assert summary.total_cycles == 2
        assert summary.final_score >= summary.initial_score

    def test_export_results(self, tmp_path):
        config_path = _make_config(tmp_path)
        exp = SimpleExperiment(config_path)
        exp.run_cycle(1)
        results_files = list(exp.results_dir.glob("results_*.json"))
        assert len(results_files) >= 1

    def test_results_dir_created(self, tmp_path):
        config_path = _make_config(tmp_path)
        exp = SimpleExperiment(config_path)
        assert exp.results_dir.exists()

    def test_generate_summary_empty(self, tmp_path):
        config_path = _make_config(tmp_path)
        exp = SimpleExperiment(config_path)
        summary = exp.generate_summary(0.0)
        assert summary.total_cycles == 0
        assert summary.best_score == 0.0

    def test_default_retry_config(self, tmp_path):
        config_path = _make_config(tmp_path)
        exp = SimpleExperiment(config_path)
        assert exp.retry_config.max_retries == 3
        assert exp.retry_config.base_delay == 1.0

    def test_custom_retry_config(self, tmp_path):
        config_path = _make_config(tmp_path)
        rc = RetryConfig(max_retries=5, base_delay=0.5)
        exp = SimpleExperiment(config_path, retry_config=rc)
        assert exp.retry_config.max_retries == 5
        assert exp.retry_config.base_delay == 0.5


class TestRetryConfig:
    def test_default_values(self):
        rc = RetryConfig()
        assert rc.max_retries == 3
        assert rc.base_delay == 1.0
        assert rc.backoff_factor == 2.0

    def test_get_delay(self):
        rc = RetryConfig(base_delay=1.0, backoff_factor=2.0)
        assert rc.get_delay(0) == 1.0
        assert rc.get_delay(1) == 2.0
        assert rc.get_delay(2) == 4.0

    def test_custom_backoff(self):
        rc = RetryConfig(base_delay=0.5, backoff_factor=3.0)
        assert rc.get_delay(0) == 0.5
        assert rc.get_delay(1) == 1.5
        assert rc.get_delay(2) == 4.5


class TestRetryLogic:
    @patch("autoresearcher.experiment.time.sleep")
    def test_retry_succeeds_after_failures(self, mock_sleep, tmp_path):
        config_path = _make_config(tmp_path, cycles=1)
        rc = RetryConfig(max_retries=3, base_delay=0.1)
        exp = FlakeyExperiment(config_path, fail_times=2, retry_config=rc)
        result = exp.run_cycle(1)
        assert result.metrics["accuracy"] == 0.9
        assert mock_sleep.call_count == 2

    @patch("autoresearcher.experiment.time.sleep")
    def test_retry_exhausted_raises(self, mock_sleep, tmp_path):
        config_path = _make_config(tmp_path, cycles=1)
        rc = RetryConfig(max_retries=2, base_delay=0.1)
        exp = FlakeyExperiment(config_path, fail_times=5, retry_config=rc)
        with pytest.raises(RuntimeError, match="Transient failure"):
            exp.run_cycle(1)
        assert mock_sleep.call_count == 2

    @patch("autoresearcher.experiment.time.sleep")
    def test_no_retry_on_success(self, mock_sleep, tmp_path):
        config_path = _make_config(tmp_path, cycles=1)
        rc = RetryConfig(max_retries=3, base_delay=0.1)
        exp = SimpleExperiment(config_path, retry_config=rc)
        result = exp.run_cycle(1)
        assert "accuracy" in result.metrics
        mock_sleep.assert_not_called()

    @patch("autoresearcher.experiment.time.sleep")
    def test_retry_with_zero_retries(self, mock_sleep, tmp_path):
        config_path = _make_config(tmp_path, cycles=1)
        rc = RetryConfig(max_retries=0, base_delay=0.1)
        exp = FlakeyExperiment(config_path, fail_times=1, retry_config=rc)
        with pytest.raises(RuntimeError):
            exp.run_cycle(1)
        mock_sleep.assert_not_called()

    @patch("autoresearcher.experiment.time.sleep")
    def test_retry_backoff_delays(self, mock_sleep, tmp_path):
        config_path = _make_config(tmp_path, cycles=1)
        rc = RetryConfig(max_retries=3, base_delay=1.0, backoff_factor=2.0)
        exp = FlakeyExperiment(config_path, fail_times=3, retry_config=rc)
        result = exp.run_cycle(1)
        assert result.metrics["accuracy"] == 0.9
        delays = [call.args[0] for call in mock_sleep.call_args_list]
        assert delays == [1.0, 2.0, 4.0]

    @patch("autoresearcher.experiment.time.sleep")
    def test_retryable_exceptions_filter(self, mock_sleep, tmp_path):
        """Only retry on specified exception types."""
        config_path = _make_config(tmp_path, cycles=1)
        rc = RetryConfig(max_retries=3, base_delay=0.1, retryable_exceptions=(ValueError,))
        exp = FlakeyExperiment(config_path, fail_times=1, retry_config=rc)
        # FlakeyExperiment raises RuntimeError, not ValueError
        with pytest.raises(RuntimeError):
            exp.run_cycle(1)
        mock_sleep.assert_not_called()


class TestLogging:
    def test_init_logs_info(self, tmp_path, caplog):
        config_path = _make_config(tmp_path)
        with caplog.at_level(logging.INFO, logger="autoresearcher.experiment"):
            SimpleExperiment(config_path)
        assert any("Experiment initialized" in r.message for r in caplog.records)

    def test_run_cycle_logs_start_and_completion(self, tmp_path, caplog):
        config_path = _make_config(tmp_path, cycles=1)
        exp = SimpleExperiment(config_path)
        with caplog.at_level(logging.INFO, logger="autoresearcher.experiment"):
            exp.run_cycle(1)
        messages = [r.message for r in caplog.records]
        assert any("Starting cycle" in m for m in messages)
        assert any("completed successfully" in m for m in messages)

    def test_run_logs_experiment_summary(self, tmp_path, caplog):
        config_path = _make_config(tmp_path, cycles=1)
        exp = SimpleExperiment(config_path)
        with caplog.at_level(logging.INFO, logger="autoresearcher.experiment"):
            exp.run()
        messages = [r.message for r in caplog.records]
        assert any("Starting experiment run" in m for m in messages)
        assert any("completed" in m for m in messages)

    def test_debug_logs_config(self, tmp_path, caplog):
        config_path = _make_config(tmp_path)
        with caplog.at_level(logging.DEBUG, logger="autoresearcher.experiment"):
            SimpleExperiment(config_path)
        messages = [r.message for r in caplog.records]
        assert any("config" in m.lower() for m in messages)

    def test_error_logged_on_failure(self, tmp_path, caplog):
        config_path = _make_config(tmp_path, cycles=1)
        rc = RetryConfig(max_retries=0)
        exp = FlakeyExperiment(config_path, fail_times=1, retry_config=rc)
        with caplog.at_level(logging.ERROR, logger="autoresearcher.experiment"):
            with pytest.raises(RuntimeError):
                exp.run()
        assert any(r.levelno == logging.ERROR for r in caplog.records)

    @patch("autoresearcher.experiment.time.sleep")
    def test_retry_logs_warning(self, mock_sleep, tmp_path, caplog):
        config_path = _make_config(tmp_path, cycles=1)
        rc = RetryConfig(max_retries=3, base_delay=0.1)
        exp = FlakeyExperiment(config_path, fail_times=1, retry_config=rc)
        with caplog.at_level(logging.WARNING, logger="autoresearcher.experiment"):
            exp.run_cycle(1)
        assert any(r.levelno == logging.WARNING for r in caplog.records)
        assert any("Evaluation failed" in r.message for r in caplog.records)
