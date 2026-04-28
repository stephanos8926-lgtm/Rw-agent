# ADR-001: Context Caching & Semantic Routing Strategy

## Context
We need to implement caching mechanisms for the Forge Agentic OS to reduce token usage and latency. Gemini 2.5 Flash supports Context Caching, but there are structural limits and behavior quirks to account for. We also need to cache agentic thought/action loops at the application tier.

## Decisions Made

### 1. Two-Tier Caching Architecture
- **Tier 1 (Application/Semantic Level):** We use a local semantic cache (`semantic_cache.py`) backed by `text-embedding-004`. It intercepts standard LLM graph steps based on conversation context hashes and cosine similarity of user intents. 
    - *Experimentation configured:* We added an experiment tracker to evaluate hit/miss rates across the [0.95 - 0.99] threshold spectrum.
- **Tier 2 (API Level):** We use `google.genai.caching` (`context_cache.py`) to cache our largest payloads: system instructions and AST code maps over 32k tokens.

### 2. Context Caching Nuances & Best Practices
- **Minimum Token Limit:** Google's API requires at least 32,768 tokens for a payload to be cached. For small toy projects, the API falls back to standard execution (`[Context Cache BYPASSED]`). We implemented a manual fallback to handle this.
- **Dynamic Appending vs Full Cache:** The API design allows you to cache a `cached_content` blob (e.g. System Prompt + AST Map) and dynamically push `contents` (the interactive messages) per request without invalidating the cache. We structured `agent.py` to use `config_kwargs["cached_content"]` instead of passing the giant AST in the `contents` list every turn.
- **TTL Adjustments:** We are using a 1-hour TTL, checking OS `mtime` of the source `context.json` to ensure staleness never affects the agent.

## Future Improvements (Room for Improvement)

1. **Abstract Syntax Tree Integration with Tree-Sitter:** 
    We currently use standard Python `ast`. `tree-sitter` bindings are included in `.requirements.txt` but need to be wired up for polyglot AST mapping (e.g. mapping JS/TS).
2. **Optimistic Tool Caching:**
    Tools like `execute_shell("ls -la")` or `get_os_info()` could be cached at the *tool level* with a 5-second TTL using a simple hash map, bypassing the LLM semantic layer entirely for rapid-fire duplicate checks.
3. **Agentic Reflection on Thresholds:**
    The hit/miss rates mapped in our `SemanticCache.log_stats()` function should eventually feed back into the agent so that it can dynamically tune its own threshold based on workflow speed.
