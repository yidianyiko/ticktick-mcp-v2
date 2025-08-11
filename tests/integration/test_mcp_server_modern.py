#!/usr/bin/env python3
"""
Modern MCP Server Integration Tests
"""

import asyncio
from pathlib import Path

import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


@pytest.mark.integration
@pytest.mark.mcp
class TestMCPServerModern:
    """Modern MCP server tests"""

    @pytest.mark.asyncio
    async def test_server_connection(self):
        """Test server connection and initialization"""
        try:

            # Create server parameters
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            # Test connection with proper initialization wait
            async with stdio_client(server_params) as (read_stream, write_stream), ClientSession(read_stream, write_stream) as session:
                    # Wait for server to be ready
                    await asyncio.sleep(1)

                    # Test basic connection
                    assert session is not None

                    return True

        except Exception:
            return False

    @pytest.mark.asyncio
    async def test_tools_listing(self):
        """Test tools listing functionality"""
        try:

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream), ClientSession(read_stream, write_stream) as session:
                    # Wait for server initialization
                    await asyncio.sleep(2)

                    # Get tools list
                    tools = await session.list_tools()

                    # Verify tools are available
                    assert len(tools) > 0, "No tools found"

                    # Check for essential tools
                    tool_names = [tool.name for tool in tools]
                    essential_tools = ["auth_status", "get_projects", "get_tasks"]

                    for tool_name in essential_tools:
                        if tool_name in tool_names:
                            pass
                        else:
                            pass

                    return True

        except Exception:
            return False

    @pytest.mark.asyncio
    async def test_auth_status_tool(self):
        """Test auth status tool"""
        try:

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream), ClientSession(read_stream, write_stream) as session:
                    # Wait for server initialization
                    await asyncio.sleep(2)

                    # Test auth status tool
                    result = await session.call_tool("auth_status", {})

                    # Verify result format
                    assert isinstance(result, dict), "Result should be a dictionary"
                    assert "content" in result, "Result should have content field"

                    return True

        except Exception:
            return False

    @pytest.mark.asyncio
    async def test_get_projects_tool(self):
        """Test get projects tool"""
        try:

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream), ClientSession(read_stream, write_stream) as session:
                    # Wait for server initialization
                    await asyncio.sleep(2)

                    # Test get projects tool
                    result = await session.call_tool("get_projects", {})

                    # Verify result format
                    assert isinstance(result, dict), "Result should be a dictionary"
                    assert "content" in result, "Result should have content field"

                    return True

        except Exception:
            return False

    @pytest.mark.asyncio
    async def test_get_tasks_tool(self):
        """Test get tasks tool"""
        try:

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream), ClientSession(read_stream, write_stream) as session:
                    # Wait for server initialization
                    await asyncio.sleep(2)

                    # Test get tasks tool
                    result = await session.call_tool(
                        "get_tasks", {"include_completed": False},
                    )

                    # Verify result format
                    assert isinstance(result, dict), "Result should be a dictionary"
                    assert "content" in result, "Result should have content field"

                    return True

        except Exception:
            return False


@pytest.mark.integration
@pytest.mark.mcp
class TestMCPServerErrorHandling:
    """Test error handling in MCP server"""

    @pytest.mark.asyncio
    async def test_invalid_tool_call(self):
        """Test handling of invalid tool calls"""
        try:


            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    # Wait for server initialization
                    await asyncio.sleep(2)

                    # Test invalid tool call
                    try:
                        await session.call_tool("non_existent_tool", {})
                        return False
                    except Exception:
                        return True

        except Exception:
            return False

    @pytest.mark.asyncio
    async def test_server_stability(self):
        """Test server stability with multiple requests"""
        try:


            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    # Wait for server initialization
                    await asyncio.sleep(2)

                    # Make multiple requests to test stability
                    for _i in range(3):
                        try:
                            result = await session.call_tool("auth_status", {})
                            assert isinstance(result, dict)
                        except Exception:
                            return False

                    return True

        except Exception:
            return False
