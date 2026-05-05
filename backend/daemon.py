import asyncio
import time
from .message_bus import message_bus
from .swarm_dispatcher import swarm_dispatcher

class AgentDaemon:
    def __init__(self, interval_seconds: int = 3600):
        self.interval_seconds = interval_seconds
        self.running = False
        self.task = None
        
    def start(self):
        if not self.running:
            self.running = True
            message_bus.publish("daemon_started", {"interval": self.interval_seconds})
            self.task = asyncio.create_task(self._daemon_loop())
            
    def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()
        message_bus.publish("daemon_stopped", {})
        
    async def _daemon_loop(self):
        while self.running:
            try:
                # Dispatch background maintenance or briefing agents
                message_bus.publish("daemon_trigger", {"action": "background_maintenance"})
                await swarm_dispatcher.spawn_agent("Perform routine system cleanup and summarize recent activity logs.", role="maintenance")
                
                # Wait for next interval
                await asyncio.sleep(self.interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                message_bus.publish("daemon_error", {"error": str(e)})
                await asyncio.sleep(60) # Wait a bit before retrying

agent_daemon = AgentDaemon(interval_seconds=3600) # 1 hour default
