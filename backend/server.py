from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import os
import sys
import argparse

# Ensure backend module is resolvable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.workspace_manager import workspace_manager
from backend.config_manager import ConfigManager
from backend.message_bus import MessageBus
from backend.plugin_system import PluginSystem
from backend.tools import get_os_info, build_ast_symbol_map
from backend.context_manager import context_manager
import logging

# WORKSPACE_DIR will be managed via the workspace manager
WORKSPACE_DIR = workspace_manager.get_workspace_dir()

# Initialization
config_dir = os.path.join(WORKSPACE_DIR, ".forge", "configs")
os.makedirs(config_dir, exist_ok=True)
config_manager = ConfigManager(config_dir)

message_bus = MessageBus()

plugins_dir = os.path.join(WORKSPACE_DIR, ".forge", "plugins")
os.makedirs(plugins_dir, exist_ok=True)
plugin_system = PluginSystem(plugins_dir)

from backend.agent import app_graph
from backend.status_manager import status_manager
from backend.skills_loader import skills_loader
from backend.ast_parser import build_ast_symbol_map
from backend.tools import set_yolo
from backend.mcp_loader import start_mcp_loader
from backend.telemetry import init_tracer
import os

app = FastAPI(title="Forge Agentic OS")
init_tracer()

# Initialize MCP Loader
MCP_TOOLS_DIR = "/backend/mcp_tools"
mcp_loader = start_mcp_loader(MCP_TOOLS_DIR)

# Serve static files from the 'dist' directory
app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

@app.get("/")
async def read_index():
    return FileResponse("dist/index.html")

@app.get("/{path:path}")
async def read_static(path: str):
    return FileResponse(f"dist/{path}")

@app.get("/api/health")
def health_check():
    return {"status": "online", "version": "1.0.0", "message": "Agentic OS Backend running"}

@app.get("/api/status")
def get_status():
    return json.loads(status_manager.read_status())

@app.get("/api/skills")
def get_skills():
    return {"skills": skills_loader.skills}

@app.get("/api/os-info")
def get_os_info_route():
    return {"info": get_os_info()}

@app.get("/api/ast")
def get_ast():
    cached_ast = context_manager.get("ast_symbol_map")
    if cached_ast:
        return cached_ast
    
    ast_map = json.loads(build_ast_symbol_map(directory=WORKSPACE_DIR))
    context_manager.set("ast_symbol_map", ast_map)
    return ast_map

@app.websocket("/ws/agent")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Initialize connection state
    state = {
        "messages": [],
        "current_plan": "Awaiting instructions",
        "completed_tasks": []
    }
    
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_input = payload.get("message", "")
            
            if not user_input:
                continue

            # --- Slash Command Parsing ---
            if user_input.startswith("/"):
                parts = user_input.split(" ")
                command = parts[0]
                args = parts[1:]

                if command == "/yolo":
                    duration = int(args[0]) if len(args) > 0 else 0
                    set_yolo(True, duration)
                    response = f"YOLO mode enabled {f'for {duration}s' if duration > 0 else 'indefinitely'}."
                    await websocket.send_json({"type": "message", "role": "agent", "content": response})
                    continue
                elif command == "/yolo-off":
                    set_yolo(False)
                    await websocket.send_json({"type": "message", "role": "agent", "content": "YOLO mode disabled."})
                    continue
                elif command == "/status":
                    status = status_manager.read_status()
                    await websocket.send_json({"type": "message", "role": "agent", "content": f"Current Status: {str(status)}"})
                    continue

            # Stream user message back to UI
            await websocket.send_json({"type": "message", "role": "user", "content": user_input})
            
            # Update state with user message
            state["messages"].append({"role": "user", "content": user_input})
            
            # Run the LangGraph
            try:
                # We use stream to get interim updates (tool calls, etc)
                for event in app_graph.stream(state):
                    for node_name, node_data in event.items():
                        if "messages" in node_data and len(node_data["messages"]) > 0:
                            latest_msg = node_data["messages"][-1]
                            
                            # Update our running state
                            state["messages"].append(latest_msg)
                            
                            if latest_msg["role"] == "model" and "function_call" in latest_msg:
                                await websocket.send_json({
                                    "type": "tool_intent",
                                    "tool": latest_msg["function_call"]["name"],
                                    "content": f"Agent is calling {latest_msg['function_call']['name']}..."
                                })
                            elif latest_msg["role"] == "tool":
                                await websocket.send_json({
                                    "type": "tool_result",
                                    "content": latest_msg["content"]
                                })
                            elif latest_msg["role"] == "model":
                                await websocket.send_json({
                                    "type": "message",
                                    "role": "agent",
                                    "content": latest_msg["content"]
                                })
                                
            except Exception as e:
                await websocket.send_json({"type": "error", "content": f"Graph Execution Error: {str(e)}"})

    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    # The user intends to run this on their Debian server
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
