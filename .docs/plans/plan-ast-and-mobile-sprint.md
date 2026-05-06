# Plan: AST Integration & Mobile Refinement Sprint

## 1. Goal
Integrate backend-generated AST symbols into the workspace sidebar for navigation/search and overhaul the mobile user experience.

## 2. Architecture & Components
- **AST Integration:**
  - Need to fetch AST data (likely via `/api/ast` or similar if available, or WebSocket update).
  - Component: `src/components/WorkspaceSidebar.tsx` needs to map over AST symbols.
- **Mobile Refinement:**
  - Audit `MobileCommandBar`.
  - Fix layout responsiveness in `App.tsx` (sidebar toggle, chat behavior).
  - Ensure touch-ready targets (>44px).

## 3. Milestones
- [x] Phase 1: AST Backend API verification & Frontend Data Hook.
- [x] Phase 2: Sidebar AST implementation (display + search).
- [x] Phase 3: Mobile audit & redesign (Command Bar, layout).
- [x] Phase 4: Final verification and polish.

## 4. Open Questions
- What is the exact schema for the AST symbol map provided by the backend?
- Should navigation be an accordion, tree-view, or flat-mapped list?
