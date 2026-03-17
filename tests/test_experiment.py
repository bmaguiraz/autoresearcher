"""Tests for the experiment module."""

import json

import pytest

from autoresearcher.experiment import (
    BaseExperiment,
    ExperimentResult,
    ExperimentSummary,
)


class TestExperimentResult:
    def test_aggregate_score_single_metric(self):
        result = ExperimentResult(
            experiment_id="test", cycle=1, metrics={"accuracy": 0.85}
        )
        assert result.aggregate_score == 0.85

    def test_aggregate_score_multiple_metrics(self):
        result = ExperimentResult(
            experiment_id="test",
            cycle=1,
            metrics={"accuracy": 0.8, "precision": 0.9},
        )
        assert result.aggregate_score == pytest.approx(0.85)

    def test_aggregate_score_empty_metrics(self):
        result = ExperimentResult(
            experiment_id="test", cycle=1, metrics={}
        )
        assert result.aggregate_score == 0.0

    def test_to_dict_includes_aggregate_score(self):
        result = ExperimentResult(
            experiment_id="test", cycle=1, metrics={"accuracy": 0.75}
        )
        d = result.to_dict()
        assert d["experiment_id"] == "test"
        assert d["cycle"] == 1
        assert d["aggregate_score"] == 0.75

    def test_metadata_default_empty(self):
        result = ExperimentResult(
            experiment_id="test", cycle=1, metrics={"acc": 0.5}
        )
        assert result.metadata == {}

    def test_timestamp_auto_set(self):
        result = ExperimentResult(
            experiment_id="test", cycle=1, metrics={"acc": 0.5}
        )
        assert result.timestamp


class TestExperimentSummary:
    def test_improvement_positive(self):
        summary = ExperimentSummary(
            total_cycles=3,
            initial_score=0.7,
            final_score=0.9,
            best_score=0.9,
            average_score=0.8,
            elapsed_seconds=10.0,
        )
        assert summary.improvement == 0.2

    def test_improvement_negative(self):
        summary = ExperimentSummary(
            total_cycles=3,
            initial_score=0.9,
            final_score=0.7,
            best_score=0.9,
            average_score=0.8,
            elapsed_seconds=10.0,
        )
        assert summary.improvement == -0.2

    def test_improvement_percentage(self):
        summary = ExperimentSummary(
            total_cycles=3,
            initial_score=0.5,
            final_score=0.75,
            best_score=0.75,
            average_score=0.6,
            elapsed_seconds=10.0,
        )
        assert summary.improvement_percentage == 50.0

    def test_improvement_percentage_zero_initial(self):
        summary = ExperimentSummary(
            total_cycles=1,
            initial_score=0.0,
            final_score=0.5,
            best_score=0.5,
            average_score=0.5,
            elapsed_seconds=5.0,
        )
        assert summary.improvement_percentage == 0.0

    def test_to_dict(self):
        summary = ExperimentSummary(
            total_cycles=2,
            initial_score=0.6,
            final_score=0.8,
            best_score=0.8,
            average_score=0.7,
            elapsed_seconds=15.0,
        )
        d = summary.to_dict()
        assert d["total_cycles"] == 2
        assert "improvement" in d
        assert "improvement_percentage" in d


class _DummyExperiment(BaseExperiment):
    """Concrete experiment subclass for testing."""

    def __init__(self, config_path, eval_results=None):
        super().__init__(config_path)
        self._eval_results = eval_results or [
            {"accuracy": 0.7 + i * 0.1} for i in range(self.max_cycles)
        ]
        self.optimize_calls = []

    def evaluate(self, cycle):
        return self._eval_results[cycle - 1]

    def optimize(self, result):
        self.optimize_calls.append(result)


class TestBaseExperiment:
    def test_init_loads_config(self, tmp_experiment_dir):
        _, config_file = tmp_experiment_dir
        exp = _DummyExperiment(config_file)
        assert exp.experiment_id == "test-exp-001"
        assert exp.max_cycles == 3

    def test_init_creates_results_dir(self, tmp_experiment_dir):
        tmp_path, config_file = tmp_experiment_dir
        exp = _DummyExperiment(config_file)
        assert (tmp_path / "results").is_dir()

    def test_run_cycle(self, tmp_experiment_dir):
        _, config_file = tmp_experiment_dir
        exp = _DummyExperiment(config_file)
        result = exp.run_cycle(1)
        assert result.cycle == 1
        assert "accuracy" in result.metrics
        assert len(exp.results) == 1

    def test_run_completes_all_cycles(self, tmp_experiment_dir):
        _, config_file = tmp_experiment_dir
        exp = _DummyExperiment(config_file)
        summary = exp.run()
        assert summary.total_cycles == 3
        assert len(exp.results) == 3

    def test_optimize_called_except_last_cycle(self, tmp_experiment_dir):
        _, config_file = tmp_experiment_dir
        exp = _DummyExperiment(config_file)
        exp.run()
        assert len(exp.optimize_calls) == 2

    def test_save_results_creates_files(self, tmp_experiment_dir):
        tmp_path, config_file = tmp_experiment_dir
        exp = _DummyExperiment(config_file)
        exp.run_cycle(1)
        results_dir = tmp_path / "results"
        assert (results_dir / "results_latest.json").exists()

    def test_generate_summary(self, tmp_experiment_dir):
        _, config_file = tmp_experiment_dir
        exp = _DummyExperiment(config_file)
        exp.run()
        summary = exp.generate_summary(10.0)
        assert summary.initial_score == exp.results[0].aggregate_score
        assert summary.final_score == exp.results[-1].aggregate_score
