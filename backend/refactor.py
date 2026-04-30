import os
from tree_sitter import Parser
from backend.ast_parser import LANG_MAP

def refactor_rename(directory, target_name, new_name):
    """Simple AST-based renaming tool."""
    files_modified = []
    
    for root, _, files in os.walk(directory):
        if "venv" in root or "__pycache__" in root or ".git" in root or "node_modules" in root:
             continue
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in LANG_MAP:
                filepath = os.path.join(root, file)
                
                # Perform renaming
                modified = _rename_in_file(filepath, ext, target_name, new_name)
                if modified:
                    files_modified.append(filepath)
                    
    return f"Refactoring complete. Files modified: {', '.join(files_modified)}"

def _rename_in_file(filepath, ext, target_name, new_name):
    lang, _ = LANG_MAP[ext]
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    parser = Parser()
    parser.set_language(lang)
    tree = parser.parse(source.encode())
    
    # Simple strategy: Traverse AST, find identifiers matching target_name
    # This is a naive implementation, but fits the requirement for an AST-based start.
    
    # Note: Implementing actual node replacement is complex with tree-sitter+python.
    # A safer approach for now is to use the AST to get positions, then apply replacements.
    
    changes = []
    
    def traverse(node):
        if node.type == "identifier" and node.text.decode('utf-8') == target_name:
            # We found an occurrence.
            start = node.start_byte
            end = node.end_byte
            changes.append((start, end))
            
        for child in node.children:
            traverse(child)

    traverse(tree.root_node)
    
    if not changes:
        return False
        
    # Apply changes in reverse order to keep byte offsets valid
    source_bytes = bytearray(source, 'utf-8')
    for start, end in reversed(changes):
        source_bytes[start:end] = new_name.encode('utf-8')
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(source_bytes.decode('utf-8'))
        
    return True
