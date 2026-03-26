# -*- coding: utf-8 -*-
"""Base experiment classes for the autoresearcher framework."""

import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

__version__ = "0.2.0"
__all__ = ["RetryConfig", "ExperimentResult", "ExperimentSummary", "BaseExperiment"]

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Configuration for retry behavior with exponential backoff."""

    max_retries: int = 3
    base_delay: float = 1.0
    backoff_factor: float = 2.0
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,)

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for a given retry attempt (0-indexed)."""
        return self.base_delay * (self.backoff_factor ** attempt)


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
    status_test_id: str = "experiment-status"

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

    def __init__(self, config_path: str | Path, retry_config: RetryConfig | None = None):
        self.config_path = Path(config_path)
        self.experiment_dir = self.config_path.parent
        self.results_dir = self.experiment_dir / "results"
        self.results_dir.mkdir(exist_ok=True)

        logger.info("Initializing experiment from config: %s", self.config_path)

        with open(self.config_path) as f:
            self.config = json.load(f)

        self.experiment_id: str = self.config.get("experiment_id", "unknown")
        self.max_cycles: int = self.config.get("cycles", 5)
        self.retry_config: RetryConfig = retry_config or RetryConfig()
        self.results: list[ExperimentResult] = []

        logger.info("Experiment initialized: id=%s, max_cycles=%d", self.experiment_id, self.max_cycles)
        logger.debug("Experiment config: %s", json.dumps(self.config, indent=2))

    @abstractmethod
    def evaluate(self, cycle: int) -> dict[str, float]:
        """Run evaluation and return a dict of metric_name -> score."""
        ...

    @abstractmethod
    def optimize(self, result: ExperimentResult) -> None:
        """Apply optimization based on the latest result."""
        ...

    def _evaluate_with_retry(self, cycle: int) -> dict[str, float]:
        """Run evaluate() with retry logic on failure."""
        last_exception: Exception | None = None
        max_attempts = 1 + self.retry_config.max_retries

        for attempt in range(max_attempts):
            try:
                return self.evaluate(cycle)
            except self.retry_config.retryable_exceptions as exc:
                last_exception = exc
                if attempt < self.retry_config.max_retries:
                    delay = self.retry_config.get_delay(attempt)
                    logger.warning(
                        "Evaluation failed (attempt %d/%d): %s. Retrying in %.1fs...",
                        attempt + 1, max_attempts, exc, delay,
                    )
                    print(f"  Evaluation failed (attempt {attempt + 1}/{max_attempts}): {exc}")
                    print(f"  Retrying in {delay:.1f}s...")
                    time.sleep(delay)

        raise last_exception  # type: ignore[misc]

    def run_cycle(self, cycle: int) -> ExperimentResult:
        """Execute a single experiment cycle with retry support."""
        logger.info("Starting cycle %d/%d for experiment %s", cycle, self.max_cycles, self.experiment_id)
        sep = "=" * 50
        print(f"\n{sep}")
        print(f"Cycle {cycle}/{self.max_cycles}")
        print(sep)

        print("\n[1/3] Evaluating...")
        logger.debug("Running evaluation for cycle %d", cycle)
        eval_start = time.time()
        metrics = self._evaluate_with_retry(cycle)
        eval_duration = time.time() - eval_start
        logger.info("Evaluation completed in %.2fs with %d metrics", eval_duration, len(metrics))

        result = ExperimentResult(
            experiment_id=self.experiment_id,
            cycle=cycle,
            metrics=metrics,
        )
        self.results.append(result)

        logger.info("Cycle %d aggregate score: %.3f", cycle, result.aggregate_score)
        logger.debug("Cycle %d metrics: %s", cycle, json.dumps(metrics, indent=2))
        print(f"  Aggregate Score: {result.aggregate_score:.3f}")
        for name, value in metrics.items():
            print(f"  {name}: {value:.3f}")

        if cycle < self.max_cycles:
            print("\n[2/3] Optimizing...")
            logger.debug("Running optimization for cycle %d", cycle)
            opt_start = time.time()
            self.optimize(result)
            opt_duration = time.time() - opt_start
            logger.info("Optimization completed in %.2fs", opt_duration)

        print("\n[3/3] Saving results...")
        logger.debug("Saving results for cycle %d", cycle)
        self.save_results()
        logger.info("Cycle %d completed successfully", cycle)

        return result

    def run(self) -> ExperimentSummary:
        """Execute the full experiment loop."""
        logger.info("Starting experiment run: %s with %d cycles", self.experiment_id, self.max_cycles)
        print(f"\n# Experiment: {self.experiment_id}")
        print(f"# Cycles: {self.max_cycles}\n")

        start_time = time.time()

        try:
            for cycle in range(1, self.max_cycles + 1):
                self.run_cycle(cycle)
        except Exception:
            logger.error("Experiment failed during execution", exc_info=True)
            raise

        elapsed = time.time() - start_time
        summary = self.generate_summary(elapsed)

        logger.info(
            "Experiment %s completed: initial=%.3f, final=%.3f, "
            "improvement=%+.3f (%.1f%%), best=%.3f, elapsed=%.1fs",
            self.experiment_id, summary.initial_score, summary.final_score,
            summary.improvement, summary.improvement_percentage,
            summary.best_score, elapsed,
        )

        sep = "=" * 50
        print(f"\n{sep}")
        print("Experiment Complete!")
        print(f"  Initial Score: {summary.initial_score:.3f}")
        print(f"  Final Score:   {summary.final_score:.3f}")
        print(f"  Improvement:   {summary.improvement:+.3f} ({summary.improvement_percentage:.1f}%)")
        print(f"  Best Score:    {summary.best_score:.3f}")
        print(f"  Elapsed:       {elapsed:.1f}s")

        return summary

    def generate_summary(self, elapsed: float) -> ExperimentSummary:
        """Generate summary statistics from collected results."""
        logger.debug("Generating summary for %d results", len(self.results))
        scores = [r.aggregate_score for r in self.results]
        summary = ExperimentSummary(
            total_cycles=len(self.results),
            initial_score=scores[0] if scores else 0.0,
            final_score=scores[-1] if scores else 0.0,
            best_score=max(scores) if scores else 0.0,
            average_score=round(sum(scores) / len(scores), 4) if scores else 0.0,
            elapsed_seconds=round(elapsed, 1),
        )
        logger.debug("Summary generated: %s", summary.to_dict())
        return summary

    def save_results(self) -> Path:
        """Save current results to disk. Returns the path to the results file."""
        logger.debug("Saving %d results to disk", len(self.results))
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
            logger.info("Results saved to: %s", results_file)

            latest_file = self.results_dir / "results_latest.json"
            with open(latest_file, "w") as f:
                json.dump(output, f, indent=2)
            logger.debug("Latest results saved to: %s", latest_file)
        except Exception:
            logger.error("Failed to save results", exc_info=True)
            raise

        return results_file
