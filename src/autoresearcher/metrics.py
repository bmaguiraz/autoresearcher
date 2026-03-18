# -*- coding: utf-8 -*-
"""Metrics tracking and comparison utilities."""

from dataclasses import dataclass
from typing import Any


@dataclass
class MetricDefinition:
    """Defines a metric with its expected range and optimization direction."""

    name: str
    description: str = ""
    min_value: float = 0.0
    max_value: float = 1.0
    higher_is_better: bool = True

    def is_improvement(self, old_value: float, new_value: float) -> bool:
        """Check if new_value is an improvement over old_value."""
        if self.higher_is_better:
            return new_value > old_value
        return new_value < old_value


class MetricsTracker:
    """Tracks metrics across experiment cycles and compares results."""

    def __init__(self, metric_definitions: list[MetricDefinition] | None = None):
        self.definitions: dict[str, MetricDefinition] = {}
        if metric_definitions:
            for defn in metric_definitions:
                self.definitions[defn.name] = defn
        self.history: list[dict[str, float]] = []

    def record(self, metrics: dict[str, float]) -> None:
        """Record a set of metrics for one cycle."""
        self.history.append(dict(metrics))

    def get_best(self, metric_name: str) -> tuple[int, float]:
        """Get the cycle index and value of the best result for a metric.

        Returns (cycle_index, best_value).
        """
        if not self.history:
            raise ValueError("No metrics recorded yet")

        values = [h.get(metric_name, 0.0) for h in self.history]
        defn = self.definitions.get(metric_name)

        if defn and not defn.higher_is_better:
            best_idx = min(range(len(values)), key=lambda i: values[i])
        else:
            best_idx = max(range(len(values)), key=lambda i: values[i])

        return best_idx, values[best_idx]

    def get_trend(self, metric_name: str) -> list[float]:
        """Get the value history for a specific metric."""
        return [h.get(metric_name, 0.0) for h in self.history]

    def is_improving(self, metric_name: str, window: int = 3) -> bool:
        """Check if a metric is trending upward over the last N cycles."""
        trend = self.get_trend(metric_name)
        if len(trend) < 2:
            return True

        recent = trend[-window:] if len(trend) >= window else trend
        defn = self.definitions.get(metric_name)

        if defn and not defn.higher_is_better:
            return recent[-1] < recent[0]
        return recent[-1] > recent[0]

    def summary(self) -> dict[str, Any]:
        """Generate a summary of all tracked metrics."""
        if not self.history:
            return {}

        result = {}
        all_metric_names = set()
        for h in self.history:
            all_metric_names.update(h.keys())

        for name in sorted(all_metric_names):
            values = [h.get(name, 0.0) for h in self.history]
            result[name] = {
                "first": values[0],
                "last": values[-1],
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "improving": self.is_improving(name),
            }

        return result
