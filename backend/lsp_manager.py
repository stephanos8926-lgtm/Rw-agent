import subprocess
import json
from .message_bus import message_bus

class LSPManager:
    """
    Manages Language Server Protocol / typescript compilation error streams.
    Feeds them into the agent memory or message bus.
    """
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir

    def run_type_check(self):
        diagnostics = []
        
        # 1. TypeScript Check
        try:
            result = subprocess.run(
                ["npx", "tsc", "--noEmit"], 
                cwd=self.workspace_dir, 
                capture_output=True, 
                text=True
            )
            if result.returncode != 0:
                diagnostics.append(f"--- TypeScript Errors ---\n{result.stdout}")
        except Exception as e:
            pass # tsc might not be initialized yet

        # 2. Python Check (Syntax only)
        try:
            # Find all .py files and check syntax
            result = subprocess.run(
                ["python3", "-m", "compileall", "-q", "."],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                diagnostics.append(f"--- Python Syntax Errors ---\n{result.stderr}")
        except Exception:
            pass

        if diagnostics:
            combined = "\n\n".join(diagnostics)
            message_bus.publish("lsp_errors", {"errors": combined})
            return combined
        
        message_bus.publish("lsp_clear", {})
        return None

lsp_manager = LSPManager(".")
