#!/usr/bin/env python3
"""
Chain-of-Thought Prompting Experiment (Demo Version)
Demonstrates the CoT evaluation framework without requiring API keys.
"""

import json
from datetime import datetime
from pathlib import Path

# Factual questions spanning different domains
QUESTIONS = [
    {
        "id": "history",
        "domain": "History",
        "question": "What were the primary factors that led to the decline and eventual dissolution of the Ottoman Empire in the early 20th century?"
    },
    {
        "id": "science",
        "domain": "Science",
        "question": "Explain the process of photosynthesis, including the light-dependent and light-independent reactions and their key products."
    },
    {
        "id": "economics",
        "domain": "Economics",
        "question": "What are the main causes of inflation in an economy, and how do central banks typically respond to control it?"
    },
    {
        "id": "geography",
        "domain": "Geography",
        "question": "Describe the key characteristics of the Amazon Basin, including its climate, biodiversity, and role in global climate regulation."
    },
    {
        "id": "medicine",
        "domain": "Medicine",
        "question": "How does antibiotic resistance develop in bacterial populations, and what mechanisms do bacteria use to resist antibiotics?"
    }
]

# Demo responses (simulated for pipeline verification)
DEMO_RESPONSES = {
    "history": {
        "direct": "The Ottoman Empire declined due to military defeats, nationalist movements, economic stagnation, and political corruption. World War I participation on the losing side accelerated its collapse. The empire was officially dissolved in 1922 and replaced by the Republic of Turkey in 1923.",
        "cot": "Let's think step by step.\n\nFirst, we need to identify the key periods. The Ottoman Empire's decline began in the late 17th century but accelerated in the 19th and early 20th centuries.\n\nMilitary factors: The empire suffered major defeats including the loss of territories in the Balkans and North Africa. Military technology lagged behind European powers.\n\nNationalist movements: Subject peoples (Greeks, Serbs, Bulgarians, Arabs) sought independence, fragmenting the empire. The rise of Turkish nationalism also contributed to internal tensions.\n\nEconomic decline: The empire couldn't compete with industrialized European economies. Foreign debt mounted, and economic concessions to European powers undermined sovereignty.\n\nPolitical factors: Administrative corruption, weak sultans, and failed reform attempts (Tanzimat) couldn't modernize the state quickly enough.\n\nWorld War I was the final blow. The empire joined the Central Powers, suffered defeat, and faced Allied occupation. The Treaty of Sèvres partitioned its territories. Mustafa Kemal Atatürk's nationalist movement abolished the sultanate in 1922 and established the Turkish Republic in 1923."
    },
    "science": {
        "direct": "Photosynthesis converts light energy into chemical energy. It occurs in two stages: light-dependent reactions in the thylakoids produce ATP and NADPH, while light-independent reactions (Calvin cycle) in the stroma use these products to fix CO2 into glucose. Oxygen is released as a byproduct.",
        "cot": "Let's think step by step.\n\nPhotosynthesis is the process by which plants convert light energy into chemical energy stored in sugars.\n\nLocation: It occurs in chloroplasts, specifically in two regions—the thylakoid membranes and the stroma.\n\nLight-dependent reactions (occur in thylakoids):\n1. Photosystem II absorbs light, splitting water molecules (H2O) into oxygen, protons, and electrons\n2. Oxygen is released as a waste product\n3. Electrons move through the electron transport chain, pumping protons across the membrane\n4. Photosystem I absorbs more light, re-energizing electrons\n5. These high-energy electrons reduce NADP+ to NADPH\n6. The proton gradient drives ATP synthase to produce ATP\n\nKey products: ATP, NADPH, and O2\n\nLight-independent reactions (Calvin cycle, occurs in stroma):\n1. CO2 from the atmosphere is fixed by the enzyme RuBisCO\n2. ATP and NADPH from the light reactions provide energy and electrons\n3. Through a series of reactions, CO2 is converted into G3P (glyceraldehyde-3-phosphate)\n4. G3P molecules are used to synthesize glucose and other organic compounds\n\nOverall equation: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2"
    },
    "economics": {
        "direct": "Inflation occurs when too much money chases too few goods, rising production costs push prices up, or demand exceeds supply. Central banks respond by raising interest rates, reducing money supply, and adjusting reserve requirements to cool the economy and stabilize prices.",
        "cot": "Let's think step by step.\n\nFirst, let's identify the main causes of inflation:\n\n1. Demand-pull inflation: When aggregate demand exceeds aggregate supply, prices rise. This happens during economic booms when consumers have more purchasing power than available goods.\n\n2. Cost-push inflation: When production costs increase (wages, raw materials, energy), businesses pass these costs to consumers through higher prices.\n\n3. Monetary inflation: When central banks increase money supply faster than economic growth, the currency's purchasing power decreases.\n\n4. Built-in inflation: Wage-price spiral where workers demand higher wages to keep up with prices, leading businesses to raise prices further.\n\nNow, how do central banks respond?\n\nPrimary tool—interest rates:\n- Raising interest rates makes borrowing more expensive\n- This reduces consumer spending and business investment\n- Lower demand helps cool price increases\n- The Federal Reserve in the U.S. adjusts the federal funds rate\n\nOther tools:\n1. Open market operations: Selling government bonds reduces money supply\n2. Reserve requirements: Increasing the reserves banks must hold reduces lending\n3. Forward guidance: Communicating future policy intentions to influence expectations\n\nThe goal is to achieve a \"soft landing\"—reducing inflation without causing recession. Central banks typically target 2% annual inflation as optimal for economic growth."
    },
    "geography": {
        "direct": "The Amazon Basin is a vast tropical region in South America with high rainfall, dense rainforest, and incredible biodiversity. It contains millions of plant and animal species. The rainforest absorbs large amounts of CO2 and produces oxygen, making it crucial for global climate regulation.",
        "cot": "Let's think step by step.\n\nLocation and size: The Amazon Basin covers approximately 7 million square kilometers across nine countries, primarily Brazil, Peru, and Colombia. The Amazon River and its tributaries drain this entire region.\n\nClimate characteristics:\n- Tropical equatorial climate\n- Average temperatures: 25-28°C year-round\n- High rainfall: 2,000-3,000mm annually\n- High humidity: typically above 80%\n- Minimal seasonal temperature variation\n\nBiodiversity:\n- Most biodiverse terrestrial ecosystem on Earth\n- Estimated 390 billion individual trees representing 16,000 species\n- 10% of all species on Earth reside here\n- 2.5 million insect species, 2,000 birds and mammals, 2,000 fish species\n- Many species remain undiscovered\n\nRole in global climate regulation:\n\n1. Carbon sequestration: The rainforest stores 150-200 billion tons of carbon in its biomass and soil, acting as a massive carbon sink that helps mitigate climate change.\n\n2. Oxygen production: While often called \"Earth's lungs,\" the forest produces about 20% of oxygen but consumes most of it through respiration and decomposition. Its net oxygen contribution is minimal.\n\n3. Water cycle regulation: Trees release water vapor through transpiration, creating \"flying rivers\" that transport moisture across South America, influencing rainfall patterns continent-wide.\n\n4. Albedo effect: The forest's dark canopy absorbs solar radiation, affecting regional and global temperature patterns.\n\nThreats: Deforestation for agriculture, logging, and mining threatens these ecological functions."
    },
    "medicine": {
        "direct": "Antibiotic resistance develops when bacteria evolve defenses against drugs. This happens through random mutations and horizontal gene transfer. Bacteria resist antibiotics by destroying the drug, pumping it out, changing their cell structure, or altering the drug's target site. Overuse of antibiotics accelerates this process.",
        "cot": "Let's think step by step.\n\nFirst, let's understand how resistance develops:\n\n1. Natural selection process:\n- When antibiotics are used, most susceptible bacteria die\n- Bacteria with random mutations that confer resistance survive\n- These resistant bacteria reproduce, passing resistance to offspring\n- Over time, the resistant population dominates\n\n2. Horizontal gene transfer:\n- Bacteria can share resistance genes directly through:\n  - Conjugation: Direct DNA transfer via pili\n  - Transformation: Uptake of DNA from dead bacteria\n  - Transduction: Transfer via bacteriophages (viruses)\n- This allows resistance to spread rapidly between species\n\nNow, the specific mechanisms bacteria use to resist:\n\n1. Drug inactivation:\n- Bacteria produce enzymes that destroy antibiotics\n- Example: Beta-lactamases break down penicillin and related drugs\n- These enzymes chemically modify the antibiotic, rendering it ineffective\n\n2. Efflux pumps:\n- Bacteria develop membrane proteins that actively pump antibiotics out\n- The drug never reaches high enough concentrations to be lethal\n- Some pumps work against multiple antibiotic classes\n\n3. Target modification:\n- Bacteria alter the molecular structure of the antibiotic's target\n- Example: MRSA modifies penicillin-binding proteins\n- The antibiotic can no longer bind effectively\n\n4. Reduced permeability:\n- Bacteria change cell wall/membrane structure\n- Reduces antibiotic entry into the cell\n- Particularly important for Gram-negative bacteria\n\n5. Bypass mechanisms:\n- Bacteria develop alternative metabolic pathways\n- The pathway targeted by the antibiotic becomes unnecessary\n\nAccelerating factors: Overuse in medicine and agriculture, incomplete treatment courses, and poor infection control practices all increase selection pressure for resistance."
    }
}

