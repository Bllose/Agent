import os


def read_file(file_path: str) -> dict:
    """
    Read the contents of a file from the filesystem.

    Args:
        file_path: Absolute path to the file to read

    Returns:
        dict with 'success' (bool), 'content' (str), and 'error' (str) if failed
    """
    try:
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            "success": True,
            "content": content
        }
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: {file_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error reading file: {str(e)}"
        }


def write_file(file_path: str, content: str) -> dict:
    """
    Write or overwrite a file with new content.

    Args:
        file_path: Absolute path to the file to write
        content: Content to write to the file

    Returns:
        dict with 'success' (bool), 'error' (str) if failed
    """
    try:
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return {"success": True}
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: {file_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error writing file: {str(e)}"
        }


def edit_file(file_path: str, old_string: str, new_string: str) -> dict:
    """
    Edit a file by replacing specific text.

    Args:
        file_path: Absolute path to the file to edit
        old_string: Text to replace
        new_string: New text to replace with

    Returns:
        dict with 'success' (bool), 'error' (str) if failed
    """
    try:
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if old_string not in content:
            return {
                "success": False,
                "error": f"Text not found in file: '{old_string[:50]}...'"
            }

        new_content = content.replace(old_string, new_string)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return {"success": True}
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: {file_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error editing file: {str(e)}"
        }
