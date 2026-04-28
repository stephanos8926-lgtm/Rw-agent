import subprocess
import os
import time
import hashlib
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field
from backend.status_manager import status_manager
from backend.ast_parser import build_ast_symbol_map, SymbolMapArgs
import platform
import psutil

# Simple in-memory cache for tool outputs
tool_cache = {}

def cache_tool(ttl_seconds=5):
    """Decorator to cache tool outputs for a short period."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create a unique key for the call
            key = hashlib.sha256(str((func.__name__, args, kwargs)).encode()).hexdigest()
            current_time = time.time()
            
            if key in tool_cache:
                result, timestamp = tool_cache[key]
                if current_time - timestamp < ttl_seconds:
                    return result
            
            result = func(*args, **kwargs)
            tool_cache[key] = (result, current_time)
            return result
        return wrapper
    return decorator

class FileReadArgs(BaseModel):
    filepath: str = Field(description="The absolute or relative path to the file to read. E.g., 'src/main.py' or '/etc/os-release'.")
    start_line: int = Field(description="Optional. The line to start reading from (1-indexed).", default=None)
    end_line: int = Field(description="Optional. The line to end reading at (inclusive, 1-indexed).", default=None)

class FileWriteArgs(BaseModel):
    filepath: str = Field(description="The absolute or relative path to the file to write.")
    content: str = Field(description="The content to write to the file.")
    overwrite: bool = Field(description="Whether to overwrite if the file exists.", default=False)

class WriteMultipleFilesArgs(BaseModel):
    files: Dict[str, str] = Field(description="A dictionary mapping filepaths to their content.")

class DocumentParseArgs(BaseModel):
    filepath: str = Field(description="The path to the document to parse.")

class PytestArgs(BaseModel):
    directory: str = Field(description="The directory containing tests to run.", default="tests")

class DebugArgs(BaseModel):
    script_path: str = Field(description="The path to the Python script to debug.")

class ShellExecArgs(BaseModel):
    command: str = Field(description="The exact shell command to execute in the system terminal (e.g., 'ls -la', 'cat file.txt', 'python script.py').")

class ListFilesArgs(BaseModel):
    directory: str = Field(description="The target directory path to list files from. Defaults to current directory ('.').", default=".")
    max_depth: int = Field(description="The maximum directory depth to recurse into. Limits output size. Default is 2.", default=2)

def list_files(directory: str = ".", max_depth: int = 2) -> str:
    """Lists files in a directory up to a max_depth."""
    try:
        output = []
        base_depth = directory.rstrip(os.sep).count(os.sep)
        for root, dirs, files in os.walk(directory):
            current_depth = root.count(os.sep) - base_depth
            if current_depth >= max_depth:
                del dirs[:]
            indent = '  ' * current_depth
            output.append(f"{indent}{os.path.basename(root)}/")
            subindent = '  ' * (current_depth + 1)
            for f in files:
                output.append(f"{subindent}{f}")
        return "\n".join(output)
    except Exception as e:
        return f"Error listing files: {str(e)}"

class RipgrepArgs(BaseModel):
    query: str = Field(description="The text pattern to search for.")
    path: str = Field(description="The directory path to search in. Defaults to current directory ('.').", default=".")
    include_pattern: str = Field(description="Optional file pattern to include (e.g., '*.py').", default=None)

def run_ripgrep(query: str, path: str = ".", include_pattern: str = None) -> str:
    """Searches for a pattern using ripgrep (`rg`) or falls back to `grep`."""
    command = "rg"
    # Fallback check
    if subprocess.run(["which", "rg"], capture_output=True).returncode != 0:
        command = "grep -r"
    
    full_command = f"{command} '{query}' {path}"
    if include_pattern:
        if command == "rg":
            full_command += f" -g '{include_pattern}'"
        else:
            # grep doesn't support -g natively, this is a simplification
            full_command += f" --include='{include_pattern}'"
            
    return execute_shell(full_command)

@cache_tool(ttl_seconds=5)
def get_os_info() -> str:
    """Gets operating system and hardware info."""
    try:
        info = []
        info.append(f"OS: {platform.system()} {platform.release()}")
        info.append(f"Architecture: {platform.machine()}")
        info.append(f"CPU Cores (Logical): {psutil.cpu_count()}")
        info.append(f"Memory Total: {psutil.virtual_memory().total / (1024**3):.2f} GB")
        info.append(f"Memory Available: {psutil.virtual_memory().available / (1024**3):.2f} GB")
        return "\n".join(info)
    except Exception as e:
        return f"Error getting OS info: {str(e)}"

def read_file(filepath: str, start_line: int = None, end_line: int = None) -> str:
    """Reads the contents of a file, optionally restricted to a line range."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if start_line is not None or end_line is not None:
            # Handle 1-indexing and defaults
            start = (start_line - 1) if start_line is not None else 0
            end = end_line if end_line is not None else len(lines)
            lines = lines[max(0, start):min(len(lines), end)]
            
        return "".join(lines)
    except FileNotFoundError:
        return f"Error: File not found at {filepath}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(filepath: str, content: str, overwrite: bool = False) -> str:
    """Writes content to a file, optionally overwriting."""
    if os.path.exists(filepath) and not overwrite:
        return f"Error: File already exists at {filepath}. Set overwrite=True to replace."
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {filepath}."
    except Exception as e:
        return f"Error writing file: {str(e)}"

def write_multiple_files(files: Dict[str, str]) -> str:
    """Writes multiple files in a batch."""
    results = []
    for filepath, content in files.items():
        results.append(write_file(filepath, content, overwrite=True))
    return "\n".join(results)