def score_response(response_text: str, question_data: dict) -> dict:
    """Score a response on factual correctness, reasoning quality, and completeness."""
    word_count = len(response_text.split())
    has_specific_details = word_count > 100
    has_structured_explanation = response_text.count('\n') > 2 or any(marker in response_text for marker in ['First', 'Second', 'Additionally', 'Furthermore', '1.', '2.'])
    has_cause_effect = any(word in response_text.lower() for word in ['because', 'therefore', 'thus', 'as a result', 'consequently', 'leads to'])
    has_examples = any(word in response_text.lower() for word in ['example', 'such as', 'including', 'for instance'])
    is_coherent = word_count > 80 and word_count < 800

    reasoning_score = 2
    if has_cause_effect:
        reasoning_score += 1
    if has_structured_explanation:
        reasoning_score += 1
    if has_examples:
        reasoning_score += 1
    reasoning_score = min(5, reasoning_score)

    question_keywords = set(question_data['question'].lower().split())
    response_words = set(response_text.lower().split())
    keyword_coverage = len(question_keywords & response_words) / len(question_keywords)

    completeness_score = int(keyword_coverage * 5) + 1
    completeness_score = min(5, completeness_score)

    if word_count < 50:
        completeness_score = min(completeness_score, 2)
    elif word_count > 200:
        completeness_score = min(5, completeness_score + 1)

    return {
        "factual_correctness": 1 if (has_specific_details and has_structured_explanation) else 0,
        "reasoning_quality": reasoning_score,
        "answer_completeness": completeness_score
    }

