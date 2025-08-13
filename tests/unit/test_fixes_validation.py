#!/usr/bin/env python3
"""
Unit tests for validating the functionality of complete_task and delete_task after fixes
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from adapters.client import TickTickAdapter


class TestTaskFixesValidation:
    """Test validation of fixes for task-related functions"""

    def test_complete_task_fix(self):
        """Test complete_task fix: ensure the full task object is passed, not just the task_id"""
        # Mock client and task data
        mock_client = Mock()
        mock_task = {
            "id": "test_task_id",
            "title": "Test Task",
            "projectId": "test_project_id",
            "status": 0,
        }

        # Mock get_by_id to return a task
        mock_client.get_by_id.return_value = mock_task

        # Mock the task.complete method
        mock_client.task.complete.return_value = mock_task

        # Create adapter and mock client
        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.complete_task("test_task_id")

            # Validate return value
            assert result is True

            # Validate call arguments: get_by_id should be called first to get the full task object
            mock_client.get_by_id.assert_called_once_with("test_task_id")

            # Validate call arguments: the full task object should be passed, not the task_id
            mock_client.task.complete.assert_called_once_with(mock_task)

    def test_complete_task_task_not_found(self):
        """Test complete_task error handling when task does not exist"""
        mock_client = Mock()

        # Mock the case where the task does not exist
        mock_client.get_by_id.return_value = None

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            with pytest.raises(Exception, match="Task test_task_id not found"):
                adapter.complete_task("test_task_id")

    def test_delete_task_with_project_id(self):
        """Test delete_task behavior when project_id is provided"""
        mock_client = Mock()
        mock_client.task.delete.return_value = True

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.delete_task("provided_project_id", "test_task_id")

            # Validate return value
            assert result is True

            # Validate that the delete method was called
            mock_client.task.delete.assert_called_once_with("test_task_id")

            # When project_id is provided, get_by_id should not be called
            mock_client.get_by_id.assert_not_called()

    def test_delete_task_without_project_id(self):
        """Test delete_task behavior of auto-fetching when project_id is not provided"""
        mock_client = Mock()
        mock_task = {
            "id": "test_task_id",
            "title": "Test Task",
            "projectId": "inbox123456",
        }

        # Mock get_by_id to return a task (to get project_id)
        mock_client.get_by_id.return_value = mock_task
        mock_client.task.delete.return_value = True

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.delete_task("", "test_task_id")  # Empty project_id

            # Validate return value
            assert result is True

            # Validate that get_by_id should be called to get task information
            mock_client.get_by_id.assert_called_once_with("test_task_id")

            # Validate that the delete method was called
            mock_client.task.delete.assert_called_once_with("test_task_id")

    def test_delete_task_none_project_id(self):
        """Test delete_task behavior when project_id is None"""
        mock_client = Mock()
        mock_task = {
            "id": "test_task_id",
            "title": "Test Task",
            "projectId": "inbox123456",
        }

        mock_client.get_by_id.return_value = mock_task
        mock_client.task.delete.return_value = True

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.delete_task(None, "test_task_id")  # None project_id

            # Validate return value
            assert result is True

            # Validate that get_by_id should be called to get task information
            mock_client.get_by_id.assert_called_once_with("test_task_id")

            # Validate that the delete method was called
            mock_client.task.delete.assert_called_once_with("test_task_id")

    def test_complete_task_with_empty_task_dict(self):
        """Test complete_task error handling when get_by_id returns an empty dictionary"""
        mock_client = Mock()

        # Mock get_by_id returning an empty dictionary (task does not exist)
        mock_client.get_by_id.return_value = {}

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            with pytest.raises(Exception, match="Task test_task_id not found"):
                adapter.complete_task("test_task_id")

    def test_delete_task_task_not_found_for_project_id(self):
        """Test delete_task behavior when task does not exist but project_id is needed"""
        mock_client = Mock()

        # Mock the case where the task does not exist
        mock_client.get_by_id.return_value = None
        mock_client.task.delete.return_value = True

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            # Even if the task does not exist, the delete operation should still proceed
            result = adapter.delete_task("", "test_task_id")

            assert result is True
            mock_client.get_by_id.assert_called_once_with("test_task_id")
            mock_client.task.delete.assert_called_once_with("test_task_id")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
