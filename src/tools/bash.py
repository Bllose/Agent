import subprocess
import re
from src.core.logger import get_logger

logger = get_logger('agent.tools.bash')


def _check_command_safety(command: str) -> tuple[bool, str | None]:
    """
    Check if a command contains dangerous operations.

    Args:
        command: Shell command to check

    Returns:
        tuple of (is_safe, error_message)
        If is_safe is True, error_message is None
        If is_safe is False, error_message contains the reason
    """
    # Normalize command for checking (lowercase, trim)
    normalized = command.lower().strip()

    # Define dangerous patterns and their descriptions
    dangerous_patterns = [
        # File deletion operations
        (r'\brm\s+.*-rf\b', 'Recursive force delete (rm -rf) is blocked for safety'),
        (r'\brm\s+.*-fr\b', 'Recursive force delete (rm -fr) is blocked for safety'),
        (r'\brm\s+.*-r\s+.*-f\b', 'Recursive force delete is blocked for safety'),
        (r'\brm\s+.*-f\s+.*-r\b', 'Recursive force delete is blocked for safety'),
        (r'\brm\s+.*\*/\b', 'Deleting all files recursively is blocked'),
        (r'\brmdir\s+.*/\b', 'Deleting directory recursively is blocked'),
        (r'\bdel\s+.*$', 'Deleting all files is blocked'),
        (r'\brm\s+-rf\s+/', 'Deleting root directory is blocked'),
        (r'\brm\s+-rf\s+\*\*', 'Deleting all files is blocked'),

        # System formatting/destruction
        (r'\bmkfs\b', 'Filesystem formatting is blocked'),
        (r'\bformat\b', 'Disk formatting is blocked'),
        (r'\bdd\s+.*of=.*\b', 'Direct disk write (dd) is blocked'),
        (r':\(\)\s*\{\s*:\|:&\s*\};\s*:', 'Fork bomb is blocked'),
        (r'\bwhile\s+true\s*;.*do.*:\|:&.*done\b', 'Fork bomb pattern detected'),

        # Permission escalation
        (r'\bsudo\s+rm\b', 'Sudo with delete commands is blocked'),
        (r'\bsudo\s+mkfs\b', 'Sudo with format commands is blocked'),
        (r'\bsudo\s+chmod\s+777\b', 'Setting world-writable permissions is blocked'),
        (r'\bsu\s+-\s+root\b', 'Switching to root is blocked'),
        (r'\bchmod\s+777\s+/\b', 'Making root world-writable is blocked'),
        (r'\bchmod\s+-R\s+777\b', 'Recursive chmod 777 is blocked'),

        # System shutdown/reboot
        (r'\breboot\b', 'System reboot is blocked'),
        (r'\bshutdown\b', 'System shutdown is blocked'),
        (r'\bpoweroff\b', 'System poweroff is blocked'),
        (r'\bhalt\b', 'System halt is blocked'),
        (r'\binit\s+0\b', 'System shutdown to runlevel 0 is blocked'),

        # System services
        (r'\bsystemctl\s+stop\b', 'Stopping system services is blocked'),
        (r'\bservice\s+\w+\s+stop\b', 'Stopping services is blocked'),
        (r'\bsystemctl\s+disable\b', 'Disabling system services is blocked'),

        # Network attacks
        (r'\bnmap\b', 'Network scanning (nmap) is blocked'),
        (r'\bnetcat\b', 'Netcat is blocked'),
        (r'\bnc\s+-l\b', 'Netcat listener is blocked'),

        # Process termination (all processes)
        (r'\bkillall\b', 'Killing all processes is blocked'),
        (r'\bkill\s+-9\s+-1\b', 'Killing all processes is blocked'),

        # Database destruction
        (r'\bdrop\s+database\b', 'Dropping databases is blocked'),
        (r'\bdrop\s+table\b', 'Dropping tables is blocked'),
        (r'\bdelete\s+from\b', 'DELETE without WHERE clause warning (use with caution)'),
        (r'\btruncate\s+table\b', 'Truncating tables is blocked'),

        # History manipulation
        (r'\bhistory\s+-c\b', 'Clearing shell history is blocked'),

        # User management
        (r'\buserdel\b', 'Deleting users is blocked'),
        (r'\buserdel\s+-r\b', 'Deleting users with home directory is blocked'),
        (r'\bgroupdel\b', 'Deleting groups is blocked'),

        # Password manipulation
        (r'\bpasswd\b', 'Changing passwords is blocked'),

        # Chain loading and bootloader
        (r'\bgrub-install\b', 'Installing GRUB bootloader is blocked'),
        (r'\bbootloader\b', 'Bootloader manipulation is blocked'),

        # Pipe to nothing (disk space exhaustion)
        (r':\s*>\s*/dev/null\s*:\s*', 'Disk space exhaustion pattern detected'),
        (r'\bwhile\s+true\s*;.*>\s*/dev/null', 'Disk space exhaustion pattern detected'),

        # Cryptocurrency mining indicators
        (r'\bminer\b', 'Cryptocurrency mining is blocked'),
        (r'\bcryptonight\b', 'Cryptocurrency mining is blocked'),
    ]

    # Check each dangerous pattern
    for pattern, description in dangerous_patterns:
        if re.search(pattern, normalized, re.IGNORECASE):
            logger.warning(f"Command blocked: {description} (command: {command[:50]}...)")
            return False, description

    # Special check for DELETE without WHERE (SQL injection prevention)
    if 'delete' in normalized and 'where' not in normalized and 'from' in normalized:
        logger.warning("DELETE without WHERE clause blocked")
        return False, 'DELETE command without WHERE clause is blocked'

    return True, None


def bash(command: str) -> dict:
    """
    Execute shell commands and get the output.

    Args:
        command: Shell command to execute

    Returns:
        dict with 'success' (bool), 'output' (str), 'error' (str)
    """
    logger.info(f"Executing command: {command[:100]}...")
    # Security check before execution
    is_safe, error_msg = _check_command_safety(command)
    if not is_safe:
        logger.error(f"Command blocked: {error_msg}")
        return {
            "success": False,
            "error": f"Command blocked: {error_msg}"
        }

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'  # 替换无法解码的字符而不是抛出异常
        )

        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"

        logger.info(f"Command completed with return code: {result.returncode}")
        return {
            "success": True,
            "output": output,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        logger.error("Command timed out after 30 seconds")
        return {
            "success": False,
            "error": "Command timed out after 30 seconds"
        }
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Error executing command: {str(e)}"
        }


if __name__ == "__main__":
    # Example usage
    command = "del C:\\*"
    blocked, description = _check_command_safety(command)
    print(blocked, description)