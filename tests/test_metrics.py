# -*- coding: utf-8 -*-
"""Tests for the metrics tracking module."""

from autoresearcher.metrics import MetricDefinition, MetricsTracker


class TestMetricDefinition:
    def test_is_improvement_higher_is_better(self):
        m = MetricDefinition(name="accuracy", higher_is_better=True)
        assert m.is_improvement(0.5, 0.8) is True
        assert m.is_improvement(0.8, 0.5) is False

    def test_is_improvement_lower_is_better(self):
        m = MetricDefinition(name="loss", higher_is_better=False)
        assert m.is_improvement(0.8, 0.5) is True
        assert m.is_improvement(0.5, 0.8) is False

    def test_defaults(self):
        m = MetricDefinition(name="score")
        assert m.min_value == 0.0
        assert m.max_value == 1.0
        assert m.higher_is_better is True


class TestMetricsTracker:
    def test_record_and_history(self):
        tracker = MetricsTracker()
        tracker.record({"accuracy": 0.5})
        tracker.record({"accuracy": 0.7})
        assert len(tracker.history) == 2

    def test_get_best_higher_is_better(self):
        defn = MetricDefinition(name="accuracy", higher_is_better=True)
        tracker = MetricsTracker([defn])
        tracker.record({"accuracy": 0.5})
        tracker.record({"accuracy": 0.9})
        tracker.record({"accuracy": 0.7})
        idx, val = tracker.get_best("accuracy")
        assert idx == 1
        assert val == 0.9

    def test_get_best_lower_is_better(self):
        defn = MetricDefinition(name="loss", higher_is_better=False)
        tracker = MetricsTracker([defn])
        tracker.record({"loss": 0.8})
        tracker.record({"loss": 0.3})
        tracker.record({"loss": 0.5})
        idx, val = tracker.get_best("loss")
        assert idx == 1
        assert val == 0.3

    def test_get_best_no_history_raises(self):
        tracker = MetricsTracker()
        try:
            tracker.get_best("accuracy")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_get_trend(self):
        tracker = MetricsTracker()
        tracker.record({"accuracy": 0.5})
        tracker.record({"accuracy": 0.7})
        tracker.record({"accuracy": 0.6})
        assert tracker.get_trend("accuracy") == [0.5, 0.7, 0.6]

    def test_is_improving_upward(self):
        defn = MetricDefinition(name="accuracy", higher_is_better=True)
        tracker = MetricsTracker([defn])
        tracker.record({"accuracy": 0.5})
        tracker.record({"accuracy": 0.7})
        assert tracker.is_improving("accuracy") is True

    def test_is_improving_downward_for_loss(self):
        defn = MetricDefinition(name="loss", higher_is_better=False)
        tracker = MetricsTracker([defn])
        tracker.record({"loss": 0.8})
        tracker.record({"loss": 0.5})
        assert tracker.is_improving("loss") is True

    def test_is_improving_single_entry(self):
        tracker = MetricsTracker()
        tracker.record({"accuracy": 0.5})
        assert tracker.is_improving("accuracy") is True

    def test_summary(self):
        tracker = MetricsTracker()
        tracker.record({"accuracy": 0.5, "f1": 0.4})
        tracker.record({"accuracy": 0.7, "f1": 0.6})
        s = tracker.summary()
        assert "accuracy" in s
        assert "f1" in s
        assert s["accuracy"]["first"] == 0.5
        assert s["accuracy"]["last"] == 0.7
        assert s["accuracy"]["max"] == 0.7

    def test_summary_empty(self):
        tracker = MetricsTracker()
        assert tracker.summary() == {}

    def test_get_best_undefined_metric(self):
        tracker = MetricsTracker()
        tracker.record({"accuracy": 0.5})
        tracker.record({"accuracy": 0.9})
        idx, val = tracker.get_best("accuracy")
        assert idx == 1
        assert val == 0.9
