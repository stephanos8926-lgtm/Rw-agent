import os
import shutil
import json

class WorkspaceManager:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.current_workspace = "."

    def set_workspace(self, workspace_name):
        workspace_path = os.path.join(self.base_dir, workspace_name)
        if not os.path.exists(workspace_path):
            os.makedirs(workspace_path)
            self._initialize_workspace(workspace_path)
        self.current_workspace = workspace_path
        return workspace_path

    def _initialize_workspace(self, path):
        forge_dir = os.path.join(path, ".forge")
        os.makedirs(os.path.join(forge_dir, ".cache"))
        os.makedirs(os.path.join(forge_dir, "plugins"))
        with open(os.path.join(forge_dir, "settings.json"), "w") as f:
            json.dump({}, f)

    def get_workspace_dir(self):
        return self.current_workspace

workspace_manager = WorkspaceManager(os.getcwd())