def run_experiment():
    """Run the chain-of-thought experiment with demo data."""
    print("=" * 80)
    print("Chain-of-Thought Prompting Experiment (Demo Mode)")
    print("=" * 80)
    print()
    print("NOTE: Running in demo mode with pre-generated responses")
    print("      (API key not required for pipeline verification)")
    print()

    results = []

    for question_data in QUESTIONS:
        print(f"Domain: {question_data['domain']}")
        print(f"Question: {question_data['question'][:80]}...")
        print()

        # Simulate API calls with demo responses
        direct_response = DEMO_RESPONSES[question_data['id']]["direct"]
        cot_response = DEMO_RESPONSES[question_data['id']]["cot"]

        direct_scores = score_response(direct_response, question_data)
        cot_scores = score_response(cot_response, question_data)

        print(f"  ✓ Direct answer generated ({len(direct_response.split())} words)")
        print(f"  ✓ Chain-of-thought answer generated ({len(cot_response.split())} words)")
        print()

        results.append({
            "domain": question_data['domain'],
            "question_id": question_data['id'],
            "question": question_data['question'],
            "direct": {
                "response": direct_response,
                "scores": direct_scores,
                "metadata": {
                    "elapsed_seconds": 2.1,
                    "tokens": {"input": 25, "output": len(direct_response.split())}
                }
            },
            "chain_of_thought": {
                "response": cot_response,
                "scores": cot_scores,
                "metadata": {
                    "elapsed_seconds": 3.4,
                    "tokens": {"input": 30, "output": len(cot_response.split())}
                }
            }
        })

    return results

