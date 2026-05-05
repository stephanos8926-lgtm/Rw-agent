# Mobile Swarm Command: Strategic Blueprint

Goal: Enable high-fidelity software engineering from a mobile device via a swarm of specialized agents.

## Strategic Pillars

1. **Information Density & "The Thumb"**: The UI must prioritize actionable insights over wall-of-text logs. Critical commands must be easily accessible to thumb-reach (bottom-oriented).
2. **Polyglot AST Grounding**: The agents must navigate codebases via semantic indexes (tree-sitter), not just grep, to understand context on small screens.
3. **MCP-first Interoperability**: Every core system capability should be a tool validated by Pydantic.
4. **Self-Healing Infrastructure**: The reflection node must catch and fix compiler errors before the user even sees them.

## Gap Analysis (Preliminary)

- [ ] **Mobile Responsive UI**: `SwarmObserver` is too dense; needs a "Condensed" mode.
- [ ] **Command Input**: Text-heavy `/commands` are slow on mobile keyboards; need a "Quick-Action" radial menu or bar.
- [ ] **Context Windowing**: Backend needs better summarization for mobile retrieval (Semantic hit/miss tuning).
- [ ] **State persistence**: Real-time message bus sync over flaky mobile networks.
