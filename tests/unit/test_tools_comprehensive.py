#!/usr/bin/env python3
"""
Comprehensive tools module unit tests
"""

import os
import sys
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from tools import projects, tasks


@pytest.mark.unit
class TestTaskToolsComprehensive:
    """Comprehensive task tools tests"""

    @patch("tools.tasks.get_client")
    @patch("tools.tasks.convert_tasks_times_to_local")
    def test_get_tasks_success(self, mock_convert, mock_get_client):
        """Test get_tasks success path"""
        mock_adapter = Mock()
        mock_tasks = [{"id": "task1", "title": "Task 1"}]
        mock_adapter.get_tasks.return_value = mock_tasks
        mock_get_client.return_value = mock_adapter
        mock_convert.return_value = mock_tasks

        result = tasks.get_tasks(include_completed=True)

        assert result == mock_tasks
        mock_adapter.get_tasks.assert_called_once_with(True)
        mock_convert.assert_called_once_with(mock_tasks)

    @patch("tools.tasks.get_client")
    def test_get_tasks_exception(self, mock_get_client):
        """Test get_tasks exception handling"""
        mock_get_client.side_effect = Exception("Test error")

        result = tasks.get_tasks()

        assert result == []

    @patch("tools.tasks.get_client")
    @patch("tools.tasks.convert_task_times_to_local")
    def test_create_task_success(self, mock_convert, mock_get_client):
        """Test create_task success path"""
        mock_adapter = Mock()
        mock_task = {"id": "new_task", "title": "New Task"}
        mock_adapter.create_task.return_value = mock_task
        mock_get_client.return_value = mock_adapter
        mock_convert.return_value = mock_task

        result = tasks.create_task("New Task", project_id="proj1", priority=3)

        assert result == mock_task
        mock_adapter.create_task.assert_called_once_with(
            title="New Task",
            projectId="proj1",
            priority=3,
        )
        mock_convert.assert_called_once_with(mock_task)

    @patch("tools.tasks.get_client")
    def test_create_task_no_optional_params(self, mock_get_client):
        """Test create_task with only required parameters"""
        mock_adapter = Mock()
        mock_task = {"id": "new_task", "title": "New Task"}
        mock_adapter.create_task.return_value = mock_task
        mock_get_client.return_value = mock_adapter

        with patch("tools.tasks.convert_task_times_to_local", return_value=mock_task):
            result = tasks.create_task("New Task")

        assert result == mock_task
        # Verify only title and priority are passed
        mock_adapter.create_task.assert_called_once_with(
            title="New Task",
            priority=0,
        )

    @patch("tools.tasks.get_client")
    def test_create_task_exception(self, mock_get_client):
        """Test create_task exception handling"""
        mock_get_client.side_effect = Exception("Test error")

        with pytest.raises(Exception):
            tasks.create_task("New Task")

    @patch("tools.tasks.get_client")
    @patch("tools.tasks.convert_task_times_to_local")
    def test_update_task_success(self, mock_convert, mock_get_client):
        """Test update_task success path"""
        mock_adapter = Mock()
        mock_task = {"id": "task1", "title": "Updated Task"}
        mock_adapter.update_task.return_value = mock_task
        mock_get_client.return_value = mock_adapter
        mock_convert.return_value = mock_task

        result = tasks.update_task("task1", title="Updated Task", priority=5)

        assert result == mock_task
        mock_adapter.update_task.assert_called_once_with(
            "task1",
            None,  # project_id
            title="Updated Task",
            priority=5,
        )

    @patch("tools.tasks.get_client")
    def test_update_task_no_updates(self, mock_get_client):
        """Test update_task with no update data"""
        mock_adapter = Mock()
        mock_task = {"id": "task1", "title": "Task 1"}
        mock_adapter.update_task.return_value = mock_task
        mock_get_client.return_value = mock_adapter

        with patch("tools.tasks.convert_task_times_to_local", return_value=mock_task):
            result = tasks.update_task("task1")

        assert result == mock_task
        # Should still call update_task but with no additional parameters
        mock_adapter.update_task.assert_called_once()

    @patch("tools.tasks.get_client")
    def test_delete_task_success(self, mock_get_client):
        """Test delete_task success path"""
        mock_adapter = Mock()
        mock_adapter.delete_task.return_value = True
        mock_get_client.return_value = mock_adapter

        result = tasks.delete_task("task1")

        assert result is True
        mock_adapter.delete_task.assert_called_once_with(None, "task1")

    @patch("tools.tasks.get_client")
    def test_delete_task_exception(self, mock_get_client):
        """Test delete_task exception handling"""
        mock_get_client.side_effect = Exception("Test error")

        with pytest.raises(Exception):
            tasks.delete_task("task1")

    @patch("tools.tasks.get_client")
    def test_complete_task_success(self, mock_get_client):
        """Test complete_task success path"""
        mock_adapter = Mock()
        mock_adapter.complete_task.return_value = True
        mock_get_client.return_value = mock_adapter

        result = tasks.complete_task("task1")

        assert result is True
        mock_adapter.complete_task.assert_called_once_with("task1")

    @patch("tools.tasks.get_client")
    def test_complete_task_exception(self, mock_get_client):
        """Test complete_task exception handling"""
        mock_get_client.side_effect = Exception("Test error")

        with pytest.raises(Exception):
            tasks.complete_task("task1")

    @patch("tools.tasks.get_client")
    @patch("tools.tasks.convert_tasks_times_to_local")
    def test_search_tasks_success(self, mock_convert, mock_get_client):
        """Test search_tasks success path"""
        mock_adapter = Mock()
        mock_tasks = [{"id": "task1", "title": "Test Task"}]
        mock_adapter.search_tasks.return_value = mock_tasks
        mock_get_client.return_value = mock_adapter
        mock_convert.return_value = mock_tasks

        result = tasks.search_tasks("test")

        assert result == mock_tasks
        mock_adapter.search_tasks.assert_called_once_with("test")

    @patch("tools.tasks.get_client")
    def test_search_tasks_exception(self, mock_get_client):
        """Test search_tasks exception handling"""
        mock_get_client.side_effect = Exception("Test error")

        result = tasks.search_tasks("test")

        assert result == []

    @patch("tools.tasks.get_client")
    @patch("tools.tasks.convert_tasks_times_to_local")
    def test_get_tasks_by_priority_success(self, mock_convert, mock_get_client):
        """Test get_tasks_by_priority success path"""
        mock_adapter = Mock()
        mock_tasks = [{"id": "task1", "priority": 5}]
        mock_adapter.get_tasks_by_priority.return_value = mock_tasks
        mock_get_client.return_value = mock_adapter
        mock_convert.return_value = mock_tasks

        result = tasks.get_tasks_by_priority(5)

        assert result == mock_tasks
        mock_adapter.get_tasks_by_priority.assert_called_once_with(5)

    @patch("tools.tasks.get_client")
    def test_get_tasks_by_priority_exception(self, mock_get_client):
        """Test get_tasks_by_priority exception handling"""
        mock_get_client.side_effect = Exception("Test error")

        result = tasks.get_tasks_by_priority(3)

        assert result == []

    @patch("tools.tasks.get_client")
    @patch("tools.tasks.convert_tasks_times_to_local")
    def test_get_tasks_due_today_success(self, mock_convert, mock_get_client):
        """Test get_tasks_due_today success path"""
        mock_adapter = Mock()
        mock_tasks = [{"id": "task1", "dueDate": "2024-01-01"}]
        mock_adapter.get_tasks_due_today.return_value = mock_tasks
        mock_get_client.return_value = mock_adapter
        mock_convert.return_value = mock_tasks

        result = tasks.get_tasks_due_today()

        assert result == mock_tasks
        mock_adapter.get_tasks_due_today.assert_called_once()

    @patch("tools.tasks.get_client")
    def test_get_tasks_due_today_exception(self, mock_get_client):
        """Test get_tasks_due_today exception handling"""
        mock_get_client.side_effect = Exception("Test error")

        result = tasks.get_tasks_due_today()

        assert result == []

    @patch("tools.tasks.get_client")
    @patch("tools.tasks.convert_tasks_times_to_local")
    def test_get_overdue_tasks_success(self, mock_convert, mock_get_client):
        """Test get_overdue_tasks success path"""
        mock_adapter = Mock()
        mock_tasks = [{"id": "task1", "dueDate": "2023-01-01"}]
        mock_adapter.get_overdue_tasks.return_value = mock_tasks
        mock_get_client.return_value = mock_adapter
        mock_convert.return_value = mock_tasks

        result = tasks.get_overdue_tasks()

        assert result == mock_tasks
        mock_adapter.get_overdue_tasks.assert_called_once()

    @patch("tools.tasks.get_client")
    def test_get_overdue_tasks_exception(self, mock_get_client):
        """Test get_overdue_tasks exception handling"""
        mock_get_client.side_effect = Exception("Test error")

        result = tasks.get_overdue_tasks()

        assert result == []


