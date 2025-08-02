# TickTick MCP v2

A Model Context Protocol (MCP) server for TickTick that enables interacting with your TickTick task management system directly through Claude and other MCP clients.

## Features

- 📋 View all your TickTick projects and tasks
- ✏️ Create new projects and tasks through natural language
- 🔄 Update existing task details (title, content, dates, priority)
- ✅ Mark tasks as complete
- 🗑️ Delete tasks and projects
- 🔐 Username/password authentication with local credential storage

## Quick Start

### 1. Install Dependencies
```bash
git clone <repository-url>
cd ticktick-mcp-v2
# Initialize and update Git submodules
git submodule update --init --recursive
uv pip install -r requirements.txt
```

### 2. Authenticate
```bash
uv run ticktick-mcp auth
```
Enter your TickTick username and password when prompted. Credentials will be saved locally.

### 3. Test Configuration
```bash
uv run ticktick-mcp test
```

### 4. Run Server
```bash
uv run ticktick-mcp run
```

## Integration with Claude Desktop

1. Edit your Claude Desktop configuration file:
   **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the MCP server configuration:

   **Option 1: Auto-authentication (Recommended)**
   ```json
   {
     "mcpServers": {
       "ticktick-mcp-v2": {
         "command": "uv",
         "args": [
           "run",
           "--directory", 
           "/absolute/path/to/your/ticktick-mcp-v2",
           "ticktick-mcp",
           "run"
         ],
         "env": {
           "TICKTICK_USERNAME": "your_username_here",
           "TICKTICK_PASSWORD": "your_password_here"
         }
       }
     }
   }
   ```

   **Option 2: Manual authentication**
   ```json
   {
     "mcpServers": {
       "ticktick-mcp-v2": {
         "command": "uv",
         "args": [
           "run",
           "--directory", 
           "/absolute/path/to/your/ticktick-mcp-v2",
           "ticktick-mcp",
           "run"
         ]
       }
     }
   }
   ```

3. Restart Claude Desktop

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

## CLI Commands

- `auth` - Authenticate with TickTick
- `run` - Run the MCP server
- `test` - Test configuration
- `logout` - Clear saved credentials

## Authentication

This server supports multiple authentication methods:

1. **CLI Authentication** (Primary): `uv run ticktick-mcp auth`
2. **Environment Variables**: Set `TICKTICK_USERNAME` and `TICKTICK_PASSWORD`
3. **MCP Config**: Add credentials in Claude Desktop config
4. **Local Storage**: Credentials saved to `~/.ticktick-mcp/credentials.json`

### Running Tests
```bash
python -m pytest tests/
```
## Acknowledgments

This project would not be possible without the excellent work of the following open source projects:

### 🎯 [ticktick-py](https://github.com/lazeroffmichael/ticktick-py)
**Original Author**: [Michael Lazeroff](https://github.com/lazeroffmichael)  
**Fork Maintainer**: [yidianyiko](https://github.com/yidianyiko)

The core TickTick Python SDK that powers this MCP server. This unofficial API library provides comprehensive access to TickTick's functionality, enabling seamless integration with the TickTick task management platform.


### 🤝 Contributing

If you find this project useful, please consider:
- ⭐ Starring the maintained [fork repository](https://github.com/yidianyiko/ticktick-py)
- 🐛 Reporting issues or suggesting improvements
- 📖 Contributing to documentation

## License

MIT License - see LICENSE file for details. 