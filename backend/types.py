from typing import TypedDict, Annotated, List

class AgentState(TypedDict):
    messages: Annotated[list, "The conversation history"]
    memory_buffer: Annotated[List[str], "Summarized past interactions"]
    current_plan: str
    completed_tasks: List[str]
    reflection: str
    summary: str
    next_agent: str
