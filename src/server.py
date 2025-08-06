#!/usr/bin/env python3
"""
TickTick MCP Server - Simplified Implementation
"""

import asyncio
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp.server.stdio import stdio_server
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent

# Import our tools
from tools.projects import (
    get_projects as get_projects_impl,
    get_project as get_project_impl,
    create_project as create_project_impl,
    delete_project as delete_project_impl,
    get_project_tasks as get_project_tasks_impl,
)
from tools.tasks import (
    get_tasks as get_tasks_impl,
    create_task as create_task_impl,
    update_task as update_task_impl,
    delete_task as delete_task_impl,
    complete_task as complete_task_impl,
    search_tasks as search_tasks_impl,
    get_tasks_by_priority as get_tasks_by_priority_impl,
    get_tasks_due_today as get_tasks_due_today_impl,
    get_overdue_tasks as get_overdue_tasks_impl,
)
from tools.auth import AuthTools
from auth import TickTickAuth

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = FastMCP("ticktick")

# Initialize authentication tools
auth_tools = AuthTools()


# Global client check (similar to reference project)
def ensure_authenticated():
    """Ensure client is authenticated, similar to reference project's initialize_client."""
    auth = TickTickAuth()
    if not auth.is_authenticated():
        # Try to authenticate using environment variables if available
        username = os.getenv("TICKTICK_USERNAME")
        password = os.getenv("TICKTICK_PASSWORD")

        if username and password:
            logger.info("Attempting automatic authentication using environment variables")
            if auth.authenticate(username, password):
                logger.info("Automatic authentication successful")
                return True
            else:
                logger.warning("Automatic authentication failed")
                return False
        else:
            logger.warning("No authentication credentials found")
            return False
    return True


# Helper function to format results
def format_result(data: Any) -> str:
    """Format tool results as readable text."""
    # Add detailed debugging information
    logger.info(f"format_result received data type: {type(data)}")
    if isinstance(data, list):
        logger.info(f"format_result received list with {len(data)} items")
        if data and len(data) > 0:
            logger.info(f"First item type: {type(data[0])}")
            if isinstance(data[0], dict):
                logger.info(f"First item keys: {list(data[0].keys())}")
                logger.info(f"First item content: {data[0]}")
            else:
                logger.info(f"First item: {data[0]}")

    if isinstance(data, list):
        if not data:
            return "No items found."

        # Check if this is a list of MCP result format items (with content field)
        if len(data) > 0 and isinstance(data[0], dict) and "content" in data[0]:
            # Handle MCP result format for multiple items
            result = f"Found {len(data)} items:\n\n"
            for i, item in enumerate(data, 1):
                if "content" in item and isinstance(item["content"], list):
                    content = item["content"]
                    if len(content) > 0 and "text" in content[0]:
                        result += f"Item {i}:\n{content[0]['text']}\n\n"
                    else:
                        result += f"Item {i}:\n"
                        for key, value in item.items():
                            if key not in ["content", "type"]:
                                result += f"  {key}: {value}\n"
                        result += "\n"
                else:
                    result += f"Item {i}:\n"
                    for key, value in item.items():
                        if key not in ["content", "type"]:
                            result += f"  {key}: {value}\n"
                    result += "\n"
            return result

        # Format regular list of items (tasks or projects)
        result = f"Found {len(data)} items:\n\n"
        for i, item in enumerate(data, 1):
            if isinstance(item, dict):
                result += f"Item {i}:\n"
                # Log the actual item structure
                logger.info(f"Processing item {i}: {item}")

                # Handle tasks - show key information
                if "title" in item:
                    result += f"  Title: {item.get('title', 'Unknown')}\n"
                    result += f"  ID: {item.get('id', 'Unknown')}\n"
                    result += f"  Project ID: {item.get('projectId', 'Unknown')}\n"
                    result += f"  Priority: {item.get('priority', 0)}\n"
                    result += f"  Status: {item.get('status', 0)}\n"
                    if item.get("dueDate"):
                        result += f"  Due Date: {item.get('dueDate', 'No due date')}\n"
                    if item.get("content"):
                        result += f"  Content: {item.get('content', 'No content')}\n"
                    result += "\n"
                # Handle projects - show key information
                elif "name" in item:
                    result += f"  Name: {item.get('name', 'Unknown')}\n"
                    result += f"  ID: {item.get('id', 'Unknown')}\n"
                    result += f"  Color: {item.get('color', 'Default')}\n"
                    result += f"  View Mode: {item.get('view_mode', 'list')}\n"
                    if item.get("createdTime"):
                        result += f"  Created: {item.get('createdTime', 'Unknown')}\n"
                    result += "\n"
                # Handle other dictionary items
                else:
                    for key, value in item.items():
                        if key not in ["content", "type"]:  # Skip internal fields
                            result += f"  {key}: {value}\n"
                    result += "\n"
            else:
                result += f"{i}. {item}\n"
        return result

    elif isinstance(data, dict):
        if "content" in data and isinstance(data["content"], list):
            # Handle MCP result format
            content = data["content"]
            if len(content) > 0 and "text" in content[0]:
                return content[0]["text"]

        # Format dict
        result = ""
        for key, value in data.items():
            if key not in ["content", "type"]:  # Skip internal fields
                result += f"{key}: {value}\n"
        return result

    else:
        return str(data)


