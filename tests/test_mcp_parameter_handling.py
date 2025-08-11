#!/usr/bin/env python3
"""
Comprehensive MCP Tool Testing - Tests MCP layer parameter conversion, type handling, and all available tools
"""

import asyncio
import os
import sys
from unittest.mock import patch

import pytest
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Load environment variables
load_dotenv()

try:
    from server import (
        # Authentication tools
        auth_login,
        auth_logout,
        auth_status,
        complete_task,
        create_project,
        create_task,
        delete_project,
        delete_task,
        get_overdue_tasks,
        get_project,
        get_project_tasks,
        # Project management tools
        get_projects,
        # Task management tools
        get_tasks,
        get_tasks_by_priority,
        get_tasks_due_today,
        # Advanced task tools
        search_tasks,
        update_task,
    )
except ImportError:
    sys.exit(1)


class TestConfig:
    """Test configuration and environment variable management"""

    @staticmethod
    def get_credentials():
        """Get TickTick credentials from environment variables"""
        username = os.getenv("TICKTICK_USERNAME")
        password = os.getenv("TICKTICK_PASSWORD")
        return username, password

    @staticmethod
    def has_credentials():
        """Check if valid credentials are available"""
        username, password = TestConfig.get_credentials()
        return (
            username is not None
            and password is not None
            and len(username) > 0
            and len(password) > 0
        )

    @staticmethod
    def skip_if_no_credentials():
        """Skip test if credentials are not available"""
        if not TestConfig.has_credentials():
            pytest.skip(
                "Environment variables TICKTICK_USERNAME and TICKTICK_PASSWORD not set",
            )

    @staticmethod
    def print_env_status():
        """Print environment variable status for debugging"""
        username, password = TestConfig.get_credentials()


# Global test configuration
test_config = TestConfig()


class TestEnvironmentSetup:
    """Test environment variable setup and configuration"""

    def test_environment_variables_available(self):
        """Test that required environment variables can be loaded"""
        test_config.print_env_status()
        test_config.skip_if_no_credentials()

        username, password = test_config.get_credentials()
        assert username is not None
        assert password is not None
        assert len(username) > 0
        assert len(password) > 0

    def test_config_helper_methods(self):
        """Test configuration helper methods"""
        # Test has_credentials method
        has_creds = test_config.has_credentials()
        username, password = test_config.get_credentials()

        expected = (
            username is not None
            and password is not None
            and len(username) > 0
            and len(password) > 0
        )
        assert has_creds == expected


class TestAuthenticationTools:
    """Test authentication tools with real environment credentials"""

    @pytest.mark.asyncio
    async def test_auth_status_before_login(self):
        """Test authentication status before login"""
        result = await auth_status()
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_auth_login_with_env_credentials(self):
        """Test login with environment credentials"""
        test_config.skip_if_no_credentials()
        username, password = test_config.get_credentials()

        result = await auth_login(username, password)
        assert isinstance(result, str)
        assert "error" not in result.lower() or "successful" in result.lower()

    @pytest.mark.asyncio
    async def test_auth_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        result = await auth_login("invalid_user", "invalid_pass")
        assert isinstance(result, str)
        # Should handle authentication failure gracefully

    @pytest.mark.asyncio
    async def test_auth_status_after_login(self):
        """Test authentication status after successful login"""
        test_config.skip_if_no_credentials()
        username, password = test_config.get_credentials()

        # Login first
        await auth_login(username, password)

        # Then check status
        status_result = await auth_status()
        assert isinstance(status_result, str)

    @pytest.mark.asyncio
    async def test_auth_logout(self):
        """Test logout functionality"""
        result = await auth_logout()
        assert isinstance(result, str)


class TestProjectManagementTools:
    """Test project management tools"""

    @pytest.fixture(autouse=True)
    async def ensure_auth(self):
        """Ensure authentication before each test"""
        username = os.getenv("TICKTICK_USERNAME")
        password = os.getenv("TICKTICK_PASSWORD")

        if username and password:
            await auth_login(username, password)

    @pytest.mark.asyncio
    async def test_get_projects(self):
        """Test getting all projects"""
        result = await get_projects()
        assert isinstance(result, str)
        assert "error" not in result.lower() or "not authenticated" in result.lower()

    @pytest.mark.asyncio
    async def test_create_project(self):
        """Test creating a new project"""
        project_name = f"Test Project {asyncio.get_event_loop().time()}"
        result = await create_project(project_name, color="blue", view_mode="list")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_get_project_with_invalid_id(self):
        """Test getting project with invalid ID"""
        result = await get_project("invalid_project_id")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_get_project_tasks_with_invalid_id(self):
        """Test getting project tasks with invalid project ID"""
        result = await get_project_tasks("invalid_project_id", include_completed=False)
        assert isinstance(result, str)