@pytest.mark.unit
class TestProjectToolsComprehensive:
    """Comprehensive project tools tests"""

    @patch("tools.projects.get_client")
    def test_get_projects_success(self, mock_get_client):
        """Test get_projects success path"""
        mock_adapter = Mock()
        mock_projects = [{"id": "proj1", "name": "Project 1"}]
        mock_adapter.get_projects.return_value = mock_projects
        mock_get_client.return_value = mock_adapter

        result = projects.get_projects()

        assert result == mock_projects
        mock_adapter.get_projects.assert_called_once()

    @patch("tools.projects.get_client")
    def test_get_projects_exception(self, mock_get_client):
        """Test get_projects exception handling"""
        mock_get_client.side_effect = Exception("Test error")

        result = projects.get_projects()

        assert result == []

    @patch("tools.projects.get_client")
    def test_get_project_success(self, mock_get_client):
        """Test get_project success path"""
        mock_adapter = Mock()
        mock_project = {"id": "proj1", "name": "Project 1"}
        mock_adapter.get_project.return_value = mock_project
        mock_get_client.return_value = mock_adapter

        result = projects.get_project("proj1")

        assert result == mock_project
        mock_adapter.get_project.assert_called_once_with("proj1")

    @patch("tools.projects.get_client")
    def test_get_project_exception(self, mock_get_client):
        """Test get_project exception handling"""
        mock_get_client.side_effect = Exception("Test error")

        with pytest.raises(Exception):
            projects.get_project("proj1")

    @patch("tools.projects.get_client")
    def test_create_project_success(self, mock_get_client):
        """Test create_project success path"""
        mock_adapter = Mock()
        mock_client = Mock()
        mock_project = {"id": "new_proj", "name": "New Project"}
        mock_client.project.create.return_value = mock_project
        mock_adapter._ensure_client.return_value = mock_client
        mock_get_client.return_value = mock_adapter

        result = projects.create_project("New Project", color="blue")

        assert result == mock_project
        mock_client.project.create.assert_called_once_with("New Project", "#45B7D1")

    @patch("tools.projects.get_client")
    def test_create_project_exception(self, mock_get_client):
        """Test create_project exception handling"""
        mock_get_client.side_effect = Exception("Test error")

        with pytest.raises(Exception):
            projects.create_project("New Project")

    @patch("tools.projects.get_client")
    def test_delete_project_success(self, mock_get_client):
        """Test delete_project success path"""
        mock_adapter = Mock()
        mock_client = Mock()
        mock_client.project.delete.return_value = True
        mock_adapter._ensure_client.return_value = mock_client
        mock_get_client.return_value = mock_adapter

        result = projects.delete_project("proj1")

        assert result is True
        mock_client.project.delete.assert_called_once_with("proj1")

    @patch("tools.projects.get_client")
    def test_delete_project_exception(self, mock_get_client):
        """Test delete_project exception handling"""
        mock_get_client.side_effect = Exception("Test error")

        with pytest.raises(Exception):
            projects.delete_project("proj1")

    @patch("tools.projects.get_client")
    @patch("tools.projects.convert_tasks_times_to_local")
    def test_get_project_tasks_success(self, mock_convert, mock_get_client):
        """Test get_project_tasks success path"""
        mock_adapter = Mock()
        mock_client = Mock()
        all_tasks = [
            {"id": "task1", "projectId": "proj1", "status": 0},
            {"id": "task2", "projectId": "proj2", "status": 0},
            {"id": "task3", "projectId": "proj1", "status": 2},  # completed
        ]
        mock_client.state = {"tasks": all_tasks}
        mock_adapter._ensure_client.return_value = mock_client
        mock_get_client.return_value = mock_adapter

        filtered_tasks = [{"id": "task1", "projectId": "proj1", "status": 0}]
        mock_convert.return_value = filtered_tasks

        result = projects.get_project_tasks("proj1", include_completed=False)

        assert result == filtered_tasks
        mock_convert.assert_called_once()

    @patch("tools.projects.get_client")
    def test_get_project_tasks_exception(self, mock_get_client):
        """Test get_project_tasks exception handling"""
        mock_get_client.side_effect = Exception("Test error")

        result = projects.get_project_tasks("proj1")

        assert result == []


