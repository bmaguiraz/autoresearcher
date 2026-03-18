# Contributing to Autoresearcher

## Setup

```bash
# Clone and set up the repository
git clone https://github.com/bmaguiraz/autoresearcher.git
cd autoresearcher
uv sync  # Install dependencies (uv recommended)
```

For experiments, navigate to the experiment directory and run `uv sync` there.

## Running Tests

```bash
pytest tests/                      # Run all tests
pytest tests/ --cov=autoresearcher # Run with coverage
pytest tests/integration/          # Run integration tests only
```

Note: Integration tests create real Linear issues marked with `[TEST]` prefix.

## Running Experiments Locally

```bash
cd experiments/02-llm-prompt-opt  # Navigate to experiment
uv sync                            # Install dependencies
python eval.py                     # Run the experiment
```

See individual experiment `README.md` files for specific instructions.

## Pull Request Conventions

- **Branch naming**: `feature/<task-id>` or `fix/<task-id>`
- **Commit format**: `<TASK-ID>: Short description` with detailed explanation if needed
- **Before submitting**: Run tests and ensure they pass
- **PR description**: Include summary of changes and test plan

## Code Standards

- Python 3.10+ with type hints
- Follow PEP 8 style guidelines
- Add tests for new functionality
