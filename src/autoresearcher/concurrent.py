# -*- coding: utf-8 -*-
"""Concurrent execution utilities for running experiments in parallel."""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Callable, Any

from .experiment import BaseExperiment, ExperimentSummary

logger = logging.getLogger(__name__)


@dataclass
class ConcurrentExperimentResult:
    """Result from running an experiment concurrently."""

    experiment_id: str
    summary: ExperimentSummary
    success: bool
    error: str | None = None


class BatchEvaluationError(Exception):
    """Raised when one or more items in a batch evaluation fail.

    Attributes:
        results: List with successful results and None for failed items.
        errors: Dict mapping item index to the exception that occurred.
    """

    def __init__(
        self,
        message: str,
        results: list[dict[str, float] | None],
        errors: dict[int, Exception],
    ):
        super().__init__(message)
        self.results = results
        self.errors = errors


class ConcurrentExperimentRunner:
    """Runner for executing multiple experiments concurrently.

    This allows parallel execution of independent experiments, significantly
    reducing total execution time when running multiple experiments.
    """

    def __init__(self, max_workers: int | None = None):
        """Initialize the concurrent runner.

        Args:
            max_workers: Maximum number of concurrent workers.
                        Defaults to None (uses ThreadPoolExecutor default).
        """
        self.max_workers = max_workers

    def run_experiments(
        self, experiments: list[BaseExperiment]
    ) -> list[ConcurrentExperimentResult]:
        """Run multiple experiments concurrently.

        Args:
            experiments: List of experiment instances to run.

        Returns:
            List of ConcurrentExperimentResult objects with results and status.
        """
        if not experiments:
            logger.debug("No experiments to run, returning empty results")
            return []

        logger.info(
            "Starting concurrent run: %d experiments, max_workers=%s",
            len(experiments), self.max_workers or "default",
        )

        print(f"\n{'='*60}")
        print(f"Running {len(experiments)} experiments concurrently")
        print(f"Max workers: {self.max_workers or 'default'}")
        print(f"{'='*60}\n")

        start_time = time.time()
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all experiments
            future_to_exp = {
                executor.submit(self._run_single_experiment, exp): exp
                for exp in experiments
            }
            logger.debug("Submitted %d experiments to thread pool", len(future_to_exp))

            # Collect results as they complete
            for future in as_completed(future_to_exp):
                exp = future_to_exp[future]
                result = future.result()
                results.append(result)

                if result.success:
                    logger.info("Experiment %s completed successfully", result.experiment_id)
                else:
                    logger.warning("Experiment %s failed: %s", result.experiment_id, result.error)

                status = "+" if result.success else "x"
                print(f"{status} {result.experiment_id} completed")

        elapsed = time.time() - start_time
        successful = sum(1 for r in results if r.success)

        logger.info(
            "Concurrent run finished: %d/%d successful in %.1fs",
            successful, len(results), elapsed,
        )

        print(f"\n{'='*60}")
        print(f"All experiments complete in {elapsed:.1f}s")
        print(f"Successful: {successful}/{len(results)}")
        print(f"{'='*60}\n")

        return results

    def _run_single_experiment(
        self, experiment: BaseExperiment
    ) -> ConcurrentExperimentResult:
        """Run a single experiment and capture its result.

        Args:
            experiment: The experiment to run.

        Returns:
            ConcurrentExperimentResult with success status and summary/error.
        """
        logger.debug("Running experiment: %s", experiment.experiment_id)
        try:
            summary = experiment.run()
            logger.debug(
                "Experiment %s finished: score=%.3f, cycles=%d",
                experiment.experiment_id, summary.final_score, summary.total_cycles,
            )
            return ConcurrentExperimentResult(
                experiment_id=experiment.experiment_id,
                summary=summary,
                success=True,
            )
        except Exception as e:
            logger.error("Experiment %s raised an exception: %s", experiment.experiment_id, e)
            return ConcurrentExperimentResult(
                experiment_id=experiment.experiment_id,
                summary=None,  # type: ignore
                success=False,
                error=str(e),
            )


class ConcurrentEvaluator:
    """Utility for running multiple evaluations concurrently.

    Useful for batch evaluation scenarios where multiple independent
    evaluations can be executed in parallel.
    """

    def __init__(self, max_workers: int | None = None):
        """Initialize the concurrent evaluator.

        Args:
            max_workers: Maximum number of concurrent workers.
        """
        self.max_workers = max_workers

    def evaluate_batch(
        self,
        eval_fn: Callable[[Any], dict[str, float]],
        items: list[Any],
    ) -> list[dict[str, float]]:
        """Evaluate a batch of items concurrently.

        Args:
            eval_fn: Function that takes an item and returns metrics dict.
            items: List of items to evaluate.

        Returns:
            List of metric dicts in the same order as input items.

        Raises:
            BatchEvaluationError: If any evaluation fails. The exception
                carries partial results and per-item errors so callers
                can recover successful results.
        """
        if not items:
            logger.debug("No items to evaluate, returning empty results")
            return []

        logger.info(
            "Starting batch evaluation: %d items, max_workers=%s",
            len(items), self.max_workers or "default",
        )
        results: list[dict[str, float] | None] = [None] * len(items)
        errors: dict[int, Exception] = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all evaluations with their index
            future_to_idx = {
                executor.submit(eval_fn, item): idx for idx, item in enumerate(items)
            }

            # Collect results in order
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    results[idx] = future.result()
                except Exception as exc:
                    logger.error("Batch item %d failed: %s", idx, exc)
                    errors[idx] = exc

        if errors:
            successful = len(items) - len(errors)
            logger.warning(
                "Batch evaluation partial failure: %d/%d succeeded",
                successful, len(items),
            )
            raise BatchEvaluationError(
                f"{len(errors)}/{len(items)} evaluations failed",
                results=results,
                errors=errors,
            )

        logger.info("Batch evaluation complete: %d items processed", len(items))
        return results  # type: ignore
