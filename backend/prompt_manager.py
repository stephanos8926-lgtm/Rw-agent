import os
import yaml
from pathlib import Path
import time

class SystemPromptManager:
    def __init__(self, config_dir: str = "backend/configs/system_prompts"):
        self.config_dir = Path(config_dir)
        self.prompts = {}
        self.last_modified = {}
        self._ensure_config_dir()
        self.reload_prompts()

    def _ensure_config_dir(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        default_prompt = self.config_dir / "default.yaml"
        if not default_prompt.exists():
            with open(default_prompt, 'w') as f:
                yaml.dump({
                    "name": "default",
                    "instruction": "You are a Senior Pair Programmer and Agentic OS assistant running on a headless Debian server. You have access to CLI tools. Always prioritize clarity, safety, and strict tool syntax over assumption. Before calling commands, verify tool usage."
                }, f)

    def reload_prompts(self):
        """Reads all yaml files in the config dir and updates memory."""
        for file_path in self.config_dir.glob("*.yaml"):
            mtime = os.path.getmtime(file_path)
            if file_path.name not in self.last_modified or self.last_modified[file_path.name] < mtime:
                with open(file_path, 'r') as f:
                    try:
                        data = yaml.safe_load(f)
                        if "instruction" in data:
                            self.prompts[file_path.stem] = data["instruction"]
                            self.last_modified[file_path.name] = mtime
                    except yaml.YAMLError as e:
                        print(f"Error loading {file_path.name}: {e}")

    def get_prompt(self, name: str = "default") -> str:
        """Gets a prompt. Checks for file changes on access (lazy hot-reload)."""
        prompt_path = self.config_dir / f"{name}.yaml"
        if prompt_path.exists():
            mtime = os.path.getmtime(prompt_path)
            if f"{name}.yaml" not in self.last_modified or self.last_modified[f"{name}.yaml"] < mtime:
                self.reload_prompts()
        return self.prompts.get(name, "You are a helpful AI assistant.")

# Global singleton
prompt_manager = SystemPromptManager()
