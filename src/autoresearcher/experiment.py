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

        logger.info(f"Initializing experiment from config: {self.config_path}")

        with open(self.config_path) as f:
            self.config = json.load(f)

        self.experiment_id: str = self.config.get("experiment_id", "unknown")
        self.max_cycles: int = self.config.get("cycles", 5)
        self.results: list[ExperimentResult] = []

        logger.info(f"Experiment initialized: id={self.experiment_id}, max_cycles={self.max_cycles}")
        logger.debug(f"Experiment config: {json.dumps(self.config, indent=2)}")

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
        logger.info(f"Starting cycle {cycle}/{self.max_cycles} for experiment {self.experiment_id}")
        print(f"\n{'='*50}")
        print(f"Cycle {cycle}/{self.max_cycles}")
        print(f"{'='*50}")

        print("\n[1/3] Evaluating...")
        logger.debug(f"Running evaluation for cycle {cycle}")
        eval_start = time.time()
        metrics = self.evaluate(cycle)
        eval_duration = time.time() - eval_start
        logger.info(f"Evaluation completed in {eval_duration:.2f}s with {len(metrics)} metrics")

        result = ExperimentResult(
            experiment_id=self.experiment_id,
            cycle=cycle,
            metrics=metrics,
        )
        self.results.append(result)

        logger.info(f"Cycle {cycle} aggregate score: {result.aggregate_score:.3f}")
        logger.debug(f"Cycle {cycle} metrics: {json.dumps(metrics, indent=2)}")
        print(f"  Aggregate Score: {result.aggregate_score:.3f}")
        for name, value in metrics.items():
            print(f"  {name}: {value:.3f}")

        if cycle < self.max_cycles:
            print("\n[2/3] Optimizing...")
            logger.debug(f"Running optimization for cycle {cycle}")
            opt_start = time.time()
            self.optimize(result)
            opt_duration = time.time() - opt_start
            logger.info(f"Optimization completed in {opt_duration:.2f}s")

        print("\n[3/3] Saving results...")
        logger.debug(f"Saving results for cycle {cycle}")
        self.save_results()
        logger.info(f"Cycle {cycle} completed successfully")

        return result

    def run(self) -> ExperimentSummary:
        """Execute the full experiment loop."""
        logger.info(f"Starting experiment run: {self.experiment_id} with {self.max_cycles} cycles")
        print(f"\n# Experiment: {self.experiment_id}")
        print(f"# Cycles: {self.max_cycles}\n")

        start_time = time.time()

        try:
            for cycle in range(1, self.max_cycles + 1):
                self.run_cycle(cycle)
        except Exception as e:
            logger.error(f"Experiment failed at cycle {cycle}: {str(e)}", exc_info=True)
            raise

        elapsed = time.time() - start_time
        summary = self.generate_summary(elapsed)

        logger.info(f"Experiment {self.experiment_id} completed successfully")
        logger.info(f"Summary: initial={summary.initial_score:.3f}, final={summary.final_score:.3f}, "
                   f"improvement={summary.improvement:+.3f} ({summary.improvement_percentage:.1f}%), "
                   f"best={summary.best_score:.3f}, elapsed={elapsed:.1f}s")

        print(f"\n{'='*50}")
        print("Experiment Complete!")
        print(f"  Initial Score: {summary.initial_score:.3f}")
        print(f"  Final Score:   {summary.final_score:.3f}")
        print(f"  Improvement:   {summary.improvement:+.3f} ({summary.improvement_percentage:.1f}%)")
        print(f"  Best Score:    {summary.best_score:.3f}")
        print(f"  Elapsed:       {elapsed:.1f}s")

        return summary

    def generate_summary(self, elapsed: float) -> ExperimentSummary:
        """Generate summary statistics from collected results."""
        logger.debug(f"Generating summary for {len(self.results)} results")
        scores = [r.aggregate_score for r in self.results]
        summary = ExperimentSummary(
            total_cycles=len(self.results),
            initial_score=scores[0] if scores else 0.0,
            final_score=scores[-1] if scores else 0.0,
            best_score=max(scores) if scores else 0.0,
            average_score=round(sum(scores) / len(scores), 4) if scores else 0.0,
            elapsed_seconds=round(elapsed, 1),
        )
        logger.debug(f"Summary generated: {summary.to_dict()}")
        return summary

    def save_results(self) -> Path:
        """Save current results to disk. Returns the path to the results file."""
        logger.debug(f"Saving {len(self.results)} results to disk")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"results_{timestamp}.json"

        output = {
            "experiment_id": self.experiment_id,
            "config": self.config,
            "cycles_completed": len(self.results),
            "results": [r.to_dict() for r in self.results],
        }

        try:
            with open(results_file, "w") as f:
                json.dump(output, f, indent=2)
            logger.info(f"Results saved to: {results_file}")

            latest_file = self.results_dir / "results_latest.json"
            with open(latest_file, "w") as f:
                json.dump(output, f, indent=2)
            logger.debug(f"Latest results saved to: {latest_file}")
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}", exc_info=True)
            raise

        return results_file
