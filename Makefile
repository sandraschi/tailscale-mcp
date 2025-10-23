.PHONY: help install install-dev test test-cov lint format clean build publish docker docker-dev pre-commit setup

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv pip install -e .

install-dev: ## Install development dependencies
	uv pip install -e ".[dev]"

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage
	uv run pytest --cov=tailscalemcp --cov-report=html --cov-report=term-missing

lint: ## Run linting
	uv run ruff check .
	uv run mypy src/

format: ## Format code
	uv run ruff format .

format-check: ## Check code formatting
	uv run ruff format --check .

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf coverage_html/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

build: ## Build package
	uv run python -m build

publish: ## Publish to PyPI
	uv run twine upload dist/*

docker: ## Build Docker image
	docker build -t tailscalemcp:latest .

docker-dev: ## Build development Docker image
	docker build -f Dockerfile.dev -t tailscalemcp:dev .

docker-run: ## Run Docker container
	docker run --rm -p 8000:8000 tailscalemcp:latest

docker-run-dev: ## Run development Docker container
	docker run --rm -p 8000:8000 -v $(PWD):/app tailscalemcp:dev

pre-commit: ## Install pre-commit hooks
	uv run pre-commit install

setup: install-dev pre-commit ## Setup development environment

ci: lint test-cov ## Run CI checks locally

all: clean build test-cov lint ## Run all checks

# Development shortcuts
dev: install-dev pre-commit ## Setup for development
run: ## Run the MCP server
	uv run python -m tailscalemcp

# Docker Compose commands
up: ## Start services with docker-compose
	docker-compose up -d

down: ## Stop services with docker-compose
	docker-compose down

logs: ## View logs from docker-compose
	docker-compose logs -f

dev-up: ## Start development services with docker-compose
	docker-compose --profile dev up -d
