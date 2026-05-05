from backend.types import AgentState
from backend.agent import client
from backend.semantic_cache import semantic_cache
from backend.lsp_manager import lsp_manager
import re

def reflect_on_plan(state: AgentState):
    messages = state["messages"]
    current_plan = state["current_plan"]
    
    # Get current stats representing workflow speed and hit/miss rates
    stats_summary = semantic_cache.log_stats()
    
    # Run LSP diagnostics for feedback loop
    lsp_diagnostics = lsp_manager.run_type_check()
    lsp_context = f"\n\n[SYSTEM]: Compile/Syntax Errors Detected:\n{lsp_diagnostics}\nFIX THESE ERRORS IN THE NEXT ACTION." if lsp_diagnostics else "\n\n[SYSTEM]: Compiler Status: OK (No syntax errors)."

    # Logic to tune semantic_cache threshold
    stats = semantic_cache.get_stats_summary()
    hit_rate = stats.get("hit_rate", 0)
    current_threshold = semantic_cache.threshold
    
    if hit_rate < 0.15:
        semantic_cache.threshold = max(0.85, current_threshold - 0.01)
    elif hit_rate > 0.45:
        semantic_cache.threshold = min(0.99, current_threshold + 0.005)
        
    threshold_context = f"\n\n[CACHE ADVISORY]: Current hit rate is {hit_rate:.1%}. Threshold adjusted to {semantic_cache.threshold:.3f}."

    reflection_prompt = f"""Current plan: {current_plan}

Conversation history: {messages[-5:]}

Semantic Cache Stats: {stats_summary}{threshold_context}
{lsp_context}

Reflect on progress and suggest plan updates if needed.
Also consider tuning the `semantic_cache` threshold based on the hit rates. If the workflow needs more speed and hit rates drop too low, lower the threshold (e.g. 0.95, 0.96). If there are false positives (wrong semantic matches), raise it (e.g. 0.98, 0.99).
If you want to tune it, output exactly: `[TUNE_THRESHOLD: 0.9X]` where 0.9X is the new threshold.
"""

    reflection = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=reflection_prompt,
    )
    
    text = reflection.text
    
    # Check for threshold tuning signal
    match = re.search(r"\[TUNE_THRESHOLD:\s*([0-9\.]+)\]", text)
    if match:
        try:
            new_val = float(match.group(1))
            semantic_cache.set_threshold(new_val)
        except ValueError:
            pass
            
    return {"reflection": text}
