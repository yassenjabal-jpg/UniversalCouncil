---
name: universal-memory
description: Use automatically for ongoing UniversalCouncil, RevenueSystem, Media, YouTube, venture, tooling, architecture, policy, or other project work where prior decisions or durable state may matter. Load canonical memory from GitHub before material work and write a durable memory delta after a material decision, requirement, status, capability, cancellation, policy, architecture, evidence, or preference change. Do not use for casual conversation or transient reasoning.
---

# Universal Memory workflow

Canonical repository: `yassenjabal-jpg/UniversalCouncil`
Canonical branch: `main`
Canonical memory root: `memory/`

GitHub is the durable source of truth for memory. Do not treat ChatGPT recollection, a local cache, or this skill package as the canonical project memory.

## Start-of-task preflight

For any ongoing Council/project task where prior context could affect the answer or action:

1. Use the connected GitHub tools to fetch `memory/catalog.json` from `yassenjabal-jpg/UniversalCouncil` on `main`.
2. Always consider the `global` scope and, for Council work, the `council` scope.
3. Select the smallest relevant project/venture scopes from the catalog.
4. Fetch only the relevant generated snapshots:
   - `memory/snapshots/GLOBAL.md`
   - `memory/snapshots/COUNCIL.md`
   - `memory/snapshots/projects/<name>.md`
   - `memory/snapshots/ventures/<name>.md`
5. If the catalog reports a conflict for a relevant scope+subject, do not guess. Surface the conflict and resolve it before treating either value as canonical.
6. Repository/evidence truth still outranks memory when the two disagree.

Do not load all snapshots or event history by default. Retrieve narrowly to reduce tokens.

## Durable delta detection

After any assistant turn or tool workflow that materially changes durable state, determine whether a memory delta exists.

Durable changes include:
- owner decisions or directives;
- accepted/rejected requirements;
- project status transitions;
- capability verification or loss;
- architecture/policy changes;
- cancellations or replacements;
- durable user preferences for a project;
- evidence that changes a prior conclusion.

Do not persist:
- brainstorming that was not adopted;
- temporary reasoning;
- duplicated facts;
- transient logs;
- passwords, tokens, API keys, credentials, private keys;
- sensitive personal/health/private information;
- content the user asked not to retain.

If no durable delta exists, write nothing.

## Write protocol

When a durable delta exists:

1. Fetch the current catalog again if the task was long or other writes may have occurred.
2. Choose a stable `scope` and `subject`.
3. If the same scope+subject already has an active event, place its event ID in `supersedes`.
4. Create a new immutable event file at:
   `memory/events/YYYY-MM-DD/MEM-YYYYMMDD-HHMMSS-xxxxxx.json`
   where `xxxxxx` is a new six-character lowercase alphanumeric suffix.
5. Use the connected GitHub file-creation action to create the file directly on `main`.
6. Never update or delete an existing published event. Corrections are new events that supersede old IDs.
7. Do not edit generated snapshots or `memory/catalog.json` directly. The repository workflow rebuilds them from events.
8. If file creation reports a collision, generate a different suffix and retry. If GitHub write access is unavailable, state that durable memory could not be written instead of claiming success.

## Event contract

Every event must contain exactly:

- `schema_version`: `"1.0"`
- `event_id`
- `created_at`: timezone-aware ISO-8601
- `scope`: `global`, `council`, `project/<slug>`, or `venture/<slug>`
- `level`: `L2_PROJECT`, `L3_CANONICAL`, or `L4_OWNER_DIRECTIVE`
- `kind`: one of `decision`, `requirement`, `status`, `capability`, `preference`, `cancellation`, `evidence`, `proposal`, `policy`, `architecture`
- `subject`: stable dotted identifier
- `summary`: concise current meaning
- `details`: structured non-secret fields
- `supersedes`: event IDs replaced by this event
- `confidence`: `owner_confirmed`, `verified`, `evidence_backed`, or `proposal`
- `sensitivity`: `normal` or `private_non_sensitive`
- `tags`
- `source`: object containing `type` and optional `ref`/`commit`

`L4_OWNER_DIRECTIVE` always requires `owner_confirmed`.

## End-of-task rule

Before finishing a material ongoing project/Council task:
- check whether a durable delta was created;
- write it if needed;
- never claim it was persisted unless the GitHub event-file creation succeeded.

This workflow is proactive but is not a platform-level post-message hook. It cannot guarantee interception of every unrelated ChatGPT conversation unless this plugin is active/selected or the workflow is triggered by the conversation context.
