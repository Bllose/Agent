# AI Agent Project

This is an AI Agent project similar to Claude Code, designed to help with software engineering tasks.

## Project Overview

This Agent provides:
- Interactive CLI interface for AI-assisted coding
- Tool system for file operations, command execution, and web requests
- Memory system for context persistence
- Skill/Plugin system for extensibility
- Multiple LLM provider support

## Architecture

- **src/cli/** - Entry point and REPL loop
- **src/core/** - Core Agent logic and conversation management
- **src/tools/** - Callable tools (file, bash, search, web, etc.)
- **src/memory/** - Persistent memory storage
- **src/skills/** - Extensible skill system
- **src/llm/** - LLM client abstraction layer

## Development Guidelines

- Use Python to Developing
- Follow the existing directory structure
- Tools should be registered in src/tools/index.py
- Configuration lives in config/default.json
- System prompts in templates/system.md
