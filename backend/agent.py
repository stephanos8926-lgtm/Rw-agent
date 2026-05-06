import os
import json
import time
from backend.types import AgentState
from backend import reflection, telemetry
from typing import Annotated, List, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from google import genai
from google.genai import types

from backend.tools import TOOLS_REGISTRY, TOOLS_METADATA, read_status
from backend.prompt_manager import prompt_manager
from backend.context_cache import context_cache_manager
from backend.semantic_cache import semantic_cache, compute_context_hash
from backend.skills_loader import skills_loader
from backend.security import human_approval_gate
from backend.persistence import swarm_persistence


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

# Initialize client once at module level for efficiency
client = initialize_genai_client()

def agent_node(state: AgentState):
    """The main reasoning node that uses Gemini 2.5 Flash."""
    messages = state["messages"]
    memory_buffer = state.get("memory_buffer", [])

    system_instruction = prompt_manager.get_prompt("default")
    
    # Inject memory buffer into system instruction if present
    if memory_buffer:
        system_instruction += "\n\n--- Memory Buffer (Summarized Past Interactions) ---\n"
        system_instruction += "\n".join(memory_buffer)
        system_instruction += "\n----------------------------------------------------"

    skills_context = skills_loader.get_formatted_context()
    if skills_context:
        system_instruction += "\n\n" + skills_context

    # ----- ... keep existing caching logic ... -----
    # Note: Using module-level 'client'

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
        from backend.telemetry import log_error
        log_error(e, {"messages_count": len(messages)})
        return {"messages": [{"role": "model", "content": f"AI Error: {str(e)}"}]}

from backend.tool_cache import tool_cache

def tool_node(state: AgentState):
    """Executes the tool requested by the model."""
    last_message = state["messages"][-1]
    
    if "function_call" not in last_message:
        return {"messages": [{"role": "tool", "content": "Error: No function call found."}]}
        
    fc = last_message["function_call"]
    func_name = fc["name"]
    args = fc["args"]
    
    if not human_approval_gate(func_name, args):
        return {"messages": [{"role": "tool", "content": f"Human approval required for: {func_name}. Please approve in UI."}]}
    
    if func_name in TOOLS_REGISTRY:
        try:
            # Log Tool Start
            agent_id = state.get("agent_id", "system")
            swarm_persistence.log_event(agent_id, "tool_start", {"tool": func_name, "args": args})

            # Check Tool Cache
            cached_result = tool_cache.get(func_name, args)
            if cached_result is not None:
                swarm_persistence.log_event(agent_id, "tool_cache_hit", {"tool": func_name})
                return {"messages": [{"role": "tool", "content": f"Result from {func_name} (cached):\n{cached_result}"}]}
                
            print(f"Executing tool: {func_name} with args: {args}")
            start_time = time.time()
            result = TOOLS_REGISTRY[func_name](**args)
            telemetry.trace_tool_execution(func_name, args, start_time, agent_id=agent_id)
            
            # Log Tool Success
            swarm_persistence.log_event(agent_id, "tool_completion", {"tool": func_name, "status": "success"})

            # Store Tool Cache
            # We only cache rapid-fire checks or side-effect-free looking tools theoretically,
            # but per requirements: "for frequently used tools like execute_shell("ls -la") or get_os_info()"
            # We cache them all for 5 seconds to bypass LLM re-evaluations for identical repeated calls.
            tool_cache.store(func_name, args, result)
            
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
    
    # Self-correction loop: if reflection detected errors, retry via supervisor
    reflection_text = state.get("reflection", "")
    if "[SYSTEM]: Compile/Syntax Errors Detected:" in reflection_text:
        print("Self-Correction Triggered: Routing back to supervisor.")
        return "retry"

    # AST Symbol Integrity Check: If the symbols have changed significantly, we might need a re-plan
    if "ast_symbols" in state and len(state["ast_symbols"]) < 2:
        return "tools" # Force symbol scan if missing
        
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

    workflow.add_conditional_edges("reflection", should_continue, {
        "tools": "tools", 
        "retry": "supervisor",
        "end": "summarization"
    })
    workflow.add_edge("summarization", END)
    workflow.add_edge("tools", "supervisor") # Back to supervisor after tool
    
    checkpointer = SqliteSaver.from_conn_string("sqlite:///data/agent_checkpoints.db")
    return workflow.compile(checkpointer=checkpointer)

