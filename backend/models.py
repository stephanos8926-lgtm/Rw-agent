from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

class AgentStateDraft(BaseModel):
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str
    status: str = "spawned" # spawned, active, completed, failed
    state_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class LifecycleEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    event_type: str # spawn, transition, check_in, error, completion
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
