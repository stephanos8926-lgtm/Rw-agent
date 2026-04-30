import aiosqlite
import asyncio
import json
import logging

class MessageBus:
    def __init__(self, db_path="events.db"):
        self.db_path = db_path
        self.subscribers = []

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, type TEXT, payload TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
            await db.commit()

    async def publish(self, event_type, payload):
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("INSERT INTO events (type, payload) VALUES (?, ?)", (event_type, json.dumps(payload)))
                await db.commit()
            
            # Async notify subscribers
            await self._notify(event_type, payload)
        except Exception as e:
            logging.error(f"Failed to publish event: {e}")

    async def _notify(self, event_type, payload):
        for callback in self.subscribers:
            try:
                # Assuming callback is an async function
                await callback(event_type, payload)
            except Exception as e:
                logging.error(f"Subscriber callback failed: {e}")

    def subscribe(self, callback):
        self.subscribers.append(callback)
