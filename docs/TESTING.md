# Testing Guide

## Overview

This document provides comprehensive guidance for testing the AI Research Agent. The testing infrastructure is built around pytest with support for unit, integration, and end-to-end testing, featuring a professional development workflow with code quality enforcement.

## 📊 Current Test Status

**Test Results: 58/59 tests passing (98.3% success rate)**
- ✅ **Unit Tests**: 40/40 passing (100%)
- ✅ **Integration Tests**: 13/13 passing (100%)
- ✅ **E2E Tests**: 6/7 passing (85.7%)

## 🏗️ Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests (40 tests)
│   ├── test_config.py       # Configuration management tests
│   ├── test_state.py        # State management tests
│   ├── test_llm_client.py   # LLM client tests
│   ├── test_setup.py        # Setup and validation tests
│   ├── test_node_config.py  # Node configuration tests
│   ├── test_restart_logic.py # Restart logic tests
│   └── test_logging.py      # Logging system tests
├── integration/             # Integration tests (13 tests)
│   ├── test_workflow_integration.py # Node-to-node integration
│   ├── test_multi_provider.py      # Multi-provider LLM tests
│   └── test_mcp_integration.py     # MCP tool integration
├── e2e/                     # End-to-end tests (7 tests)
│   └── test_e2e_workflow.py # Complete workflow tests
└── fixtures/                # Test fixtures
    └── __init__.py
```

## 🚀 Quick Start

### Installation
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Install pre-commit hooks
pre-commit install
```

### Running Tests
```bash
# Run all tests
make test

# Run specific test categories
make test-unit           # Unit tests only
make test-integration    # Integration tests only
make test-e2e           # End-to-end tests only

# Run with coverage
make test-coverage

# Run in parallel
make test-parallel
```

### Alternative Commands
```bash
# Using pytest directly
python -m pytest tests/unit/              # Unit tests
python -m pytest tests/integration/       # Integration tests
python -m pytest tests/e2e/              # E2E tests
python -m pytest --cov=agent --cov-report=html  # With coverage
```

## 🔧 Development Workflow

### Pre-commit Hooks
The repository uses pre-commit hooks to ensure code quality:

```bash
# Hooks automatically run on commit
git commit -m "Your changes"

# Run hooks manually
pre-commit run --all-files

# Individual hooks
pre-commit run black --all-files
pre-commit run flake8 --all-files
pre-commit run isort --all-files
```

**Active Hooks:**
- **Code formatting**: black (120 char line length)
- **Import sorting**: isort (black profile)
- **Linting**: flake8 (with custom ignore rules)
- **File checks**: trailing whitespace, end-of-file, YAML/TOML syntax
- **Security**: Built-in checks for debug statements, large files
- **JSON formatting**: prettier (excludes proposals/)

### Code Quality Tools
```bash
# Format code
make format              # Run black and isort

# Lint code
make lint               # Run flake8, mypy, bandit

# Full quality check
make ci-check           # Simulate CI environment
```

## 📝 Test Categories & Markers

### Test Markers
Use pytest markers to categorize and run specific tests:

```python
@pytest.mark.unit
def test_config_loading():
    pass

@pytest.mark.integration
def test_workflow_integration():
    pass

@pytest.mark.e2e
def test_complete_workflow():
    pass

@pytest.mark.slow
def test_long_running():
    pass

@pytest.mark.requires_api
def test_with_real_api():
    pass
```

### Running by Markers
```bash
# Run only unit tests
pytest -m unit

# Run only tests that don't require API keys
pytest -m "not requires_api"

# Run integration and e2e tests
pytest -m "integration or e2e"
```

## 🧪 Test Development

### Writing Unit Tests
```python
# tests/unit/test_example.py
import pytest
from unittest.mock import Mock, patch
from agent.config import Config

class TestExample:
    def test_basic_functionality(self, mock_config):
        """Test basic functionality with mocked dependencies."""
        # Use fixtures from conftest.py
        assert mock_config.default_llm_provider == "openai"

    @patch('agent.llm_client.OpenAI')
    def test_with_mock(self, mock_openai):
        """Test with patched external dependencies."""
        mock_openai.return_value.complete.return_value = "test response"
        # Test code here
```

### Writing Integration Tests
```python
# tests/integration/test_example.py
import pytest
from unittest.mock import patch, Mock

class TestIntegration:
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_component_integration(self):
        """Test integration between components."""
        # Test component interactions
        pass
```

### Writing E2E Tests
```python
# tests/e2e/test_example.py
import pytest
from unittest.mock import AsyncMock, patch

class TestE2E:
    @pytest.mark.asyncio
    @patch('agent.nodes.plan.MCPClient')
    async def test_workflow(self, mock_mcp):
        """Test complete workflow end-to-end."""
        # Configure mocks
        mock_mcp.return_value.get_available_tool_names.return_value = ["search"]

        # Test complete workflow
        pass
```

