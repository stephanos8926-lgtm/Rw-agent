import os
import json
from typing import TypedDict, Annotated, List, Any
from langgraph.graph import StateGraph, END
from google import genai
from google.genai import types

from backend.tools import TOOLS_REGISTRY, TOOLS_METADATA, read_status
from backend.prompt_manager import prompt_manager
from backend.context_cache import context_cache_manager
from backend.semantic_cache import semantic_cache, compute_context_hash
from backend.skills_loader import skills_loader

class AgentState(TypedDict):
    messages: Annotated[list, "The conversation history"]
    current_plan: str
    completed_tasks: List[str]
    reflection: str
    summary: str
    next_agent: str

def get_fallback_context() -> types.Content:
    """Loads the pre-computed symbol map and injects it manually if API Context Caching is bypassed."""
    context_str = "Project Structure Context: Not generated yet."
    if os.path.exists("context.json"):
        with open("context.json", "r", encoding="utf-8") as f:
             context_str = "Project Structure Context:\n" + f.read()
    return types.Content(role="user", parts=[types.Part.from_text(context_str)])

def initialize_genai_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
         print("Warning: GEMINI_API_KEY not found in environment.")
    return genai.Client(api_key=api_key)

def agent_node(state: AgentState):
    """The main reasoning node that uses Gemini 2.5 Flash."""
    client = initialize_genai_client()
    messages = state["messages"]

    system_instruction = prompt_manager.get_prompt("default")
    skills_context = skills_loader.get_formatted_context()
    if skills_context:
        system_instruction += "\n\n" + skills_context

    # ----- 1. INTERCEPT: Semantic Caching -----
    # Dynamically cache repetitive tool outputs and identical LLM reasoning requests
    if len(messages) > 0:
        latest_query = messages[-1].get("content", "")
        ctx_hash = compute_context_hash(messages)
        
        cached_response = semantic_cache.search(client, latest_query, ctx_hash)
        if cached_response:
             return {"messages": [cached_response]}
    # ------------------------------------------

    # ----- 2. SETUP: Context Caching (google.genai) -----
    cached_content_name = context_cache_manager.get_or_create_cache(client, system_instruction)
    # ----------------------------------------------------

    contents = []
    
    # If API Context caching failed (e.g., token count < 32k limits), fall back to manual context injection.
    if not cached_content_name and len(messages) > 0 and len(messages) < 3:
        contents.append(get_fallback_context())

    for msg in messages:
        role = msg.get("role", "user")
        if role == "tool":
           role = "user"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(msg["content"])]))
        
    try:
        # Build Config
        config_kwargs = {
            "tools": [types.Tool(function_declarations=TOOLS_METADATA)],
            "temperature": 0.4
        }
        
        if cached_content_name:
            config_kwargs["cached_content"] = cached_content_name
            # system_instruction is bundled inside the Context Cache
        else:
            config_kwargs["system_instruction"] = system_instruction

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(**config_kwargs)
        )
        
        new_msg = None
        if response.function_calls:
            fc = response.function_calls[0]
            new_msg = {
                "role": "model", 
                "content": f"[Intent]: Invoking {fc.name}",
                "function_call": {"name": fc.name, "args": fc.args}
            }
        else:
            new_msg = {"role": "model", "content": response.text}
            
        # Store back dynamically into Semantic Cache
        if len(messages) > 0:
             latest_query = messages[-1].get("content", "")
             ctx_hash = compute_context_hash(messages)
             semantic_cache.store(client, latest_query, ctx_hash, new_msg)
             
        return {"messages": [new_msg]}
            
    except Exception as e:
        return {"messages": [{"role": "model", "content": f"AI Error: {str(e)}"}]}

