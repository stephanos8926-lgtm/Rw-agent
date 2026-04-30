import subprocess
from typing import List, Dict, Any, Optional

# Define allowed commands and their required permissions level
ALLOWED_COMMANDS = {
    "ls": {"required_level": "basic"},
    "grep": {"required_level": "basic"},
    "cat": {"required_level": "basic"},
    "git": {"required_level": "basic"},
    "npm": {"required_level": "basic"},
    "rm": {"required_level": "admin"}, # Sensitive
    "chmod": {"required_level": "admin"}, # Sensitive
}

def execute_safely(command: List[str], admin_approved: bool = False) -> Dict[str, Any]:
    """
    Executes a shell command if allowed, 
    triggering an approval workflow for sensitive operations.
    """
    cmd_name = command[0]
    
    if cmd_name not in ALLOWED_COMMANDS:
        return {"success": False, "error": f"Command '{cmd_name}' not allowed."}
        
    policy = ALLOWED_COMMANDS[cmd_name]
    
    if policy["required_level"] == "admin" and not admin_approved:
        return {"success": False, "error": f"Command '{cmd_name}' requires admin approval."}
        
    result = subprocess.run(command, capture_output=True, text=True)
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr
    }
