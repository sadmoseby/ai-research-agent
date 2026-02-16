# AI Research Agent - Development Makefile

.PHONY: help install test test-unit test-integration test-e2e test-all clean lint format setup consolidate \
        docker-build docker-push docker-run docker-clean

# Docker configuration — override on the command line as needed:
#   make docker-build IMAGE_TAG=v1.2.3
#   make docker-push  REGISTRY=us-central1-docker.pkg.dev/my-project/my-repo
IMAGE_NAME ?= ai-research-agent
IMAGE_TAG  ?= latest
REGISTRY   ?=
_FULL_IMAGE = $(if $(REGISTRY),$(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG),$(IMAGE_NAME):$(IMAGE_TAG))

# Default target
help:
	@echo "AI Research Agent - Available commands:"
	@echo ""
	@echo "Setup and Installation:"
	@echo "  setup          - Complete project setup (install deps, create .env, etc.)"
	@echo "  install        - Install all dependencies"
	@echo "  install-test   - Install test dependencies"
	@echo "  consolidate    - Consolidate and organize test/example files"
	@echo ""
	@echo "Testing:"
	@echo "  test           - Run all tests"
	@echo "  test-unit      - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-e2e       - Run end-to-end tests only"
	@echo "  test-coverage  - Run tests with coverage report"
	@echo "  test-fast      - Run fast tests (no external APIs)"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint           - Run all linters (flake8, mypy, bandit)"
	@echo "  format         - Format code (black, isort)"
	@echo "  format-check   - Check code formatting without changes"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build   - Build the container image  (IMAGE_NAME, IMAGE_TAG, REGISTRY)"
	@echo "  docker-push    - Push the image to a registry"
	@echo "  docker-run     - Run the container locally   (pass extra args via ARGS=)"
	@echo "  docker-clean   - Remove the local image"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean          - Clean up temporary files and caches"
	@echo "  clean-test     - Clean up test artifacts"

# Setup and Installation
setup:
	@echo "🚀 Setting up AI Research Agent development environment..."
	$(MAKE) install
	$(MAKE) consolidate
	@echo "✅ Setup complete!"

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	pip install -r requirements-test.txt

install-test:
	@echo "📦 Installing test dependencies..."
	pip install -r requirements-test.txt


# Testing
test: test-unit test-integration
	@echo "✅ All tests completed!"

test-unit:
	@echo "🧪 Running unit tests..."
	pytest tests/unit/ -v --no-cov

test-integration:
	@echo "🔗 Running integration tests..."
	pytest tests/integration/ -v -m "not requires_api" --no-cov

test-e2e:
	@echo "🎯 Running end-to-end tests..."
	pytest tests/e2e/ -v

test-all:
	@echo "🧪 Running all tests including those requiring API keys..."
	pytest tests/ -v

test-coverage:
	@echo "📊 Running tests with coverage..."
	pytest --cov=agent --cov-report=html --cov-report=term-missing tests/

test-fast:
	@echo "⚡ Running fast tests (no external APIs)..."
	pytest tests/ -v -m "not requires_api and not slow"

test-requires-api:
	@echo "🌐 Running tests that require API keys..."
	pytest tests/ -v -m "requires_api"

test-slow:
	@echo "🐌 Running slow tests..."
	pytest tests/ -v -m "slow"

# Code Quality
lint:
	@echo "🔍 Running linters..."
	flake8 agent/ tests/ examples/ --max-line-length=120 --extend-ignore=E203,W503,F401,F841,E402
	mypy agent/ --ignore-missing-imports
	bandit -r agent/ -f json -o bandit-report.json || true

format:
	@echo "🎨 Formatting code..."
	black agent/ tests/ examples/ --line-length=120
	isort agent/ tests/ examples/ --profile=black --line-length=120

format-check:
	@echo "🎨 Checking code formatting..."
	black --check agent/ tests/ examples/ --line-length=120
	isort --check-only agent/ tests/ examples/ --profile=black --line-length=120

# Development helpers
run-example:
	@echo "🏃 Running basic example..."
	python examples/basic_usage.py

run-multi-provider-example:
	@echo "🏃 Running multi-provider example..."
	python examples/multi_provider_setup.py

run-node-config-example:
	@echo "🏃 Running node configuration example..."
	python examples/node_configuration.py

# Cleanup
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	find . -name "*~" -delete 2>/dev/null || true

clean-test:
	@echo "🧹 Cleaning test artifacts..."
	rm -rf htmlcov/ .coverage .pytest_cache/
	find tests/ -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Documentation
docs-serve:
	@echo "📚 Starting documentation server..."
	@echo "View documentation at: http://localhost:8000"
	python -m http.server 8000 --directory docs/

# Continuous Integration simulation
ci:
	@echo "🚀 Running CI pipeline simulation..."
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) test-fast
	$(MAKE) test-coverage
	@echo "✅ CI pipeline completed!"

# Pre-commit setup
pre-commit-install:
	@echo "🔗 Installing pre-commit hooks..."
	pre-commit install

pre-commit-run:
	@echo "🔗 Running pre-commit hooks..."
	pre-commit run --all-files

# Environment management
env-example:
	@echo "📝 Creating .env from template..."
	cp .env.template .env
	@echo "⚠️  Please edit .env and add your API keys"

env-test:
	@echo "📝 Creating test environment..."
	cp .env.test .env.test.local
	@echo "⚠️  Please edit .env.test.local and add test API keys"

# Project status and information
status:
	@echo "📊 Project Status:"
	@echo ""
	@echo "Python version: $$(python --version)"
	@echo "Pip version: $$(pip --version)"
	@echo ""
	@echo "Dependencies:"
	@pip freeze | grep -E "(langchain|openai|anthropic|pytest)" || echo "No key dependencies found"
	@echo ""
	@echo "Test files:"
	@find tests/ -name "*.py" | wc -l | xargs echo "  Python test files:"
	@echo ""
	@echo "Example files:"
	@find examples/ -name "*.py" 2>/dev/null | wc -l | xargs echo "  Python example files:" || echo "  Example files: 0"

# Quick development commands
dev: format lint test-fast
	@echo "✅ Development checks completed!"

full-check: format lint test-coverage
	@echo "✅ Full quality check completed!"

# Docker
docker-build:
	@echo "Building Docker image $(_FULL_IMAGE)..."
	docker build -t $(_FULL_IMAGE) .

docker-push:
	@echo "Pushing Docker image $(_FULL_IMAGE)..."
	docker push $(_FULL_IMAGE)

docker-run:
	@echo "Running Docker container $(_FULL_IMAGE)..."
	docker run --rm --env-file .env $(_FULL_IMAGE) $(ARGS)

docker-clean:
	@echo "Removing Docker image $(_FULL_IMAGE)..."
	docker rmi $(_FULL_IMAGE) || true