def planner_node(state: AgentState):
    """Generates a sub-task plan for long-horizon goals."""
    messages = state["messages"]
    latest_request = messages[-1].get("content", "No request provided") if messages else "No request"
    status = read_status()
    
    # Use LLM to generate a detailed plan
    planning_prompt = f"""You are a Task Planner. Your goal is to break down the user request into a clear, numbered list of actionable sub-tasks.
    
    User Request: {latest_request}
    Current Project Status: {status}
    
    Return a concise numbered list of sub-tasks.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=planning_prompt
        )
        plan = response.text
    except Exception as e:
        print(f"Planning failed: {e}")
        plan = f"Plan for '{latest_request[:30]}...':\nStatus: {status[:50]}...\n1. Analyze requirements\n2. Break into sub-tasks\n3. Execute iteratively\n4. Review and Refine"
    
    return {"current_plan": plan}

def reflection_node(state: AgentState):
    """Critiques the previous action against the goal or current plan."""
    result = reflection.reflect_on_plan(state)
    telemetry.log_event("agent_reflection", {"result": result})
    
    # If errors were detected, we append a system message to the state so the next agent sees it
    if "[SYSTEM]: Compile/Syntax Errors Detected:" in result["reflection"]:
        return {
            "reflection": result["reflection"],
            "messages": [{"role": "user", "content": result["reflection"]}] # Injected as context for sub-agent
        }
        
    return result

def summarization_node(state: AgentState):
    """Summarizes history if too long."""
    telemetry.log_event("agent_summarization", {"messages_count": len(state["messages"])})
    return {"summary": "Interaction summarized."}

def supervisor_node(state: AgentState):
    """Routes the task to a specialized sub-agent using LLM classification."""
    client = initialize_genai_client()
    messages = state["messages"]
    current_plan = state.get("current_plan", "")
    
    # Simple routing classified by Gemini
    routing_prompt = f"""You are the Swarm Supervisor. Based on the current interaction and plan, decide which specialized agent should take the next action.
Agents:
- code_executor: For writing code, debugging, and system operations.
- designer: For UI/UX changes, styling, and frontend components.
- security_audit: For checking security rules, auth flows, and data integrity.
- reliability_engineer: For writing tests, improving error handling, and performance tuning.
- planner: For high-level roadmap strategy or ambiguous goals.

Current Plan: {current_plan}
Recent History: {[m['content'][-200:] for m in messages[-2:]]}

Respond with exactly one word: 'code_executor', 'designer', 'security_audit', 'reliability_engineer', or 'planner'.
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=routing_prompt
        )
        next_agent = response.text.strip().lower()
        valid_agents = ["code_executor", "designer", "security_audit", "reliability_engineer", "planner"]
        if next_agent not in valid_agents:
            next_agent = "planner" 
            
        print(f"Supervisor routed to: {next_agent}")
        return {"next_agent": next_agent}
    except:
        return {"next_agent": "planner"}

def _create_sub_agent_node(role: str):
    """Creates a sub-agent node with a specific prompt role."""
    def sub_agent(state: AgentState):
        """Modified agent loop that uses the specific role's system instruction."""
        print(f"Executing sub-agent: {role}")
        
        # Register Agent for Persistence
        agent_id = swarm_persistence.register_agent(role)
        swarm_persistence.log_event(agent_id, "transition", {"new_status": "active"})
        
        # Override the logic from agent_node to use specific prompt
        messages = state["messages"]
        system_instruction = prompt_manager.get_prompt(role) # LOAD THE SPECIALIZED PROMPT
        
        skills_context = skills_loader.get_formatted_context()
        if skills_context:
            system_instruction += "\n\n" + skills_context

        # Setup context caching or manual injection
        cached_content_name = context_cache_manager.get_or_create_cache(client, system_instruction)
        
        contents = []
        for msg in messages:
            role_msg = msg.get("role", "user")
            if role_msg == "tool": role_msg = "user"
            contents.append(types.Content(role=role_msg, parts=[types.Part.from_text(msg["content"])]))
            
        config_kwargs = {
            "tools": [types.Tool(function_declarations=TOOLS_METADATA)],
            "temperature": 0.3 # Lower temp for sub-agents (precision)
        }
        
        try:
            if cached_content_name:
                config_kwargs["cached_content"] = cached_content_name
            else:
                config_kwargs["system_instruction"] = system_instruction

            response = client.models.generate_content(
                model='gemini-2.0-flash', # Flash is generally better for sub-tasks
                contents=contents,
                config=types.GenerateContentConfig(**config_kwargs)
            )
            
            new_msg = None
            if response.function_calls:
                fc = response.function_calls[0]
                new_msg = {
                    "role": "model", 
                    "content": f"[{role.upper()}]: Invoking {fc.name}",
                    "function_call": {"name": fc.name, "args": fc.args}
                }
                swarm_persistence.log_event(agent_id, "tool_intent", {"tool": fc.name})
            else:
                new_msg = {"role": "model", "content": response.text}
                swarm_persistence.log_event(agent_id, "completion", {"output_length": len(response.text)})
                swarm_persistence.log_event(agent_id, "transition", {"new_status": "completed"})
                
            # Update persistent state
            swarm_persistence.update_state(agent_id, {"last_message": new_msg})
                
            return {"messages": [new_msg], "agent_id": agent_id}
        except Exception as e:
            from backend.telemetry import log_error
            log_error(e, {"role": role, "agent_id": agent_id})
            swarm_persistence.log_event(agent_id, "error", {"message": str(e)})
            return {"messages": [{"role": "model", "content": f"Sub-Agent [{role}] Failure: {str(e)}"}], "agent_id": agent_id}
        
    return sub_agent

# Initialize the compiled graph
app_graph = build_graph()
