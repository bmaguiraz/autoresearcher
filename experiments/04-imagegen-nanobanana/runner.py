#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Generation Prompt Optimization Experiment Runner (Nano)

A minimal experiment to test per-issue parallelism.
Each cycle:
1. Evaluates the current image generation prompt
2. Analyzes simulated quality metrics
3. Generates an improved version
"""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('experiment_runner.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class ImageGenPromptExperiment:
    """Manages the image generation prompt optimization experiment."""

    def __init__(self, config_path: str):
        """Initialize experiment with configuration."""
        logger.info(f"Initializing experiment with config: {config_path}")
        self.config_path = Path(config_path)
        self.experiment_dir = self.config_path.parent
        self.results_dir = self.experiment_dir / "results"
        self.results_dir.mkdir(exist_ok=True)

        # Load configuration
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
        logger.info("Configuration loaded successfully")

        self.experiment_id = self.config['experiment_id']
        self.cycles = self.config['cycles']
        self.current_prompt = self.config['baseline_prompt']
        self.results = []
        logger.info(f"Experiment initialized: ID={self.experiment_id}, Cycles={self.cycles}")

    def evaluate_prompt(self, cycle: int, prompt: str) -> dict:
        """
        Evaluate an image generation prompt's effectiveness.

        Simulates evaluation with synthetic metrics that improve over cycles.
        """
        logger.debug(f"Evaluating prompt for cycle {cycle}")

        # Simulate evaluation with improving metrics
        base_score = 0.65
        improvement_factor = cycle * 0.08

        metrics = {
            "visual_quality": min(0.95, base_score + improvement_factor + 0.05),
            "prompt_clarity": min(0.92, base_score + improvement_factor + 0.10),
            "style_consistency": min(0.90, base_score + improvement_factor),
            "composition": min(0.93, base_score + improvement_factor + 0.08)
        }

        # Calculate aggregate score
        aggregate_score = sum(metrics.values()) / len(metrics)
        logger.info(f"Cycle {cycle} evaluation complete: aggregate_score={aggregate_score:.3f}")

        return {
            "cycle": cycle,
            "prompt": prompt,
            "metrics": metrics,
            "aggregate_score": round(aggregate_score, 3),
            "timestamp": datetime.now().isoformat()
        }

    def optimize_prompt(self, current_prompt: str, previous_metrics: dict) -> str:
        """
        Generate an optimized version of the image generation prompt.

        Simulates prompt optimization with incremental improvements.
        """
        logger.debug("Generating optimized prompt")

        optimizations = [
            "A high-quality professional photograph of a banana",
            "A stunning 8K photograph of a perfect yellow banana with beautiful lighting and composition",
            "An award-winning professional photograph of a perfectly ripe banana, studio lighting, shallow depth of field, highly detailed"
        ]

        cycle = previous_metrics.get('cycle', 0)
        if cycle < len(optimizations):
            optimized = optimizations[cycle]
            logger.debug(f"Selected optimization variant {cycle}")
            return optimized
        else:
            optimized = current_prompt + ", ultra realistic, professional photography"
            logger.debug("Applied further optimization")
            return optimized

    def run_cycle(self, cycle: int) -> dict:
        """Execute a single optimization cycle."""
        logger.info(f"Starting cycle {cycle}/{self.cycles}")
        print(f"\n{'='*60}")
        print(f"Cycle {cycle}/{self.cycles}")
        print(f"{'='*60}")

        # Evaluate current prompt
        print(f"\n[1/3] Evaluating prompt...")
        evaluation = self.evaluate_prompt(cycle, self.current_prompt)

        print(f"  → Aggregate Score: {evaluation['aggregate_score']:.3f}")
        print(f"  → Visual Quality: {evaluation['metrics']['visual_quality']:.3f}")
        print(f"  → Prompt Clarity: {evaluation['metrics']['prompt_clarity']:.3f}")
        print(f"  → Style Consistency: {evaluation['metrics']['style_consistency']:.3f}")
        print(f"  → Composition: {evaluation['metrics']['composition']:.3f}")
        print(f"  → Current Prompt: \"{self.current_prompt}\"")

        # Store results
        self.results.append(evaluation)

        # Generate optimized prompt for next cycle
        if cycle < self.cycles:
            print(f"\n[2/3] Optimizing prompt for next cycle...")
            self.current_prompt = self.optimize_prompt(self.current_prompt, evaluation)
            print(f"  → Generated improved prompt")
            logger.info(f"Generated new prompt variant for next cycle")

        # Save intermediate results
        print(f"\n[3/3] Saving results...")
        self.export_results()
        print(f"  → Results saved to {self.results_dir}")
        logger.info(f"Results saved successfully")

        logger.info(f"Cycle {cycle} completed successfully")
        return evaluation

    def export_results(self):
        """Save experiment results to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"results_{timestamp}.json"

        output = {
            "experiment_id": self.experiment_id,
            "config": self.config,
            "cycles_completed": len(self.results),
            "results": self.results,
            "summary": self.generate_summary()
        }

        with open(results_file, 'w') as f:
            json.dump(output, f, indent=2)

        # Also save latest results
        latest_file = self.results_dir / "results_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(output, f, indent=2)

    def generate_summary(self) -> dict:
        """Generate summary statistics from results."""
        if not self.results:
            return {}

        scores = [r['aggregate_score'] for r in self.results]

        summary = {
            "total_cycles": len(self.results),
            "initial_score": scores[0],
            "final_score": scores[-1],
            "improvement": round(scores[-1] - scores[0], 3),
            "improvement_percentage": round((scores[-1] - scores[0]) / scores[0] * 100, 2),
            "best_score": max(scores),
            "average_score": round(sum(scores) / len(scores), 3)
        }
        return summary

    def run(self):
        """Execute the complete experiment."""
        logger.info(f"Starting experiment run: {self.experiment_id}")
        print(f"\n{'#'*60}")
        print(f"# Image Generation Prompt Optimization (Nano)")
        print(f"# Experiment ID: {self.experiment_id}")
        print(f"# Cycles: {self.cycles}")
        print(f"{'#'*60}")

        start_time = time.time()

        # Run all cycles
        for cycle in range(1, self.cycles + 1):
            self.run_cycle(cycle)
            if cycle < self.cycles:
                time.sleep(0.3)  # Small delay between cycles

        elapsed_time = time.time() - start_time
        logger.info(f"Experiment completed in {elapsed_time:.1f}s")

        # Print final summary
        print(f"\n{'='*60}")
        print(f"Experiment Complete!")
        print(f"{'='*60}")

        summary = self.generate_summary()
        print(f"\nSummary Statistics:")
        print(f"  • Total Cycles: {summary['total_cycles']}")
        print(f"  • Initial Score: {summary['initial_score']:.3f}")
        print(f"  • Final Score: {summary['final_score']:.3f}")
        print(f"  • Improvement: +{summary['improvement']:.3f} ({summary['improvement_percentage']:.1f}%)")
        print(f"  • Best Score: {summary['best_score']:.3f}")
        print(f"  • Average Score: {summary['average_score']:.3f}")
        print(f"  • Elapsed Time: {elapsed_time:.1f}s")

        print(f"\nResults saved to: {self.results_dir}")

        logger.info(f"Experiment {self.experiment_id} finished successfully")
        return summary


def main():
    """Main entry point for the experiment runner."""
    import argparse

    parser = argparse.ArgumentParser(description='Run image generation prompt optimization experiment')
    parser.add_argument('--cycles', type=int, help='Number of optimization cycles to run (overrides config)')
    args = parser.parse_args()

    logger.info("Starting experiment runner")
    script_dir = Path(__file__).parent
    config_path = script_dir / "config.json"

    if not config_path.exists():
        print(f"Error: Configuration file not found at {config_path}")
        return 1

    try:
        experiment = ImageGenPromptExperiment(str(config_path))

        # Override cycles from command line if provided
        if args.cycles is not None:
            logger.info(f"Overriding cycles from config ({experiment.cycles}) with command line argument ({args.cycles})")
            experiment.cycles = args.cycles

        experiment.run()
        return 0
    except Exception as e:
        logger.error(f"Experiment runner failed: {e}", exc_info=True)
        print(f"\nError: Experiment failed - {e}")
        return 1


if __name__ == "__main__":
    exit(main())
