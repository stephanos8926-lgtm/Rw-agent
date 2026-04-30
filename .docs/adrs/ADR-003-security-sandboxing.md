# ADR-003: Security Sandboxing & Authentication Layer

## Context
As we extend Forge Agentic OS to execute arbitrary code and interact with the filesystem, the current basic shell command filtering is insufficient for a production-grade system. We need a hardened security layer that strictly enforces resource boundaries and handles user authentication.

## Decisions Made
1. **Sandboxing:** Shell command execution will move to an isolated, restricted subprocess environment (chroot/container-based if available) instead of simple path checks.
2. **Path Hardening:** All filesystem interactions will go through a canonical path validation utility that prevents directory traversal attacks and restricts access to approved workspaces (`/app/src`, `/app/backend`, `/app/tests`).
3. **Authentication:** Implement a middleware-based authentication layer (API key-based initially) to guard sensitive backend tools and routes.

## Consequences
- **Positive:** Improved security posture mitigating RCE risks and data exfiltration.
- **Negative:** Increased complexity in tool execution paths and potential latency overhead in shell command execution.

## Future Improvements
1. **Per-Workspace Sandboxing:** Utilize ephemeral sidecar containers for tool execution.
2. **Granular RBAC:** Implement fine-grained access control based on user identity for tool availability.
