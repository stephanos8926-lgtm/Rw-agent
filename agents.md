# AGENTS.MD - Mobile Swarm Command Context

## Meta-Instructions
- Prioritize **Mobile-First UX** in all frontend changes.
- Ensure all backend tool inputs are validated via `ToolValidator`.
- Use `ASTMapper` for symbol lookup when agents are confused about imports.
- Consult `.docs/plans/mobile-swarm-command.md` before architectural shifts.

## Learned Patterns
- [2026-05-05] `affectedKeys().hasOnly()` is critical for Firebase security but must be paired with size checks.
- [2026-05-05] Pydantic `create_model` requires `Type` annotations for dynamic field generation.
- [2026-05-05] `tree-sitter` queries are faster than manual node traversal for large file parsing.
