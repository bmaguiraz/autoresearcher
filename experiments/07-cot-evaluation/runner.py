#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chain-of-Thought Prompting Evaluation Experiment
Measures how CoT prompting affects factual accuracy in research summarization.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic


# 5 factual questions spanning different domains
FACTUAL_QUESTIONS = [
    {
        "id": "history",
        "domain": "History",
        "question": "What year did the Berlin Wall fall, and who was the leader of the Soviet Union at that time?"
    },
    {
        "id": "science",
        "domain": "Science",
        "question": "What is the role of mitochondria in cellular respiration, and what molecule do they primarily produce?"
    },
    {
        "id": "economics",
        "domain": "Economics",
        "question": "What is quantitative easing, and which central bank pioneered its large-scale use during the 2008 financial crisis?"
    },
    {
        "id": "geography",
        "domain": "Geography",
        "question": "What is the longest river in South America, and through which countries does it flow?"
    },
    {
        "id": "medicine",
        "domain": "Medicine",
        "question": "What is the mechanism of action of beta-blocker medications, and what conditions are they commonly used to treat?"
    }
]


def call_claude_direct(question: str, model: str = "claude-sonnet-4-20250514") -> dict:
    """Call Claude API with direct prompting (no CoT)."""
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    prompt = f"Answer the following question concisely and accurately:\n\n{question}"

    start_time = time.time()
    response = client.messages.create(
        model=model,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    elapsed_time = time.time() - start_time

    return {
        "prompting_style": "direct",
        "response": response.content[0].text,
        "elapsed_seconds": round(elapsed_time, 2),
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
    }


def call_claude_cot(question: str, model: str = "claude-sonnet-4-20250514") -> dict:
    """Call Claude API with chain-of-thought prompting."""
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    prompt = f"Answer the following question. Think step by step and show your reasoning:\n\n{question}"

    start_time = time.time()
    response = client.messages.create(
        model=model,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    elapsed_time = time.time() - start_time

    return {
        "prompting_style": "chain-of-thought",
        "response": response.content[0].text,
        "elapsed_seconds": round(elapsed_time, 2),
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
    }


def evaluate_response(response_text: str, question: dict) -> dict:
    """
    Evaluate a response on three dimensions.

    Returns:
    - factual_correctness: 0 or 1 (binary, based on keyword presence)
    - reasoning_quality: 1-5 (based on structure and explanation depth)
    - answer_completeness: 1-5 (based on addressing all question parts)
    """
    response_lower = response_text.lower()

    # Domain-specific factual checks (simplified heuristics)
    factual_correct = 0
    if question['id'] == 'history':
        # Berlin Wall fell in 1989, leader was Gorbachev
        if '1989' in response_text and ('gorbachev' in response_lower or 'mikhail' in response_lower):
            factual_correct = 1
    elif question['id'] == 'science':
        # Mitochondria produce ATP through cellular respiration
        if 'atp' in response_lower and ('energy' in response_lower or 'electron' in response_lower):
            factual_correct = 1
    elif question['id'] == 'economics':
        # QE involves buying assets, Fed pioneered large-scale use
        if ('federal reserve' in response_lower or 'fed' in response_lower or 'bank of japan' in response_lower) and \
           ('asset' in response_lower or 'bond' in response_lower or 'purchase' in response_lower or 'securities' in response_lower):
            factual_correct = 1
    elif question['id'] == 'geography':
        # Amazon River, flows through multiple countries including Brazil and Peru
        if 'amazon' in response_lower and ('brazil' in response_lower or 'peru' in response_lower):
            factual_correct = 1
    elif question['id'] == 'medicine':
        # Beta-blockers block adrenaline/beta receptors, treat heart conditions
        if ('beta' in response_lower or 'adrenaline' in response_lower or 'receptor' in response_lower) and \
           ('heart' in response_lower or 'blood pressure' in response_lower or 'hypertension' in response_lower):
            factual_correct = 1

    # Reasoning quality: assess structure and explanation depth
    has_structure = response_text.count('\n') > 1 or any(marker in response_lower for marker in ['first', 'second', 'because', 'therefore', 'thus'])
    has_explanation = len(response_text.split()) > 30
    shows_reasoning = any(word in response_lower for word in ['step', 'reason', 'because', 'therefore', 'thus', 'consequently'])

    reasoning_quality = 2  # baseline
    if has_structure:
        reasoning_quality += 1
    if has_explanation:
        reasoning_quality += 1
    if shows_reasoning:
        reasoning_quality += 1
    reasoning_quality = min(5, reasoning_quality)

    # Answer completeness: check if both parts of the question are addressed
    question_parts = question['question'].split(',')
    words_per_part = len(response_text.split()) / len(question_parts)

    completeness = 2  # baseline
    if words_per_part > 15:
        completeness += 1
    if words_per_part > 25:
        completeness += 1
    if len(question_parts) == 2 and all(any(word in response_lower for word in part.lower().split()[:3]) for part in question_parts):
        completeness += 1
    completeness = min(5, completeness)

    return {
        "factual_correctness": factual_correct,
        "reasoning_quality": reasoning_quality,
        "answer_completeness": completeness
    }


def run_experiment():
    """Run the full CoT evaluation experiment."""
    print("=" * 80)
    print("Chain-of-Thought Prompting Evaluation")
    print("Measuring CoT impact on factual accuracy")
    print("=" * 80)
    print()

    results = []

    for question in FACTUAL_QUESTIONS:
        print(f"Domain: {question['domain']}")
        print(f"Question: {question['question']}")
        print()

        # Direct prompting (no CoT)
        print("  Calling Claude with direct prompting...")
        direct_result = call_claude_direct(question['question'])
        direct_scores = evaluate_response(direct_result['response'], question)
        print(f"    ✓ Response received ({direct_result['usage']['output_tokens']} tokens, {direct_result['elapsed_seconds']}s)")

        # Chain-of-thought prompting
        print("  Calling Claude with CoT prompting...")
        cot_result = call_claude_cot(question['question'])
        cot_scores = evaluate_response(cot_result['response'], question)
        print(f"    ✓ Response received ({cot_result['usage']['output_tokens']} tokens, {cot_result['elapsed_seconds']}s)")
        print()

        results.append({
            "question_id": question['id'],
            "domain": question['domain'],
            "question": question['question'],
            "direct": {
                "response": direct_result['response'],
                "scores": direct_scores,
                "metadata": {
                    "elapsed_seconds": direct_result['elapsed_seconds'],
                    "tokens": direct_result['usage']
                }
            },
            "cot": {
                "response": cot_result['response'],
                "scores": cot_scores,
                "metadata": {
                    "elapsed_seconds": cot_result['elapsed_seconds'],
                    "tokens": cot_result['usage']
                }
            }
        })

    return results


def generate_report(results: list) -> str:
    """Generate markdown report with results table and analysis."""

    # Calculate aggregate scores
    direct_totals = {"factual_correctness": 0, "reasoning_quality": 0, "answer_completeness": 0}
    cot_totals = {"factual_correctness": 0, "reasoning_quality": 0, "answer_completeness": 0}

    for result in results:
        for metric in direct_totals.keys():
            direct_totals[metric] += result['direct']['scores'][metric]
            cot_totals[metric] += result['cot']['scores'][metric]

    n = len(results)
    direct_avg = {k: v/n for k, v in direct_totals.items()}
    cot_avg = {k: v/n for k, v in cot_totals.items()}

    # Build markdown report
    report = []
    report.append("# Chain-of-Thought Prompting Evaluation")
    report.append("")
    report.append("**Experiment**: Measuring CoT impact on factual accuracy in research summarization")
    report.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d')}")
    report.append(f"**Questions**: {len(FACTUAL_QUESTIONS)} factual questions across diverse domains")
    report.append(f"**Model**: Claude Sonnet 4")
    report.append("")

    report.append("## Results Summary")
    report.append("")
    report.append("| Domain | Prompting Style | Factual Correctness | Reasoning Quality | Answer Completeness |")
    report.append("|--------|----------------|---------------------|-------------------|---------------------|")

    for result in results:
        direct_scores = result['direct']['scores']
        cot_scores = result['cot']['scores']

        report.append(f"| {result['domain']} | Direct | {direct_scores['factual_correctness']} | {direct_scores['reasoning_quality']}/5 | {direct_scores['answer_completeness']}/5 |")
        report.append(f"| | Chain-of-Thought | {cot_scores['factual_correctness']} | {cot_scores['reasoning_quality']}/5 | {cot_scores['answer_completeness']}/5 |")

    report.append("")
    report.append("## Aggregate Scores")
    report.append("")
    report.append("| Prompting Style | Factual Correctness | Reasoning Quality | Answer Completeness |")
    report.append("|----------------|---------------------|-------------------|---------------------|")
    report.append(f"| Direct | {direct_totals['factual_correctness']}/{n} ({direct_avg['factual_correctness']*100:.0f}%) | {direct_avg['reasoning_quality']:.2f}/5 | {direct_avg['answer_completeness']:.2f}/5 |")
    report.append(f"| Chain-of-Thought | {cot_totals['factual_correctness']}/{n} ({cot_avg['factual_correctness']*100:.0f}%) | {cot_avg['reasoning_quality']:.2f}/5 | {cot_avg['answer_completeness']:.2f}/5 |")

    report.append("")
    report.append("## Analysis")
    report.append("")

    # Calculate improvements
    factual_improvement = (cot_avg['factual_correctness'] - direct_avg['factual_correctness']) * 100
    reasoning_improvement = ((cot_avg['reasoning_quality'] - direct_avg['reasoning_quality']) / 5) * 100
    completeness_improvement = ((cot_avg['answer_completeness'] - direct_avg['answer_completeness']) / 5) * 100

    # Generate summary paragraph
    if factual_improvement > 0:
        factual_statement = f"improved factual accuracy by {factual_improvement:.0f} percentage points"
    elif factual_improvement < 0:
        factual_statement = f"decreased factual accuracy by {abs(factual_improvement):.0f} percentage points"
    else:
        factual_statement = "maintained the same factual accuracy"

    summary = (f"Chain-of-thought prompting {factual_statement} compared to direct prompting "
              f"({cot_avg['factual_correctness']*100:.0f}% vs {direct_avg['factual_correctness']*100:.0f}%). "
              f"Reasoning quality scores {'increased' if reasoning_improvement > 0 else 'decreased' if reasoning_improvement < 0 else 'remained stable'} "
              f"by {abs(reasoning_improvement):.1f}%, while answer completeness {'improved' if completeness_improvement > 0 else 'declined' if completeness_improvement < 0 else 'stayed consistent'} "
              f"by {abs(completeness_improvement):.1f}%. "
              f"All 10 API calls completed successfully. "
              f"{'CoT prompting demonstrates clear benefits for factual accuracy and reasoning depth.' if factual_improvement > 0 and reasoning_improvement > 0 else 'Results suggest direct prompting may be sufficient for straightforward factual queries.' if factual_improvement <= 0 else 'CoT shows mixed results, benefiting some dimensions while not improving others.'}")

    report.append(summary)
    report.append("")

    report.append("## Detailed Responses")
    report.append("")

    for result in results:
        report.append(f"### {result['domain']}: {result['question']}")
        report.append("")
        report.append("**Direct Prompting:**")
        report.append("```")
        report.append(result['direct']['response'])
        report.append("```")
        report.append("")
        report.append("**Chain-of-Thought Prompting:**")
        report.append("```")
        report.append(result['cot']['response'])
        report.append("```")
        report.append("")

    return "\n".join(report)


def main():
    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        return 1

    # Run experiment
    results = run_experiment()

    # Generate report
    report = generate_report(results)

    # Save results
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save full results as JSON
    with open(results_dir / f"results_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)

    # Save markdown report
    report_path = results_dir / f"report_{timestamp}.md"
    with open(report_path, "w") as f:
        f.write(report)

    print("=" * 80)
    print("Experiment Complete!")
    print("=" * 80)
    print(f"Report saved to: {report_path}")
    print()
    print(report)

    return 0


if __name__ == "__main__":
    exit(main())
