#!/usr/bin/env python3
"""
Adapter module comprehensive unit tests
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from adapters.client import TickTickAdapter


@pytest.mark.unit
class TestTickTickAdapter:
    """TickTick adapter comprehensive tests"""

    def test_adapter_initialization(self):
        """Test adapter initialization"""
        adapter = TickTickAdapter()
        assert adapter is not None
        assert hasattr(adapter, "auth")
        assert hasattr(adapter, "client")

    @patch("adapters.client.TickTickAuth")
    def test_ensure_client_success(self, mock_auth_class):
        """Test _ensure_client method success"""
        mock_auth = Mock()
        mock_auth.is_authenticated.return_value = True
        mock_client = Mock()
        mock_auth.get_client.return_value = mock_client
        mock_auth_class.return_value = mock_auth

        adapter = TickTickAdapter()
        result = adapter._ensure_client()

        assert result == mock_client
        mock_auth.is_authenticated.assert_called_once()
        mock_auth.get_client.assert_called_once()

    @patch("adapters.client.TickTickAuth")
    def test_ensure_client_not_authenticated(self, mock_auth_class):
        """Test _ensure_client when not authenticated"""
        mock_auth = Mock()
        mock_auth.is_authenticated.return_value = False
        mock_auth_class.return_value = mock_auth

        adapter = TickTickAdapter()
        result = adapter._ensure_client()

        assert result is None

    def test_get_user_timezone_success(self):
        """Test _get_user_timezone success"""
        mock_client = Mock()
        mock_client.time_zone = "Asia/Shanghai"

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter._get_user_timezone()
            assert result == "Asia/Shanghai"

    def test_get_user_timezone_no_timezone(self):
        """Test _get_user_timezone when client has no timezone"""
        mock_client = Mock()
        del mock_client.time_zone  # Remove the attribute

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter._get_user_timezone()
            assert result == ""

    def test_get_user_timezone_exception(self):
        """Test _get_user_timezone exception handling"""
        adapter = TickTickAdapter()
        with patch.object(
            adapter, "_ensure_client", side_effect=Exception("Test error"),
        ):
            result = adapter._get_user_timezone()
            assert result == ""


@pytest.mark.unit
class TestTickTickAdapterProjects:
    """Test project-related methods"""

    def test_get_projects_success(self):
        """Test get_projects success"""
        mock_client = Mock()
        mock_projects = [
            {"id": "proj1", "name": "Project 1"},
            {"id": "proj2", "name": "Project 2"},
        ]
        mock_client.state = {"projects": mock_projects}

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.get_projects()

        assert result == mock_projects
        assert len(result) == 2

    def test_get_projects_empty(self):
        """Test get_projects with empty state"""
        mock_client = Mock()
        mock_client.state = {}

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.get_projects()

        assert result == []

    def test_get_projects_exception(self):
        """Test get_projects exception handling"""
        adapter = TickTickAdapter()
        with patch.object(
            adapter, "_ensure_client", side_effect=Exception("Test error"),
        ):
            result = adapter.get_projects()

        assert result == []

    def test_get_project_success(self):
        """Test get_project success"""
        mock_client = Mock()
        mock_projects = [
            {"id": "proj1", "name": "Project 1"},
            {"id": "proj2", "name": "Project 2"},
        ]
        mock_client.state = {"projects": mock_projects}

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.get_project("proj1")

        assert result == {"id": "proj1", "name": "Project 1"}

    def test_get_project_not_found(self):
        """Test get_project when project not found"""
        mock_client = Mock()
        mock_client.state = {"projects": []}

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.get_project("nonexistent")

        assert result is None

    def test_get_project_exception(self):
        """Test get_project exception handling"""
        adapter = TickTickAdapter()
        with patch.object(
            adapter, "_ensure_client", side_effect=Exception("Test error"),
        ):
            result = adapter.get_project("proj1")

        assert result is None


@pytest.mark.unit
class TestTickTickAdapterTasks:
    """Test task-related methods"""

    def test_get_tasks_success(self):
        """Test get_tasks success"""
        mock_client = Mock()
        mock_tasks = [
            {"id": "task1", "title": "Task 1", "status": 0},
            {"id": "task2", "title": "Task 2", "status": 2},  # completed
        ]
        mock_client.state = {"tasks": mock_tasks}

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.get_tasks(include_completed=False)

        # Should filter out completed tasks (status=2)
        assert len(result) == 1
        assert result[0]["id"] == "task1"

    def test_get_tasks_include_completed(self):
        """Test get_tasks including completed tasks"""
        mock_client = Mock()
        mock_tasks = [
            {"id": "task1", "title": "Task 1", "status": 0},
            {"id": "task2", "title": "Task 2", "status": 2},  # completed
        ]
        mock_client.state = {"tasks": mock_tasks}

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.get_tasks(include_completed=True)

        assert len(result) == 2

    def test_create_task_success(self):
        """Test create_task success"""
        mock_client = Mock()
        mock_task = {"id": "new_task", "title": "New Task"}
        mock_client.task.builder.return_value = Mock()
        mock_client.task.create.return_value = mock_task

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.create_task("New Task", project_id="proj1")

        assert result == mock_task
        mock_client.task.builder.assert_called_once_with("New Task")
        mock_client.task.create.assert_called_once()

    def test_create_task_without_project(self):
        """Test create_task without project_id"""
        mock_client = Mock()
        mock_task = {"id": "new_task", "title": "New Task"}
        mock_local_task = Mock()
        mock_client.task.builder.return_value = mock_local_task
        mock_client.task.create.return_value = mock_task

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.create_task("New Task")

        assert result == mock_task
        # Verify projectId was not added to task_data
        mock_local_task.update.assert_called_once()
        call_args = mock_local_task.update.call_args[0][0]
        assert "projectId" not in call_args

    def test_update_task_success(self):
        """Test update_task success"""
        mock_client = Mock()
        mock_task = {"id": "task1", "title": "Updated Task"}
        mock_client.get_by_id.return_value = mock_task
        mock_client.task.update.return_value = mock_task

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.update_task("task1", title="Updated Task")

        assert result == mock_task
        mock_client.get_by_id.assert_called_once_with("task1")
        mock_client.task.update.assert_called_once()

    def test_update_task_not_found(self):
        """Test update_task when task not found"""
        mock_client = Mock()
        mock_client.get_by_id.return_value = None

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            with pytest.raises(Exception, match="Task task1 not found"):
                adapter.update_task("task1", title="Updated Task")

    def test_delete_task_with_project_id(self):
        """Test delete_task with project_id provided"""
        mock_client = Mock()
        mock_client.task.delete.return_value = True

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.delete_task("proj1", "task1")

        assert result is True
        mock_client.task.delete.assert_called_once_with("task1")
        # Should not call get_by_id when project_id is provided
        mock_client.get_by_id.assert_not_called()

    def test_delete_task_without_project_id(self):
        """Test delete_task without project_id"""
        mock_client = Mock()
        mock_task = {"id": "task1", "projectId": "proj1"}
        mock_client.get_by_id.return_value = mock_task
        mock_client.task.delete.return_value = True

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.delete_task("", "task1")

        assert result is True
        mock_client.get_by_id.assert_called_once_with("task1")
        mock_client.task.delete.assert_called_once_with("task1")

    def test_complete_task_success(self):
        """Test complete_task success"""
        mock_client = Mock()
        mock_task = {"id": "task1", "title": "Task 1", "status": 0}
        mock_client.get_by_id.return_value = mock_task
        mock_client.task.complete.return_value = mock_task

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.complete_task("task1")

        assert result is True
        mock_client.get_by_id.assert_called_once_with("task1")
        mock_client.task.complete.assert_called_once_with(mock_task)

    def test_complete_task_not_found(self):
        """Test complete_task when task not found"""
        mock_client = Mock()
        mock_client.get_by_id.return_value = None

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            with pytest.raises(Exception, match="Task task1 not found"):
                adapter.complete_task("task1")

    def test_complete_task_empty_dict(self):
        """Test complete_task when get_by_id returns empty dict"""
        mock_client = Mock()
        mock_client.get_by_id.return_value = {}

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            with pytest.raises(Exception, match="Task task1 not found"):
                adapter.complete_task("task1")


@pytest.mark.unit
class TestTickTickAdapterSearch:
    """Test search and filter methods"""

    @patch("adapters.client.search_tasks_helper")
    def test_search_tasks_success(self, mock_search_helper):
        """Test search_tasks success"""
        mock_client = Mock()
        mock_all_tasks = [
            {"id": "task1", "title": "Task 1"},
            {"id": "task2", "title": "Task 2"},
        ]
        mock_filtered_tasks = [{"id": "task1", "title": "Task 1"}]

        mock_client.state = {"tasks": mock_all_tasks}
        mock_search_helper.return_value = mock_filtered_tasks

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            with patch.object(adapter, "get_tasks", return_value=mock_all_tasks):
                result = adapter.search_tasks("Task 1")

        assert result == mock_filtered_tasks
        mock_search_helper.assert_called_once_with(mock_all_tasks, "Task 1")

    def test_get_tasks_by_priority_success(self):
        """Test get_tasks_by_priority success"""
        mock_client = Mock()
        mock_tasks = [
            {"id": "task1", "title": "Task 1", "priority": 3},
            {"id": "task2", "title": "Task 2", "priority": 1},
            {"id": "task3", "title": "Task 3", "priority": 3},
        ]
        mock_client.state = {"tasks": mock_tasks}

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.get_tasks_by_priority(3)

        assert len(result) == 2
        assert all(task["priority"] == 3 for task in result)

    @patch("adapters.client.is_task_due_today")
    def test_get_tasks_due_today_success(self, mock_is_due_today):
        """Test get_tasks_due_today success"""
        mock_client = Mock()
        mock_client.time_zone = "Asia/Shanghai"
        mock_tasks = [
            {"id": "task1", "title": "Task 1"},
            {"id": "task2", "title": "Task 2"},
        ]
        mock_client.state = {"tasks": mock_tasks}

        # Mock first task as due today, second as not
        mock_is_due_today.side_effect = [True, False]

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            with patch.object(
                adapter, "_get_user_timezone", return_value="Asia/Shanghai",
            ):
                result = adapter.get_tasks_due_today()

        assert len(result) == 1
        assert result[0]["id"] == "task1"

    @patch("adapters.client.is_task_overdue")
    def test_get_overdue_tasks_success(self, mock_is_overdue):
        """Test get_overdue_tasks success"""
        mock_client = Mock()
        mock_client.time_zone = "Asia/Shanghai"
        mock_tasks = [
            {"id": "task1", "title": "Task 1"},
            {"id": "task2", "title": "Task 2"},
        ]
        mock_client.state = {"tasks": mock_tasks}

        # Mock first task as overdue, second as not
        mock_is_overdue.side_effect = [True, False]

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            with patch.object(
                adapter, "_get_user_timezone", return_value="Asia/Shanghai",
            ):
                result = adapter.get_overdue_tasks()

        assert len(result) == 1
        assert result[0]["id"] == "task1"


@pytest.mark.unit
class TestTickTickAdapterErrorHandling:
    """Test error handling scenarios"""

    def test_all_methods_handle_client_none(self):
        """Test all methods handle client being None"""
        adapter = TickTickAdapter()

        with patch.object(adapter, "_ensure_client", return_value=None):
            # These should not raise exceptions but return appropriate defaults
            assert adapter.get_projects() == []
            assert adapter.get_project("test") is None
            assert adapter.get_tasks() == []
            assert adapter.search_tasks("test") == []
            assert adapter.get_tasks_by_priority(1) == []
            assert adapter.get_tasks_due_today() == []
            assert adapter.get_overdue_tasks() == []

            # These should raise exceptions
            with pytest.raises(Exception):
                adapter.create_task("test")
            with pytest.raises(Exception):
                adapter.update_task("test")
            with pytest.raises(Exception):
                adapter.delete_task("proj", "task")
            with pytest.raises(Exception):
                adapter.complete_task("task")

    def test_methods_handle_exceptions_gracefully(self):
        """Test methods handle internal exceptions gracefully"""
        adapter = TickTickAdapter()

        with patch.object(
            adapter, "_ensure_client", side_effect=Exception("Test error"),
        ):
            # Read methods should return empty results
            assert adapter.get_projects() == []
            assert adapter.get_project("test") is None
            assert adapter.get_tasks() == []
            assert adapter.search_tasks("test") == []
            assert adapter.get_tasks_by_priority(1) == []
            assert adapter.get_tasks_due_today() == []
            assert adapter.get_overdue_tasks() == []

            # Write methods should raise exceptions
            with pytest.raises(Exception):
                adapter.create_task("test")
            with pytest.raises(Exception):
                adapter.update_task("test")
            with pytest.raises(Exception):
                adapter.delete_task("proj", "task")
            with pytest.raises(Exception):
                adapter.complete_task("task")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
