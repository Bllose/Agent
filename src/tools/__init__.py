from . import file, bash, todo


def get_all_tools():
    """
    Get all available tools with their schemas.
    Returns a list of tool definitions for the LLM.
    """
    return [
        {
            "name": "read_file",
            "description": "Read the contents of a file from the filesystem",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the file to read"
                    }
                },
                "required": ["file_path"]
            }
        },
        {
            "name": "write_file",
            "description": "Write or overwrite a file with new content",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["file_path", "content"]
            }
        },
        {
            "name": "edit_file",
            "description": "Edit a file by replacing specific text",
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the file to edit"
                    },
                    "old_string": {
                        "type": "string",
                        "description": "Text to replace"
                    },
                    "new_string": {
                        "type": "string",
                        "description": "New text to replace with"
                    }
                },
                "required": ["file_path", "old_string", "new_string"]
            }
        },
        {
            "name": "bash",
            "description": "Execute shell commands and get the output",
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute"
                    }
                },
                "required": ["command"]
            }
        },
        {
            "name": "todo_create",
            "description": "Create a new task list for tracking complex multi-step work",
            "input_schema": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string"},
                                "status": {
                                    "type": "string",
                                    "enum": ["pending", "in_progress", "completed"]
                                },
                                "activeForm": {
                                    "type": "string",
                                    "description": "Optional present-continuous label"
                                }
                            },
                            "required": ["content", "status"]
                        }
                    }
                },
                "required": ["items"]
            }
        },
        {
            "name": "todo_list",
            "description": "List all todo tasks with their current status",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "todo_next",
            "description": "Get the next pending or in-progress task to work on",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "todo_update",
            "description": "Update task status or properties",
            "input_schema": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to update"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                        "description": "New task status"
                    },
                    "content": {
                        "type": "string",
                        "description": "Task description"
                    },
                    "activeForm": {
                        "type": "string",
                        "description": "Present-continuous form label"
                    }
                },
                "required": ["task_id"]
            }
        },
        {
            "name": "todo_delete",
            "description": "Delete a todo task",
            "input_schema": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to delete"
                    }
                },
                "required": ["task_id"]
            }
        },
        {
            "name": "todo_clear",
            "description": "Clear all todo tasks",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "todo_reset_retry",
            "description": "Reset retry count for a specific task",
            "input_schema": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of task to reset retry count"
                    }
                },
                "required": ["task_id"]
            }
        },
        {
            "name": "todo_status",
            "description": "Get detailed status of a specific task",
            "input_schema": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of task to get status"
                    }
                },
                "required": ["task_id"]
            }
        }
    ]


def execute_tool(tool_name: str, tool_input: dict) -> dict:
    """
    Execute a tool by name with given input.

    Args:
        tool_name: Name of the tool to execute
        tool_input: Input parameters for the tool

    Returns:
        dict with tool execution result
    """
    if tool_name == "read_file":
        return file.read_file(**tool_input)
    elif tool_name == "write_file":
        return file.write_file(**tool_input)
    elif tool_name == "edit_file":
        return file.edit_file(**tool_input)
    elif tool_name == "bash":
        return bash.bash(**tool_input)
    elif tool_name == "todo_create":
        return todo.todo_create(**tool_input)
    elif tool_name == "todo_list":
        return todo.todo_list(**tool_input)
    elif tool_name == "todo_next":
        return todo.todo_next(**tool_input)
    elif tool_name == "todo_update":
        return todo.todo_update(**tool_input)
    elif tool_name == "todo_delete":
        return todo.todo_delete(**tool_input)
    elif tool_name == "todo_clear":
        return todo.todo_clear(**tool_input)
    elif tool_name == "todo_reset_retry":
        return todo.todo_reset_retry(**tool_input)
    elif tool_name == "todo_status":
        return todo.todo_status(**tool_input)
    else:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        }
