---
name: universal-memory
description: Use proactively at the start and end of any conversation involving the user's ongoing projects, UniversalCouncil, durable project decisions, requirements, plans, capabilities, tools, project status, or owner directives. Load relevant canonical memory from GitHub before relying on prior-chat recollection, and record material durable changes as append-only memory events.
---

# Universal Memory workflow

Canonical repository:
`yassenjabal-jpg/UniversalCouncil`

Canonical branch:
`main`

Canonical memory paths:
- `memory/catalog.json`
- `memory/snapshots/GLOBAL.md`
- `memory/snapshots/COUNCIL.md`
- `memory/snapshots/projects/<project>.md`
- `memory/snapshots/ventures/<venture>.md`
- `memory/events/YYYY-MM-DD/*.json`

Use the connected GitHub integration for reads and memory-event writes.

## Core rule

Repository and governing evidence remain higher authority than memory.

Universal Memory is durable context and decision continuity. It must never be used to claim implementation that the source repository does not prove.

## Start-of-task preflight

Trigger this workflow proactively when the conversation is materially about an ongoing project, Council governance, durable preferences for project work, a previous decision, or project/tool/capability state.

1. Fetch `memory/catalog.json` from `main`.
2. Identify the relevant scopes from the user's request.
3. Fetch only the relevant generated snapshot(s), plus GLOBAL and COUNCIL when governance matters.
4. Use the smallest relevant context. Do not inject the entire memory history.
5. If catalog reports conflicts, state the conflict and do not choose a fact silently.
6. If a claim concerns current implementation, verify it against the actual project repository before treating it as execution truth.

Typical scope mapping:
- Universal Council governance → `council`
- RevenueSystem / المطابقة → `project/revenuesystem`
- YouTube strategy → `project/youtube`
- media production/toolchain → `project/media`
- venture-specific work → `venture/<name>`

If no relevant memory exists, continue normally. Do not invent a memory.

## Material-delta detector

After a material user decision or completed work slice, determine whether durable memory changed.

Write a memory event when one or more of these changed:
- owner directive;
- accepted decision;
- requirement;
- architecture;
- governing policy;
- capability status;
- verified implementation status;
- project status;
- durable workflow preference;
- cancellation or replacement of prior work;
- evidence that changes a prior canonical belief.

Do not persist:
- greetings or ordinary discussion;
- temporary brainstorms unless explicitly promoted to a proposal worth retaining;
- transient tool logs;
- duplicate facts;
- unverified implementation claims;
- passwords, access tokens, API keys, credentials, private keys;
- highly sensitive personal information;
- irrelevant private conversation content.

## Event contract

Create a new UTF-8 JSON file on `main` at:

`memory/events/YYYY-MM-DD/MEM-YYYYMMDD-HHMMSS-xxxxxx.json`

The suffix must be six lowercase alphanumeric characters. If the path already exists, generate a different suffix and retry.

Required fields:

```json
{
  "schema_version": "1.0",
  "event_id": "MEM-YYYYMMDD-HHMMSS-xxxxxx",
  "created_at": "timezone-aware ISO-8601",
  "scope": "global | council | project/<id> | venture/<id>",
  "level": "L2_PROJECT | L3_CANONICAL | L4_OWNER_DIRECTIVE",
  "kind": "decision | requirement | status | capability | preference | cancellation | evidence | proposal | policy | architecture",
  "subject": "stable.subject.key",
  "summary": "concise durable fact",
  "details": {},
  "supersedes": [],
  "confidence": "owner_confirmed | verified | evidence_backed | proposal",
  "sensitivity": "normal | private_non_sensitive",
  "tags": [],
  "source": {
    "type": "chat | council | repository | tool | migration",
    "ref": "optional reference",
    "commit": "optional verified commit"
  }
}
```

## Levels

### L2_PROJECT
Durable project context that is useful across sessions.

### L3_CANONICAL
Verified or evidence-backed Council/project state, architecture, policy or capability.

### L4_OWNER_DIRECTIVE
Use only when the user explicitly directs a durable governing rule or decision.
`confidence` must be `owner_confirmed`.

Do not infer L4 from tone.

## Superseding prior memory

Published events are immutable.

Never update or delete an old memory event just because a fact changed.

When replacing an active fact:
1. Find the active event for the same `scope + subject` in the catalog/snapshot.
2. Create a new event.
3. Put the old event ID in `supersedes`.
4. Keep the same stable subject when the conceptual fact is the same.

If two different active facts would remain for the same scope + subject, do not write blindly. Resolve which event is being superseded or surface the conflict.

## GitHub write boundary

The user has approved automatic Universal Memory synchronization only for:
- new files under `memory/events/**`;
- generated `memory/snapshots/**`;
- generated `memory/catalog.json`.

From ChatGPT, normally create only the new event file. The repository's Memory Rebuild workflow regenerates snapshots/catalog.

Never use this workflow to:
- rewrite an existing published event;
- force-push;
- modify project source code;
- write outside `memory/`;
- widen GitHub permissions.

If the GitHub connector itself requires a platform confirmation for a write, do not bypass it.

## After writing

The push to `memory/events/**` triggers the repository Memory Rebuild workflow.

On a later material read, fetch the latest catalog again rather than assuming the generated snapshot has already propagated.

If needed immediately, the new event itself is authoritative as an append-only memory record once GitHub confirms the commit.

## Response discipline

Do not narrate routine memory reads/writes unless:
- a memory conflict exists;
- a write is blocked;
- the user explicitly asks about memory;
- persistence materially affects the answer.

Memory should reduce repeated questioning, not add ceremony to every reply.
