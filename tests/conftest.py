#!/usr/bin/env python3
"""
Pytest configuration file
Set up test environment and shared fixtures
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import modules needed for tests
from src.auth import TickTickAuth
from src.tools.auth import AuthTools
from src.tools import projects, tasks


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop fixture"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def auth_instance():
    """Authentication instance fixture"""
    return TickTickAuth()


@pytest.fixture
def auth_tools():
    """Authentication tools fixture"""
    return AuthTools()


@pytest.fixture
def test_credentials():
    """Test credentials fixture"""
    return {"username": "test_user@example.com", "password": "test_password"}


@pytest.fixture
def test_project_data():
    """Test project data fixture"""
    return {"name": "Test Project", "color": "blue", "view_mode": "list"}


@pytest.fixture
def test_task_data():
    """Test task data fixture"""
    return {
        "title": "Test Task",
        "content": "This is a test task",
        "priority": 3,
        "due_date": "2024-12-31",
    }


@pytest.fixture
def project_tools():
    """Project tools fixture - returns dictionary of project functions"""
    return {
        "get_projects": projects.get_projects,
        "get_project": projects.get_project,
        "create_project": projects.create_project,
        "delete_project": projects.delete_project,
        "get_project_tasks": projects.get_project_tasks,
    }


@pytest.fixture
def task_tools():
    """Task tools fixture - returns dictionary of task functions"""
    return {
        "get_tasks": tasks.get_tasks,
        "create_task": tasks.create_task,
        "update_task": tasks.update_task,
        "delete_task": tasks.delete_task,
        "complete_task": tasks.complete_task,
        "search_tasks": tasks.search_tasks,
        "get_tasks_by_priority": tasks.get_tasks_by_priority,
        "get_tasks_due_today": tasks.get_tasks_due_today,
        "get_overdue_tasks": tasks.get_overdue_tasks,
    }


# Test markers
def pytest_configure(config):
    """Configure test markers"""
    config.addinivalue_line("markers", "unit: Unit test marker")
    config.addinivalue_line("markers", "integration: Integration test marker")
    config.addinivalue_line("markers", "e2e: End-to-end test marker")
    config.addinivalue_line("markers", "slow: Slow test marker")
    config.addinivalue_line("markers", "auth: Authentication-related test marker")
    config.addinivalue_line("markers", "mcp: MCP-related test marker")
    config.addinivalue_line("markers", "performance: Performance test marker")
