import asyncio
import uuid
import traceback
from .message_bus import message_bus
from .persistence import swarm_persistence

class SwarmDispatcher:
    def __init__(self):
        self.active_tasks = {}

    async def spawn_agent(self, task_instruction: str, role: str = "general"):
        # PERSIST: Register the agent
        agent_id = swarm_persistence.register_agent(role)
        
        # Notify swarm that an agent has spawned
        swarm_persistence.log_event(agent_id, "spawn", {"instruction": task_instruction})
        message_bus.publish("agent_spawned", {
            "agent_id": agent_id,
            "role": role,
            "instruction": task_instruction
        })

        # Run detached
        task = asyncio.create_task(self._run_detached_agent(agent_id, task_instruction, role))
        self.active_tasks[agent_id] = task
        return agent_id
        
    async def _run_detached_agent(self, agent_id: str, instruction: str, role: str):
        swarm_persistence.log_event(agent_id, "transition", {"new_status": "active"})
        message_bus.publish("task_started", {
            "agent_id": agent_id,
            "role": role
        })
        
        try:
            # Simulated long-running work for the sub-agent
            steps = ["Initializing context...", "Searching knowledge base...", "Drafting plan...", "Executing changes...", "Verifying..."]
            
            for i, step in enumerate(steps):
                await asyncio.sleep(3) # Simulate work time
                swarm_persistence.log_event(agent_id, "progress", {"step": step, "index": i+1})
                message_bus.publish("task_progress", {
                    "agent_id": agent_id,
                    "progress": f"[{i+1}/{len(steps)}] {step}",
                    "role": role
                })
            
            swarm_persistence.log_event(agent_id, "transition", {"new_status": "completed"})
            message_bus.publish("task_complete", {
                "agent_id": agent_id,
                "result": f"Completed: {instruction}",
                "role": role
            })
            
        except Exception as e:
            swarm_persistence.log_event(agent_id, "error", {"message": str(e)})
            swarm_persistence.log_event(agent_id, "transition", {"new_status": "failed"})
            message_bus.publish("task_error", {
                "agent_id": agent_id,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "role": role
            })
        finally:
            if agent_id in self.active_tasks:
                del self.active_tasks[agent_id]

swarm_dispatcher = SwarmDispatcher()
