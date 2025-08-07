#!/usr/bin/env python3
"""
验证修复后的 complete_task 和 delete_task 功能的单元测试
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from adapters.client import TickTickAdapter


class TestTaskFixesValidation:
    """测试任务相关功能的修复验证"""

    def test_complete_task_fix(self):
        """测试 complete_task 修复：确保传入完整的 task 对象而不是只传入 task_id"""
        # 模拟客户端和任务数据
        mock_client = Mock()
        mock_task = {
            "id": "test_task_id",
            "title": "Test Task",
            "projectId": "test_project_id",
            "status": 0,
        }

        # 模拟 get_by_id 返回任务
        mock_client.get_by_id.return_value = mock_task

        # 模拟 task.complete 方法
        mock_client.task.complete.return_value = mock_task

        # 创建适配器并模拟客户端
        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.complete_task("test_task_id")

            # 验证返回值
            assert result is True

            # 验证调用参数：应该先调用 get_by_id 获取完整任务对象
            mock_client.get_by_id.assert_called_once_with("test_task_id")

            # 验证调用参数：应该传入完整的任务对象而不是 task_id
            mock_client.task.complete.assert_called_once_with(mock_task)

    def test_complete_task_task_not_found(self):
        """测试 complete_task 当任务不存在时的错误处理"""
        mock_client = Mock()

        # 模拟任务不存在的情况
        mock_client.get_by_id.return_value = None

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            with pytest.raises(Exception, match="Task test_task_id not found"):
                adapter.complete_task("test_task_id")

    def test_delete_task_with_project_id(self):
        """测试 delete_task 当提供了 project_id 时的行为"""
        mock_client = Mock()
        mock_client.task.delete.return_value = True

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.delete_task("provided_project_id", "test_task_id")

            # 验证返回值
            assert result is True

            # 验证 delete 方法被调用
            mock_client.task.delete.assert_called_once_with("test_task_id")

            # 当提供了 project_id 时，不应该调用 get_by_id
            mock_client.get_by_id.assert_not_called()

    def test_delete_task_without_project_id(self):
        """测试 delete_task 当未提供 project_id 时自动获取的行为"""
        mock_client = Mock()
        mock_task = {
            "id": "test_task_id",
            "title": "Test Task",
            "projectId": "inbox123456",
        }

        # 模拟 get_by_id 返回任务（用于获取 project_id）
        mock_client.get_by_id.return_value = mock_task
        mock_client.task.delete.return_value = True

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            result = adapter.delete_task("", "test_task_id")  # 空的 project_id

            # 验证返回值
            assert result is True

            # 验证应该调用 get_by_id 来获取任务信息
            mock_client.get_by_id.assert_called_once_with("test_task_id")

            # 验证 delete 方法被调用
            mock_client.task.delete.assert_called_once_with("test_task_id")

    def test_delete_task_none_project_id(self):
        """测试 delete_task 当 project_id 为 None 时的行为"""
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

            # 验证返回值
            assert result is True

            # 验证应该调用 get_by_id 来获取任务信息
            mock_client.get_by_id.assert_called_once_with("test_task_id")

            # 验证 delete 方法被调用
            mock_client.task.delete.assert_called_once_with("test_task_id")

    def test_complete_task_with_empty_task_dict(self):
        """测试 complete_task 当 get_by_id 返回空字典时的错误处理"""
        mock_client = Mock()

        # 模拟 get_by_id 返回空字典（任务不存在）
        mock_client.get_by_id.return_value = {}

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            with pytest.raises(Exception, match="Task test_task_id not found"):
                adapter.complete_task("test_task_id")

    def test_delete_task_task_not_found_for_project_id(self):
        """测试 delete_task 当任务不存在但需要获取 project_id 时的行为"""
        mock_client = Mock()

        # 模拟任务不存在的情况
        mock_client.get_by_id.return_value = None
        mock_client.task.delete.return_value = True

        adapter = TickTickAdapter()
        with patch.object(adapter, "_ensure_client", return_value=mock_client):
            # 即使任务不存在，delete 操作仍然应该继续
            result = adapter.delete_task("", "test_task_id")

            assert result is True
            mock_client.get_by_id.assert_called_once_with("test_task_id")
            mock_client.task.delete.assert_called_once_with("test_task_id")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
