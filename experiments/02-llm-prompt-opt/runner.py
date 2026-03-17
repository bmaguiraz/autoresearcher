#!/usr/bin/env python3
"""
LLM Prompt Optimization Experiment Runner

This script runs an iterative prompt optimization experiment where each cycle:
1. Evaluates the current prompt
2. Analyzes performance metrics
3. Generates an improved version
4. Records results for comparison
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path


class PromptOptimizationExperiment:
    """Manages the prompt optimization experiment lifecycle."""

    def __init__(self, config_path: str):
        """Initialize experiment with configuration."""
        self.config_path = Path(config_path)
        self.experiment_dir = self.config_path.parent
        self.results_dir = self.experiment_dir / "results"
        self.results_dir.mkdir(exist_ok=True)

        # Load configuration
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)

        self.experiment_id = self.config['experiment_id']
        self.cycles = self.config['cycles']
        self.current_prompt = self.config['baseline_prompt']
        self.results = []

    def evaluate_prompt(self, cycle: int, prompt: str) -> dict:
        """
        Evaluate a prompt's effectiveness.

        In a real implementation, this would:
        - Run the prompt against a test dataset
        - Measure response quality metrics
        - Calculate optimization criteria scores

        For this demo, we simulate evaluation with synthetic metrics.
        """
        # Simulate evaluation with improving metrics over cycles
        base_score = 0.6
        improvement_factor = cycle * 0.05

        metrics = {
            "clarity": min(0.95, base_score + improvement_factor + 0.1),
            "specificity": min(0.98, base_score + improvement_factor + 0.15),
            "response_quality": min(0.92, base_score + improvement_factor),
            "task_completion": min(0.90, base_score + improvement_factor + 0.05)
        }

        # Calculate aggregate score
        aggregate_score = sum(metrics.values()) / len(metrics)

        return {
            "cycle": cycle,
            "prompt": prompt,
            "metrics": metrics,
            "aggregate_score": round(aggregate_score, 3),
            "timestamp": datetime.now().isoformat()
        }

    def optimize_prompt(self, current_prompt: str, previous_metrics: dict) -> str:
        """
        Generate an optimized version of the prompt based on previous metrics.

        In a real implementation, this would:
        - Analyze weak points in current prompt
        - Apply optimization strategies
        - Generate improved version using LLM

        For this demo, we simulate optimization with incremental improvements.
        """
        optimizations = [
            "You are an expert AI assistant with deep knowledge across multiple domains.",
            "You are a highly capable AI assistant specialized in providing clear, actionable guidance.",
            "You are a professional AI assistant focused on delivering precise, contextual responses tailored to user needs.",
            "You are an advanced AI assistant committed to understanding user intent and providing comprehensive, well-structured solutions.",
            "You are a world-class AI assistant that excels at breaking down complex problems and delivering exceptional, personalized assistance."
        ]

        # Select optimization based on cycle (simulated improvement)
        cycle = previous_metrics.get('cycle', 0)
        if cycle < len(optimizations):
            return optimizations[cycle]
        else:
            return current_prompt + " [Further optimized]"

    def run_cycle(self, cycle: int) -> dict:
        """Execute a single optimization cycle."""
        print(f"\n{'='*60}")
        print(f"Cycle {cycle}/{self.cycles}")
        print(f"{'='*60}")

        # Evaluate current prompt
        print(f"\n[1/3] Evaluating prompt...")
        evaluation = self.evaluate_prompt(cycle, self.current_prompt)

        print(f"  → Aggregate Score: {evaluation['aggregate_score']:.3f}")
        print(f"  → Clarity: {evaluation['metrics']['clarity']:.3f}")
        print(f"  → Specificity: {evaluation['metrics']['specificity']:.3f}")
        print(f"  → Response Quality: {evaluation['metrics']['response_quality']:.3f}")
        print(f"  → Task Completion: {evaluation['metrics']['task_completion']:.3f}")

        # Store results
        self.results.append(evaluation)

        # Generate optimized prompt for next cycle
        if cycle < self.cycles:
            print(f"\n[2/3] Optimizing prompt for next cycle...")
            self.current_prompt = self.optimize_prompt(self.current_prompt, evaluation)
            print(f"  → Generated improved prompt variant")

        # Save intermediate results
        print(f"\n[3/3] Saving results...")
        self.save_results()
        print(f"  → Results saved to {self.results_dir}")

        return evaluation

    def save_results(self):
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

        return {
            "total_cycles": len(self.results),
            "initial_score": scores[0],
            "final_score": scores[-1],
            "improvement": round(scores[-1] - scores[0], 3),
            "improvement_percentage": round((scores[-1] - scores[0]) / scores[0] * 100, 2),
            "best_score": max(scores),
            "average_score": round(sum(scores) / len(scores), 3)
        }

    def run(self):
        """Execute the complete experiment."""
        print(f"\n{'#'*60}")
        print(f"# LLM Prompt Optimization Experiment")
        print(f"# Experiment ID: {self.experiment_id}")
        print(f"# Cycles: {self.cycles}")
        print(f"{'#'*60}")

        start_time = time.time()

        # Run all cycles
        for cycle in range(1, self.cycles + 1):
            self.run_cycle(cycle)

            # Small delay between cycles (simulating real processing time)
            if cycle < self.cycles:
                time.sleep(0.5)

        elapsed_time = time.time() - start_time

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
        print(f"Latest results: {self.results_dir / 'results_latest.json'}")

        return summary


def main():
    """Main entry point for the experiment runner."""
    # Determine config path
    script_dir = Path(__file__).parent
    config_path = script_dir / "config.json"

    if not config_path.exists():
        print(f"Error: Configuration file not found at {config_path}")
        return 1

    # Create and run experiment
    experiment = PromptOptimizationExperiment(str(config_path))
    experiment.run()

    return 0


if __name__ == "__main__":
    exit(main())
