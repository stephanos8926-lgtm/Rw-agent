import os
import json
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from pydantic import BaseModel, Field, ValidationError, create_model
from typing import Dict, Any, List

class MCPToolSchema(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    implementation: str = Field(description="Command to run or function to call")

from backend.tool_validator import ToolValidator

class MCPLoader:
    def __init__(self, directory):
        self.directory = directory
        self.tools = {}
        self.models = {}

    def load_tools(self):
        self.tools = {}
        self.models = {}
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        
        for filename in os.listdir(self.directory):
            if filename.endswith(".yaml"):
                try:
                    with open(os.path.join(self.directory, filename), 'r') as f:
                        tool_config = yaml.safe_load(f)
                        name = tool_config['name']
                        self.tools[name] = tool_config
                        
                        # Use ToolValidator to pre-compile Pydantic models
                        if "parameters" in tool_config:
                            self.models[name] = ToolValidator.create_model_from_schema(
                                name, 
                                tool_config["parameters"]
                            )
                except Exception as e:
                    print(f"Error loading MCP tool {filename}: {e}")
                    
        print(f"Loaded {len(self.tools)} validated MCP tools.")

    def validate_input(self, tool_name: str, input_data: Dict[str, Any]):
        if tool_name in self.models:
            # Validate using the Pydantic model and return dumped dict
            return self.models[tool_name](**input_data).model_dump()
        return input_data

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
