#!/usr/bin/env python3
"""
MCP参数处理测试 - 专门测试MCP层的参数转换和类型处理
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server import update_task, create_task, get_tasks_by_priority, delete_task


class TestMCPParameterHandling:
    """测试MCP参数处理和类型转换"""

    @pytest.mark.asyncio
    @patch('server.ensure_authenticated', return_value=True)
    @patch('server.update_task_impl')
    async def test_update_task_string_priority_conversion(self, mock_impl, mock_auth):
        """测试update_task字符串priority参数转换"""
        mock_impl.return_value = {'id': 'test', 'priority': 3}
        
        # 模拟MCP传递字符串参数
        result = await update_task('task_id', priority='3')
        
        # 验证调用时传递的是整数
        mock_impl.assert_called_once_with('task_id', None, None, None, None, None, 3)
        assert 'id: test' in result

    @pytest.mark.asyncio
    @patch('server.ensure_authenticated', return_value=True)
    async def test_update_task_invalid_priority_string(self, mock_auth):
        """测试update_task无效priority字符串处理"""
        result = await update_task('task_id', priority='invalid')
        
        assert "Error: priority must be a valid integer, got 'invalid'" in result

    @pytest.mark.asyncio
    @patch('server.ensure_authenticated', return_value=True)
    @patch('server.create_task_impl')
    async def test_create_task_string_priority_conversion(self, mock_impl, mock_auth):
        """测试create_task字符串priority参数转换"""
        mock_impl.return_value = {'id': 'test', 'priority': 5}
        
        result = await create_task('Test Task', priority='5')
        
        # 验证调用时传递的是整数
        mock_impl.assert_called_once_with('Test Task', None, None, None, None, 5)

    @pytest.mark.asyncio
    @patch('server.ensure_authenticated', return_value=True)
    @patch('server.get_tasks_by_priority_impl')
    async def test_get_tasks_by_priority_string_conversion(self, mock_impl, mock_auth):
        """测试get_tasks_by_priority字符串参数转换"""
        mock_impl.return_value = [{'id': 'task1', 'priority': 1}]
        
        result = await get_tasks_by_priority('1')
        
        mock_impl.assert_called_once_with(1)

    @pytest.mark.asyncio
    @patch('server.ensure_authenticated', return_value=True)
    @patch('server.delete_task_impl')
    async def test_delete_task_boolean_result_handling(self, mock_impl, mock_auth):
        """测试delete_task布尔返回值处理"""
        mock_impl.return_value = True
        
        result = await delete_task('project_id', 'task_id')
        
        assert result == "Task deletion successful"

    @pytest.mark.asyncio
    @patch('server.ensure_authenticated', return_value=True)
    @patch('server.delete_task_impl')
    async def test_delete_task_boolean_false_handling(self, mock_impl, mock_auth):
        """测试delete_task返回False的处理"""
        mock_impl.return_value = False
        
        result = await delete_task('project_id', 'task_id')
        
        assert result == "Task deletion failed"

    @pytest.mark.parametrize("priority_input,expected_int,should_error", [
        ("0", 0, False),
        ("1", 1, False),
        ("5", 5, False),
        ("invalid", None, True),
        ("", None, True),
        ("3.5", None, True),
        ("-1", -1, False),
    ])
    @pytest.mark.asyncio
    @patch('server.ensure_authenticated', return_value=True)
    async def test_priority_conversion_edge_cases(self, mock_auth, priority_input, expected_int, should_error):
        """测试priority转换的边界情况"""
        if should_error:
            result = await update_task('task_id', priority=priority_input)
            assert f"Error: priority must be a valid integer, got '{priority_input}'" in result
        else:
            with patch('server.update_task_impl') as mock_impl:
                mock_impl.return_value = {'id': 'test'}
                result = await update_task('task_id', priority=priority_input)
                mock_impl.assert_called_once_with('task_id', None, None, None, None, None, expected_int)


class TestMCPRealWorldScenarios:
    """测试真实世界MCP使用场景"""

    @pytest.mark.asyncio
    @patch('server.ensure_authenticated', return_value=True)
    @patch('server.update_task_impl')
    async def test_xml_parameter_simulation(self, mock_impl, mock_auth):
        """模拟XML参数传递的真实场景"""
        mock_impl.return_value = {'id': 'test', 'title': 'Updated'}
        
        # 模拟MCP客户端传递的参数（都是字符串）
        xml_params = {
            'task_id': 'task123',
            'project_id': 'proj456', 
            'title': 'Updated Task Title',
            'priority': '3'  # XML中的数字会变成字符串
        }
        
        result = await update_task(**xml_params)
        
        # 验证字符串priority被正确转换为整数
        mock_impl.assert_called_once_with(
            'task123', 'proj456', 'Updated Task Title', None, None, None, 3
        )

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
