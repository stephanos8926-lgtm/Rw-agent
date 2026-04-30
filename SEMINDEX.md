# SEMINDEX.md - Semantic Codebase Index for Agentic OS

## Core Modules
[CORE-001] /backend/agent.py:1-250 | LangGraph agent definition, node implementations (reflection, summarization, supervisor).
[CORE-002] /backend/server.py:1-100 | FastAPI entry point, service initialization.
[CORE-003] /backend/tools.py:1-300 | Core agent tools (shell, etc.) and tool isolation.
[CORE-004] /backend/sandbox.py:1-25 | Shell command execution security wrapper.

## Persistence & Observability
[PERS-001] /backend/storage.py:1-25 | GCS interaction stubs.
[PERS-002] /backend/database.py:1-10 | DB connection stubs.
[PERS-003] /backend/backup.py:1-45 | .agentark backup implementation with manifest and blake3 hashing.
[OBS-001] /backend/telemetry.py:1-40 | Telemetry logger, file-based structured events.

## Documentation
[DOC-001] /.docs/plans/ | Sprint planning documents.
[DOC-002] /.docs/adrs/ | Architectural Decision Records (ADRs 001-006).
[DOC-003] /.docs/status-agentic-os.json | Task status tracking.
[DOC-004] /.docs/adrs/ADR-007-telemetry-retention.md | Telemetry retention policy.
[DOC-005] /.docs/adrs/ADR-008-tool-sandboxing.md | Command execution security policy.
