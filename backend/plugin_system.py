import lupa
from lupa import LuaRuntime
import os
import json
import logging

class PluginSystem:
    def __init__(self, plugins_dir):
        self.plugins_dir = plugins_dir
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.plugins = {}
        self.load_plugins()

    def load_plugins(self):
        # Look in plugins_dir for directories, each with a manifest.json
        if not os.path.exists(self.plugins_dir):
            logging.warning(f"Plugins directory {self.plugins_dir} not found.")
            return
            
        for dir_name in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, dir_name)
            if os.path.isdir(plugin_path):
                manifest_path = os.path.join(plugin_path, "manifest.json")
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, 'r') as f:
                            manifest = json.load(f)
                            self._load_plugin(plugin_path, manifest)
                    except Exception as e:
                        logging.error(f"Error loading plugin {dir_name}: {e}")

    def _load_plugin(self, path, manifest):
        script_path = os.path.join(path, manifest.get("entry", "plugin.lua"))
        if os.path.exists(script_path):
            try:
                with open(script_path, 'r') as f:
                        script = f.read()
                        self.lua.execute(script)
                        self.plugins[manifest['name']] = manifest
            except Exception as e:
                logging.error(f"Error executing plugin script {script_path}: {e}")
        else:
            logging.error(f"Entry script not found for plugin: {manifest['name']}")
