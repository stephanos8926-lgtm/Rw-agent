# Agents Knowledge Base

## Roles and Instructions
- Understands local system environments (Debian).
- Generates secure, modular, Python 3 / LangGraph code.
- Builds mobile-responsive, terminal-themed React interfaces.

## Learned Patterns
- [2026-04-28] PROJECT START: Setting up hybrid Python/React workspace. The Python backend is designed to be self-hosted on the user's headless Debian server. The React frontend is built in this environment to interface with it via WebSockets.
- [2026-04-28] CACHING: Added ChromaDB for embedded vector semantic searching on tool outputs to reduce duplicate remote LLM calls.
- [2026-04-28] FEATURE PARITY: Implemented dynamic `skills_loader.py` for Claude-like SKILL.md modular capabilities. Upgraded `App.tsx` with mobile overlays, `react-markdown`, and collapsible cards for better UI. Implemented `update_status` and `read_status` tools mimicking the Antigravity agent's persistent .docs/ planning framework.

## Reflection Checkpoints
- Initial architecture set up: FastAPI + LangGraph + React WebSocket UI.
