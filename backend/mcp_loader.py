import os
import json
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class MCPLoader:
    def __init__(self, directory):
        self.directory = directory
        self.tools = {}

    def load_tools(self):
        self.tools = {}
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        
        for filename in os.listdir(self.directory):
            if filename.endswith(".yaml"):
                with open(os.path.join(self.directory, filename), 'r') as f:
                    tool_config = yaml.safe_load(f)
                    self.tools[tool_config['name']] = tool_config
        print(f"Loaded {len(self.tools)} MCP tools.")

class MCPHandler(FileSystemEventHandler):
    def __init__(self, loader):
        self.loader = loader

    def on_modified(self, event):
        if event.src_path.endswith(".yaml"):
            print(f"Detected change in {event.src_path}. Reloading tools...")
            self.loader.load_tools()

def start_mcp_loader(directory):
    loader = MCPLoader(directory)
    loader.load_tools()
    
    observer = Observer()
    handler = MCPHandler(loader)
    observer.schedule(handler, directory, recursive=False)
    observer.start()
    return loader
