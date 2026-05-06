# AGENTS.MD - Mobile Swarm Command Context

## Meta-Instructions
- Prioritize **Mobile-First UX** in all frontend changes.
- Ensure all backend tool inputs are validated via `ToolValidator`.
- Use `ASTMapper` for symbol lookup when agents are confused about imports.
- Consult `.docs/plans/mobile-swarm-command.md` before architectural shifts.
- Whenever I send you `.` Then you can interpret that as if I were to say "Make sure everything we have discussed is properly layed out in the .docs folder as implementation plans and research documentation. When you are certain things are up to date, review everything in the .docs folder and summarize for me what needs to be done and where we are now. Then determine the next most logical step forward. When ready, proceed by taking that best step and executing whatever needs to be done to accomplish finishing it with speed and accuracy. Begin a long and focused sprint to start eliminating things that are left to do within the .docs folder.. or if we have already begun the sprint, continue forward with the sprint . . Accomplishing as much as possible each turn without stopping for any reason, including human intervention with me. You are granted authority to work without needing my consent as long as possible. Only stop for discussing huge architectural pivots, design changes. Or if you encounter large systemic issues.. recurring bugs.. if you come into a problem that could be resolved by obtaining knowledge only I have.. or if you are trapped within a loop that needs to be stopped. Note however, you should stop to iterate over the changes you've made at least every 10 minutes at the least to prevent time outs and to give me enough time to safely commit changes to the upstream repository if nessecary. A message that consists of a single full stop/period/decimal symbol can be interpreted as as if I sent this very message."

## Learned Patterns
- [2026-05-05] `affectedKeys().hasOnly()` is critical for Firebase security but must be paired with size checks.
- [2026-05-05] Pydantic `create_model` requires `Type` annotations for dynamic field generation.
- [2026-05-05] `tree-sitter` queries are faster than manual node traversal for large file parsing.
- [2026-05-06] PATTERN: Sidebar AST symbols filtering - `useMemo` is crucial to prevent unnecessary recomputations when filtering large AST symbol maps.
- [2026-05-06] PATTERN: Mobile Command Bar - Standardizing icons/layout in mobile grid layouts improves usability significantly; focus on touch-ready sizes >44px for action targets.
