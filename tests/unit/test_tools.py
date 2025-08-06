#!/usr/bin/env python3
"""
Tools module unit tests
"""

import pytest

"""Project tools tests"""


def test_project_tools_initialization(project_tools):
    """Test project tools initialization"""
    assert project_tools is not None


def test_project_tools_availability(project_tools):
    """Test project tools availability"""
    expected_tools = [
        "get_projects",
        "get_project",
        "create_project",
        "delete_project",
        "get_project_tasks",
    ]

    for tool_name in expected_tools:
        assert tool_name in project_tools, f"Missing project tool: {tool_name}"
        assert callable(project_tools[tool_name]), f"Tool {tool_name} is not callable"


def test_get_projects_function(project_tools):
    """Test get projects function"""
    assert "get_projects" in project_tools
    assert callable(project_tools["get_projects"])


def test_get_project_function(project_tools):
    """Test get single project function"""
    assert "get_project" in project_tools
    assert callable(project_tools["get_project"])


def test_create_project_function(project_tools):
    """Test create project function"""
    assert "create_project" in project_tools
    assert callable(project_tools["create_project"])


def test_delete_project_function(project_tools):
    """Test delete project function"""
    assert "delete_project" in project_tools
    assert callable(project_tools["delete_project"])


@pytest.mark.unit
class TestTaskTools:
    """Task tools test"""

    def test_task_tools_initialization(self, task_tools):
        """Test task tools initialization"""
        assert task_tools is not None
        assert isinstance(task_tools, dict)
        assert len(task_tools) > 0

    def test_task_tools_availability(self, task_tools):
        """Test task tools availability"""
        required_tools = [
            "get_tasks",
            "create_task",
            "update_task",
            "delete_task",
            "complete_task",
            "search_tasks",
            "get_tasks_by_priority",
            "get_tasks_due_today",
            "get_overdue_tasks",
        ]

        for tool_name in required_tools:
            assert tool_name in task_tools, f"Missing task tool: {tool_name}"
            assert callable(task_tools[tool_name]), f"Tool {tool_name} is not callable"

    def test_get_tasks_function(self, task_tools):
        """Test get tasks function"""
        get_tasks_func = task_tools["get_tasks"]
        assert callable(get_tasks_func)

    def test_create_task_function(self, task_tools):
        """Test create task function"""
        create_task_func = task_tools["create_task"]
        assert callable(create_task_func)

    def test_update_task_function(self, task_tools):
        """Test update task function"""
        update_task_func = task_tools["update_task"]
        assert callable(update_task_func)

    def test_delete_task_function(self, task_tools):
        """Test delete task function"""
        delete_task_func = task_tools["delete_task"]
        assert callable(delete_task_func)

    def test_complete_task_function(self, task_tools):
        """Test complete task function"""
        complete_task_func = task_tools["complete_task"]
        assert callable(complete_task_func)

    def test_search_tasks_function(self, task_tools):
        """Test search tasks function"""
        search_tasks_func = task_tools["search_tasks"]
        assert callable(search_tasks_func)

    def test_get_tasks_by_priority_function(self, task_tools):
        """Test get tasks by priority function"""
        priority_func = task_tools["get_tasks_by_priority"]
        assert callable(priority_func)

    def test_get_tasks_due_today_function(self, task_tools):
        """Test get tasks due today function"""
        due_today_func = task_tools["get_tasks_due_today"]
        assert callable(due_today_func)

    def test_get_overdue_tasks_function(self, task_tools):
        """Test get overdue tasks function"""
        overdue_func = task_tools["get_overdue_tasks"]
        assert callable(overdue_func)


@pytest.mark.unit
class TestToolsIntegration:
    """Tools integration test"""

    def test_all_tools_available(self, auth_tools, project_tools, task_tools):
        """Test all tools are available"""
        # Auth tools
        auth_tools_list = auth_tools.get_tools()
        assert len(auth_tools_list) >= 3

        # Project tools
        assert len(project_tools) >= 5  # 5 project functions

        # Task tools
        assert len(task_tools) >= 8  # 8 task functions

        # Verify all tool names are unique
        all_tool_names = []
        all_tool_names.extend([tool.name for tool in auth_tools_list])
        all_tool_names.extend(project_tools.keys())
        all_tool_names.extend(task_tools.keys())

        # Check for duplicate tool names
        assert len(all_tool_names) == len(set(all_tool_names))

    def test_tool_schema_validation(self, auth_tools):
        """Test tool schema validation"""
        auth_tools_list = auth_tools.get_tools()

        for tool in auth_tools_list:
            # Check required fields
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert hasattr(tool, "inputSchema")

            # Check field types
            assert isinstance(tool.name, str)
            assert isinstance(tool.description, str)
            assert isinstance(tool.inputSchema, dict)

            # Check input schema structure
            input_schema = tool.inputSchema
            assert "type" in input_schema
            assert input_schema["type"] == "object"
            assert "properties" in input_schema
