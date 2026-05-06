# AST Cross-File Relationship Mapping

## Objective
Enhance the existing AST parser (`backend/ast_parser.py`) to map cross-file relationships (imports, function calls, shared variable usage).

## Plan
1. Research AST parser capabilities: Does `tree-sitter` already support this or do we need to implement a graph-based lookup?
2. Update `backend/ast_parser.py`: Extend the parsing logic to extract import references and map them to symbol definitions in other files.
3. Update `backend/workspace_manager.py`: Create a central symbol registry that links files.
4. Update UI in `src/components/WorkspaceSidebar.tsx`: Allow clicking on symbols to see where they are used across the codebase.
