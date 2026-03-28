#!/usr/bin/env python3
"""
Experiment 03: Data Cleaning Pipeline Optimization Runner

Orchestrates iterative optimization of data cleaning strategies.
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path


def load_config():
    """Load experiment configuration."""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path) as f:
        return json.load(f)


def generate_sample_data(size=1000):
    """Generate synthetic dirty data for cleaning."""
    data = []
    for i in range(size):
        record = {
            "id": i,
            "name": f"Record_{i}" if random.random() > 0.1 else None,
            "value": random.randint(0, 100) if random.random() > 0.08 else None,
            "category": random.choice(["A", "B", "C", "a", "b", "Invalid"]),
            "timestamp": f"2026-03-{random.randint(1,28):02d}" if random.random() > 0.12 else "invalid",
        }
        data.append(record)

    # Add duplicates
    for i in range(int(size * 0.05)):
        data.append(data[random.randint(0, len(data) - 1)].copy())

    return data


def clean_data_baseline(data):
    """Baseline cleaning strategy."""
    cleaned = []
    seen_ids = set()

    for record in data:
        # Remove nulls
        if record.get("name") is None or record.get("value") is None:
            continue

        # Basic deduplication
        if record["id"] in seen_ids:
            continue
        seen_ids.add(record["id"])

        # Standardize category
        if record["category"] in ["a", "A"]:
            record["category"] = "A"
        elif record["category"] in ["b", "B"]:
            record["category"] = "B"
        elif record["category"] not in ["A", "B", "C"]:
            record["category"] = "C"

        cleaned.append(record)

    return cleaned


def clean_data_optimized(data):
    """Optimized cleaning strategy (cycle 2)."""
    cleaned = []
    seen_ids = set()

    for record in data:
        # Impute nulls instead of removing
        if record.get("name") is None:
            record["name"] = f"Unknown_{record['id']}"
        if record.get("value") is None:
            record["value"] = 0

        # Enhanced deduplication
        if record["id"] in seen_ids:
            continue
        seen_ids.add(record["id"])

        # Standardize category (case-insensitive)
        cat = record["category"].upper()
        if cat in ["A", "B", "C"]:
            record["category"] = cat
        else:
            record["category"] = "INVALID"

        # Validate timestamp format
        if not record.get("timestamp", "").startswith("2026-03-"):
            record["timestamp"] = "2026-03-01"

        cleaned.append(record)

    return cleaned


def calculate_metrics(original_data, cleaned_data):
    """Calculate data quality metrics."""
    total_original = len(original_data)
    total_cleaned = len(cleaned_data)

    # Completeness: percentage retained
    completeness = total_cleaned / total_original if total_original > 0 else 0

    # Consistency: valid categories
    valid_categories = sum(1 for r in cleaned_data if r["category"] in ["A", "B", "C"])
    consistency = valid_categories / total_cleaned if total_cleaned > 0 else 0

    # Accuracy: valid values (simulate)
    valid_values = sum(1 for r in cleaned_data if 0 <= r.get("value", -1) <= 100)
    accuracy = valid_values / total_cleaned if total_cleaned > 0 else 0

    # Deduplication rate
    unique_ids = len(set(r["id"] for r in cleaned_data))
    deduplication_rate = unique_ids / total_cleaned if total_cleaned > 0 else 0

    return {
        "completeness": round(completeness, 4),
        "consistency": round(consistency, 4),
        "accuracy": round(accuracy, 4),
        "deduplication_rate": round(deduplication_rate, 4),
    }


def run_cycle(cycle_num, config, data):
    """Run a single optimization cycle."""
    print(f"\n{'='*50}")
    print(f"Cycle {cycle_num}")
    print(f"{'='*50}")

    # Select cleaning strategy
    if cycle_num == 1:
        strategy = "baseline"
        cleaned_data = clean_data_baseline(data)
    else:
        strategy = "optimized"
        cleaned_data = clean_data_optimized(data)

    # Calculate metrics
    metrics = calculate_metrics(data, cleaned_data)

    # Compute aggregate score (weighted average)
    aggregate_score = round(
        (metrics["completeness"] * 0.3 +
         metrics["consistency"] * 0.25 +
         metrics["accuracy"] * 0.25 +
         metrics["deduplication_rate"] * 0.2), 4
    )

    # Print results
    print(f"Strategy: {strategy}")
    print(f"Records: {len(data)} → {len(cleaned_data)}")
    print(f"Aggregate Score: {aggregate_score}")
    print(f"  Completeness: {metrics['completeness']}")
    print(f"  Consistency: {metrics['consistency']}")
    print(f"  Accuracy: {metrics['accuracy']}")
    print(f"  Deduplication: {metrics['deduplication_rate']}")

    return {
        "cycle": cycle_num,
        "strategy": strategy,
        "metrics": metrics,
        "aggregate_score": aggregate_score,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "records_processed": len(data),
        "records_cleaned": len(cleaned_data),
    }


def save_results(results, config):
    """Save experiment results to files."""
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    # Save timestamped results
    timestamped_file = results_dir / f"results_{timestamp}.json"
    with open(timestamped_file, "w") as f:
        json.dump(results, f, indent=2)

    # Save latest results
    latest_file = results_dir / "results_latest.json"
    with open(latest_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*50}")
    print("Results saved:")
    print(f"  - {timestamped_file}")
    print(f"  - {latest_file}")


def main():
    """Main experiment runner."""
    print("="*50)
    print("Experiment 03: Data Cleaning Pipeline Optimization")
    print("="*50)

    # Load configuration
    config = load_config()
    cycles = config["cycles"]

    print(f"\nConfiguration:")
    print(f"  Experiment ID: {config['experiment_id']}")
    print(f"  Cycles: {cycles}")
    print(f"  Optimization Target: {config['optimization_target']}")

    # Generate sample data
    print(f"\nGenerating sample data...")
    data = generate_sample_data(size=1000)
    print(f"  Generated {len(data)} records (including duplicates and errors)")

    # Run cycles
    cycle_results = []
    for cycle_num in range(1, cycles + 1):
        result = run_cycle(cycle_num, config, data)
        cycle_results.append(result)
        time.sleep(0.5)  # Brief pause between cycles

    # Compute summary
    initial_score = cycle_results[0]["aggregate_score"]
    final_score = cycle_results[-1]["aggregate_score"]
    improvement = round(final_score - initial_score, 4)
    improvement_pct = round((improvement / initial_score * 100) if initial_score > 0 else 0, 2)

    summary = {
        "initial_score": initial_score,
        "final_score": final_score,
        "improvement": improvement,
        "improvement_percentage": improvement_pct,
    }

    print(f"\n{'='*50}")
    print("Summary")
    print(f"{'='*50}")
    print(f"Initial Score: {initial_score}")
    print(f"Final Score: {final_score}")
    print(f"Improvement: {improvement} ({improvement_pct:+.2f}%)")

    # Save results
    results = {
        "experiment_id": config["experiment_id"],
        "session_id": "7d3a42be",
        "cycles_completed": cycles,
        "results": cycle_results,
        "summary": summary,
        "config": config,
    }

    save_results(results, config)

    print(f"\n{'='*50}")
    print("Experiment completed successfully!")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