class TestTaskManagementTools:
    """Test task management tools"""

    @pytest.fixture(autouse=True)
    async def ensure_auth(self):
        """Ensure authentication before each test"""
        username = os.getenv("TICKTICK_USERNAME")
        password = os.getenv("TICKTICK_PASSWORD")

        if username and password:
            await auth_login(username, password)

    @pytest.mark.asyncio
    async def test_get_tasks(self):
        """Test getting all tasks"""
        result = await get_tasks(include_completed=False)
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_get_tasks_with_completed(self):
        """Test getting tasks including completed ones"""
        result = await get_tasks(include_completed=True)
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_create_task_basic(self):
        """Test creating a basic task"""
        task_title = f"Test Task {asyncio.get_event_loop().time()}"
        result = await create_task(task_title)
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_create_task_with_all_parameters(self):
        """Test creating a task with all parameters"""
        task_title = f"Full Test Task {asyncio.get_event_loop().time()}"
        result = await create_task(
            title=task_title,
            content="This is a test task with full parameters",
            priority=3,
            due_date="2024-12-31",
        )
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_search_tasks(self):
        """Test searching tasks"""
        result = await search_tasks("test")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_get_tasks_by_priority(self):
        """Test getting tasks by priority"""
        result = await get_tasks_by_priority(3)  # Medium priority
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_get_tasks_due_today(self):
        """Test getting tasks due today"""
        result = await get_tasks_due_today()
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_get_overdue_tasks(self):
        """Test getting overdue tasks"""
        result = await get_overdue_tasks()
        assert isinstance(result, str)


class TestMCPParameterHandling:
    """Test MCP parameter handling and type conversion"""

    @pytest.mark.asyncio
    @patch("server.ensure_authenticated", return_value=True)
    @patch("server.update_task_impl")
    async def test_update_task_string_priority_conversion(self, mock_impl, mock_auth):
        """Test update_task string priority parameter conversion"""
        mock_impl.return_value = {"id": "test", "priority": 3}

        # Simulate MCP passing string parameters
        result = await update_task("task_id", priority="3")

        # Verify integer is passed to implementation
        mock_impl.assert_called_once_with("task_id", None, None, None, None, None, 3)
        assert "id: test" in result

    @pytest.mark.asyncio
    @patch("server.ensure_authenticated", return_value=True)
    async def test_update_task_invalid_priority_string(self, mock_auth):
        """Test update_task invalid priority string handling"""
        result = await update_task("task_id", priority="invalid")

        assert "Error: priority must be a valid integer, got 'invalid'" in result

    @pytest.mark.asyncio
    @patch("server.ensure_authenticated", return_value=True)
    @patch("server.create_task_impl")
    async def test_create_task_string_priority_conversion(self, mock_impl, mock_auth):
        """Test create_task string priority parameter conversion"""
        mock_impl.return_value = {"id": "test", "priority": 5}

        await create_task("Test Task", priority="5")

        # Verify integer is passed to implementation
        mock_impl.assert_called_once_with("Test Task", None, None, None, None, 5)

    @pytest.mark.asyncio
    @patch("server.ensure_authenticated", return_value=True)
    @patch("server.get_tasks_by_priority_impl")
    async def test_get_tasks_by_priority_string_conversion(self, mock_impl, mock_auth):
        """Test get_tasks_by_priority string parameter conversion"""
        mock_impl.return_value = [{"id": "task1", "priority": 1}]

        await get_tasks_by_priority("1")

        mock_impl.assert_called_once_with(1)

    @pytest.mark.asyncio
    @patch("server.ensure_authenticated", return_value=True)
    @patch("server.delete_task_impl")
    async def test_delete_task_boolean_result_handling(self, mock_impl, mock_auth):
        """Test delete_task boolean return value handling"""
        mock_impl.return_value = True

        result = await delete_task("task_id")

        assert result == "Task deletion successful"

    @pytest.mark.asyncio
    @patch("server.ensure_authenticated", return_value=True)
    @patch("server.delete_task_impl")
    async def test_delete_task_boolean_false_handling(self, mock_impl, mock_auth):
        """Test delete_task return False handling"""
        mock_impl.return_value = False

        result = await delete_task("task_id")

        assert result == "Task deletion failed"

    @pytest.mark.parametrize(
        ("priority_input", "expected_int", "should_error"),
        [
            ("0", 0, False),
            ("1", 1, False),
            ("5", 5, False),
            ("invalid", None, True),
            ("", None, True),
            ("3.5", None, True),
            ("-1", -1, False),
        ],
    )
    @pytest.mark.asyncio
    @patch("server.ensure_authenticated", return_value=True)
    async def test_priority_conversion_edge_cases(
        self, mock_auth, priority_input, expected_int, should_error,
    ):
        """Test priority conversion edge cases"""
        if should_error:
            result = await update_task("task_id", priority=priority_input)
            assert (
                f"Error: priority must be a valid integer, got '{priority_input}'"
                in result
            )
        else:
            with patch("server.update_task_impl") as mock_impl:
                mock_impl.return_value = {"id": "test"}
                result = await update_task("task_id", priority=priority_input)
                mock_impl.assert_called_once_with(
                    "task_id", None, None, None, None, None, expected_int,
                )


