# ADR-005: Storage & Data Persistence Strategy

## Context
Our agentic OS runs on a home server infrastructure. While SQLite is suitable for small-scale local persistence, we must implement robust, automated backups to prevent data loss due to hardware failure or corruption.

## Decisions Made
1. **Local Persistence:** Retain SQLite for primary local state storage.
2. **Automated Backup:** Implement a custom backup mechanism that archives data, configuration, and state files.
3. **Archive Format:** Use a structured archive (`.tar.bz2`) renamed to a custom extension `.agentark` containing a JSON manifest for integrity.
4. **Integrity:** Use `blake3` hashing for all files in the manifest to detect corruption.

## Consequences
- **Positive:** Full data control, no dependency on external cloud providers, robust backup system.
- **Negative:** Responsibility for hardware durability lies completely on the host.

## Future Improvements
1. **Remote Sync:** Implement a simple Rclone or SFTP sync component to move `.agentark` archives to off-site storage.
2. **Incremental Backups:** Optimize backup size by tracking only changed data.
