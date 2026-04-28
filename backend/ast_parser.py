import os
import json
from pydantic import BaseModel, Field
from tree_sitter import Language, Parser
import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_typescript

PY_LANG = Language(tree_sitter_python.language())
JS_LANG = Language(tree_sitter_javascript.language())
TS_LANG = Language(tree_sitter_typescript.language())

# Map extensions to languages and queries
LANG_MAP = {
    ".py": (PY_LANG, """
        (class_definition name: (identifier) @class)
        (function_definition name: (identifier) @function)
    """),
    ".js": (JS_LANG, """
        (class_declaration name: (identifier) @class)
        (function_declaration name: (identifier) @function)
        (method_definition name: (property_identifier) @function)
    """),
    ".ts": (TS_LANG, """
        (class_declaration name: (identifier) @class)
        (function_declaration name: (identifier) @function)
        (method_declaration name: (property_identifier) @function)
    """)
}

class SymbolMapArgs(BaseModel):
    directory: str = Field(description="The directory to map. Defaults to the current directory.")

def build_ast_symbol_map(directory: str = ".") -> str:
    """
    Parses Python, JavaScript, and TypeScript files in a directory to build a symbol graph containing classes and functions.
    Returns a JSON string representing classes, functions, and files.
    """
    symbol_graph = {}

    for root, _, files in os.walk(directory):
        if "venv" in root or "__pycache__" in root or ".git" in root or "node_modules" in root:
             continue
             
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in LANG_MAP:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()
                    
                    parser = Parser()
                    lang, query_str = LANG_MAP[ext]
                    parser.set_language(lang)
                    tree = parser.parse(source.encode())
                    
                    query = lang.query(query_str)
                    captures = query.captures(tree.root_node)
                    
                    classes = [
                        {"name": node.text.decode('utf-8'), "line": node.start_point[0] + 1} 
                        for node, capture_name in captures if capture_name == 'class'
                    ]
                    functions = [
                        {"name": node.text.decode('utf-8'), "line": node.start_point[0] + 1} 
                        for node, capture_name in captures if capture_name == 'function'
                    ]
                            
                    symbol_graph[filepath] = {
                        "classes": classes,
                        "functions": functions
                    }
                except Exception as e:
                    symbol_graph[filepath] = {"error": str(e)}

    return json.dumps(symbol_graph, indent=2)
