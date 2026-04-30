import json
import os
from typing import List, Dict, Any

class StatusManager:
    def __init__(self, status_file: str = ".docs/status-agentic-os.json"):
        self.status_file = status_file

    def _ensure_dir(self):
        os.makedirs(os.path.dirname(self.status_file), exist_ok=True)

    def read_status(self) -> str:
        if not os.path.exists(self.status_file):
            return json.dumps({
                "completed": [],
                "in_progress": [],
                "blocked": [],
                "next": [],
                "dependencies": {}
            }, indent=2)
        try:
            with open(self.status_file, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading status: {e}"

    def update_status(self, completed: List[str], in_progress: List[str], next_tasks: List[str], dependencies: Dict[str, List[str]] = None) -> str:
        self._ensure_dir()
        try:
            data = {
                "completed": completed,
                "in_progress": in_progress,
                "blocked": [],
                "next": next_tasks,
                "dependencies": dependencies or {}
            }
            with open(self.status_file, "w") as f:
                json.dump(data, f, indent=2)
            return "Status successfully updated."
        except Exception as e:
            return f"Error updating status: {e}"

status_manager = StatusManager()