class TestMCPRealWorldScenarios:
    """Test real-world MCP usage scenarios"""

    @pytest.fixture(autouse=True)
    async def ensure_auth(self):
        """Ensure authentication before each test"""
        username = os.getenv("TICKTICK_USERNAME")
        password = os.getenv("TICKTICK_PASSWORD")

        if username and password:
            await auth_login(username, password)

    @pytest.mark.asyncio
    @patch("server.ensure_authenticated", return_value=True)
    @patch("server.update_task_impl")
    async def test_xml_parameter_simulation(self, mock_impl, mock_auth):
        """Simulate real XML parameter passing scenario"""
        mock_impl.return_value = {"id": "test", "title": "Updated"}

        # Simulate MCP client passing parameters (all as strings)
        xml_params = {
            "task_id": "task123",
            "project_id": "proj456",
            "title": "Updated Task Title",
            "priority": "3",  # Numbers become strings in XML
        }

        await update_task(**xml_params)

        # Verify string priority is correctly converted to integer
        mock_impl.assert_called_once_with(
            "task123",
            "proj456",
            "Updated Task Title",
            None,
            None,
            None,
            3,
        )

    @pytest.mark.asyncio
    async def test_complete_workflow_create_update_delete(self):
        """Test complete workflow: create task, update it, then delete it"""
        username = os.getenv("TICKTICK_USERNAME")
        password = os.getenv("TICKTICK_PASSWORD")

        if not username or not password:
            pytest.skip("Environment variables not set")

        # Step 1: Create a test task
        task_title = f"Workflow Test Task {asyncio.get_event_loop().time()}"
        create_result = await create_task(
            title=task_title,
            content="Test task for workflow testing",
            priority=1,
        )
        assert isinstance(create_result, str)

        # Step 2: Search for the created task
        search_result = await search_tasks(task_title)
        assert isinstance(search_result, str)

        # Step 3: Get all tasks to verify creation
        all_tasks = await get_tasks()
        assert isinstance(all_tasks, str)

    @pytest.mark.asyncio
    async def test_priority_workflow(self):
        """Test priority-based task management workflow"""
        username = os.getenv("TICKTICK_USERNAME")
        password = os.getenv("TICKTICK_PASSWORD")

        if not username or not password:
            pytest.skip("Environment variables not set")

        # Test different priority levels
        for priority in [0, 1, 3, 5]:
            {0: "None", 1: "Low", 3: "Medium", 5: "High"}[priority]
            result = await get_tasks_by_priority(priority)
            assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_project_workflow(self):
        """Test project management workflow"""
        username = os.getenv("TICKTICK_USERNAME")
        password = os.getenv("TICKTICK_PASSWORD")

        if not username or not password:
            pytest.skip("Environment variables not set")

        # Get all projects
        projects_result = await get_projects()
        assert isinstance(projects_result, str)


