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
            logger.debug("No experiments to run")
            return []

        logger.info(f"Starting concurrent run of {len(experiments)} experiments "
                    f"with max_workers={self.max_workers or 'default'}")
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
            logger.debug(f"Submitted {len(future_to_exp)} experiments to executor")

            # Collect results as they complete
            for future in as_completed(future_to_exp):
                exp = future_to_exp[future]
                result = future.result()
                results.append(result)

                if result.success:
                    logger.info(f"Experiment {result.experiment_id} completed successfully")
                else:
                    logger.error(f"Experiment {result.experiment_id} failed: {result.error}")
                status = "✓" if result.success else "✗"
                print(f"{status} {result.experiment_id} completed")

        elapsed = time.time() - start_time

        successful = sum(1 for r in results if r.success)
        logger.info(f"All {len(results)} experiments complete in {elapsed:.1f}s "
                    f"({successful} successful, {len(results) - successful} failed)")

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
        logger.debug(f"Starting experiment: {experiment.experiment_id}")
        try:
            summary = experiment.run()
            logger.info(f"Experiment {experiment.experiment_id} finished: "
                       f"score={summary.final_score:.3f}")
            return ConcurrentExperimentResult(
                experiment_id=experiment.experiment_id,
                summary=summary,
                success=True,
            )
        except Exception as e:
            logger.error(f"Experiment {experiment.experiment_id} raised an exception: {e}",
                        exc_info=True)
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
        """
        if not items:
            logger.debug("No items to evaluate")
            return []

        logger.info(f"Evaluating batch of {len(items)} items with "
                    f"max_workers={self.max_workers or 'default'}")
        results = [None] * len(items)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all evaluations with their index
            future_to_idx = {
                executor.submit(eval_fn, item): idx for idx, item in enumerate(items)
            }

            # Collect results in order
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                results[idx] = future.result()

        logger.info(f"Batch evaluation complete: {len(results)} results")
        return results  # type: ignore
