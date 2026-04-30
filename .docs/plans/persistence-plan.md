# Persistence Sprint Plan

## Goals
1. Implement local-to-remote file synchronization in `backend/storage.py`.
2. Evaluate and integrate `SqliteSaver` replacement with persistent database.
3. Configure environment variables for storage backend.

## Milestones
- [x] Implement `persist_file` and `fetch_file` in `backend/storage.py`.
- [x] Create database schema migration plan.
- [ ] Refactor `SqliteSaver` usage to Cloud SQL/Firestore.