def tool_node(state: AgentState):
    """Executes the tool requested by the model."""
    last_message = state["messages"][-1]
    
    if "function_call" not in last_message:
        return {"messages": [{"role": "tool", "content": "Error: No function call found."}]}
        
    fc = last_message["function_call"]
    func_name = fc["name"]
    args = fc["args"]
    
    if func_name in TOOLS_REGISTRY:
        try:
            print(f"Executing tool: {func_name} with args: {args}")
            result = TOOLS_REGISTRY[func_name](**args)
            return {"messages": [{"role": "tool", "content": f"Result from {func_name}:\n{result}"}]}
        except Exception as e:
            return {"messages": [{"role": "tool", "content": f"Tool execution failed: {str(e)}"}]}
    else:
        return {"messages": [{"role": "tool", "content": f"Unknown tool: {func_name}"}]}

def should_continue(state: AgentState):
    """Router to determine the next node."""
    last_message = state["messages"][-1]
    if "function_call" in last_message:
        return "tools"
    return "end"

def build_graph():
    """Builds the LangGraph state machine."""
    workflow = StateGraph(AgentState)
    workflow.add_node("planner", planner_node)
    workflow.add_node("supervisor", supervisor_node)
    
    # Sub-agents
    workflow.add_node("code_executor", _create_sub_agent_node("code_executor"))
    workflow.add_node("designer", _create_sub_agent_node("designer"))
    workflow.add_node("planner_sub", _create_sub_agent_node("planner"))
    
    workflow.add_node("tools", tool_node)
    workflow.add_node("reflection", reflection_node)
    workflow.add_node("summarization", summarization_node)
    
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "supervisor")
    
    workflow.add_conditional_edges("supervisor", lambda state: state.get("next_agent", "planner"), {
        "code_executor": "code_executor",
        "designer": "designer",
        "planner": "planner_sub"
    })
    
    # Edges from sub-agents to reflection
    for node in ["code_executor", "designer", "planner_sub"]:
        workflow.add_edge(node, "reflection")

    workflow.add_conditional_edges("reflection", should_continue, {"tools": "tools", "end": "summarization"})
    workflow.add_edge("summarization", END)
    workflow.add_edge("tools", "supervisor") # Back to supervisor after tool
    return workflow.compile()

def planner_node(state: AgentState):
    """Generates a sub-task plan for long-horizon goals."""
    # Simple planner logic: Generate a plan based on the last message and current status
    messages = state["messages"]
    latest_request = messages[-1].get("content", "No request provided") if messages else "No request"
    status = read_status()
    
    # In a real system, we'd use the LLM to generate the plan
    plan = f"Plan for '{latest_request[:30]}...':\nStatus: {status[:50]}...\n1. Analyze requirements\n2. Break into sub-tasks\n3. Execute iteratively\n4. Review and Refine"
    
    return {"current_plan": plan}

def reflection_node(state: AgentState):
    """Critiques the previous action against the goal or current plan."""
    client = initialize_genai_client()
    messages = state["messages"]
    if not messages:
        return {"reflection": "No history to reflect on."}
        
    last_action = messages[-1].get("content", "")
    plan = state.get("current_plan", "")
    
    # Prompt the LLM for critique
    prompt = f"Review the latest action: '{last_action}'.\nGoal/Plan: {plan}.\nIs this action advancing the goal? Critique it (concisely)."
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    return {"reflection": response.text}

def summarization_node(state: AgentState):
    """Summarizes history if too long."""
    return {"summary": "Interaction summarized."}

def supervisor_node(state: AgentState):
    """Routes the task to a specialized sub-agent."""
    client = initialize_genai_client()
    # Simple routing logic: look at current_plan or messages
    last_msg = state["messages"][-1]["content"] if state["messages"] else ""
    
    # In reality, this prompt would ask the LLM to route, not hardcoded logic.
    if "code" in last_msg.lower():
        return {"next_agent": "code_executor"}
    elif "design" in last_msg.lower():
        return {"next_agent": "designer"}
    else:
        return {"next_agent": "planner"}

def _create_sub_agent_node(role: str):
    """Creates a sub-agent node with a specific prompt role."""
    def sub_agent(state: AgentState):
        # reuse agent_node logic but customize system_instruction via prompt_manager
        print(f"Running sub-agent: {role}")
        return agent_node(state) # Simplified for now
    return sub_agent

# Initialize the compiled graph
app_graph = build_graph()
