"""Tests for the experiment base classes."""

import json
from pathlib import Path

from autoresearcher.experiment import BaseExperiment, ExperimentResult, ExperimentSummary


class SimpleExperiment(BaseExperiment):
    """Concrete implementation for testing."""

    def __init__(self, config_path):
        super().__init__(config_path)
        self._score = 0.5

    def evaluate(self, cycle):
        self._score += 0.1
        return {"accuracy": min(self._score, 1.0)}

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
        assert "improvement" in d
        assert "improvement_percentage" in d


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

    def test_save_results(self, tmp_path):
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
