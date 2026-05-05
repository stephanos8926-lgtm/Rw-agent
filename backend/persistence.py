import json
from datetime import datetime
from .database import get_db
from .models import AgentStateDraft, LifecycleEvent
from .message_bus import MessageBus

# Initialize a persistence-local bus if needed, or import shared one
# The server.py seems to use a global one. Let's assume we can get it or just use the class.
message_bus = MessageBus()

class PersistenceManager:
    @staticmethod
    def register_agent(role: str) -> str:
        agent = AgentStateDraft(role=role)
        with get_db() as conn:
            conn.execute(
                "INSERT INTO agents (agent_id, role, status, state_data, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (agent.agent_id, agent.role, agent.status, json.dumps(agent.state_data), agent.created_at, agent.updated_at)
            )
            conn.commit()
        return agent.agent_id

    @staticmethod
    def log_event(agent_id: str, event_type: str, payload: dict):
        event = LifecycleEvent(agent_id=agent_id, event_type=event_type, payload=payload)
        with get_db() as conn:
            conn.execute(
                "INSERT INTO lifecycle_events (event_id, agent_id, event_type, payload, timestamp) VALUES (?, ?, ?, ?, ?)",
                (event.event_id, event.agent_id, event.event_type, json.dumps(event.payload), event.timestamp)
            )
            
            # Update status if it's a transition
            if event_type == "transition":
                status = payload.get("new_status")
                if status:
                    conn.execute(
                        "UPDATE agents SET status = ?, updated_at = ? WHERE agent_id = ?",
                        (status, datetime.now(), agent_id)
                    )
            conn.commit()
        
        # PUSH TO MESSAGE BUS FOR REAL-TIME UI
        # Run in background if possible, but for simplicity here we call it directly
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    message_bus.publish(f"agent_{event_type}", {"agent_id": agent_id, **payload}),
                    loop
                )
        except:
            pass

    @staticmethod
    def update_state(agent_id: str, state: dict):
        with get_db() as conn:
            conn.execute(
                "UPDATE agents SET state_data = ?, updated_at = ? WHERE agent_id = ?",
                (json.dumps(state), datetime.now(), agent_id)
            )
            conn.commit()

    @staticmethod
    def get_agent_history(agent_id: str):
        with get_db() as conn:
            cursor = conn.execute("SELECT * FROM lifecycle_events WHERE agent_id = ? ORDER BY timestamp ASC", (agent_id,))
            return [dict(row) for row in cursor.fetchall()]

swarm_persistence = PersistenceManager()
