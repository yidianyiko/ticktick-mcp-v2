# TickTick MCP v2 Test Documentation

## Test Architecture

This project adopts a layered test architecture to ensure code quality and functional reliability:

```
tests/
├── conftest.py              # Pytest configuration file
├── run_tests.py             # Test runner script
├── unit/                    # Unit tests
│   ├── test_auth.py        # Authentication module tests
│   └── test_tools.py       # Tools module tests
├── integration/             # Integration tests
│   └── test_mcp_server.py  # MCP server tests
├── e2e/                    # End-to-end tests
│   └── test_complete_workflow.py  # Complete workflow tests
└── utils/                  # Test utilities
```

## Test Types

### 1. Unit Tests
- **Location**: `tests/unit/`
- **Purpose**: Test individual module functionality
- **Characteristics**: Fast, independent, repeatable
- **Markers**: `@pytest.mark.unit`

### 2. Integration Tests
- **Location**: `tests/integration/`
- **Purpose**: Test interactions between modules
- **Characteristics**: Test component integration
- **Markers**: `@pytest.mark.integration`

### 3. End-to-End Tests (E2E Tests)
- **Location**: `tests/e2e/`
- **Purpose**: Test complete user workflows
- **Characteristics**: Simulate real usage scenarios
- **Markers**: `@pytest.mark.e2e`

## Running Tests

### Using Test Runner Script

```bash
# Run quick tests (recommended)
python tests/run_tests.py --type quick

# Run unit tests
python tests/run_tests.py --type unit

# Run integration tests
python tests/run_tests.py --type integration

# Run end-to-end tests
python tests/run_tests.py --type e2e

# Run all tests
python tests/run_tests.py --type all

# Run authentication-related tests
python tests/run_tests.py --type auth

# Run MCP-related tests
python tests/run_tests.py --type mcp
```

### Using pytest directly

```bash
# Run all tests
pytest tests/ -v

# Run unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run end-to-end tests
pytest tests/e2e/ -v

# Run tests with specific markers
pytest tests/ -m "unit"
pytest tests/ -m "integration"
pytest tests/ -m "e2e"
pytest tests/ -m "auth"
pytest tests/ -m "mcp"

# Skip slow tests
pytest tests/ -m "not slow"

# Generate coverage report
pytest tests/ --cov=src --cov-report=html
```

## Test Markers

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.e2e`: End-to-end tests
- `@pytest.mark.slow`: Slow tests
- `@pytest.mark.auth`: Authentication-related tests
- `@pytest.mark.mcp`: MCP-related tests

## Test Fixtures

The following fixtures are defined in `conftest.py`:

- `auth_instance`: TickTickAuth instance
- `auth_tools`: AuthTools instance
- `project_tools`: ProjectTools instance
- `task_tools`: TaskTools instance
- `test_credentials`: Test credentials
- `test_project_data`: Test project data
- `test_task_data`: Test task data

## Test Coverage

### Authentication Module
- ✅ TickTickAuth class tests
- ✅ AuthTools class tests
- ✅ Authentication flow tests
- ✅ Credential management tests

### Tools Module
- ✅ ProjectTools class tests
- ✅ TaskTools class tests
- ✅ Tool schema validation
- ✅ Tool availability tests

### MCP Server
- ✅ Server startup tests
- ✅ Tool availability tests
- ✅ Tool invocation tests
- ✅ Error handling tests

### End-to-End Workflows
- ✅ Complete workflow tests
- ✅ Tool interaction tests
- ✅ Error handling tests
- ✅ Server stability tests

## Test Best Practices

1. **Test Independence**: Each test should run independently without depending on other tests
2. **Test Repeatability**: Tests should be repeatable in any environment
3. **Test Readability**: Test names and descriptions should be clear and understandable
4. **Test Coverage**: Ensure critical functionality has test coverage
5. **Test Maintenance**: Regularly update tests to adapt to code changes

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the `src` directory is in the Python path
2. **Authentication Failures**: Check environment variables and authentication configuration
3. **Test Timeouts**: For slow tests, increase timeout duration
4. **Dependency Issues**: Ensure all dependencies are installed

### Debugging Tips

1. Use `-v` parameter for detailed output
2. Use `-s` parameter to show print output
3. Use `--tb=short` for brief error tracebacks
4. Use `--pdb` to enter debugger on failure

## Continuous Integration

Tests can be integrated into CI/CD workflows:

```yaml
# GitHub Actions example
- name: Run Tests
  run: |
    python tests/run_tests.py --type quick
    python tests/run_tests.py --type unit
    python tests/run_tests.py --type integration
```

## Test Reports

After running tests, the following reports are generated:

- **Console Output**: Real-time test results
- **Coverage Report**: HTML format code coverage report
- **Test Results**: Detailed test pass/fail information 