# Tool definitions
@server.tool()
async def auth_login(username: str, password: str) -> str:
    """Login to TickTick with username and password."""
    try:
        result = await auth_tools.call_tool(
            "auth_login", {"username": username, "password": password}, server
        )
        return format_result(result)
    except Exception as e:
        logger.error(f"Error in auth_login: {e}")
        return f"Error: {str(e)}"


@server.tool()
async def auth_logout() -> str:
    """Logout from TickTick and clear saved credentials."""
    try:
        result = await auth_tools.call_tool("auth_logout", {}, server)
        return format_result(result)
    except Exception as e:
        logger.error(f"Error in auth_logout: {e}")
        return f"Error: {str(e)}"


@server.tool()
async def auth_status() -> str:
    """Check authentication status."""
    try:
        result = await auth_tools.call_tool("auth_status", {}, server)
        return format_result(result)
    except Exception as e:
        logger.error(f"Error in auth_status: {e}")
        return f"Error: {str(e)}"


# Project Management Tools
@server.tool()
async def get_projects() -> str:
    """Get all projects from TickTick."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        projects = get_projects_impl()
        return format_result(projects)
    except Exception as e:
        logger.error(f"Error in get_projects: {e}")
        return f"Error retrieving projects: {str(e)}"


@server.tool()
async def get_project(project_id: str) -> str:
    """Get details about a specific project."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        project = get_project_impl(project_id)
        return format_result(project)
    except Exception as e:
        logger.error(f"Error in get_project: {e}")
        return f"Error retrieving project: {str(e)}"


@server.tool()
async def create_project(name: str, color: Optional[str] = None, view_mode: str = "list") -> str:
    """Create a new project."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        project = create_project_impl(name, color, view_mode)
        return format_result(project)
    except Exception as e:
        logger.error(f"Error in create_project: {e}")
        return f"Error creating project: {str(e)}"


@server.tool()
async def delete_project(project_id: str) -> str:
    """Delete a project."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        result = delete_project_impl(project_id)
        return format_result(result)
    except Exception as e:
        logger.error(f"Error in delete_project: {e}")
        return f"Error deleting project: {str(e)}"


@server.tool()
async def get_project_tasks(project_id: str, include_completed: bool = False) -> str:
    """Get all tasks in a specific project."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        tasks = get_project_tasks_impl(project_id, include_completed)
        return format_result(tasks)
    except Exception as e:
        logger.error(f"Error in get_project_tasks: {e}")
        return f"Error retrieving project tasks: {str(e)}"


# Task Management Tools
@server.tool()
async def get_tasks(include_completed: bool = False) -> str:
    """Get all tasks."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        tasks = get_tasks_impl(include_completed)
        logger.info(f"get_tasks received {len(tasks)} tasks from get_tasks_impl")
        if tasks and len(tasks) > 0:
            logger.info(f"First task type: {type(tasks[0])}")
            if isinstance(tasks[0], dict):
                logger.info(f"First task keys: {list(tasks[0].keys())}")
                logger.info(f"First task title: {tasks[0].get('title', 'No title')}")
        return format_result(tasks)
    except Exception as e:
        logger.error(f"Error in get_tasks: {e}")
        return f"Error retrieving tasks: {str(e)}"