## 🔍 Test Configuration

### Environment Variables for Testing
```bash
# Required for most tests
export OPENAI_API_KEY="test-key"

# Optional for extended testing
export ANTHROPIC_API_KEY="test-key"
export GOOGLE_API_KEY="test-key"
export TAVILY_API_KEY="test-key"
export GITHUB_TOKEN="test-token"
```

### Test Environment Files
- `.env.test` - Test-specific environment variables
- `conftest.py` - Shared fixtures and test configuration
- `requirements-test.txt` - Test dependencies

### Coverage Configuration
Coverage is configured in `pyproject.toml`:
- **Minimum coverage**: 80%
- **Source directories**: `agent/`
- **Excluded**: `tests/`, `__pycache__/`, `venv/`
- **Reports**: Terminal + HTML (`htmlcov/`)

## 🐛 Debugging Tests

### Common Issues & Solutions

1. **Import Errors**
   ```bash
   # Ensure proper Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"

   # Or use pytest's discovery
   python -m pytest tests/
   ```

2. **Mock Configuration**
   ```python
   # Use proper mock paths
   @patch('agent.nodes.plan.MCPClient')  # Where it's used
   # Not: @patch('agent.tools.mcp_client.MCPClient')  # Where it's defined
   ```

3. **Async Test Issues**
   ```python
   # Ensure async tests are marked
   @pytest.mark.asyncio
   async def test_async_function():
       result = await async_function()
       assert result is not None
   ```

### Verbose Testing
```bash
# Detailed test output
pytest -v --tb=long

# Show all output
pytest -s

# Debug specific test
pytest tests/unit/test_config.py::test_specific_function -v -s
```

## 📈 Coverage Analysis

### Generating Coverage Reports
```bash
# HTML report (most detailed)
make test-coverage
open htmlcov/index.html

# Terminal report
pytest --cov=agent --cov-report=term-missing

# XML report (for CI)
pytest --cov=agent --cov-report=xml
```

### Coverage Targets
- **Overall**: 80% minimum
- **Critical modules**: 90%+ recommended
  - `agent/config.py`
  - `agent/state.py`
  - `agent/llm_client.py`
  - `agent/graph.py`

## 🔄 Continuous Integration

### GitHub Actions Ready
The testing infrastructure is designed for CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Install dependencies
  run: |
    pip install -r requirements.txt
    pip install -r requirements-test.txt

- name: Run tests
  run: make ci-check

- name: Upload coverage
  uses: codecov/codecov-action@v1
```

### CI Commands
```bash
# Full CI simulation
make ci-check

# Individual CI steps
make install-test-deps
make test-coverage
make lint
make format-check
```

## 🛠️ Makefile Commands

The project includes 20+ Makefile commands for development:

### Testing
- `make test` - Run all tests
- `make test-unit` - Unit tests only
- `make test-integration` - Integration tests only
- `make test-e2e` - End-to-end tests only
- `make test-coverage` - Tests with coverage report
- `make test-parallel` - Parallel test execution

### Code Quality
- `make format` - Format code (black + isort)
- `make format-check` - Check formatting without changes
- `make lint` - Run all linters (flake8, mypy, bandit)
- `make security` - Security scan with bandit

### Development
- `make install-dev` - Install development dependencies
- `make install-test-deps` - Install test dependencies
- `make clean` - Clean build artifacts
- `make ci-check` - Full CI simulation

## 📚 Additional Resources

### Documentation
- `docs/ARCHITECTURE_OVERVIEW.md` - System architecture
- `docs/CONFIGURATION_GUIDE.md` - Configuration details
- `docs/MCP_INTEGRATION_GUIDE.md` - MCP tool integration
- `examples/README.md` - Example usage patterns

### Tools & Dependencies
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Coverage reporting
- **pytest-mock** - Enhanced mocking
- **pytest-xdist** - Parallel execution
- **black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking
- **bandit** - Security scanning
- **pre-commit** - Git hooks

## 🎯 Best Practices

### Test Writing
1. **Use descriptive test names** that explain what is being tested
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Mock external dependencies** to ensure test isolation
4. **Use fixtures** for common test setup
5. **Test both success and failure cases**

### Code Organization
1. **One test class per module** being tested
2. **Group related tests** in the same class
3. **Use meaningful assertions** with clear error messages
4. **Keep tests focused** - one concept per test

### Performance
1. **Use pytest-xdist** for parallel execution
2. **Mock expensive operations** (API calls, file I/O)
3. **Use appropriate test markers** to skip slow tests when needed
4. **Profile test execution** to identify bottlenecks

This comprehensive testing infrastructure ensures high code quality, developer productivity, and maintainable test suites for the AI Research Agent project.
