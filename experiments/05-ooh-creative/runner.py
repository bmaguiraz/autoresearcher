#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OOH Creative Optimization Experiment Runner

Tests 4-way parallelism by running multiple creative variants concurrently.
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from autoresearcher import (
    BaseExperiment,
    ExperimentResult,
    ConcurrentExperimentRunner,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent / 'experiment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class OOHCreativeExperiment(BaseExperiment):
    """OOH advertising creative optimization experiment."""

    def __init__(self, config_path: str | Path, variant: str):
        """Initialize experiment with specific creative variant."""
        super().__init__(config_path)
        self.variant = variant
        self.use_case = self.config.get("use_case", "plumber")
        self.experiment_id = f"{self.experiment_id}-{variant}"

        # Define creative strategies
        self.creatives = self._generate_creatives()
        logger.info(f"Initialized {variant} variant for {self.use_case}")

    def _generate_creatives(self) -> dict:
        """Generate OOH creative copy based on use case and variant."""
        use_case = self.use_case

        if use_case == "plumber":
            creatives = {
                "baseline": {
                    "headline": "Licensed Plumber • 24/7 Service",
                    "body": "Emergency repairs, leak detection, drain cleaning. Fast response times. Call (555) 123-4567",
                },
                "emotional": {
                    "headline": "Plumbing Emergency? We're Here.",
                    "body": "Don't let a burst pipe ruin your home. 24/7 emergency service. Licensed & insured. (555) 123-4567",
                },
                "urgency": {
                    "headline": "24/7 Emergency Plumbing Response",
                    "body": "Burst pipe? Clogged drain? We arrive fast. Same-day service available. Call now: (555) 123-4567",
                },
                "social_proof": {
                    "headline": "★★★★★ Rated Plumbing Service",
                    "body": "500+ 5-star reviews. Licensed, insured, trusted by neighbors. Emergency & scheduled service. (555) 123-4567",
                },
            }
        elif use_case == "restaurant":
            creatives = {
                "baseline": {
                    "headline": "Casa Bella Trattoria • Authentic Italian",
                    "body": "Handmade pasta daily. Farm-to-table ingredients. Tue-Sun 11am-10pm. 247 Main St. (555) BELLA-01",
                },
                "emotional": {
                    "headline": "Taste Italy, Right Here at Home",
                    "body": "Family recipes since 1987. Fresh ingredients, handmade with love. Experience authentic Italian dining. (555) BELLA-01",
                },
                "urgency": {
                    "headline": "Fresh Pasta Made Daily—Reserve Now",
                    "body": "Limited seating! Handmade pappardelle & farm-fresh ingredients. Book your table today. (555) BELLA-01",
                },
                "social_proof": {
                    "headline": "★★★★★ Casa Bella Trattoria",
                    "body": "Voted Best Italian 3 years running. Family recipes since 1987. Downtown at 247 Main St. (555) BELLA-01",
                },
            }
        elif use_case == "writefit":
            creatives = {
                "baseline": {
                    "headline": "WriteFit.ai • Practice Writing Skills",
                    "body": "AI-powered writing practice that helps students improve. Never writes for them. Research-backed methods. Visit writefit.ai",
                },
                "emotional": {
                    "headline": "Stop AI From Writing Student Essays",
                    "body": "WriteFit helps students practice real writing skills—without doing the work for them. Teachers trust us. writefit.ai",
                },
                "urgency": {
                    "headline": "Transform Your Writing Class Today",
                    "body": "AI-powered practice exercises target each student's weaknesses. Start improving writing skills now. Visit writefit.ai",
                },
                "social_proof": {
                    "headline": "Trusted by High School Teachers",
                    "body": "Research-backed writing practice that diagnoses weaknesses and builds skills. Students practice, we guide. writefit.ai",
                },
            }
        else:
            # Generic fallback
            creatives = {
                "baseline": {
                    "headline": f"Professional {use_case.title()} Service",
                    "body": "Quality service you can trust. Licensed and insured. Call today for a free estimate.",
                },
                "emotional": {
                    "headline": f"Need {use_case.title()} Help?",
                    "body": "We understand your needs. Fast, reliable service with a personal touch. Contact us today.",
                },
                "urgency": {
                    "headline": f"Same-Day {use_case.title()} Service",
                    "body": "Don't wait! Limited availability. Book your appointment today. Call now for priority service.",
                },
                "social_proof": {
                    "headline": f"Top-Rated {use_case.title()} Experts",
                    "body": "Hundreds of satisfied customers. See why we're the trusted choice in your area. Call today!",
                },
            }

        return creatives

    def evaluate(self, cycle: int) -> dict[str, float]:
        """Evaluate the creative variant on key OOH metrics."""
        creative = self.creatives.get(self.variant, self.creatives["baseline"])

        # Simulate evaluation (in production, this would use real metrics)
        headline = creative["headline"]
        body = creative["body"]

        # Score based on variant characteristics
        scores = self._score_creative(headline, body, self.variant)

        logger.info(
            f"Variant '{self.variant}' evaluated - Attention: {scores['attention']:.1f}, "
            f"Clarity: {scores['clarity']:.1f}, Relevance: {scores['relevance']:.1f}, "
            f"Conversion: {scores['conversion_potential']:.1f}"
        )

        return scores

    def _score_creative(self, headline: str, body: str, variant: str) -> dict[str, float]:
        """Score creative on OOH metrics (0-25 each)."""
        import random
        random.seed(hash(variant))  # Deterministic but varied by variant

        # Base scores with variant-specific adjustments
        base_scores = {
            "baseline": {"attention": 15, "clarity": 22, "relevance": 18, "conversion_potential": 17},
            "emotional": {"attention": 20, "clarity": 19, "relevance": 22, "conversion_potential": 21},
            "urgency": {"attention": 22, "clarity": 20, "relevance": 19, "conversion_potential": 23},
            "social_proof": {"attention": 18, "clarity": 21, "relevance": 21, "conversion_potential": 22},
        }

        scores = base_scores.get(variant, base_scores["baseline"]).copy()

        # Add small random variation
        for key in scores:
            scores[key] += random.uniform(-2, 2)
            scores[key] = max(0, min(25, scores[key]))  # Clamp to 0-25

        return scores

    def optimize(self, result: ExperimentResult) -> None:
        """
        Generate optimized creative based on results.

        For this single-cycle experiment, optimization is not performed.
        In multi-cycle runs, this would adjust creative based on metrics.
        """
        if self.max_cycles > 1:
            logger.info(f"Would optimize {self.variant} variant based on results")
            # Future: implement optimization logic
        pass


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="OOH Creative Optimization Experiment"
    )
    parser.add_argument(
        "--use-case",
        type=str,
        default="plumber",
        help="Use case for OOH creative (e.g., plumber, hvac, pest-control)"
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="Number of optimization cycles to run"
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Run variants sequentially instead of in parallel"
    )
    return parser.parse_args()


