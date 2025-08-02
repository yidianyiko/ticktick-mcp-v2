# TickTick MCP v2

一个用于 TickTick 的模型上下文协议(MCP)服务器，允许您通过 Claude 和其他 MCP 客户端使用 v2 接口直接与您的 TickTick 任务管理系统进行交互。

## 项目目的

本项目旨在解决当前 TickTick MCP 领域的两个问题：

1. **复杂的身份验证**：v1 接口需要的身份验证方法过于繁杂，不如直接的账户密码。

2. **有限的API功能**：官方提供的 v1 API 接口，这些接口提供的功能有限，实现更复杂的功能比较繁琐。比如另外一个 ticktick mcp 甚至不能获取 Inbox 中的任务。

## 功能特性

- 📋 查看所有您的 TickTick 项目和任务
- ✏️ 通过自然语言创建新项目和任务
- 🔄 更新现有任务详情（标题、内容、日期、优先级）
- ✅ 将任务标记为完成
- 🗑️ 删除任务和项目
- 🔐 用户名/密码身份验证，本地凭证存储

## 快速开始

### 1. 安装依赖
```bash
git clone <repository-url>
cd ticktick-mcp-v2
# 初始化和更新Git子模块
git submodule update --init --recursive
uv pip install -r requirements.txt
```

### 2. 身份验证
```bash
uv run ticktick-mcp auth
```
按提示输入您的 TickTick 用户名和密码。凭证将保存在本地。

### 3. 测试配置
```bash
uv run ticktick-mcp test
```

### 4. 运行服务器
```bash
uv run ticktick-mcp run
```

## 与Claude Desktop集成

1. 编辑您的Claude Desktop配置文件：
   **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   **Linux:** `~/.config/Claude/claude_desktop_config.json`

2. 添加MCP服务器配置：

   **选项A：自动身份验证（推荐）**
   ```json
    {
      "mcpServers": {
        "ticktick-mcp-v2": {
          "command": "uvx",
          "args": ["--from", "ticktick-mcp-v2", "ticktick-mcp", "run"],
          "env": {
            "TICKTICK_USERNAME": "",
            "TICKTICK_PASSWORD": ""
          }
        }
      }
    }
   ```

## 可用的MCP工具

| 工具 | 描述 | 参数 |
|------|------|------|
| **身份验证** |
| `auth_status` | 检查身份验证状态 | 无 |
| **项目管理** |
| `get_projects` | 列出所有项目 | 无 |
| `get_project` | 获取项目详情 | `project_id` |
| `create_project` | 创建新项目 | `name`, `color` (可选), `view_mode` (可选) |
| `delete_project` | 删除项目 | `project_id` |
| `get_project_tasks` | 获取项目中的任务 | `project_id`, `include_completed` (可选) |
| **任务管理** |
| `get_tasks` | 列出所有任务 | `include_completed` (可选) |
| `create_task` | 创建新任务 | `title`, `project_id` (可选), `content` (可选), `start_date` (可选), `due_date` (可选), `priority` (可选) |
| `update_task` | 更新任务 | `task_id`, `project_id` (可选), `title` (可选), `content` (可选), `start_date` (可选), `due_date` (可选), `priority` (可选) |
| `delete_task` | 删除任务 | `project_id`, `task_id` |
| `complete_task` | 标记任务完成 | `task_id` |
| **高级功能** |
| `search_tasks` | 搜索任务 | `query` |
| `get_tasks_by_priority` | 按优先级获取任务 | `priority` (0=无, 1=低, 3=中, 5=高) |
| `get_tasks_due_today` | 获取今日到期任务 | 无 |
| `get_overdue_tasks` | 获取逾期任务 | 无 |

## 示例提示

- "显示我所有的 TickTick 项目"
- "创建一个名为'完成文档'的高优先级任务"
- "我今天有哪些到期的任务？"
- "将任务'买杂货'标记为完成"
- "更新任务'会议记录'的到期日期为明天"

## CLI命令

- `auth` - 与TickTick进行身份验证
- `run` - 运行MCP服务器
- `test` - 测试配置
- `logout` - 清除保存的凭证

### 运行测试
```bash
python -m pytest tests/
```

## 致谢

本项目离不开以下优秀开源项目的工作：

### 🎯 [ticktick-py](https://github.com/lazeroffmichael/ticktick-py)
**原作者**: [Michael Lazeroff](https://github.com/lazeroffmichael)  
**Fork维护者**: [yidianyiko](https://github.com/yidianyiko)

为这个MCP服务器提供动力的核心TickTick Python SDK。这个非官方的API库提供了对TickTick功能的全面访问，实现了与TickTick任务管理平台的无缝集成。

### 🤝 贡献

如果您觉得这个项目有用，请考虑：
- 🐛 报告问题或提出改进建议
- 📖 贡献代码

## 许可证

MIT许可证 - 详情请参阅LICENSE文件。 