# LLM Comparison Experiment Results

## Summary and Findings

This experiment compared Claude Sonnet 4 and GPT-4o on research summarization tasks across three diverse topics:

1. Quantum computing advances in error correction and fault-tolerant quantum computing
2. mRNA vaccine mechanisms and their application beyond COVID-19
3. Ocean carbon sequestration techniques and their potential for climate change mitigation

### Key Observations

**Overall Performance:**
- claude-sonnet-4: 4.92/5.00 average across all dimensions
- gpt-4o: 4.42/5.00 average across all dimensions

**Dimension Analysis:**
- Both models produced comprehensive responses with structured formatting
- Citation quality varied, with both models including references to research and recent years
- Readability was generally high, with clear paragraph structure and logical flow
- Completeness was strong, covering key concepts, recent developments, and practical implications

### Conclusion

This lightweight experiment demonstrates that both Claude Sonnet 4 and GPT-4o are capable of producing high-quality research summaries. 
claude-sonnet-4 showed slightly better performance overall (margin: 0.50), 
though this is a limited evaluation and more rigorous benchmarking would be needed for definitive conclusions.

**Note:** This is a smoke test to exercise the research pipeline, not a rigorous benchmark. 
Scores are based on heuristic analysis. Human evaluation would provide more reliable assessments.

## Evaluation Results

| Model | Factual Accuracy | Citation Quality | Readability | Completeness | Average |
|-------|-------|-------|-------|-------|---------|
| claude-sonnet-4 | 5.00 | 4.67 | 5.00 | 5.00 | **4.92** |
| gpt-4o | 5.00 | 2.67 | 5.00 | 5.00 | **4.42** |

## Detailed Scores by Topic


### Topic 1: Quantum computing advances in error correction and fault-tolerant quantum computing

| Model | Factual Accuracy | Citation Quality | Readability | Completeness |
|-------|-------|-------|-------|-------|
| claude-sonnet-4 | 5 | 5 | 5 | 5 |
| gpt-4o | 5 | 4 | 5 | 5 |

### Topic 2: mRNA vaccine mechanisms and their application beyond COVID-19

| Model | Factual Accuracy | Citation Quality | Readability | Completeness |
|-------|-------|-------|-------|-------|
| claude-sonnet-4 | 5 | 5 | 5 | 5 |
| gpt-4o | 5 | 2 | 5 | 5 |

### Topic 3: Ocean carbon sequestration techniques and their potential for climate change mitigation

| Model | Factual Accuracy | Citation Quality | Readability | Completeness |
|-------|-------|-------|-------|-------|
| claude-sonnet-4 | 5 | 4 | 5 | 5 |
| gpt-4o | 5 | 2 | 5 | 5 |
