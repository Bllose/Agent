# Agent

An intelligent AI Agent project, similar to Claude Code, designed to assist with software engineering tasks.

## ✨ Features

- 🤖 **Interactive CLI** - Interact with the Agent using natural language
- 🛠️ **Rich Toolset** - File operations, command execution, task management, and more
- 📝 **Autonomous Task Planning** - Todo system allows the Agent to autonomously break down and complete complex tasks
- 🔄 **SubAgent Collaboration** - SubAgent support for parallel execution of independent tasks
- 💾 **Persistent Memory** - Save conversation history and task states
- 🔌 **Extensible Architecture** - Support for custom skills and plugins
- 📊 **Dynamic Context** - Automatic injection of current date, working directory, and other information

## 🚀 Quick Start

### Requirements

- Python 3.10 or higher
- Anthropic API Key

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd Agent
```

2. Install dependencies
```bash
pip install -e .
```

3. Configure environment variables
```bash
cp .env.example .env
# Edit the .env file and enter your ANTHROPIC_API_KEY
```

4. Start the Agent
```bash
python -m src.cli.main
```

## 📖 Usage Examples

### Basic Tool Usage

```
>>> List files in the current directory
>>> Read the content of README.md
>>> Create a Python file that prints "Hello World"
```

### Todo Task Management

The Agent can autonomously plan and execute complex tasks:

```
>>> Help me refactor the code structure of this project, including:
    1. Analyze existing code
    2. Design new directory structure
    3. Refactor code
    4. Update documentation
```

The Agent will automatically create a task plan and execute it step by step:

![Todo Work Flow](resources/pics/AI_Agent_todo_work.gif)

### SubAgent Parallel Execution

When encountering tasks that can be handled independently, the Agent will spawn SubAgents to execute them in parallel:

```
>>> Scan the project for security issues and fix them
    - Subtask: Static analysis of code vulnerabilities
    - Subtask: Check dependency security
    - Subtask: Generate security report
```

The Agent possesses self-evolution and optimization capabilities:

![Agent Self-Improvement](resources/pics/Agent自我进化.png)

## 🏗️ Project Architecture

```
Agent/
├── src/
│   ├── cli/           # CLI entry point and REPL loop
│   ├── core/          # Core Agent logic
│   │   ├── agent.py   # Agent main class
│   │   ├── loop.py    # Conversation loop
│   │   └── logger.py  # Logging system
│   ├── tools/         # Tool implementations
│   │   ├── file.py    # File operations
│   │   ├── bash.py    # Command execution
│   │   ├── todo.py    # Task management
│   │   └── sub_agent.py # Sub-agent
│   ├── memory/        # Persistent memory
│   ├── skills/        # Extensible skills
│   └── llm/           # LLM client abstraction layer
├── templates/
│   └── system.md      # System prompt template
├── tests/             # Test files
├── docs/              # Project documentation
└── config/            # Configuration files
```

## 🛠️ Available Tools

### File Operations
- `read_file` - Read file contents
- `write_file` - Write to or overwrite a file
- `edit_file` - Replace specific text in a file

### System Operations
- `bash` - Execute Shell commands

### Task Management
- `todo_create` - Create task list
- `todo_list` - List all tasks
- `todo_next` - Get next pending task
- `todo_update` - Update task status
- `todo_delete` - Delete task
- `todo_clear` - Clear all tasks
- `todo_reset_retry` - Reset task retry count
- `todo_status` - Get task details

### Collaboration Tools
- `sub_agent` - Spawn sub-agent for independent task execution

## ⚙️ Configuration

Configure in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key | Required |
| `ANTHROPIC_BASE_URL` | API base URL | https://api.anthropic.com |
| `MODEL` | Model to use | claude-sonnet-4-6 |
| `MAX_TOKENS` | Maximum response tokens | 4096 |

Available models:
- `claude-opus-4-6`
- `claude-sonnet-4-6`
- `claude-haiku-4-5-20251001`

## 📝 Development Guide

- Develop with Python 3.10+
- Follow existing directory structure
- Implement new tools in `src/tools/`
- Register tools in `src/tools/__init__.py`
- System prompt template in `templates/system.md`
- Configuration in `.env` file

## 🔗 Related Documentation

- [Installation Guide](INSTALL.md)
- [Development Documentation](CLAUDE.md)

## 📄 License

[LICENSE](LICENSE)