@pytest.mark.unit
class TestToolsParameterValidation:
    """Test parameter validation in tools"""

    def test_task_creation_parameter_handling(self):
        """Test task creation handles various parameter combinations"""
        with patch("tools.tasks.get_client") as mock_get_client:
            mock_adapter = Mock()
            mock_task = {"id": "task1"}
            mock_adapter.create_task_with_dates.return_value = mock_task
            mock_get_client.return_value = mock_adapter

            with patch(
                "tools.tasks.convert_task_times_to_local", return_value=mock_task,
            ):
                # Test with all parameters
                tasks.create_task(
                    title="Test Task",
                    project_id="proj1",
                    content="Test content",
                    start_date="2024-01-01",
                    due_date="2024-01-02",
                    priority=3,
                )

                # Verify the call includes all parameters
                mock_adapter.create_task_with_dates.assert_called_once()
                call_args = mock_adapter.create_task_with_dates.call_args[1]

                assert call_args["title"] == "Test Task"
                assert call_args["project_id"] == "proj1"
                assert call_args["content"] == "Test content"
                assert call_args["start_date"] == datetime.fromisoformat(
                    "2024-01-01",
                )
                assert call_args["due_date"] == datetime.fromisoformat("2024-01-02")
                assert call_args["priority"] == 3

    def test_task_update_parameter_handling(self):
        """Test task update handles parameter filtering"""
        with patch("tools.tasks.get_client") as mock_get_client:
            mock_adapter = Mock()
            mock_task = {"id": "task1"}
            mock_adapter.update_task.return_value = mock_task
            mock_get_client.return_value = mock_adapter

            with patch(
                "tools.tasks.convert_task_times_to_local", return_value=mock_task,
            ):
                # Test with some None parameters (should be filtered out)
                tasks.update_task(
                    task_id="task1",
                    title="Updated Task",
                    content=None,  # Should be filtered out
                    priority=0,  # Should be included (0 is valid)
                )

                call_args = mock_adapter.update_task.call_args[1]
                assert "title" in call_args
                assert "content" not in call_args  # Should be filtered out
                assert "priority" in call_args  # 0 should be included

    def test_empty_string_parameters(self):
        """Test handling of empty string parameters"""
        with patch("tools.tasks.get_client") as mock_get_client:
            mock_adapter = Mock()
            mock_task = {"id": "task1"}
            mock_adapter.create_task.return_value = mock_task
            mock_get_client.return_value = mock_adapter

            with patch(
                "tools.tasks.convert_task_times_to_local", return_value=mock_task,
            ):
                # Test with empty strings (should be included)
                tasks.create_task(
                    title="Test Task",
                    content="",  # Empty string should be included
                    project_id=None,  # None should be filtered out
                )

                call_args = mock_adapter.create_task.call_args[1]
                # Empty string content should be included
                if "content" in call_args:
                    assert call_args["content"] == ""
                # None project_id should be filtered out
                assert "projectId" not in call_args


