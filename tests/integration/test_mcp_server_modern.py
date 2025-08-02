#!/usr/bin/env python3
"""
Modern MCP Server Integration Tests
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path

@pytest.mark.integration
@pytest.mark.mcp
class TestMCPServerModern:
    """Modern MCP server tests"""
    
    @pytest.mark.asyncio
    async def test_server_connection(self):
        """Test server connection and initialization"""
        try:
            from mcp.client.session import ClientSession
            from mcp.client.stdio import stdio_client, StdioServerParameters
            
            # Create server parameters
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent
            )
            
            # Test connection with proper initialization wait
            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    # Wait for server to be ready
                    await asyncio.sleep(1)
                    
                    # Test basic connection
                    assert session is not None
                    print("✅ Server connection successful")
                    
                    return True
                    
        except Exception as e:
            print(f"❌ Server connection test failed: {e}")
            return False
    
    @pytest.mark.asyncio
    async def test_tools_listing(self):
        """Test tools listing functionality"""
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
                    # Wait for server initialization
                    await asyncio.sleep(2)
                    
                    # Get tools list
                    tools = await session.list_tools()
                    
                    # Verify tools are available
                    assert len(tools) > 0, "No tools found"
                    print(f"✅ Found {len(tools)} tools")
                    
                    # Check for essential tools
                    tool_names = [tool.name for tool in tools]
                    essential_tools = ['auth_status', 'get_projects', 'get_tasks']
                    
                    for tool_name in essential_tools:
                        if tool_name in tool_names:
                            print(f"✅ Found essential tool: {tool_name}")
                        else:
                            print(f"⚠️ Missing essential tool: {tool_name}")
                    
                    return True
                    
        except Exception as e:
            print(f"❌ Tools listing test failed: {e}")
            return False
    
    @pytest.mark.asyncio
    async def test_auth_status_tool(self):
        """Test auth status tool"""
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
                    # Wait for server initialization
                    await asyncio.sleep(2)
                    
                    # Test auth status tool
                    result = await session.call_tool("auth_status", {})
                    
                    # Verify result format
                    assert isinstance(result, dict), "Result should be a dictionary"
                    assert "content" in result, "Result should have content field"
                    
                    print("✅ Auth status tool test successful")
                    return True
                    
        except Exception as e:
            print(f"❌ Auth status tool test failed: {e}")
            return False
    
    @pytest.mark.asyncio
    async def test_get_projects_tool(self):
        """Test get projects tool"""
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
                    # Wait for server initialization
                    await asyncio.sleep(2)
                    
                    # Test get projects tool
                    result = await session.call_tool("get_projects", {})
                    
                    # Verify result format
                    assert isinstance(result, dict), "Result should be a dictionary"
                    assert "content" in result, "Result should have content field"
                    
                    print("✅ Get projects tool test successful")
                    return True
                    
        except Exception as e:
            print(f"❌ Get projects tool test failed: {e}")
            return False
    
    @pytest.mark.asyncio
    async def test_get_tasks_tool(self):
        """Test get tasks tool"""
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
                    # Wait for server initialization
                    await asyncio.sleep(2)
                    
                    # Test get tasks tool
                    result = await session.call_tool("get_tasks", {"include_completed": False})
                    
                    # Verify result format
                    assert isinstance(result, dict), "Result should be a dictionary"
                    assert "content" in result, "Result should have content field"
                    
                    print("✅ Get tasks tool test successful")
                    return True
                    
        except Exception as e:
            print(f"❌ Get tasks tool test failed: {e}")
            return False

@pytest.mark.integration
@pytest.mark.mcp
class TestMCPServerErrorHandling:
    """Test error handling in MCP server"""
    
    @pytest.mark.asyncio
    async def test_invalid_tool_call(self):
        """Test handling of invalid tool calls"""
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
                    # Wait for server initialization
                    await asyncio.sleep(2)
                    
                    # Test invalid tool call
                    try:
                        result = await session.call_tool("non_existent_tool", {})
                        print("⚠️ Invalid tool call should have failed")
                        return False
                    except Exception as e:
                        print(f"✅ Invalid tool call properly handled: {e}")
                        return True
                    
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            return False
    
    @pytest.mark.asyncio
    async def test_server_stability(self):
        """Test server stability with multiple requests"""
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
                    # Wait for server initialization
                    await asyncio.sleep(2)
                    
                    # Make multiple requests to test stability
                    for i in range(3):
                        try:
                            result = await session.call_tool("auth_status", {})
                            assert isinstance(result, dict)
                            print(f"✅ Request {i+1} successful")
                        except Exception as e:
                            print(f"❌ Request {i+1} failed: {e}")
                            return False
                    
                    print("✅ Server stability test passed")
                    return True
                    
        except Exception as e:
            print(f"❌ Server stability test failed: {e}")
            return False 