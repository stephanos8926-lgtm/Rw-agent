import json
import os
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

class ConfigManager:
    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.configs = {} # Dictionary of configs
        self.load_all_configs()
        self.start_watcher()

    def load_all_configs(self):
        # Walk directories and load
        # For simplicity, just load all compliant files
        for root, dirs, files in os.walk(self.config_dir):
            for file in files:
                if file.endswith(('.json', '.yaml', '.yml')):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r') as f:
                            if file.endswith('.json'):
                                self.configs[path] = json.load(f)
                            else:
                                self.configs[path] = yaml.safe_load(f)
                    except Exception as e:
                        logging.error(f"Error loading {path}: {e}")
        logging.info("Configurations reloaded.")

    def start_watcher(self):
        event_handler = ConfigHandler(self)
        observer = Observer()
        observer.schedule(event_handler, self.config_dir, recursive=True)
        observer.start()

class ConfigHandler(FileSystemEventHandler):
    def __init__(self, manager):
        self.manager = manager
    def on_modified(self, event):
        if not event.is_directory:
            logging.info(f"File {event.src_path} modified. Hot-reloading...")
            self.manager.load_all_configs()
