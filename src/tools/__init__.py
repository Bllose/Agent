from . import file, bash


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
    else:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        }
