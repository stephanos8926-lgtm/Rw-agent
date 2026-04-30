import os
from typing import List

# Approved workspaces for filesystem operations
ALLOWED_WORKSPACES = ["/app/src", "/app/backend", "/app/tests"]

# Deny-by-default whitelist for shell commands
COMMAND_WHITELIST = ["ls", "cat", "grep", "python", "pytest", "git", "rg"]

def is_path_safe(path: str) -> bool:
    """Verifies that a resolved path is within allowed workspaces."""
    try:
        resolved_path = os.path.realpath(os.path.abspath(path))
        return any(resolved_path.startswith(os.path.realpath(os.path.abspath(w))) for w in ALLOWED_WORKSPACES)
    except Exception:
        return False

def validate_shell_command(command: str) -> bool:
    """Stub for complex command validation logic."""
    dangerous_commands = ["rm -rf", "sudo", "shutdown", "reboot", "chmod", "chown"]
    return not any(dangerous in command for dangerous in dangerous_commands)

def is_command_whitelisted(command: str) -> bool:
    """Checks if the command is in the whitelist."""
    # Simple check: take the first part of the command as the program
    program = command.split()[0]
    return program in COMMAND_WHITELIST

def human_approval_gate(tool_name: str, args: dict) -> bool:
    """
    Stub for human-in-the-loop logic.
    For now, return False, indicating approval is REQUIRED. 
    In the future, this would integrate with the UI to prompt for user choice.
    """
    # For mission-critical tools (e.g. refactor_rename or git_patch), we always want to ask
    restricted_tools = ["refactor_rename", "apply_git_patch", "execute_shell"]
    if tool_name in restricted_tools:
        return False
    return True
