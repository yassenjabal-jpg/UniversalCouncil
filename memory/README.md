# Universal Memory Fabric

GitHub is the durable source of truth for cross-chat and Council memory.

## Rules

- Memory events are append-only.
- Changes supersede older event IDs; old events remain auditable.
- Canonical snapshots are generated deterministically from active events.
- Two active events for the same scope + subject are a conflict, not an invitation to guess.
- Secrets, credentials and sensitive personal data are not stored in this repository memory.
- SQLite is a rebuildable local search cache, never the source of truth.
- ChatGPT and Council should read the latest GitHub memory before material work and write a memory delta after material decisions or state changes.

## Layout

- `events/YYYY-MM-DD/*.json` — immutable memory events.
- `snapshots/*.md` — generated current-state summaries.
- `catalog.json` — generated machine-readable canonical catalog.
- `schema/event.schema.json` — portable event contract.

Generated snapshots and the catalog may be replaced; event files may not be rewritten after publication.
