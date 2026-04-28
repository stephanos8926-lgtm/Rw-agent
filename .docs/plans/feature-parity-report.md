# Deep Dive Review & Research Report: Agentic OS Feature Parity

## Overview
This report analyzes the gaps between the current Forge Agentic OS and state-of-the-art developer agents (Google AI Studio Build, OpenWebUI, Claude Code, Gemini CLI, Antigravity Agent). 

## 1. UI/UX Parity (AI Studio / OpenWebUI)
**Current State:** 
- A basic React/Tailwind frontend. 
- Added a collapsible component for tool outputs (`MessageBubble` refactored) to clean up verbose console spam.

**Target State (OpenWebUI / AI Studio Mobile):**
- **Mobile Responsiveness:** AI Studio handles mobile well through off-canvas sidebars, compact touch targets (44px min), and fluid typography. Our app lacks structural sidebar support for mobile.
- **Progressive Disclosure:** Using collapsible `tool_result` cards is a step in the right direction. We need markdown rendering (`react-markdown`), syntax highlighting (`rehype-highlight`), and streaming typewriter effects.
- **Thread Management:** OpenWebUI provides robust conversation branching and history scrolling.

## 2. Backend Parity (Antigravity Agent)
**Current State:**
- Simple LangGraph state machine (`AgentState` with `messages`) using `gemini-2.5-flash`.
- In-memory/ChromaDB semantic caching for speed.

**Target State (Antigravity Long-Horizon Tasks):**
- **Sub-task Planning:** Antigravity excels at planning by creating file-based or internal hierarchical JSON plans (`.docs/plans/` strategy). Wait, we have this loosely in our system prompts but the agent graph doesn't formally enforce a "Planning Node" prior to "Execution Nodes".
- **Reflection & Self-Correction:** The LangGraph implementation needs a `reflect` edge where the agent validates its output against the goal before responding to the user.
- **Context Management:** Antigravity maintains context over hundreds of turns by summarizing past events. We need a `summarize` node that triggers when `len(messages) > MAX_TURNS`.

## 3. Skills & Sub-agent Parity (Claude Code / Gemini CLI)
**Current State:**
- Static system prompt via `prompt_manager.py`. Tools are Python functions.

**Target State (SKILL.md & Subagents):**
- **Skill Format:** Claude Code and AI Studio use `SKILL.md` frontmatter formats to dynamically load capabilities based on intent triggers. We must implement a `skill_loader.py` that parses `skills/**/*.md` and provides them to the context cache.
- **Subagents:** Instead of one massive agent that does everything (Bash, AST parsing), we should launch specific subagents. E.g., `DesignerSubAgent` for CSS tasks, `SystemSubAgent` for Debian tasks. We can use LangGraph's `Supervisor` pattern.

# Implementation Plan

## Phase 1: Frontend Polish (Immediate)
- [x] Refactor `MessageBubble` for collapsible structured tool data.
- [ ] Incorporate `react-markdown` in the React frontend.
- [ ] Add mobile UI overlays (hamburger menu, sliding sidebar).

## Phase 2: Skills Architecture
- [ ] Create `backend/skills/` directory.
- [ ] Implement `SKILL.md` parser traversing YAML frontmatter (`name`, `description`).
- [ ] Feed skills as specific `function_declarations` (tools) or context files.

## Phase 3: Long-Horizon Tasks & Subagents (Antigravity)
- [ ] Refactor `LangGraph` topology from `[Agent -> Tools -> Agent]` to: `[User -> Planner -> Router -> (Subagent A | Subagent B) -> Tools -> Reflection -> Ext]`.
- [ ] Introduce a `.docs/status-manager.py` that the backend uses to autonomously update its own plan milestones.
- [ ] Implement context summarization (Memory Buffer).
