import os
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_typescript as tstypescript
from typing import Dict, List, Any, Optional

# Pre-compile languages
PY_LANGUAGE = Language(tspython.language())
JS_LANGUAGE = Language(tsjavascript.language())
TS_LANGUAGE = Language(tstypescript.language())

class ASTMapper:
    """
    Polyglot AST Mapper using tree-sitter to index code symbols
    and track cross-language dependencies.
    """
    def __init__(self):
        self.parsers = {
            ".py": Parser(PY_LANGUAGE),
            ".js": Parser(JS_LANGUAGE),
            ".ts": Parser(TS_LANGUAGE),
            ".tsx": Parser(TS_LANGUAGE)
        }
        self.queries = {
            ".py": PY_LANGUAGE.query("""
                (class_definition name: (identifier) @class)
                (function_definition name: (identifier) @function)
                (assignment left: (identifier) @variable)
            """),
            ".js": JS_LANGUAGE.query("""
                (class_declaration name: (identifier) @class)
                (function_declaration name: (identifier) @function)
                (method_definition name: (property_identifier) @function)
                (variable_declarator name: (identifier) @variable)
            """),
            ".ts": TS_LANGUAGE.query("""
                (class_declaration name: (identifier) @class)
                (function_declaration name: (identifier) @function)
                (method_declaration name: (property_identifier) @function)
                (interface_declaration name: (identifier) @interface)
                (type_alias_declaration name: (identifier) @type)
            """)
        }
        self.symbol_index = {}

    def parse_file(self, file_path: str):
        _, ext = os.path.splitext(file_path)
        if ext not in self.parsers or ext not in self.queries:
            return None
        
        parser = self.parsers[ext]
        query = self.queries[ext]
        
        try:
            with open(file_path, "rb") as f:
                content = f.read()
                tree = parser.parse(content)
                
            captures = query.captures(tree.root_node)
            symbols = {"classes": [], "functions": [], "interfaces": [], "types": [], "variables": []}
            
            for node, name in captures:
                symbol_name = node.text.decode('utf-8')
                line = node.start_point[0] + 1
                
                if name == "class": symbols["classes"].append({"name": symbol_name, "line": line})
                elif name == "function": symbols["functions"].append({"name": symbol_name, "line": line})
                elif name == "interface": symbols["interfaces"].append({"name": symbol_name, "line": line})
                elif name == "type": symbols["types"].append({"name": symbol_name, "line": line})
                elif name == "variable": symbols["variables"].append({"name": symbol_name, "line": line})
            
            self.symbol_index[file_path] = symbols
            return symbols
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def _extract_symbols(self, tree, ext: str) -> Dict[str, List[str]]:
        symbols = {"functions": [], "classes": [], "imports": []}
        root = tree.root_node
        
        # Simple traversal for demonstration
        # In a real implementation, we'd use tree-sitter queries for performance
        query_str = ""
        if ext == ".py":
            query_str = """
            (function_definition name: (identifier) @func)
            (class_definition name: (identifier) @class)
            (import_from_statement module_name: (dotted_name) @import)
            """
        else: # JS/TS
            query_str = """
            (function_declaration name: (identifier) @func)
            (class_declaration name: (identifier) @class)
            (import_statement source: (string) @import)
            """
            
        lang = PY_LANGUAGE if ext == ".py" else TS_LANGUAGE
        query = lang.query(query_str)
        captures = query.captures(root)
        
        for node, tag in captures:
            name = node.text.decode("utf-8")
            if tag == "func":
                symbols["functions"].append(name)
            elif tag == "class":
                symbols["classes"].append(name)
            elif tag == "import":
                symbols["imports"].append(name)
                
        return symbols

    def get_all_symbols(self, root_dir: str):
        self.symbol_index = {} # Clear for fresh scan
        for root, _, files in os.walk(root_dir):
            if any(exc in root for exc in ["node_modules", ".git", "__pycache__"]):
                continue
            for file in files:
                if any(file.endswith(ext) for ext in self.parsers):
                    full_path = os.path.join(root, file)
                    self.parse_file(full_path)
        return self.symbol_index

ast_mapper = ASTMapper()

def build_ast_symbol_map(directory: str):
    import json
    symbols = ast_mapper.get_all_symbols(directory)
    return json.dumps(symbols)
