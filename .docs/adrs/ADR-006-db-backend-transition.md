# ADR-006: Database Backend Strategy

## Context
Our agentic OS runs on a home server. While NoSQL/Firestore was considered for cloud-native scalability, it introduces unnecessary overhead and network dependency for a local-first, home-server deployment.

## Decisions Made
1. **Target Backend:** Retain SQLite for agent state and checkpointing, leveraging local ACID guarantees and simplicity.
2. **Persistence Abstraction:** Create `backend/database.py` to abstract DB operations, allowing us to swap backends (e.g., PostgreSQL) if requirements change later, but keeping local SQLite for now.
3. **Robustness:** Ensure durability through the new robust `.agentark` backup strategy (see ADR-005).

## Consequences
- **Positive:** Low latency, no external infrastructure dependencies, simple single-file deployment.
- **Negative:** SQLite does not support high-concurrency writes, which is acceptable for single-user/small-team home usage.