def parse_document(filepath: str) -> str:
    """Parses a document (PDF, DOCX, etc.) using LlamaParse."""
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    if not api_key:
        return "Error: LlamaParse is not configured. LLAMA_CLOUD_API_KEY is not set."
    try:
        from llama_parse import LlamaParse
        parser = LlamaParse(api_key=api_key)
        result = parser.load_data(filepath)
        return "\n".join([doc.text for doc in result])
    except Exception as e:
        return f"Error parsing document: {str(e)}"

def run_tests(directory: str = "tests") -> str:
    """Runs pytest in the specified directory."""
    import sys
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", directory],
            capture_output=True,
            text=True
        )
        return f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    except Exception as e:
        return f"Error running tests: {str(e)}"

def debug_script(script_path: str) -> str:
    """Runs a Python script in a tracing mode to debug execution."""
    import sys
    import traceback
    
    output = []
    def trace_calls(frame, event, arg):
        if event == 'call':
            output.append(f"Calling: {frame.f_code.co_name} in {frame.f_code.co_filename}")
        return trace_calls

    try:
        sys.settrace(trace_calls)
        exec(open(script_path).read())
        sys.settrace(None)
        return "\n".join(output)
    except Exception:
        sys.settrace(None)
        return traceback.format_exc()

@cache_tool(ttl_seconds=5)
def execute_shell(command: str) -> str:
    """
    Executes a shell command.
    WARNING: This executes directly on the OS. Needs strict sandboxing in production.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            timeout=30 # 30s timeout to prevent hanging commands
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]:\n{result.stderr}"
        
        # Cap output length to avoid context window explosion
        max_length = 4000
        if len(output) > max_length:
            return output[:max_length] + f"\n... (truncated {len(output) - max_length} chars)"
            
        return output or "[Command executed successfully with no output]"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error executing shell command: {str(e)}"

# LangGraph tool definitions
class UpdateStatusArgs(BaseModel):
    completed: list[str] = Field(description="List of completed task IDs")
    in_progress: list[str] = Field(description="List of in-progress task IDs")
    next_tasks: list[str] = Field(description="List of next task IDs to be done")

TOOLS_REGISTRY = {
    "read_file": read_file,
    "write_file": write_file,
    "write_multiple_files": write_multiple_files,
    "execute_shell": execute_shell,
    "run_tests": run_tests,
    "debug_script": debug_script,
    "get_symbol_map": build_ast_symbol_map,
    "list_files": list_files,
    "run_ripgrep": run_ripgrep,
    "get_os_info": get_os_info,
    "read_status": status_manager.read_status,
    "update_status": status_manager.update_status
}

if os.environ.get("LLAMA_CLOUD_API_KEY"):
    TOOLS_REGISTRY["parse_document"] = parse_document

class EmptyArgs(BaseModel):
    pass

TOOLS_METADATA = [
    {
        "name": "read_file",
        "description": "Reads the text content of a specified local file, optionally restricted to a range of lines. Use this to inspect code, configuration, or data files.",
        "parameters": FileReadArgs.model_json_schema()
    },
    {
        "name": "write_file",
        "description": "Writes text content to a specified local file. Use this for creating or updating files.",
        "parameters": FileWriteArgs.model_json_schema()
    },
    {
        "name": "write_multiple_files",
        "description": "Writes text content to multiple specified local files in a batch. Use this for creating or updating multiple files at once.",
        "parameters": WriteMultipleFilesArgs.model_json_schema()
    },
]

if os.environ.get("LLAMA_CLOUD_API_KEY"):
    TOOLS_METADATA.append({
        "name": "parse_document",
        "description": "Parses diverse document types (PDF, DOCX) into text for agent processing using LlamaParse.",
        "parameters": DocumentParseArgs.model_json_schema()
    })

TOOLS_METADATA.extend([
    {
        "name": "run_tests",
        "description": "Runs a pytest suite against a directory to automatically verify code changes.",
        "parameters": PytestArgs.model_json_schema()
    },
    {
        "name": "debug_script",
        "description": "Executes a Python script with basic call tracing for debugging and variable inspection.",
        "parameters": DebugArgs.model_json_schema()
    },
    {
        "name": "execute_shell",
        "description": "Executes a shell command on the underlying Debian OS and returns the stdout/stderr. Use for system administration, package management, running scripts, or interacting with the environment.",
        "parameters": ShellExecArgs.model_json_schema()
    },
    {
        "name": "get_symbol_map",
        "description": "Parses Python, JavaScript, and TypeScript files in a target directory to build a symbol graph containing classes and functions. Use this to understand codebase architecture across multiple languages without reading every file.",
        "parameters": SymbolMapArgs.model_json_schema()
    },
    {
        "name": "list_files",
        "description": "Recursively lists files and directories from a starting path up to a maximum depth. Use this to explore project structure and find relevant files.",
        "parameters": ListFilesArgs.model_json_schema()
    },
    {
        "name": "run_ripgrep",
        "description": "Search for a text pattern in files using ripgrep (or grep fallback). Use this for codebase-wide code searches.",
        "parameters": RipgrepArgs.model_json_schema()
    },
    {
        "name": "get_os_info",
        "description": "Retrieves critical operating system details, including platform, architecture, CPU logical cores, and available memory. Use this to understand the execution environment.",
        "parameters": EmptyArgs.model_json_schema()
    },
    {
        "name": "read_status",
        "description": "Reads the current project status from .docs/status-agentic-os.json to maintain long-horizon context.",
        "parameters": EmptyArgs.model_json_schema()
    },
    {
        "name": "update_status",
        "description": "Updates the project status file to keep track of completed, in-progress, and next tasks across long-horizon interactions.",
        "parameters": UpdateStatusArgs.model_json_schema()
    }
])
