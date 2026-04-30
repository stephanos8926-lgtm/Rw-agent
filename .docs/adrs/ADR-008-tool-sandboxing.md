# ADR-008: External Tool & Command Sandboxing

## Context
Our agentic OS uses `execute_shell` to perform tasks on the host system. This is a powerful but dangerous capability. We need a defined security policy for command execution to protect the home server from malicious or unintended actions.

## Decisions Made
1. **Tool Isolation:** All external commands must be executed through specific tools that wrap commands in restricted environments.
2. **Deny-by-Default:** Commands not explicitly allowed in the `ALLOWED_COMMANDS` whitelist will be rejected.
3. **Sensitive Operations:** Any operation resulting in file system destruction (rm), networking reconfiguration (iptables), or user/permission management (chown/chmod) must trigger an `Administrative Mode` approval workflow.
4. **Logging:** All executed shell command inputs and outputs must be logged through the telemetry service.

## Consequences
- **Positive:** Improved security posture; prevents accidental system damage.
- **Negative:** Increased overhead for user approval on sensitive tasks.

## Future Improvements
1. **Containerized Sandboxing:** Once environment allows, move command execution into light-weight ephemeral containers (e.g., Docker or GVisor).
2. **Dynamic Whitelisting:** Build a UI for managing command permissions.
