# Contributing to Tailscale MCP

Thank you for your interest in contributing.

## Code of Conduct

This project adheres to the Contributor Covenant [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting bugs / enhancements

Use the [issue tracker](https://github.com/sandraschi/tailscale-mcp/issues).

### Making changes

1. Fork and branch.
2. Follow the style and testing steps below.
3. Open a PR with a clear description.

## Development setup

### Prerequisites

- Python **3.12+**
- [uv](https://docs.astral.sh/uv/)

### Environment

```bash
git clone https://github.com/sandraschi/tailscale-mcp.git
cd tailscale-mcp
uv sync
```

Install hooks:

```bash
uv run pre-commit install
```

### Tests

```bash
uv run pytest
```

### Code style

- [Ruff](https://github.com/astral-sh/ruff) — lint, import sort, format
- [mypy](https://mypy-lang.org/) — types (also via pre-commit)

```bash
uv run ruff check .
uv run ruff format .
uv run mypy src/
```

## Pull request process

1. Run tests and linters.
2. Update docs if behavior or public surfaces change.
3. Submit the PR with a clear description.

## License

Contributions are licensed under the [MIT License](LICENSE).
