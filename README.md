# TickTick MCP v2

A Model Context Protocol (MCP) server for TickTick that enables interacting with your TickTick task management system directly through Claude and other MCP clients using v2 interfaces.

## Project Purpose

1. **Easy Authentication**: Direct username/password authentication.

2. **Rich API Functionality**: The v2 interfaces easy to implement more complex features. For example, other v1 TickTick interface cannot even retrieve tasks from the Inbox.

## Features

- 📋 View all your TickTick projects and tasks
- ✏️ Create new projects and tasks through natural language
- 🔄 Update existing task details (title, content, dates, priority)
- ✅ Mark tasks as complete
- 🗑️ Delete tasks and projects
- 🔐 Username/password authentication with local credential storage

## Quick Start

Create a `mcp.json` file:

```json
{
  "mcpServers": {
    "ticktick-mcp-v2": {
      "command": "uvx",
      "args": ["--from", "ticktick-mcp-v2", "ticktick-mcp", "run"],
      "env": {
        "TICKTICK_USERNAME": "your_username",
        "TICKTICK_PASSWORD": "your_password"
      }
    }
  }
}
```

### Start Using

You can now interact with your TickTick tasks directly! Try asking:
- "Show me all my TickTick projects"
- "Create a task called 'Finish documentation' with high priority"
- "What tasks do I have due today?"

## Development Setup

1. **Install and authenticate:**
   ```bash
   uvx --from ticktick-mcp-v2 ticktick-mcp auth
   ```

2. **Test the connection:**
   ```bash
   uvx --from ticktick-mcp-v2 ticktick-mcp test
   ```

3. **Run the server:**
   ```bash
   uvx --from ticktick-mcp-v2 ticktick-mcp run
   ```

## Usage Examples

### Using with other MCP clients
Any MCP-compatible client can connect using the configuration above.

## Available MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| **Authentication** |
| `auth_status` | Check authentication status | None |
| **Project Management** |
| `get_projects` | List all projects | None |
| `get_project` | Get project details | `project_id` |
| `create_project` | Create new project | `name`, `color` (optional), `view_mode` (optional) |
| `delete_project` | Delete project | `project_id` |
| `get_project_tasks` | Get tasks in project | `project_id`, `include_completed` (optional) |
| **Task Management** |
| `get_tasks` | List all tasks | `include_completed` (optional) |
| `create_task` | Create new task | `title`, `project_id` (optional), `content` (optional), `start_date` (optional), `due_date` (optional), `priority` (optional) |
| `update_task` | Update task | `task_id`, `project_id` (optional), `title` (optional), `content` (optional), `start_date` (optional), `due_date` (optional), `priority` (optional) |
| `delete_task` | Delete task | `project_id`, `task_id` |
| `complete_task` | Mark task complete | `task_id` |
| **Advanced Features** |
| `search_tasks` | Search tasks | `query` |
| `get_tasks_by_priority` | Get tasks by priority | `priority` (0=None, 1=Low, 3=Medium, 5=High) |
| `get_tasks_due_today` | Get tasks due today | None |
| `get_overdue_tasks` | Get overdue tasks | None |

## Example Prompts

- "Show me all my TickTick projects"
- "Create a task called 'Finish documentation' with high priority"
- "What tasks do I have due today?"
- "Mark the task 'Buy groceries' as complete"
- "Update task 'Meeting notes' with new due date tomorrow"

## Acknowledgments

This project would not be possible without the excellent work of the following open source projects:

### 🎯 [ticktick-py](https://github.com/lazeroffmichael/ticktick-py)
**Original Author**: [Michael Lazeroff](https://github.com/lazeroffmichael)  
**Fork Maintainer**: [yidianyiko](https://github.com/yidianyiko)

The core TickTick Python SDK that powers this MCP server. This unofficial API library provides comprehensive access to TickTick's functionality, enabling seamless integration with the TickTick task management platform.

### 🤝 Contributing

If you find this project useful, please consider:
- 🐛 Reporting issues or suggesting improvements
- 📖 Contributing 

## License

MIT License - see LICENSE file for details. 
