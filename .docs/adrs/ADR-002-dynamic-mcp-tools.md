# ADR-002: Dynamic MCP Tool System Architecture

## Context
We need to move beyond static tool definitions to a dynamic, hot-reloadable system for adding functionality to Forge Agentic OS. This allows users and the agent to install and update tools without restarting the server.

## Decisions Made
1. **Tool Specification:** Tools are defined as YAML files located in `/backend/mcp_tools/`. Each file contains the tool name, description, parameters schema, and implementation reference.
2. **Dynamic Loader:** Implemented `mcp_loader.py` using `watchdog` to monitor `/backend/mcp_tools/` for changes.
3. **Hot-Reloading:** When a `.yaml` file is added, removed, or modified:
   - Tool registry in Memory is automatically updated.
   - New tool definitions are scanned and parsed immediately.
4. **Tool Execution:** The backend dynamically maps incoming agent tool calls to implementations based on the registry.

## Consequences
- **Positive:** Massive reduction in development cycle time for adding tools. No server restarts needed.
- **Negative:** Increased runtime risk if a user provides an invalid YAML file (need robust validation).
- **Security:** Tools executed dynamically MUST be restricted to the project environment using path/workspace validation.

## Future Improvements
1. **Tool Sandboxing:** Move execution of dynamically loaded tools into a restricted sub-process (e.g., specific docker container).
2. **Schema Enforcement:** Use `pydantic` dynamically to validate tool inputs against the YAML-defined schema upon registration.
3. **Registry Discovery:** Allow the agent to `list_registered_tools` and `get_tool_schema` as native primitives.
