# Memory Snapshot — GLOBAL

> Generated from append-only memory events. Do not edit manually.

## memory.fabric.required
- **Event:** `MEM-20261012-182100-b2c3d4`
- **Level:** `L4_OWNER_DIRECTIVE`
- **Kind:** `architecture`
- **Confidence:** `owner_confirmed`
- **Updated:** `2026-10-12T18:21:00+03:00`
- **Summary:** Use a durable cross-chat and Council memory layer that preserves material changes, retrieves relevant context in future conversations, and synchronizes canonical memory automatically with GitHub.
- **Details:**
  - `canonical_store`: GitHub main
  - `change_model`: append-only events with supersedes
  - `claude_mem_role`: optional legacy source only; not canonical
  - `local_search`: SQLite FTS rebuildable cache
- **Tags:** memory, github, cross-chat, council

## source_of_truth.priority
- **Event:** `MEM-20261012-182000-a1b2c3`
- **Level:** `L4_OWNER_DIRECTIVE`
- **Kind:** `policy`
- **Confidence:** `owner_confirmed`
- **Updated:** `2026-10-12T18:20:00+03:00`
- **Summary:** For Council and project work, actual repositories and governing files outrank chat recollection; Universal Memory records durable deltas but does not override repository truth.
- **Details:**
  - `memory_role`: durable context and decision continuity
  - `priority`: ["actual repository state", "current main SHA", "governing contracts and evidence", "canonical memory", "chat recollection"]
- **Tags:** source-of-truth, governance, memory
