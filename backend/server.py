from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import os
import sys
import argparse

# Ensure backend module is resolvable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

parser = argparse.ArgumentParser(description="Forge Agentic OS Backend")
parser.add_argument("--workspace", default=".", help="Workspace root directory")
args = parser.parse_args()
WORKSPACE_DIR = args.workspace if args.workspace != "." else os.getcwd()

from backend.agent import app_graph
from backend.status_manager import status_manager
from backend.skills_loader import skills_loader
from backend.ast_parser import build_ast_symbol_map

app = FastAPI(title="Forge Agentic OS")

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

@app.get("/api/ast")
def get_ast():
    return json.loads(build_ast_symbol_map(directory=WORKSPACE_DIR))

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