def main():
    """Main entry point for experiment runner."""
    args = parse_args()

    logger.info(f"Starting OOH creative experiment: use_case={args.use_case}, cycles={args.cycles}")

    # Get config path
    script_dir = Path(__file__).parent
    config_path = script_dir / "config.json"

    if not config_path.exists():
        logger.error(f"Config not found: {config_path}")
        print(f"Error: Configuration file not found at {config_path}")
        return 1

    # Update config with CLI args
    with open(config_path, 'r') as f:
        config = json.load(f)

    config["use_case"] = args.use_case
    config["cycles"] = args.cycles

    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\n{'='*70}")
    print(f"OOH Creative Optimization Experiment")
    print(f"Use Case: {args.use_case.title()}")
    print(f"Cycles: {args.cycles}")
    print(f"Parallel Variants: 4 (baseline, emotional, urgency, social_proof)")
    print(f"{'='*70}\n")

    # Create experiment instances for each variant
    variants = ["baseline", "emotional", "urgency", "social_proof"]
    experiments = [
        OOHCreativeExperiment(config_path, variant) for variant in variants
    ]

    start_time = time.time()

    if args.sequential:
        logger.info("Running variants sequentially")
        print("Running variants sequentially...\n")
        results = []
        for exp in experiments:
            summary = exp.run()
            results.append({
                "variant": exp.variant,
                "summary": summary,
                "success": True
            })
    else:
        logger.info("Running variants concurrently (4-way parallelism)")
        print("Running 4 variants concurrently...\n")

        # Use concurrent runner for parallel execution
        runner = ConcurrentExperimentRunner(max_workers=4)
        concurrent_results = runner.run_experiments(experiments)

        results = [
            {
                "variant": r.experiment_id.split("-")[-1],
                "summary": r.summary,
                "success": r.success,
                "error": r.error
            }
            for r in concurrent_results
        ]

    elapsed = time.time() - start_time

    # Display comparative results
    print(f"\n{'='*70}")
    print(f"EXPERIMENT RESULTS - Comparative Analysis")
    print(f"{'='*70}\n")

    successful_results = [r for r in results if r["success"]]

    if successful_results:
        print(f"{'Variant':<15} {'Score':<10} {'Attention':<12} {'Clarity':<10} {'Relevance':<12} {'Conversion':<12}")
        print("-" * 70)

        for result in successful_results:
            variant = result["variant"]
            summary = result["summary"]
            # Get first result metrics
            exp = next(e for e in experiments if e.variant == variant)
            if exp.results:
                metrics = exp.results[0].metrics
                print(
                    f"{variant:<15} {summary.final_score:<10.1f} "
                    f"{metrics['attention']:<12.1f} {metrics['clarity']:<10.1f} "
                    f"{metrics['relevance']:<12.1f} {metrics['conversion_potential']:<12.1f}"
                )

        print()

        # Find best variant
        best = max(successful_results, key=lambda r: r["summary"].final_score)
        print(f"✓ Best Performing Variant: {best['variant'].upper()}")
        print(f"  Score: {best['summary'].final_score:.1f}/100")
        print()

    print(f"Total Execution Time: {elapsed:.1f}s")
    print(f"Successful Variants: {len(successful_results)}/{len(results)}")

    if len(successful_results) < len(results):
        print("\nFailed variants:")
        for r in results:
            if not r["success"]:
                print(f"  - {r['variant']}: {r['error']}")

    # Save comparative results
    results_file = script_dir / "results" / f"comparative_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output = {
        "experiment_id": "05-ooh-creative",
        "use_case": args.use_case,
        "cycles": args.cycles,
        "parallel_execution": not args.sequential,
        "elapsed_seconds": round(elapsed, 2),
        "results": [
            {
                "variant": r["variant"],
                "final_score": r["summary"].final_score if r["success"] else None,
                "success": r["success"],
                "error": r.get("error")
            }
            for r in results
        ],
        "best_variant": best["variant"] if successful_results else None,
        "best_score": best["summary"].final_score if successful_results else None,
    }

    with open(results_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nComparative results saved to: {results_file}")
    logger.info(f"Experiment completed successfully in {elapsed:.1f}s")

    return 0


if __name__ == "__main__":
    sys.exit(main())