@pytest.mark.unit
class TestToolsEdgeCases:
    """Test edge cases and boundary conditions"""

    @patch("tools.tasks.get_client")
    def test_task_priority_boundaries(self, mock_get_client):
        """Test task priority boundary values"""
        mock_adapter = Mock()
        mock_task = {"id": "task1"}
        mock_adapter.create_task.return_value = mock_task
        mock_get_client.return_value = mock_adapter

        with patch("tools.tasks.convert_task_times_to_local", return_value=mock_task):
            # Test minimum priority
            tasks.create_task("Test Task", priority=0)
            call_args = mock_adapter.create_task.call_args[1]
            assert call_args["priority"] == 0

            # Test maximum priority
            tasks.create_task("Test Task", priority=5)
            call_args = mock_adapter.create_task.call_args[1]
            assert call_args["priority"] == 5

    @patch("tools.tasks.get_client")
    def test_long_task_title(self, mock_get_client):
        """Test handling of very long task titles"""
        mock_adapter = Mock()
        mock_task = {"id": "task1"}
        mock_adapter.create_task.return_value = mock_task
        mock_get_client.return_value = mock_adapter

        with patch("tools.tasks.convert_task_times_to_local", return_value=mock_task):
            long_title = "A" * 1000  # Very long title
            tasks.create_task(long_title)

            call_args = mock_adapter.create_task.call_args[1]
            assert call_args["title"] == long_title

    @patch("tools.tasks.get_client")
    def test_special_characters_in_task_data(self, mock_get_client):
        """Test handling of special characters in task data"""
        mock_adapter = Mock()
        mock_task = {"id": "task1"}
        mock_adapter.create_task.return_value = mock_task
        mock_get_client.return_value = mock_adapter

        with patch("tools.tasks.convert_task_times_to_local", return_value=mock_task):
            special_title = "测试任务 🎯 @#$%^&*()"
            special_content = "Content with\nnewlines and\ttabs"

            tasks.create_task(special_title, content=special_content)

            call_args = mock_adapter.create_task.call_args[1]
            assert call_args["title"] == special_title
            assert call_args["content"] == special_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
