"""Base experiment classes for the autoresearcher framework."""

import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ExperimentResult:
    """Stores the result of a single experiment run."""

    experiment_id: str
    cycle: int
    metrics: dict[str, float]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def aggregate_score(self) -> float:
        """Calculate the mean of all metric values."""
        if not self.metrics:
            return 0.0
        return sum(self.metrics.values()) / len(self.metrics)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        d = asdict(self)
        d["aggregate_score"] = self.aggregate_score
        return d


@dataclass
class ExperimentSummary:
    """Summary statistics across multiple experiment runs."""

    total_cycles: int
    initial_score: float
    final_score: float
    best_score: float
    average_score: float
    elapsed_seconds: float

    @property
    def improvement(self) -> float:
        return round(self.final_score - self.initial_score, 4)

    @property
    def improvement_percentage(self) -> float:
        if self.initial_score == 0:
            return 0.0
        return round((self.final_score - self.initial_score) / self.initial_score * 100, 2)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["improvement"] = self.improvement
        d["improvement_percentage"] = self.improvement_percentage
        return d


class BaseExperiment(ABC):
    """Abstract base class for all experiments.

    Subclasses must implement:
        - evaluate(): Run evaluation and return metrics
        - optimize(): Generate an improved configuration
    """

    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        self.experiment_dir = self.config_path.parent
        self.results_dir = self.experiment_dir / "results"
        self.results_dir.mkdir(exist_ok=True)

        with open(self.config_path) as f:
            self.config = json.load(f)

        self.experiment_id: str = self.config.get("experiment_id", "unknown")
        self.max_cycles: int = self.config.get("cycles", 5)
        self.results: list[ExperimentResult] = []

    @abstractmethod
    def evaluate(self, cycle: int) -> dict[str, float]:
        """Run evaluation and return a dict of metric_name -> score."""
        ...

    @abstractmethod
    def optimize(self, result: ExperimentResult) -> None:
        """Apply optimization based on the latest result."""
        ...

    def run_cycle(self, cycle: int) -> ExperimentResult:
        """Execute a single experiment cycle."""
        logger.info("=" * 50)
        logger.info(f"Cycle {cycle}/{self.max_cycles}")
        logger.info("=" * 50)

        logger.info("[1/3] Evaluating...")
        metrics = self.evaluate(cycle)

        result = ExperimentResult(
            experiment_id=self.experiment_id,
            cycle=cycle,
            metrics=metrics,
        )
        self.results.append(result)

        logger.info(f"  Aggregate Score: {result.aggregate_score:.3f}")
        for name, value in metrics.items():
            logger.info(f"  {name}: {value:.3f}")

        if cycle < self.max_cycles:
            logger.info("[2/3] Optimizing...")
            self.optimize(result)

        logger.info("[3/3] Saving results...")
        self.save_results()

        return result

    def run(self) -> ExperimentSummary:
        """Execute the full experiment loop."""
        logger.info(f"# Experiment: {self.experiment_id}")
        logger.info(f"# Cycles: {self.max_cycles}")

        start_time = time.time()

        for cycle in range(1, self.max_cycles + 1):
            self.run_cycle(cycle)

        elapsed = time.time() - start_time
        summary = self.generate_summary(elapsed)

        logger.info("=" * 50)
        logger.info("Experiment Complete!")
        logger.info(f"  Initial Score: {summary.initial_score:.3f}")
        logger.info(f"  Final Score:   {summary.final_score:.3f}")
        logger.info(f"  Improvement:   {summary.improvement:+.3f} ({summary.improvement_percentage:.1f}%)")
        logger.info(f"  Best Score:    {summary.best_score:.3f}")
        logger.info(f"  Elapsed:       {elapsed:.1f}s")

        return summary

    def generate_summary(self, elapsed: float) -> ExperimentSummary:
        """Generate summary statistics from collected results."""
        scores = [r.aggregate_score for r in self.results]
        return ExperimentSummary(
            total_cycles=len(self.results),
            initial_score=scores[0] if scores else 0.0,
            final_score=scores[-1] if scores else 0.0,
            best_score=max(scores) if scores else 0.0,
            average_score=round(sum(scores) / len(scores), 4) if scores else 0.0,
            elapsed_seconds=round(elapsed, 1),
        )

    def save_results(self) -> Path:
        """Save current results to disk. Returns the path to the results file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"results_{timestamp}.json"

        output = {
            "experiment_id": self.experiment_id,
            "config": self.config,
            "cycles_completed": len(self.results),
            "results": [r.to_dict() for r in self.results],
        }

        with open(results_file, "w") as f:
            json.dump(output, f, indent=2)

        latest_file = self.results_dir / "results_latest.json"
        with open(latest_file, "w") as f:
            json.dump(output, f, indent=2)

        return results_file
