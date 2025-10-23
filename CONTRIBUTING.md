# Contributing to Tailscale MCP

Thank you for your interest in contributing to the Tailscale MCP project! We appreciate your time and effort in helping us improve this project.

## Code of Conduct

This project adheres to the Contributor Covenant [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in the [issue tracker](https://github.com/yourusername/tailscalemcp/issues).
2. If not, create a new issue with a clear title and description, including steps to reproduce the bug.

### Suggesting Enhancements

1. Check if the enhancement has already been suggested in the [issue tracker](https://github.com/yourusername/tailscalemcp/issues).
2. If not, create a new issue describing the enhancement and why it would be valuable.

### Making Changes

1. Fork the repository and create a new branch for your changes.
2. Make your changes following the coding style and guidelines below.
3. Add tests for your changes.
4. Run the test suite to ensure all tests pass.
5. Submit a pull request with a clear description of your changes.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- [Poetry](https://python-poetry.org/) for dependency management

### Setting Up the Development Environment

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/yourusername/tailscalemcp.git
   cd tailscalemcp
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Running Tests

Run the test suite with:

```bash
pytest
```

### Code Style

This project uses:

- [Black](https://github.com/psf/black) for code formatting
- [isort](https://github.com/timothycrosley/isort) for import sorting
- [mypy](http://mypy-lang.org/) for static type checking

Format and check the code with:

```bash
black .
isort .
mypy .
```

## Pull Request Process

1. Ensure your code follows the project's style guidelines.
2. Update the documentation if necessary.
3. Add tests for your changes.
4. Ensure all tests pass.
5. Submit a pull request with a clear description of your changes.

## License

By contributing to this project, you agree that your contributions will be licensed under the [MIT License](LICENSE).
