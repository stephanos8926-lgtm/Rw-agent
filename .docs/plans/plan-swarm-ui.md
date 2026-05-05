# 🐝 Swarm Observability UI Plan (Phase 6 Parity)

## Context
With the shift towards the OpenClaw / Distributed Agentic OS architecture, the system is no longer just a single conversational agent. It is a swarm mechanism mapping tasks to background sub-agents across long horizon objectives. The previously built **SQLite-based Message Bus** is the connective tissue, allowing detached agents to publish lifecycle events (`task_started`, `agent_spawned`, `task_progress`, `error`).

## Objective
To provide a beautiful, real-time React UI capable of monitoring these detached background agents via the Message Bus.

## Architecture & Implementation Steps

### 1. Backend: Realtime Event Streaming Server 
- Add a new WebSocket endpoint (`/ws/events`) in `server.py`.
- Tie into `MessageBus.subscribe(callback)`.
- The callback pipes the real-time event payloads directly to connected React clients via WebSockets.
- Gracefully handle `WebSocketDisconnect` to `unsubscribe` and prevent memory leaks.

### 2. Frontend: `useSwarmEvents` Hook
- Create `src/hooks/useSwarmEvents.ts` to manage the WebSocket connection to `/ws/events`.
- Store arriving events in a rolling buffer state.

### 3. Frontend: `SwarmObserver.tsx` UI Component
- Build a dedicated, polished dashboard component.
- **Top Section:** Summary metrics containing total agents currently active, completed tasks, and errors.
- **Layout Matrix:** Visual nodes representing different active agents or processes.
- **Live Event Feed:** A beautifully styled sliding terminal interface (`<motion.div>`) that animates new message bus events into the DOM in real-time.

### 4. Integration into `App.tsx`
- Introduce a Tabbed layout in the main viewing area:
  - **Chat Mode (Current)**
  - **Swarm Operations**
- Or accessible via a prominent Sidebar action ("Enter Swarm Mode").