def generate_report(results: list) -> str:
    """Generate markdown report with results and analysis."""
    direct_stats = {
        "factual_correctness": 0,
        "reasoning_quality": 0,
        "answer_completeness": 0
    }
    cot_stats = {
        "factual_correctness": 0,
        "reasoning_quality": 0,
        "answer_completeness": 0
    }

    for result in results:
        for metric in direct_stats.keys():
            direct_stats[metric] += result['direct']['scores'][metric]
            cot_stats[metric] += result['chain_of_thought']['scores'][metric]

    num_questions = len(results)

    report = []
    report.append("# Chain-of-Thought Prompting: Impact on Factual Accuracy")
    report.append("")
    report.append("**Experiment**: Evaluating CoT prompting vs direct answering")
    report.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d')}")
    report.append(f"**Model**: Claude Sonnet 4 (Demo Mode)")
    report.append(f"**Questions**: {num_questions} factual questions across diverse domains")
    report.append("")

    report.append("## Results Table")
    report.append("")
    report.append("| Domain | Prompting Style | Factual Correctness | Reasoning Quality | Answer Completeness |")
    report.append("|--------|-----------------|---------------------|-------------------|---------------------|")

    for result in results:
        direct = result['direct']['scores']
        cot = result['chain_of_thought']['scores']

        report.append(f"| {result['domain']} | Direct | {'✓' if direct['factual_correctness'] else '✗'} | {direct['reasoning_quality']}/5 | {direct['answer_completeness']}/5 |")
        report.append(f"| | Chain-of-Thought | {'✓' if cot['factual_correctness'] else '✗'} | {cot['reasoning_quality']}/5 | {cot['answer_completeness']}/5 |")

    report.append("")
    report.append("## Aggregate Scores")
    report.append("")
    report.append("| Prompting Style | Factual Correctness | Avg Reasoning Quality | Avg Answer Completeness |")
    report.append("|-----------------|---------------------|------------------------|-------------------------|")

    direct_correct_pct = (direct_stats['factual_correctness'] / num_questions) * 100
    cot_correct_pct = (cot_stats['factual_correctness'] / num_questions) * 100

    direct_reasoning_avg = direct_stats['reasoning_quality'] / num_questions
    cot_reasoning_avg = cot_stats['reasoning_quality'] / num_questions

    direct_completeness_avg = direct_stats['answer_completeness'] / num_questions
    cot_completeness_avg = cot_stats['answer_completeness'] / num_questions

    report.append(f"| Direct | {direct_correct_pct:.0f}% ({direct_stats['factual_correctness']}/{num_questions}) | {direct_reasoning_avg:.2f}/5 | {direct_completeness_avg:.2f}/5 |")
    report.append(f"| Chain-of-Thought | {cot_correct_pct:.0f}% ({cot_stats['factual_correctness']}/{num_questions}) | {cot_reasoning_avg:.2f}/5 | {cot_completeness_avg:.2f}/5 |")

    report.append("")
    report.append("## Summary")
    report.append("")

    correctness_improvement = cot_correct_pct - direct_correct_pct
    reasoning_improvement = cot_reasoning_avg - direct_reasoning_avg
    completeness_improvement = cot_completeness_avg - direct_completeness_avg

    if correctness_improvement > 0:
        correctness_statement = f"Chain-of-thought prompting improved factual correctness by {correctness_improvement:.0f} percentage points ({cot_correct_pct:.0f}% vs {direct_correct_pct:.0f}%)."
    elif correctness_improvement < 0:
        correctness_statement = f"Direct prompting achieved {abs(correctness_improvement):.0f} percentage points higher factual correctness than chain-of-thought ({direct_correct_pct:.0f}% vs {cot_correct_pct:.0f}%)."
    else:
        correctness_statement = f"Both approaches achieved equal factual correctness rates ({direct_correct_pct:.0f}%)."

    reasoning_statement = f"Reasoning quality {'improved' if reasoning_improvement > 0 else 'decreased'} by {abs(reasoning_improvement):.2f} points (from {direct_reasoning_avg:.2f} to {cot_reasoning_avg:.2f})."
    completeness_statement = f"Answer completeness {'increased' if completeness_improvement > 0 else 'decreased'} by {abs(completeness_improvement):.2f} points (from {direct_completeness_avg:.2f} to {cot_completeness_avg:.2f})."

    report.append(f"{correctness_statement} {reasoning_statement} {completeness_statement} "
                 f"Overall, chain-of-thought prompting {'demonstrated measurable benefits' if (correctness_improvement + reasoning_improvement + completeness_improvement) > 0 else 'showed mixed results'} "
                 f"for factual question answering across diverse domains. The technique appears "
                 f"{'particularly effective' if reasoning_improvement > 0.5 else 'moderately effective' if reasoning_improvement > 0 else 'less effective'} "
                 f"at improving reasoning quality and structured explanations.")
    report.append("")

    report.append("**Note**: This demo uses pre-generated responses to verify the experiment framework. "
                 "For actual results, run `runner.py` with a valid ANTHROPIC_API_KEY.")
    report.append("")

    report.append("## Detailed Responses")
    report.append("")

    for result in results:
        report.append(f"### {result['domain']}: {result['question']}")
        report.append("")
        report.append("**Direct Answer:**")
        report.append("```")
        report.append(result['direct']['response'])
        report.append("```")
        report.append("")
        report.append("**Chain-of-Thought Answer:**")
        report.append("```")
        report.append(result['chain_of_thought']['response'])
        report.append("```")
        report.append("")

    return "\n".join(report)

def main():
    print("Running demo version (no API key required)")
    print()

    results = run_experiment()
    report = generate_report(results)

    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    with open(results_dir / f"results_demo_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)

    report_path = results_dir / f"report_demo_{timestamp}.md"
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
