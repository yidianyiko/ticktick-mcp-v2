# TickTick MCP Test Suite

This comprehensive test suite validates all MCP tools, parameter handling, authentication, and real-world usage scenarios for the TickTick MCP v2 server.

## Features

### 🔧 Environment Setup
- Reads environment variables from `.env` file
- Validates TICKTICK_USERNAME and TICKTICK_PASSWORD
- Automatic authentication for integration tests

### 🧪 Test Categories

#### 1. **Environment Setup Tests**
- Validates environment variable availability
- Ensures proper configuration

#### 2. **Authentication Tests**
- Login with environment credentials
- Invalid credential handling
- Authentication status checking
- Logout functionality

#### 3. **Project Management Tests**
- Get all projects
- Create new projects
- Get project details
- Get project tasks
- Error handling for invalid project IDs

#### 4. **Task Management Tests**
- Get all tasks (with/without completed)
- Create tasks (basic and with all parameters)
- Update task details
- Delete tasks
- Complete tasks
- Search tasks
- Get tasks by priority
- Get tasks due today
- Get overdue tasks

#### 5. **MCP Parameter Handling Tests**
- String to integer conversion (priority parameters)
- Invalid parameter validation
- Boolean return value handling
- Edge case handling

#### 6. **Real-World Integration Tests**
- Complete CRUD workflows
- Priority-based task management
- Project workflow testing
- XML parameter simulation

#### 7. **Error Handling Tests**
- Operations without authentication
- Invalid parameter handling
- Graceful error responses

#### 8. **Utilities & Helpers**
- Test environment file creation
- Import validation
- Test configuration

## Setup Instructions

### 1. Create Environment File

```bash
# Copy template and add your credentials
cp env.template .env

# Edit .env with your TickTick credentials
TICKTICK_USERNAME=your_username
TICKTICK_PASSWORD=your_password
```

### 2. Install Dependencies

Make sure you're in the virtual environment [[memory:3891968]]:

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install test dependencies
pip install pytest pytest-asyncio python-dotenv
```

### 3. Run Tests

```bash
# Run all tests
python tests/test_mcp_parameter_handling.py

# Run with pytest for more control
pytest tests/test_mcp_parameter_handling.py -v

# Run only unit tests (no authentication required)
pytest tests/test_mcp_parameter_handling.py -v -m "not integration"

# Run only integration tests (requires credentials)
pytest tests/test_mcp_parameter_handling.py -v -m "integration"

# Run specific test class
pytest tests/test_mcp_parameter_handling.py::TestAuthenticationTools -v
```

## Test Markers

The test suite uses pytest markers to categorize tests:

- `integration` - Tests requiring real TickTick credentials
- `auth` - Tests requiring authentication

## Environment Variables

Required for integration tests:

```bash
TICKTICK_USERNAME=your_ticktick_username
TICKTICK_PASSWORD=your_ticktick_password
```

Optional:

```bash
TICKTICK_AUTHENTICATED=false  # Will be set automatically after login
```

## Test Output

### Successful Run Example

```
================================== test session starts ==================================
platform linux -- Python 3.11.0, pytest-7.4.0, pluggy-1.3.0 -- 
collected 25 items

tests/test_mcp_parameter_handling.py::TestEnvironmentSetup::test_environment_variables_available PASSED
tests/test_mcp_parameter_handling.py::TestAuthenticationTools::test_auth_status_before_login PASSED
tests/test_mcp_parameter_handling.py::TestAuthenticationTools::test_auth_login_with_env_credentials PASSED
tests/test_mcp_parameter_handling.py::TestProjectManagementTools::test_get_projects PASSED
tests/test_mcp_parameter_handling.py::TestTaskManagementTools::test_get_tasks PASSED
...

================================== 25 passed in 45.23s ==================================
```

### Skipped Tests (No Credentials)

If environment variables are not set, integration tests will be skipped:

```
SKIPPED [1] Environment variables TICKTICK_USERNAME and TICKTICK_PASSWORD not set
```

## Test Structure

### Mock Tests
- Test parameter conversion logic
- Test error handling
- Test return value formatting
- No actual API calls

### Integration Tests  
- Test real API interactions
- Require valid TickTick credentials
- Test complete workflows
- Validate actual responses

## Coverage Areas

✅ **All MCP Tools Tested**
- Authentication: `auth_login`, `auth_logout`, `auth_status`
- Projects: `get_projects`, `get_project`, `create_project`, `delete_project`, `get_project_tasks`
- Tasks: `get_tasks`, `create_task`, `update_task`, `delete_task`, `complete_task`
- Advanced: `search_tasks`, `get_tasks_by_priority`, `get_tasks_due_today`, `get_overdue_tasks`

✅ **Parameter Handling**
- String to integer conversion
- Invalid parameter validation
- Boolean return handling
- XML parameter simulation

✅ **Error Scenarios**
- Authentication failures
- Invalid credentials
- Missing parameters
- Network errors (graceful handling)

✅ **Real-World Workflows**
- Complete task lifecycle
- Priority management
- Project workflows
- Search functionality

## Troubleshooting

### Import Errors
```bash
# Make sure you're in the project root
cd /path/to/ticktick-mcp-v2

# Run tests from project root
python tests/test_mcp_parameter_handling.py
```

### Authentication Failures
```bash
# Verify credentials in .env file
cat .env

# Test authentication manually
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Username:', os.getenv('TICKTICK_USERNAME'))
print('Password length:', len(os.getenv('TICKTICK_PASSWORD', '')))
"
```

### Timeout Issues
```bash
# Run with increased timeout for slow connections
pytest tests/test_mcp_parameter_handling.py -v --timeout=60
```

## Contributing

When adding new tests:

1. **Follow the naming convention**: `test_feature_description`
2. **Add appropriate markers**: `@pytest.mark.integration` for tests requiring credentials
3. **Include docstrings**: Describe what the test validates
4. **Handle errors gracefully**: Use `pytest.skip()` for missing requirements
5. **Clean up resources**: Ensure tests don't leave test data in TickTick

## Example Usage

```python
# Run a quick smoke test
from tests.test_mcp_parameter_handling import TestEnvironmentSetup
test = TestEnvironmentSetup()
test.test_environment_variables_available()

# Manual authentication test
import asyncio
from server import auth_login, auth_status

async def quick_auth_test():
    status = await auth_status()
    print(f"Status: {status}")
    
    # Login if needed
    result = await auth_login("username", "password")
    print(f"Login: {result}")

asyncio.run(quick_auth_test())
```

This test suite provides comprehensive validation of the TickTick MCP v2 server, ensuring reliability and proper functionality across all tools and scenarios.