@server.tool()
async def create_task(
    title: str,
    project_id: Optional[str] = None,
    content: Optional[str] = None,
    start_date: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: str = "0",
) -> str:
    """Create a new task."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        # Convert priority to int if it's a string (MCP parameter conversion)
        converted_priority = 0
        if isinstance(priority, str):
            try:
                converted_priority = int(priority)
            except ValueError:
                return f"Error: priority must be a valid integer, got '{priority}'"
        else:
            converted_priority = priority
        
        task = create_task_impl(title, project_id, content, start_date, due_date, converted_priority)
        return format_result(task)
    except Exception as e:
        logger.error(f"Error in create_task: {e}")
        return f"Error creating task: {str(e)}"


@server.tool()
async def update_task(
    task_id: str,
    project_id: Optional[str] = None,
    title: Optional[str] = None,
    content: Optional[str] = None,
    start_date: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[str] = None,
) -> str:
    """Update an existing task."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        # Convert priority to int if it's a string (MCP parameter conversion)
        converted_priority = None
        if priority is not None:
            if isinstance(priority, str):
                try:
                    converted_priority = int(priority)
                except ValueError:
                    return f"Error: priority must be a valid integer, got '{priority}'"
            else:
                converted_priority = priority
        
        task = update_task_impl(task_id, project_id, title, content, start_date, due_date, converted_priority)
        return format_result(task)
    except Exception as e:
        logger.error(f"Error in update_task: {e}")
        return f"Error updating task: {str(e)}"


@server.tool()
async def delete_task(project_id: str, task_id: str) -> str:
    """Delete a task."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        result = delete_task_impl(project_id, task_id)
        # Handle boolean result from delete operation
        if isinstance(result, bool):
            return f"Task deletion {'successful' if result else 'failed'}"
        else:
            return format_result(result)
    except Exception as e:
        logger.error(f"Error in delete_task: {e}")
        return f"Error deleting task: {str(e)}"


@server.tool()
async def complete_task(task_id: str) -> str:
    """Mark a task as completed."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        result = complete_task_impl(task_id)
        return format_result(result)
    except Exception as e:
        logger.error(f"Error in complete_task: {e}")
        return f"Error completing task: {str(e)}"


@server.tool()
async def search_tasks(query: str) -> str:
    """Search tasks by query."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        tasks = search_tasks_impl(query)
        return format_result(tasks)
    except Exception as e:
        logger.error(f"Error in search_tasks: {e}")
        return f"Error searching tasks: {str(e)}"


@server.tool()
async def get_tasks_by_priority(priority: str) -> str:
    """Get tasks by priority level (0=None, 1=Low, 3=Medium, 5=High)."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        # Convert priority to int if it's a string (MCP parameter conversion)
        converted_priority = 0
        if isinstance(priority, str):
            try:
                converted_priority = int(priority)
            except ValueError:
                return f"Error: priority must be a valid integer, got '{priority}'"
        else:
            converted_priority = priority
        
        tasks = get_tasks_by_priority_impl(converted_priority)
        return format_result(tasks)
    except Exception as e:
        logger.error(f"Error in get_tasks_by_priority: {e}")
        return f"Error retrieving tasks by priority: {str(e)}"


@server.tool()
async def get_tasks_due_today() -> str:
    """Get tasks due today."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        tasks = get_tasks_due_today_impl()
        return format_result(tasks)
    except Exception as e:
        logger.error(f"Error in get_tasks_due_today: {e}")
        return f"Error retrieving tasks due today: {str(e)}"


@server.tool()
async def get_overdue_tasks() -> str:
    """Get overdue tasks."""
    if not ensure_authenticated():
        return "Not authenticated. Please use auth_login tool to login first."

    try:
        tasks = get_overdue_tasks_impl()
        return format_result(tasks)
    except Exception as e:
        logger.error(f"Error in get_overdue_tasks: {e}")
        return f"Error retrieving overdue tasks: {str(e)}"


async def main():
    """Main function to run the server."""
    # Check authentication at startup (similar to reference project)
    if not ensure_authenticated():
        logger.warning("Not authenticated. Please use auth_login tool to login.")

    logger.info("Starting TickTick MCP server...")

    # Run the server with FastMCP using stdio transport
    await server.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
