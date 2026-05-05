import sqlite3
import os
from contextlib import contextmanager

DB_PATH = "swarm_memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Agent Registry
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            agent_id TEXT PRIMARY KEY,
            role TEXT NOT NULL,
            status TEXT NOT NULL,
            state_data TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    
    # Lifecycle Logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lifecycle_events (
            event_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY(agent_id) REFERENCES agents(agent_id)
        )
    """)
    
    conn.commit()
    conn.close()

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL") # Enable write-ahead logging
    try:
        yield conn
    finally:
        conn.close()

init_db()
