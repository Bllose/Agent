import subprocess


def bash(command: str) -> dict:
    """
    Execute shell commands and get the output.

    Args:
        command: Shell command to execute

    Returns:
        dict with 'success' (bool), 'output' (str), 'error' (str)
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"

        return {
            "success": True,
            "output": output,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out after 30 seconds"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error executing command: {str(e)}"
        }
