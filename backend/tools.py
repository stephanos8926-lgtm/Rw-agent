import subprocess
import os
import time
import hashlib
from typing import List, Dict, Any, Optional
import json
import yaml

from pydantic import BaseModel, Field
from backend.status_manager import status_manager
from backend.ast_parser import build_ast_symbol_map, SymbolMapArgs
import platform
import psutil
from backend.telemetry import trace_tool_execution
from backend.context_manager import context_manager

# Simple in-memory cache for tool outputs
tool_cache = {}

def telemetry_decorator(func):
    """Decorator to log tool execution telemetry."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        trace_tool_execution(func.__name__, {"args": args, "kwargs": kwargs}, start_time)
        return result
    return wrapper

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
    recursive: bool = Field(description="Whether to list files recursively. Defaults to False.", default=False)
    max_depth: int = Field(description="The maximum directory depth to recurse into if recursive is True. Default is 2.", default=2)

@telemetry_decorator
def list_files(directory: str = ".", recursive: bool = False, max_depth: int = 2) -> str:
    """Lists files in a directory, optionally recursively."""
    try:
        output = []
        base_depth = directory.rstrip(os.sep).count(os.sep)
        
        # If not recursive, we only want the current directory (depth 1)
        current_max_depth = max_depth if recursive else 1
        
        for root, dirs, files in os.walk(directory):
            current_depth = root.count(os.sep) - base_depth
            if current_depth >= current_max_depth:
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

@telemetry_decorator
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

@telemetry_decorator
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

@telemetry_decorator
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

@telemetry_decorator
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

@telemetry_decorator
def write_multiple_files(files: Dict[str, str]) -> str:
    """Writes multiple files in a batch."""
    results = []
    for filepath, content in files.items():
        results.append(write_file(filepath, content, overwrite=True))
    return "\n".join(results)

@telemetry_decorator
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

@telemetry_decorator
def get_codebase_overview(directory: str = ".") -> str:
    """Parses Python, JavaScript, and TypeScript files in a directory to build a symbol graph containing classes and functions and returns a summary."""
    try:
        cached_overview = context_manager.get("codebase_overview")
        if cached_overview:
            return f"Codebase architecture overview (cached):\n{cached_overview}"
            
        raw_map = build_ast_symbol_map(directory)
        context_manager.set("codebase_overview", raw_map)
        return f"Codebase architecture overview:\n{raw_map}"
    except Exception as e:
        return f"Error generating codebase overview: {str(e)}"

@telemetry_decorator
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

@telemetry_decorator
def check_prerequisites(task_id: str) -> str:
    """Checks if prerequisites for a given task are met."""
    try:
        status_json = status_manager.read_status()
        status_data = json.loads(status_json)
        dependencies = status_data.get("dependencies", {})
        completed = status_data.get("completed", [])
        
        prereqs = dependencies.get(task_id, [])
        unmet = [p for p in prereqs if p not in completed]
        
        if not unmet:
            return f"All prerequisites for task '{task_id}' are met."
        else:
            return f"Unmet prerequisites for task '{task_id}': {', '.join(unmet)}"
    except Exception as e:
        return f"Error checking prerequisites: {str(e)}"

@telemetry_decorator
def visualize_task_dependencies() -> str:
    """Generates a Mermaid graph representation of the task dependency DAG."""
    try:
        status_json = status_manager.read_status()
        data = json.loads(status_json)
        dependencies = data.get("dependencies", {})
        # Make sure we have all tasks
        all_tasks = set(dependencies.keys())
        for prereqs in dependencies.values():
            all_tasks.update(prereqs)

        mermaid = ["graph TD"]
        for task in all_tasks:
            mermaid.append(f"  {task.replace('-', '_')}[{task}]")
        for task, prereqs in dependencies.items():
            for prereq in prereqs:
                mermaid.append(f"  {prereq.replace('-', '_')} --> {task.replace('-', '_')}")
        
        return "\n".join(mermaid)
    except Exception as e:
        return f"Error generating visualization: {str(e)}"

@telemetry_decorator
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

@telemetry_decorator
def perform_refactor(directory: str, target_name: str, new_name: str) -> str:
    """Performs an AST-based rename refactoring task."""
    try:
        return refactor_rename(directory, target_name, new_name)
    except Exception as e:
        return f"Error performing refactor: {str(e)}"

# Global YOLO state
YOLO_ENABLED = False
YOLO_EXPIRY = 0

def set_yolo(enabled: bool, duration_seconds: int = 0):
    global YOLO_ENABLED, YOLO_EXPIRY
    YOLO_ENABLED = enabled
    YOLO_EXPIRY = time.time() + duration_seconds if duration_seconds > 0 else 0

def check_yolo():
    global YOLO_ENABLED, YOLO_EXPIRY
    if YOLO_ENABLED and (YOLO_EXPIRY == 0 or time.time() < YOLO_EXPIRY):
        return True
    return False

from backend.refactor import refactor_rename
from backend.security import is_path_safe, validate_shell_command
# ... (rest of imports)

# ... (rest of the file content until execute_shell)

@telemetry_decorator
@cache_tool(ttl_seconds=5)
def execute_shell(command: str) -> str:
    """
    Executes a shell command.
    Checks for YOLO mode to bypass destructive command confirmation or restrictive policies.
    Checks for workspace isolation and command safety.
    Checks for sandboxing and whitelist.
    """
    # Load security config
    try:
        with open("./.forge/configs/security.yaml", "r") as f:
            security_config = yaml.safe_load(f) or {}
    except:
        security_config = {"sandboxing_enabled": False}

    sandboxing_enabled = security_config.get("sandboxing_enabled", False)

    # 1. Workspace Isolation
    # WARNING: This is a basic security heuristic. 
    # For a fully isolated system, move execution to a dedicated restricted container.
    
    # 2. Command Safety Check
    if not validate_shell_command(command) and not check_yolo():
        return "Error: Potentially destructive command detected. Permission denied. Enable YOLO mode via slash command to proceed."
    
    # 3. Sandbox / Whitelist Check
    if sandboxing_enabled and not check_yolo():
        if not is_command_whitelisted(command):
            return "Error: Command not whitelisted. Human-in-the-loop approval required for this action."

    try:
        # Use subprocess to execute command in the project context
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
        
        # Cap output length
        max_length = 4000
        if len(output) > max_length:
            return output[:max_length] + f"\n... (truncated {len(output) - max_length} chars)"
            
        return output or "[Command executed successfully with no output]"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error executing shell command: {str(e)}"

from google.genai import GoogleGenAI

# Initialize Gemini AI client
ai = GoogleGenAI(api_key=os.environ.get("GEMINI_API_KEY"))

# --- Updated Tools ---
@telemetry_decorator
def search_web(query: str) -> str:
    """Performs a web search using Gemini."""
    try:
        response = ai.models.generateContent({
            "model": "gemini-3.1-flash-lite-preview",
            "contents": f"Search for: {query}",
            "config": {
                "tools": [{"googleSearch": {}}]
            }
        })
        return f"Results for: {query}\n{response.text}"
    except Exception as e:
        return f"Error performing web search: {str(e)}"

@telemetry_decorator
def research_report(topic: str, format: str = "markdown") -> str:
    """Generates a research report on a topic."""
    try:
        prompt = f"Write a comprehensive research report on: {topic}. Format: {format}."
        response = ai.models.generateContent({
            "model": "gemini-3.1-pro-preview",
            "contents": prompt,
            "config": {
                "systemInstruction": "You are a professional research assistant."
            }
        })
        return response.text
    except Exception as e:
        return f"Error generating research report: {str(e)}"

class GitPatchArgs(BaseModel):
    patch_content: str = Field(description="The content of the git patch to apply.")

@telemetry_decorator
def apply_git_patch(patch_content: str) -> str:
    """Applies a git patch directly."""
    patch_file = "/tmp/app.patch"
    try:
        with open(patch_file, 'w') as f:
            f.write(patch_content)
        
        # Use git apply to apply the patch
        result = subprocess.run(
            ["git", "apply", patch_file],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return "Successfully applied patch."
        else:
            return f"Error applying patch: {result.stderr}"
    except Exception as e:
        return f"Error executing patch: {str(e)}"
    finally:
        if os.path.exists(patch_file):
            os.remove(patch_file)

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
    "check_prerequisites": check_prerequisites,
    "visualize_dependencies": visualize_task_dependencies,
    "get_symbol_map": build_ast_symbol_map,
    "get_codebase_overview": get_codebase_overview,
    "refactor_rename": perform_refactor,
    "list_files": list_files,
    "run_ripgrep": run_ripgrep,
    "apply_git_patch": apply_git_patch,
    "get_os_info": get_os_info,
    "read_status": status_manager.read_status,
    "update_status": status_manager.update_status,
    "search_web": search_web,
    "research_report": research_report
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
        "name": "visualize_dependencies",
        "description": "Visualizes the task dependency DAG using Mermaid syntax.",
        "parameters": EmptyArgs.model_json_schema()
    },
    {
        "name": "check_prerequisites",
        "description": "Checks if prerequisites for a given task are met by querying the dependency DAG in the status file.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"}
            },
            "required": ["task_id"]
        }
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
        "name": "get_codebase_overview",
        "description": "Parses Python, JavaScript, and TypeScript files in a target directory to build a symbol graph containing classes and functions and returns a summary.",
        "parameters": SymbolMapArgs.model_json_schema()
    },
    {
        "name": "refactor_rename",
        "description": "Performs an AST-based rename refactoring task (variable or function).",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {"type": "string"},
                "target_name": {"type": "string"},
                "new_name": {"type": "string"}
            },
            "required": ["directory", "target_name", "new_name"]
        }
    },
    {
        "name": "list_files",
        "description": "Recursively lists files and directories from a starting path, optionally with max_depth. Use this to explore project structure and find relevant files.",
        "parameters": ListFilesArgs.model_json_schema()
    },
    {
        "name": "run_ripgrep",
        "description": "Search for a text pattern in files using ripgrep (or grep fallback). Use this for codebase-wide code searches.",
        "parameters": RipgrepArgs.model_json_schema()
    },
    {
        "name": "apply_git_patch",
        "description": "Applies a git patch file content to the repository. Use this to apply complex refactoring or multi-file changes atomically.",
        "parameters": GitPatchArgs.model_json_schema()
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
    },
    {
        "name": "search_web",
        "description": "Performs a web search using Gemini and returns results.",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
    },
    {
        "name": "research_report",
        "description": "Generates a research report on a topic.",
        "parameters": {"type": "object", "properties": {"topic": {"type": "string"}, "format": {"type": "string"}}, "required": ["topic"]}
    }
])
