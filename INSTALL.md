# Agent Installation Guide

## Prerequisites

- Python 3.10 or higher
- Anthropic API key

## Setup

1. Install dependencies:
   ```bash
   pip install -e .
   ```

2. Create configuration file:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` file with your settings:
   ```bash
   # Anthropic API Configuration
   ANTHROPIC_API_KEY=your_api_key_here
   ANTHROPIC_BASE_URL=https://api.anthropic.com

   # Model Configuration
   MODEL=claude-sonnet-4-6
   MAX_TOKENS=4096
   ```

4. Run the agent:
   ```bash
   python -m src.cli.main
   ```

## Usage

The agent starts an interactive REPL where you can give it commands:

```
>>> List files in current directory

>>> Read the content of README.md

>>> Create a Python file that prints hello world
```

Type `exit` or `quit` to leave the agent.

## Configuration Options

All configuration is done via the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Required |
| `ANTHROPIC_BASE_URL` | Anthropic API base URL | https://api.anthropic.com |
| `MODEL` | Model to use | claude-sonnet-4-6 |
| `MAX_TOKENS` | Maximum tokens for responses | 4096 |

## Available Tools

- **read_file**: Read file contents
- **write_file**: Write or overwrite files
- **edit_file**: Edit files by replacing text
- **bash**: Execute shell commands
