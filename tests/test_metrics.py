"""Tests for the metrics module."""

import pytest

from autoresearcher.metrics import MetricDefinition, MetricsTracker


class TestMetricDefinition:
    def test_is_improvement_higher_is_better(self):
        defn = MetricDefinition(name="accuracy", higher_is_better=True)
        assert defn.is_improvement(0.5, 0.8) is True
        assert defn.is_improvement(0.8, 0.5) is False
        assert defn.is_improvement(0.5, 0.5) is False

    def test_is_improvement_lower_is_better(self):
        defn = MetricDefinition(name="loss", higher_is_better=False)
        assert defn.is_improvement(0.8, 0.5) is True
        assert defn.is_improvement(0.5, 0.8) is False

    def test_default_values(self):
        defn = MetricDefinition(name="test")
        assert defn.min_value == 0.0
        assert defn.max_value == 1.0
        assert defn.higher_is_better is True
        assert defn.description == ""


class TestMetricsTracker:
    def test_record_and_history(self):
        tracker = MetricsTracker()
        tracker.record({"accuracy": 0.5})
        tracker.record({"accuracy": 0.7})
        assert len(tracker.history) == 2
        assert tracker.history[0]["accuracy"] == 0.5

    def test_get_best_higher_is_better(self):
        tracker = MetricsTracker([
            MetricDefinition(name="accuracy", higher_is_better=True)
        ])
        tracker.record({"accuracy": 0.5})
        tracker.record({"accuracy": 0.9})
        tracker.record({"accuracy": 0.7})
        idx, val = tracker.get_best("accuracy")
        assert idx == 1
        assert val == 0.9

    def test_get_best_lower_is_better(self):
        tracker = MetricsTracker([
            MetricDefinition(name="loss", higher_is_better=False)
        ])
        tracker.record({"loss": 0.8})
        tracker.record({"loss": 0.3})
        tracker.record({"loss": 0.5})
        idx, val = tracker.get_best("loss")
        assert idx == 1
        assert val == 0.3

    def test_get_best_no_definition_defaults_higher(self):
        tracker = MetricsTracker()
        tracker.record({"score": 0.2})
        tracker.record({"score": 0.9})
        idx, val = tracker.get_best("score")
        assert idx == 1
        assert val == 0.9

    def test_get_best_empty_raises(self):
        tracker = MetricsTracker()
        with pytest.raises(ValueError, match="No metrics recorded"):
            tracker.get_best("accuracy")

    def test_get_trend(self):
        tracker = MetricsTracker()
        tracker.record({"accuracy": 0.5})
        tracker.record({"accuracy": 0.7})
        tracker.record({"accuracy": 0.6})
        assert tracker.get_trend("accuracy") == [0.5, 0.7, 0.6]

    def test_get_trend_missing_metric(self):
        tracker = MetricsTracker()
        tracker.record({"accuracy": 0.5})
        assert tracker.get_trend("missing") == [0.0]

    def test_is_improving_upward_trend(self):
        tracker = MetricsTracker()
        tracker.record({"accuracy": 0.5})
        tracker.record({"accuracy": 0.6})
        tracker.record({"accuracy": 0.7})
        assert tracker.is_improving("accuracy") is True

    def test_is_improving_downward_trend(self):
        tracker = MetricsTracker()
        tracker.record({"accuracy": 0.7})
        tracker.record({"accuracy": 0.6})
        tracker.record({"accuracy": 0.5})
        assert tracker.is_improving("accuracy") is False

    def test_is_improving_single_entry(self):
        tracker = MetricsTracker()
        tracker.record({"accuracy": 0.5})
        assert tracker.is_improving("accuracy") is True

    def test_is_improving_lower_is_better(self):
        tracker = MetricsTracker([
            MetricDefinition(name="loss", higher_is_better=False)
        ])
        tracker.record({"loss": 0.8})
        tracker.record({"loss": 0.6})
        tracker.record({"loss": 0.4})
        assert tracker.is_improving("loss") is True

    def test_summary(self):
        tracker = MetricsTracker()
        tracker.record({"accuracy": 0.5, "loss": 0.8})
        tracker.record({"accuracy": 0.7, "loss": 0.6})
        tracker.record({"accuracy": 0.9, "loss": 0.4})
        s = tracker.summary()
        assert "accuracy" in s
        assert "loss" in s
        assert s["accuracy"]["first"] == 0.5
        assert s["accuracy"]["last"] == 0.9
        assert s["accuracy"]["min"] == 0.5
        assert s["accuracy"]["max"] == 0.9
        assert s["accuracy"]["improving"] is True

    def test_summary_empty(self):
        tracker = MetricsTracker()
        assert tracker.summary() == {}
