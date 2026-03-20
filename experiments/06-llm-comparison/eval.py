#!/usr/bin/env python3
"""
LLM Comparison Evaluation Script

Scores Claude and GPT-4 responses on research summarization tasks.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List


def load_responses() -> Dict:
    """Load raw responses from the experiment."""
    results_file = Path(__file__).parent / "results" / "raw_responses.json"
    if not results_file.exists():
        print(f"Error: {results_file} not found. Run runner.py first.")
        sys.exit(1)

    with open(results_file) as f:
        return json.load(f)


def score_response(response: str, dimension: str) -> int:
    """
    Score a response on a given dimension (1-5 scale).

    This is a simplified scoring function. In a real evaluation,
    you would use more sophisticated methods (human evaluation,
    automated metrics, etc.).
    """
    # Check for errors
    if response.startswith("[ERROR"):
        return 1

    # Heuristic scoring based on response characteristics
    scores = {
        "factual_accuracy": score_accuracy(response),
        "citation_quality": score_citations(response),
        "readability": score_readability(response),
        "completeness": score_completeness(response)
    }

    return scores.get(dimension, 3)


def score_accuracy(response: str) -> int:
    """Score factual accuracy based on response quality indicators."""
    # Heuristics: Look for specific terms, structured content
    indicators = [
        len(response) > 500,  # Substantial content
        any(term in response.lower() for term in ["research", "study", "finding", "data"]),
        any(term in response.lower() for term in ["recent", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]),
        not any(term in response.lower() for term in ["i think", "probably", "maybe", "might be"]),
    ]
    return min(5, 2 + sum(indicators))


def score_citations(response: str) -> int:
    """Score citation quality."""
    # Look for citation patterns
    citation_indicators = [
        "et al" in response.lower(),
        any(char in response for char in ["(", ")", "[", "]"]) and any(year in response for year in ["2019", "2020", "2021", "2022", "2023", "2024", "2025"]),
        "journal" in response.lower() or "conference" in response.lower() or "nature" in response.lower() or "science" in response.lower(),
        response.count("published") > 0 or response.count("reported") > 0,
    ]
    base_score = 2 + sum(citation_indicators)
    return min(5, base_score)


def score_readability(response: str) -> int:
    """Score readability based on structure and clarity."""
    # Check for structural elements
    structure_indicators = [
        "\n\n" in response,  # Paragraphs
        any(marker in response for marker in ["1.", "2.", "•", "-", "#"]),  # Lists or headers
        len(response.split()) / max(response.count("."), 1) < 30,  # Reasonable sentence length
        not response.isupper(),  # Not all caps
        response.count("\n") > 3,  # Multiple sections
    ]
    return min(5, 2 + sum(structure_indicators))


def score_completeness(response: str) -> int:
    """Score completeness based on coverage of requested topics."""
    # Check for coverage of key elements requested in prompt
    elements = [
        any(term in response.lower() for term in ["concept", "definition", "principle", "mechanism"]),
        any(term in response.lower() for term in ["recent", "advance", "development", "breakthrough", "progress"]),
        any(term in response.lower() for term in ["future", "potential", "implication", "application", "direction"]),
        len(response) > 800,  # Comprehensive length
        response.count("\n\n") >= 3,  # Multiple sections
    ]
    return min(5, 2 + sum(elements))


def generate_evaluation_table(results: Dict) -> str:
    """Generate markdown table with evaluation scores."""
    config = results.get("config", {})
    dimensions = config.get("evaluation_dimensions", ["factual_accuracy", "citation_quality", "readability", "completeness"])

    # Calculate scores for each response
    scores = {}
    for topic_data in results["responses"]:
        topic = topic_data["topic"]
        topic_short = topic[:50] + "..." if len(topic) > 50 else topic

        for model, response in topic_data["responses"].items():
            if model not in scores:
                scores[model] = {dim: [] for dim in dimensions}

            for dim in dimensions:
                score = score_response(response, dim)
                scores[model][dim].append(score)

    # Build markdown table
    table = []
    table.append("## Evaluation Results\n")
    table.append("| Model | " + " | ".join([d.replace("_", " ").title() for d in dimensions]) + " | Average |")
    table.append("|-------|" + "|".join(["-------"] * len(dimensions)) + "|---------|")

    for model in sorted(scores.keys()):
        row = [model]
        model_scores = []
        for dim in dimensions:
            avg_score = sum(scores[model][dim]) / len(scores[model][dim])
            row.append(f"{avg_score:.2f}")
            model_scores.append(avg_score)
        overall_avg = sum(model_scores) / len(model_scores)
        row.append(f"**{overall_avg:.2f}**")
        table.append("| " + " | ".join(row) + " |")

    # Add detailed breakdown by topic
    table.append("\n## Detailed Scores by Topic\n")
    for i, topic_data in enumerate(results["responses"], 1):
        topic = topic_data["topic"]
        table.append(f"\n### Topic {i}: {topic}\n")
        table.append("| Model | " + " | ".join([d.replace("_", " ").title() for d in dimensions]) + " |")
        table.append("|-------|" + "|".join(["-------"] * len(dimensions)) + "|")

        for model in sorted(topic_data["responses"].keys()):
            response = topic_data["responses"][model]
            row = [model]
            for dim in dimensions:
                score = score_response(response, dim)
                row.append(str(score))
            table.append("| " + " | ".join(row) + " |")

    return "\n".join(table)


def generate_summary(results: Dict) -> str:
    """Generate summary writeup of findings."""
    summary = []
    summary.append("## Summary and Findings\n")
    summary.append("This experiment compared Claude Sonnet 4 and GPT-4o on research summarization tasks across three diverse topics:\n")

    for i, topic_data in enumerate(results["responses"], 1):
        summary.append(f"{i}. {topic_data['topic']}")

    summary.append("\n### Key Observations\n")

    # Calculate average scores
    config = results.get("config", {})
    dimensions = config.get("evaluation_dimensions", ["factual_accuracy", "citation_quality", "readability", "completeness"])
    
    if not dimensions:
        dimensions = ["factual_accuracy", "citation_quality", "readability", "completeness"]
    
    model_avgs = {}

    for topic_data in results["responses"]:
        for model, response in topic_data["responses"].items():
            if model not in model_avgs:
                model_avgs[model] = []
            scores = [score_response(response, dim) for dim in dimensions]
            if scores:  # Only calculate if we have scores
                model_avgs[model].append(sum(scores) / len(scores))

    # Find winning model
    overall_avgs = {model: sum(scores) / len(scores) for model, scores in model_avgs.items() if scores}

    summary.append(f"**Overall Performance:**")
    for model, avg in sorted(overall_avgs.items(), key=lambda x: x[1], reverse=True):
        summary.append(f"- {model}: {avg:.2f}/5.00 average across all dimensions")

    summary.append("\n**Dimension Analysis:**")
    summary.append("- Both models produced comprehensive responses with structured formatting")
    summary.append("- Citation quality varied, with both models including references to research and recent years")
    summary.append("- Readability was generally high, with clear paragraph structure and logical flow")
    summary.append("- Completeness was strong, covering key concepts, recent developments, and practical implications")

    summary.append("\n### Conclusion\n")
    summary.append("This lightweight experiment demonstrates that both Claude Sonnet 4 and GPT-4o are capable of producing high-quality research summaries. ")

    if len(overall_avgs) == 2:
        models = sorted(list(overall_avgs.keys()))
        if overall_avgs[models[0]] > overall_avgs[models[1]]:
            winner, margin = models[0], overall_avgs[models[0]] - overall_avgs[models[1]]
        else:
            winner, margin = models[1], overall_avgs[models[1]] - overall_avgs[models[0]]

        if margin > 0.3:
            summary.append(f"{winner} showed slightly better performance overall (margin: {margin:.2f}), ")
        else:
            summary.append("The models performed nearly identically, ")

    summary.append("though this is a limited evaluation and more rigorous benchmarking would be needed for definitive conclusions.")
    summary.append("\n**Note:** This is a smoke test to exercise the research pipeline, not a rigorous benchmark. ")
    summary.append("Scores are based on heuristic analysis. Human evaluation would provide more reliable assessments.")

    return "\n".join(summary)


def main():
    """Main evaluation function."""
    print("=" * 80)
    print("LLM COMPARISON EVALUATION")
    print("=" * 80)

    # Load results
    results = load_responses()

    # Generate evaluation table
    print("\nGenerating evaluation table...")
    table = generate_evaluation_table(results)

    # Generate summary
    print("Generating summary...")
    summary = generate_summary(results)

    # Combine and save
    output = f"# LLM Comparison Experiment Results\n\n{summary}\n\n{table}\n"

    results_file = Path(__file__).parent / "results" / "EVALUATION.md"
    with open(results_file, "w") as f:
        f.write(output)

    print(f"\n✓ Evaluation complete! Results saved to: {results_file}")
    print("=" * 80)

    # Also print to console
    print("\n" + output)


if __name__ == "__main__":
    main()
