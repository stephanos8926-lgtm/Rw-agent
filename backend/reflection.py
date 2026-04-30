from backend.types import AgentState
from backend.agent import client

def reflect_on_plan(state: AgentState):
    messages = state["messages"]
    current_plan = state["current_plan"]
    
    reflection = client.models.generateContent({
        "model": "gemini-3.1-pro-preview",
        "contents": f"Current plan: {current_plan}\n\nConversation history: {messages[-5:]}\n\nReflect on progress and suggest plan updates if needed.",
    })                
    return {"reflection": reflection.text}
