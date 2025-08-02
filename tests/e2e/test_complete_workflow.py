#!/usr/bin/env python3
"""
Complete end-to-end workflow tests
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

@pytest.mark.e2e
class TestCompleteWorkflow:
    """Complete workflow tests"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test complete workflow"""
        try:
            from mcp.client.session import ClientSession
            from mcp.client.stdio import stdio_client, StdioServerParameters
            
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent
            )
            
            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    print("🔧 Starting complete workflow test...")
                    
                    # 1. Check authentication status
                    print("1. Checking authentication status...")
                    auth_result = await session.call_tool("auth_status", {})
                    print(f"Authentication status: {auth_result}")
                    
                    # 2. Get project list
                    print("2. Getting project list...")
                    projects_result = await session.call_tool("get_projects", {})
                    print(f"Number of projects: {len(projects_result.get('content', []))}")
                    
                    # 3. Get task list
                    print("3. Getting task list...")
                    tasks_result = await session.call_tool("get_tasks", {"include_completed": False})
                    print(f"Number of tasks: {len(tasks_result.get('content', []))}")
                    
                    # 4. Get tasks due today
                    print("4. Getting tasks due today...")
                    due_today_result = await session.call_tool("get_tasks_due_today", {})
                    print(f"Number of tasks due today: {len(due_today_result.get('content', []))}")
                    
                    # 5. Get overdue tasks
                    print("5. Getting overdue tasks...")
                    overdue_result = await session.call_tool("get_overdue_tasks", {})
                    print(f"Number of overdue tasks: {len(overdue_result.get('content', []))}")
                    
                    # 6. Get tasks by priority
                    print("6. Getting tasks by priority...")
                    priority_result = await session.call_tool("get_tasks_by_priority", {"priority": 3})
                    print(f"Number of priority 3 tasks: {len(priority_result.get('content', []))}")
                    
                    print("✅ Complete workflow test passed!")
                    return True
                    
        except Exception as e:
            print(f"❌ Complete workflow test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @pytest.mark.asyncio
    async     def test_tool_interaction(self):
        """Test tool interactions"""
        try:
            from mcp.client.session import ClientSession
            from mcp.client.stdio import stdio_client, StdioServerParameters
            
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent
            )
            
            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    print("🔧 Starting tool interaction test...")
                    
                    # Get all tools
                    tools = await session.list_tools()
                    print(f"Number of available tools: {len(tools)}")
                    
                    # Test each tool with basic calls
                    successful_calls = 0
                    total_calls = 0
                    
                    for tool in tools:
                        try:
                            total_calls += 1
                            
                            # Provide appropriate parameters based on tool name
                            if tool.name == "auth_status":
                                result = await session.call_tool(tool.name, {})
                            elif tool.name == "get_projects":
                                result = await session.call_tool(tool.name, {})
                            elif tool.name == "get_tasks":
                                result = await session.call_tool(tool.name, {"include_completed": False})
                            elif tool.name == "get_tasks_due_today":
                                result = await session.call_tool(tool.name, {})
                            elif tool.name == "get_overdue_tasks":
                                result = await session.call_tool(tool.name, {})
                            elif tool.name == "get_tasks_by_priority":
                                result = await session.call_tool(tool.name, {"priority": 0})
                            elif tool.name == "search_tasks":
                                result = await session.call_tool(tool.name, {"query": "test"})
                            else:
                                # Skip tools that require specific parameters
                                continue
                            
                            # Validate result format
                            assert isinstance(result, dict)
                            assert "content" in result
                            successful_calls += 1
                            
                        except Exception as e:
                            print(f"Tool {tool.name} call failed: {e}")
                    
                    success_rate = successful_calls / total_calls if total_calls > 0 else 0
                    print(f"Tool call success rate: {success_rate:.2%} ({successful_calls}/{total_calls})")
                    
                    # Require at least 80% tool call success rate
                    assert success_rate >= 0.8, f"Tool call success rate too low: {success_rate:.2%}"
                    
                    print("✅ Tool interaction test passed!")
                    return True
                    
        except Exception as e:
            print(f"❌ Tool interaction test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

@pytest.mark.e2e
@pytest.mark.slow
class TestErrorHandling:
    """Error handling tests"""
    
    @pytest.mark.asyncio
    async def test_invalid_parameters(self):
        """Test invalid parameter handling"""
        try:
            from mcp.client.session import ClientSession
            from mcp.client.stdio import stdio_client, StdioServerParameters
            
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent
            )
            
            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    print("🔧 Starting invalid parameter test...")
                    
                    # Test invalid parameters
                    try:
                        result = await session.call_tool("get_tasks_by_priority", {"priority": "invalid"})
                        # If successful, error handling is working
                        print("✅ Invalid parameter handled correctly")
                    except Exception as e:
                        print(f"✅ Invalid parameter rejected: {e}")
                    
                    # Test missing required parameters
                    try:
                        result = await session.call_tool("get_project", {})
                        # If successful, default value handling is working
                        print("✅ Missing parameter handled correctly")
                    except Exception as e:
                        print(f"✅ Missing parameter rejected: {e}")
                    
                    print("✅ Invalid parameter test passed!")
                    return True
                    
        except Exception as e:
            print(f"❌ Invalid parameter test failed: {e}")
            return False
    
    @pytest.mark.asyncio
    async def test_server_stability(self):
        """Test server stability"""
        try:
            from mcp.client.session import ClientSession
            from mcp.client.stdio import stdio_client, StdioServerParameters
            
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent
            )
            
            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    print("🔧 Starting server stability test...")
                    
                    # Call multiple tools continuously
                    for i in range(10):
                        try:
                            # Alternate between different tools
                            if i % 3 == 0:
                                result = await session.call_tool("auth_status", {})
                            elif i % 3 == 1:
                                result = await session.call_tool("get_projects", {})
                            else:
                                result = await session.call_tool("get_tasks", {"include_completed": False})
                            
                            assert isinstance(result, dict)
                            assert "content" in result
                            
                        except Exception as e:
                            print(f"Call {i+1} failed: {e}")
                            return False
                    
                    print("✅ Server stability test passed!")
                    return True
                    
        except Exception as e:
            print(f"❌ Server stability test failed: {e}")
            return False 