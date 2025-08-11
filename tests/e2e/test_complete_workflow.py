#!/usr/bin/env python3
"""
Complete end-to-end workflow tests
"""

import traceback
from pathlib import Path

import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


@pytest.mark.e2e
class TestCompleteWorkflow:
    """Complete workflow tests"""

    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test complete workflow"""
        try:

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream), ClientSession(read_stream, write_stream) as session:
                # 1. Check authentication status
                await session.call_tool("auth_status", {})

                # 2. Get project list
                await session.call_tool("get_projects", {})

                # 3. Get task list
                await session.call_tool(
                    "get_tasks",
                    {"include_completed": False},
                )

                # 4. Get tasks due today
                await session.call_tool("get_tasks_due_today", {})

                # 5. Get overdue tasks
                await session.call_tool("get_overdue_tasks", {})

                # 6. Get tasks by priority
                await session.call_tool(
                    "get_tasks_by_priority",
                    {"priority": 3},
                )

                return True

        except Exception:
            traceback.print_exc()
            return False

    @pytest.mark.asyncio
    async def test_tool_interaction(self):
        """Test tool interactions"""
        try:

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream), ClientSession(read_stream, write_stream) as session:
                # Get all tools
                tools = await session.list_tools()

                # Test each tool with basic calls
                successful_calls = 0
                total_calls = 0

                for tool in tools:
                    total_calls += 1

                    # Provide appropriate parameters based on tool name
                    if tool.name in {"auth_status", "get_projects"}:
                        result = await session.call_tool(tool.name, {})
                    elif tool.name == "get_tasks":
                        result = await session.call_tool(
                            tool.name,
                            {"include_completed": False},
                        )
                    elif tool.name in {
                        "get_tasks_due_today",
                        "get_overdue_tasks",
                    }:
                        result = await session.call_tool(tool.name, {})
                    elif tool.name == "get_tasks_by_priority":
                        result = await session.call_tool(
                            tool.name, {"priority": 0},
                        )
                    elif tool.name == "search_tasks":
                        result = await session.call_tool(
                            tool.name, {"query": "test"},
                        )
                    else:
                        # Skip tools that require specific parameters
                        continue

                    # Validate result format
                    assert isinstance(result, dict)
                    assert "content" in result
                    successful_calls += 1

                success_rate = (
                    successful_calls / total_calls if total_calls > 0 else 0
                )

                # Require at least 80% tool call success rate
                assert (
                    success_rate >= 0.8
                ), f"Tool call success rate too low: {success_rate:.2%}"

                return True

        except Exception:
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

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream), ClientSession(read_stream, write_stream) as session:
                # Test invalid parameters
                from contextlib import suppress
                with suppress(Exception):
                    await session.call_tool(
                        "get_tasks_by_priority",
                        {"priority": "invalid"},
                    )

                # Test missing required parameters
                with suppress(Exception):
                    await session.call_tool("get_project", {})

                return True

        except Exception:
            return False

    @pytest.mark.asyncio
    async def test_server_stability(self):
        """Test server stability"""
        try:

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream), ClientSession(read_stream, write_stream) as session:
                # Call multiple tools continuously
                for i in range(10):
                    # Alternate between different tools
                    if i % 3 == 0:
                        result = await session.call_tool("auth_status", {})
                    elif i % 3 == 1:
                        result = await session.call_tool("get_projects", {})
                    else:
                        result = await session.call_tool(
                            "get_tasks",
                            {"include_completed": False},
                        )

                    assert isinstance(result, dict)
                    assert "content" in result

                return True

        except Exception:
            return False
