# Contributing

## Development Workflow

1. Create a feature branch from `main`: `git checkout -b feature/<task-id>`
2. Make your changes and commit frequently
3. Run tests: `pytest tests/`
4. Push and create a pull request

## Code Standards

- Python 3.10+ with type hints
- Follow PEP 8 style guidelines
- Add tests for new functionality
- Keep experiments self-contained

## Commit Messages

Use descriptive commit messages that explain the "why" behind changes:

```
<TASK-ID>: Short description of the change

Longer explanation if needed.

Co-Authored-By: Name <email>
```

## Adding Experiments

See [Running Experiments](experiments.md) for the standard experiment structure. New experiments should:

- Follow the naming convention: `<id>-<name>/`
- Include a `program.md` with methodology
- Include a `pyproject.toml` with dependencies
- Be documented in the project README