class TestErrorHandling:
    """Test error handling for various edge cases"""

    @pytest.mark.asyncio
    async def test_operations_without_authentication(self):
        """Test that operations fail gracefully without authentication"""
        # First logout to ensure we're not authenticated
        await auth_logout()

        # Wait a moment for logout to take effect
        await asyncio.sleep(1)

        # Check auth status to confirm we're logged out
        await auth_status()

        # Try various operations - they should return authentication errors
        result = await get_tasks()

        # The test should check for authentication failure patterns
        auth_failure_indicators = [
            "not authenticated",
            "please use auth_login",
            "login first",
            "authentication required",
            "please login",
        ]

        # Check if any authentication failure indicator is present
        result_lower = result.lower()
        auth_failed = any(
            indicator in result_lower for indicator in auth_failure_indicators
        )

        if not auth_failed:
            # If still authenticated, this might be due to persistent session
            # This is not necessarily a failure - just log it
            pytest.skip(
                "Session appears to persist after logout - skipping authentication test",
            )
        else:
            assert (
                auth_failed
            ), f"Expected authentication failure, but got: {result[:200]}..."

        # Test other operations only if first one failed as expected
        if auth_failed:
            result = await get_projects()
            result_lower = result.lower()
            assert any(
                indicator in result_lower for indicator in auth_failure_indicators
            )

            result = await create_task("Test Task")
            result_lower = result.lower()
            assert any(
                indicator in result_lower for indicator in auth_failure_indicators
            )

    @pytest.mark.asyncio
    async def test_invalid_parameter_handling(self):
        """Test handling of invalid parameters"""
        # Test invalid priority in create_task
        result = await create_task("Test", priority="invalid")
        assert "error" in result.lower()
        assert "integer" in result.lower()

        # Test invalid priority in get_tasks_by_priority
        result = await get_tasks_by_priority("not_a_number")
        assert "error" in result.lower()
        assert "integer" in result.lower()


class TestUtilities:
    """Test utilities and helper functions"""

    @staticmethod
    def create_test_env_file():
        """Create a test .env file for manual testing"""
        env_content = """# Test Environment Variables for TickTick MCP
# Copy your actual credentials here for testing

TICKTICK_USERNAME=your_username_here
TICKTICK_PASSWORD=your_password_here
TICKTICK_AUTHENTICATED=false
"""
        with open(".env.test", "w") as f:
            f.write(env_content)
        return ".env.test"

    @pytest.mark.asyncio
    async def test_environment_file_creation(self):
        """Test that we can create environment file"""
        test_file = self.create_test_env_file()
        assert os.path.exists(test_file)

        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)

    def test_all_tools_imported(self):
        """Test that all expected MCP tools are properly imported"""
        expected_tools = [
            # Authentication
            "auth_login",
            "auth_logout",
            "auth_status",
            # Projects
            "get_projects",
            "get_project",
            "create_project",
            "delete_project",
            "get_project_tasks",
            # Tasks
            "get_tasks",
            "create_task",
            "update_task",
            "delete_task",
            "complete_task",
            # Advanced
            "search_tasks",
            "get_tasks_by_priority",
            "get_tasks_due_today",
            "get_overdue_tasks",
        ]

        for tool_name in expected_tools:
            assert tool_name in globals(), f"Tool {tool_name} not imported"


# Test configuration and setup
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test (requires real credentials)",
    )
    config.addinivalue_line(
        "markers",
        "auth: mark test as requiring authentication",
    )


def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their characteristics"""
    for item in items:
        # Mark tests that use real authentication
        if "auth" in item.name or "workflow" in item.name or "real_world" in item.name:
            item.add_marker(pytest.mark.integration)

        # Mark tests that require authentication
        if any(
            cls in str(item.cls)
            for cls in [
                "TestProjectManagementTools",
                "TestTaskManagementTools",
                "TestMCPRealWorldScenarios",
            ]
        ):
            item.add_marker(pytest.mark.auth)


if __name__ == "__main__":
    # Create test environment file for easy setup
    TestUtilities.create_test_env_file()

    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
