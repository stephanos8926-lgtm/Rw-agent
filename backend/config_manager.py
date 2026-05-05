import json
import os
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from copy import deepcopy

class ConfigManager:
    LAYER_WEIGHTS = {
        'base': 0,
        'workspace': 1,
        'task': 2,
        'user': 3
    }

    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.raw_configs = {}
        self.layer_configs = {layer: {} for layer in self.LAYER_WEIGHTS}
        self._resolved_config = {}
        
        # Ensure config dir exists
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        self.load_all_configs()
        self.start_watcher()

    def deep_update(self, d, u):
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self.deep_update(d.get(k, {}), v)
            else:
                d[k] = deepcopy(v)
        return d

    def resolve_configs(self):
        resolved = {}
        for layer in sorted(self.LAYER_WEIGHTS, key=self.LAYER_WEIGHTS.get):
            for path, conf in self.layer_configs[layer].items():
                if isinstance(conf, dict):
                    self.deep_update(resolved, conf)
        self._resolved_config = resolved

    def get_config(self, key=None, default=None):
        if key is None:
            return deepcopy(self._resolved_config)
        keys = key.split('.')
        val = self._resolved_config
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return deepcopy(val)

    def _determine_layer(self, filename):
        name = filename.lower()
        if 'user' in name: return 'user'
        if 'task' in name: return 'task'
        if 'workspace' in name: return 'workspace'
        return 'base'

    def load_all_configs(self):
        self.layer_configs = {layer: {} for layer in self.LAYER_WEIGHTS}
        self.raw_configs = {}
        for root, dirs, files in os.walk(self.config_dir):
            for file in files:
                if file.endswith(('.json', '.yaml', '.yml')):
                    path = os.path.join(root, file)
                    layer = self._determine_layer(file)
                    try:
                        with open(path, 'r') as f:
                            if file.endswith('.json'):
                                data = json.load(f)
                            else:
                                data = yaml.safe_load(f)
                            if not data:
                                data = {}
                            self.raw_configs[path] = data
                            self.layer_configs[layer][path] = data
                    except Exception as e:
                        logging.error(f"Error loading {path}: {e}")
        self.resolve_configs()
        logging.info("Configurations reloaded and conflicts resolved by layer.")

    def start_watcher(self):
        event_handler = ConfigHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.config_dir, recursive=True)
        self.observer.start()

class ConfigHandler(FileSystemEventHandler):
    def __init__(self, manager):
        self.manager = manager
    def on_modified(self, event):
        if not event.is_directory:
            logging.info(f"File {event.src_path} modified. Hot-reloading...")
            self.manager.load_all_configs()

