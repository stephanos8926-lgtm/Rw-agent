# Forge Agentic OS - Architecture Plan

## Goal
Build a high-performance agentic OS backend and a feature-rich, Open WebUI-inspired frontend to enable autonomous agentic interactions with codebase and environment.

## Research-Driven Feature Parity Objectives
- **Agentic Autonomy:** Implement robust self-reflection, automated testing, and multi-step plan execution (e.g., Claude Code, Qwen-code-cli).
- **Codebase Awareness:** Deepen AST-aware code navigation and context caching (e.g., tools like Gemini-cli).
- **Workspace UX:** Develop workspace management, chat history, and model/function configuration interfaces modeled after Open WebUI.

## Milestones
1. [x] Project Initialization & Planning
2. [x] Backend Foundation
3. [x] Frontend Agent UI
4. [x] Context Awareness & AST Enhancements
5. [x] Agent Reflection & Automated Verification Capabilities
6. [x] Dynamic MCP Tool Loading & Hot-Reloading
7. [x] Workspace UX & Frontend Feature Parity Enhancement
8. [x] Security Sandboxing & Auth

## Phase 4: Observability
9. [x] Implement Event Tracing
10. [x] Integrate Telemetry Service


## Phase 7: Telemetry Management
13. [x] Implement log rotation and retention policies (ADR-007).
14. [x] Instrument core agent modules with log-rotation-safe event streams.
15. [x] Implement sandbox whitelist and approval workflow (ADR-008).

- Security: What level of sandboxing is assumed for the `execute_shell` tool on the target hosting environment?
- Context Caching: Benchmarking impact on Gemini 2.5 Flash token cost.
