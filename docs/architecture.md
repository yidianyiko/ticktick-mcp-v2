# TickTick MCP v2 Architecture

## Project Overview

TickTick MCP v2 is a Model Context Protocol (MCP) based TickTick task management integration server, **completely implemented based on the `ticktick.py` library**, providing seamless integration with Claude and other MCP clients.

## Architecture Design Principles

1. **Based on Mature Libraries**: Completely based on `ticktick.py` library, avoiding reinventing the wheel
2. **Username/Password Authentication**: Uses native authentication method of `ticktick.py` library
3. **Lightweight**: Focuses on MCP tool definition and interface adaptation
4. **Easy to Maintain**: Clear module division, easy to extend and debug
5. **User-Friendly**: Simple authentication and configuration management

## Directory Structure

```
ticktick-mcp-v2/
├── src/                          # Source code directory
│   ├── adapters/                 # Adapter layer
│   │   ├── __init__.py
│   │   └── client.py            # TickTick client adapter (based on ticktick.py)
│   ├── tools/                    # MCP tools layer
│   │   ├── __init__.py
│   │   ├── projects.py          # Project-related MCP tools
│   │   ├── tasks.py             # Task-related MCP tools
│   │   └── auth.py              # Authentication-related MCP tools
│   ├── utils/                    # Utility functions layer
│   │   ├── __init__.py
│   │   └── helpers.py           # Helper functions
│   ├── auth.py                   # Authentication module (based on ticktick.py)
│   ├── server.py                 # MCP server main file
│   └── cli.py                    # Command line interface
├── tests/                        # Test directory
│   ├── test_auth.py             # Authentication tests
│   ├── test_mcp_integration.py  # MCP integration tests
│   ├── test_ticktick_integration.py # TickTick integration tests
│   ├── simple_server.py         # Simple server tests
│   └── integration/             # Integration tests
├── docs/                         # Documentation directory
│   ├── architecture.md          # Architecture documentation
│   ├── api.md                   # API documentation
│   └── usage.md                 # Usage guide
├── requirements.txt              # Project dependencies
├── pyproject.toml               # Project configuration
└── README.md                    # Project description
```

## Architecture Layers

### 1. Authentication Layer
- **Responsibility**: Username/password authentication based on `ticktick.py` library
- **Components**:
  - `auth.py`: Authentication manager, uses `TickTickClient(username, password)`
  - `tools/auth.py`: Authentication-related MCP tools

### 2. Adapter Layer
- **Responsibility**: Encapsulates `ticktick.py` client, provides unified interface
- **Components**:
  - `client.py`: Client adapter based on `ticktick.py`

### 3. Tools Layer
- **Responsibility**: Defines and implements MCP tools
- **Components**:
  - `projects.py`: Project-related MCP tools (uses `client.project`)
  - `tasks.py`: Task-related MCP tools (uses `client.task`)
  - `auth.py`: Authentication-related MCP tools

### 4. Utility Functions Layer
- **Responsibility**: General utility functions
- **Components**:
  - `helpers.py`: Helper functions

### 5. Server Layer
- **Responsibility**: MCP server main program
- **Components**:
  - `server.py`: MCP server implementation

## Technology Stack

- **Python 3.10+**: Main development language
- **MCP 1.2+**: Model Context Protocol
- **ticktick.py**: TickTick Python SDK (complete integration)
- **Username/Password Authentication**: Authentication method based on ticktick.py library

## Core Features

### 1. Authentication Features
- Username/password login (based on `ticktick.py` library)
- Local credential storage
- Automatic session management
- Authentication status checking

### 2. Project Management
- Get project list (uses `client.state['projects']`)
- Get project details 