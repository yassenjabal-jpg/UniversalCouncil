# Universal Memory Fabric

Status: IMPLEMENTED / GITHUB-CANONICAL

## Goal

Provide durable, versioned memory shared by:
- UniversalCouncil on YASSIN;
- ChatGPT conversations using the Universal Memory private plugin;
- future Council runtimes and project agents.

GitHub `yassenjabal-jpg/UniversalCouncil` on `main` is the canonical memory store. Local SQLite is only a rebuildable search index.

## Memory lifecycle

### Read
Before material work on an ongoing project:
1. refresh canonical memory from GitHub;
2. validate all memory events;
3. fail if active facts conflict;
4. rebuild local FTS;
5. retrieve only relevant active memory.

### Write
After a material durable change:
1. classify the change;
2. create a new append-only event;
3. if it replaces an active fact, reference the old event in `supersedes`;
4. validate that no secret-like fields are present;
5. rebuild snapshots and reject unresolved conflicts;
6. sync the event to GitHub;
7. GitHub Action rebuilds canonical snapshots/catalog.

Normal conversation, temporary reasoning, duplicated observations and transient tool logs are not durable memory.

## Authority levels

- `L2_PROJECT`: project-scoped durable context.
- `L3_CANONICAL`: verified Council/project state or evidence-backed architectural decision.
- `L4_OWNER_DIRECTIVE`: explicit Owner directive. Requires `owner_confirmed`.

Memory never overrides the underlying repository or governing evidence for a project.

## Event immutability

Published events are immutable.

A correction is a new event:
```
new_event.supersedes = [old_event_id]
```

The old record remains available for audit and history.

If two active events exist for the same `scope + subject` without a superseding relationship, Memory Preflight fails instead of choosing one.

## Privacy boundary

Do not store in repository memory:
- passwords;
- API keys or access tokens;
- credentials or private keys;
- highly sensitive personal information;
- transient private conversation content that is not required for project continuity.

The validator rejects secret-like keys in event details.

## Repository layout

```
memory/
  events/YYYY-MM-DD/*.json
  snapshots/
    GLOBAL.md
    COUNCIL.md
    projects/*.md
    ventures/*.md
  catalog.json
  schema/event.schema.json
```

The event tree is canonical. Snapshots and catalog are deterministic generated views.

## Local commands

Refresh from GitHub and rebuild local SQLite index:

```
python tools/memory_preflight.py
```

Search canonical memory:

```
python tools/memory_search.py "youtube strategy"
```

Write an event spec and autosync:

```
python tools/memory_write.py memory-spec.json
```

Rebuild current working-tree snapshots:

```
python tools/memory_rebuild.py
```

Explicit autosync:

```
python tools/memory_sync.py
```

## GitHub autosync

Local writes do **not** modify the tracked `memory/` tree first. `memory_write.py` validates the delta against the latest GitHub memory, then places it in the gitignored pending queue under `.runtime/memory/pending/events/`.

The sync routine:
- serializes writers with a bounded lock wait and stale-lock recovery;
- opens a temporary detached worktree based on the latest `origin/main`;
- takes a snapshot of pending events and copies only that snapshot;
- refuses an event path whose content differs from the canonical copy;
- rebuilds snapshots and refuses canonical conflicts;
- commits with a dedicated Memory Fabric identity;
- pushes to `main`;
- retries after a push race;
- deletes only pending events confirmed present in the successful sync.

A new event that arrives while a sync is already running remains queued for the next lock holder; it is never removed by the earlier sync.

The current feature/work branch is not switched or overwritten, and normal memory writes do not leave tracked files dirty.

## GitHub Action

`.github/workflows/memory-rebuild.yml` watches `memory/events/**` on `main`.

After a new event arrives it:
- validates and rebuilds memory;
- regenerates snapshots/catalog;
- commits generated views if they changed.

A generated-snapshot commit does not retrigger the event workflow.

## ChatGPT private plugin

The Universal Memory private plugin is a cross-chat gateway, not a second database.

At the start of relevant project/Council work it retrieves the latest catalog and relevant snapshot from GitHub.

After a material change it creates a new event file directly on `main` through the authenticated GitHub connector. The GitHub Action then rebuilds snapshots.

This lets ChatGPT use the same durable memory when YASSIN is offline.

### Platform limitation

ChatGPT does not expose a guaranteed account-wide post-message hook that can silently process every message in every future conversation. The plugin therefore uses proactive workflow instructions:
- preflight when a conversation involves ongoing Council/project context;
- write a delta after material changes.

GitHub synchronization itself is automatic once an event is emitted.

## Council integration

`tools/council_preflight.py` includes Memory Preflight. A Council material session therefore fails closed when:
- canonical Git memory cannot be validated;
- a memory conflict exists;
- the search index cannot be rebuilt.

This prevents the Council from silently using stale or contradictory memory.
