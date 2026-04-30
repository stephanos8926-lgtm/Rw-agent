# ADR-007: Telemetry Retention Policy

## Context
Our agentic OS is running on a local home server with limited storage. We cannot store telemetry logs indefinitely. We need a retention policy for structured event logs (`/logs/events.jsonl` or similar) to prevent disk space exhaustion.

## Decisions Made
1. **Retention Period:** Keep event logs for 30 days.
2. **Rotation Strategy:** Daily rotation of log files.
3. **Archival:** Keep only the first day of each month for long-term trend analysis; delete others.

## Consequences
- **Positive:** Predictable storage usage, reduced risk of disk saturation.
- **Negative:** Limited history for debugging older agent interactions beyond 30 days.

## Future Improvements
1. **Log Aggregation:** Integrate with a lightweight local tool like Loki/Grafana if telemetry analysis needs become complex.
