import aiosqlite
import asyncio
import json
import logging
from abc import ABC, abstractmethod

class MessageBusAdapter(ABC):
    @abstractmethod
    async def init(self):
        pass

    @abstractmethod
    async def publish(self, event_type, payload):
        pass

class MemoryAdapter(MessageBusAdapter):
    def __init__(self):
        self.events = []
    
    async def init(self):
        logging.info("MemoryAdapter initialized.")
        
    async def publish(self, event_type, payload):
        self.events.append({'type': event_type, 'payload': payload})

class SQLiteAdapter(MessageBusAdapter):
    def __init__(self, db_path="events.db"):
        self.db_path = db_path

    async def init(self):
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, type TEXT, payload TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
                await db.commit()
            logging.info("SQLiteAdapter initialized.")
        except Exception as e:
            logging.error(f"Failed to init SQLiteAdapter db: {e}")

    async def publish(self, event_type, payload):
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("INSERT INTO events (type, payload) VALUES (?, ?)", (event_type, json.dumps(payload)))
                await db.commit()
        except Exception as e:
            logging.error(f"SQLiteAdapter failed to publish event: {e}")

class MessageBus:
    def __init__(self, adapter: MessageBusAdapter = None):
        self.adapter = adapter or SQLiteAdapter()
        self.subscribers = []

    async def init_bus(self):
        await self.adapter.init()

    async def publish(self, event_type, payload):
        await self.adapter.publish(event_type, payload)
        await self._notify(event_type, payload)

    async def _notify(self, event_type, payload):
        for callback in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event_type, payload)
                else:
                    callback(event_type, payload)
            except Exception as e:
                logging.error(f"Subscriber callback failed: {e}")

    def subscribe(self, callback):
        if callback not in self.subscribers:
            self.subscribers.append(callback)

