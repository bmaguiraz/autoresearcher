<!-- MCP e2e test -->
<!-- SDK 0.1.50 e2e test -->
<!-- final e2e test -->
<!-- final observability test -->
<!-- v35 test -->
<!-- v32 archive test 2026-03-23 -->
<!-- observability test 2026-03-22 -->
<!-- Test timestamp: 2026-03-21 22:52:24 UTC - MOR-108 warm repo caching test (session 2 - warm cache) -->
<!-- Context7 MCP Test: Next.js Image Component Key Props
     Required: src, alt, width/height (unless using fill or static import)
     Layout: fill (fills parent container, parent needs position: relative)
     Performance: priority (preload for LCP/above-fold), loading (lazy/eager), sizes (responsive hints)
     Quality: quality (1-100, default 75), placeholder (empty/blur), blurDataURL
     Styling: style prop for objectFit, objectPosition, etc.
-->
# Autoresearcher

![Build Status](https://github.com/bmaguiraz/autoresearcher/actions/workflows/ci.yml/badge.svg?branch=main)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)

AI-powered autonomous research and optimization platform.

Autoresearcher automates iterative experimentation workflows using LLMs. It provides a framework for running optimization experiments, tracking results, and systematically improving prompts and configurations.

## Project Status

- **Linear Project**: autoresearcher (MOR team)
- **Status**: Active development

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/bmaguiraz/autoresearcher.git
cd autoresearcher

# Install dependencies for an experiment
cd experiments/02-llm-prompt-opt
uv sync
```

### Running an Experiment

```bash
cd experiments/02-llm-prompt-opt
python eval.py
```

See individual experiment READMEs in `experiments/` for detailed instructions.

## Project Structure

```
autoresearcher/
  src/                  # Core library code
  experiments/          # Optimization experiments
    02-llm-prompt-opt/  # LLM prompt optimization experiment
  tests/                # Test suites
  docs/                 # Documentation
    architecture.md     # System architecture overview
    experiments.md      # Guide to running experiments
    contributing.md     # Contribution guidelines
  config/               # Shared configuration
```

## Experiments

Each experiment lives in its own directory under `experiments/` with:

- `program.md` -- Instructions and methodology
- `config.json` -- Experiment configuration
- `runner.py` -- Experiment runner script
- `eval.py` -- Evaluation script
- `results/` -- Output directory for results

### Current Experiments

| ID | Name | Description |
|----|------|-------------|
| 02 | LLM Prompt Optimization | Iterative prompt refinement for sentiment classification |

## Documentation

- [Architecture Overview](docs/architecture.md)
- [Running Experiments](docs/experiments.md)
- [Contributing](docs/contributing.md)

## Development

### Running Tests

```bash
pytest tests/
```

### Project Conventions

- Python 3.10+ with type hints
- Each experiment is self-contained with its own dependencies
- Results are tracked in version control for reproducibility

## License

Private repository. All rights reserved.

# cache debug test
# v3 test
# v4 session reuse test
# observability test
