# Agents Knowledge Base

## Roles and Instructions
- Understands local system environments (Debian).
- Generates secure, modular, Python 3 / LangGraph code.
- Builds mobile-responsive, terminal-themed React interfaces.

## Learned Patterns
- [2026-04-28] PROJECT START: Setting up hybrid Python/React workspace. The Python backend is designed to be self-hosted on the user's headless Debian server. The React frontend is built in this environment to interface with it via WebSockets.
- [2026-04-28] CACHING: Added ChromaDB for embedded vector semantic searching on tool outputs to reduce duplicate remote LLM calls.
- [2026-04-28] FEATURE PARITY: Implemented dynamic `skills_loader.py` for Claude-like SKILL.md modular capabilities. Upgraded `App.tsx` with mobile overlays, `react-markdown`, and collapsible cards for better UI. Implemented `update_status` and `read_status` tools mimicking the Antigravity agent's persistent .docs/ planning framework.
- [2026-04-28] ARCHITECTURE: Home-server infrastructure requires local-first persistence (SQLite) + file-based backup (.agentark) rather than cloud-native services (Firestore).
- [2026-04-28] ROBUSTNESS: Always pair file archives with an integrity manifest (JSON) containing cryptographic hashes (BLAKE3 preferred) to ensure data stability.
- [2026-04-28] OBSERVABILITY: Instrument LangGraph nodes (reflection/summarization) and tool execution (backend/tools.py) with structured telemetry events immediately upon creation.
- [2026-04-28] TELEMENTRY: Local-first architecture (limited storage) necessitates explicit log rotation and retention policies (ADR-007).
- [2026-04-28] SANDBOX: External commands must be whitelisted, logged, and sensitive operations require a formal approval workflow (ADR-008).

## Reflection Checkpoints
- Initial architecture set up: FastAPI + LangGraph + React WebSocket UI.
- Phase 1-5 observability and persistence complete. Shifted architecture from cloud-native to home-server-native.
