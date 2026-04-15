import os
from src.core.logger import get_logger

logger = get_logger('agent.tools.file')


def read_file(file_path: str) -> dict:
    """
    Read contents of a file from the filesystem.

    Args:
        file_path: Absolute path to file to read

    Returns:
        dict with 'success' (bool), 'content' (str), and 'error' (str) if failed
    """
    logger.debug(f"Reading file: {file_path}")
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        logger.info(f"File read successfully: {file_path}")
        return {
            "success": True,
            "content": content
        }
    except PermissionError:
        logger.error(f"Permission denied: {file_path}")
        return {
            "success": False,
            "error": f"Permission denied: {file_path}"
        }
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Error reading file: {str(e)}"
        }


def write_file(file_path: str, content: str) -> dict:
    """
    Write or overwrite a file with new content.

    Args:
        file_path: Absolute path to file to write
        content: Content to write to file

    Returns:
        dict with 'success' (bool), 'error' (str) if failed
    """
    logger.debug(f"Writing file: {file_path}")
    try:
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"File written successfully: {file_path}")
        return {"success": True}
    except PermissionError:
        logger.error(f"Permission denied: {file_path}")
        return {
            "success": False,
            "error": f"Permission denied: {file_path}"
        }
    except Exception as e:
        logger.error(f"Error writing file: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Error writing file: {str(e)}"
        }


def edit_file(file_path: str, old_string: str, new_string: str) -> dict:
    """
    Edit a file by replacing specific text.

    Args:
        file_path: Absolute path to file to edit
        old_string: Text to replace
        new_string: New text to replace with

    Returns:
        dict with 'success' (bool), 'error' (str) if failed
    """
    logger.debug(f"Editing file: {file_path}")
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if old_string not in content:
            logger.error(f"Text not found in file: '{old_string[:50]}...'")
            return {
                "success": False,
                "error": f"Text not found in file: '{old_string[:50]}...'"
            }

        new_content = content.replace(old_string, new_string)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        logger.info(f"File edited successfully: {file_path}")
        return {"success": True}
    except PermissionError:
        logger.error(f"Permission denied: {file_path}")
        return {
            "success": False,
            "error": f"Permission denied: {file_path}"
        }
    except Exception as e:
        logger.error(f"Error editing file: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Error editing file: {str(e)}"
        }
