# Memory Fabric — Visual Review Compatibility Repair
Date: 2026-10-19
Status: CANDIDATE / TESTING
Issue: #41
Base: `3aa9af7c0e79c5601636b395f4ae9ca5cd9ca560`

## Problem

The immutable published event:

`memory/events/2026-10-18/MEM-20261018-235600-vis1lock.json`

was authored with an evidence vocabulary newer than the runtime validator:
- kind: `gate_lock`
- confidence: `verified_evidence`
- source.type: `github_ci_and_visual_review`
- source provenance fields:
  - `product_commit`
  - `ci_run_id`
  - `governance_commit`

The event must not be rewritten in place because published memory events are append-only audit records.

## Repair

The runtime now has a bounded compatibility vocabulary:
- `COMPAT_KINDS = {"gate_lock"}`
- `COMPAT_CONFIDENCE = {"verified_evidence"}`
- `COMPAT_SOURCE_TYPES = {"github_ci_and_visual_review"}`

Ordinary source types keep their original allowed fields:
- `type`
- `ref`
- `commit`

Only the visual-review compatibility source may additionally contain:
- `product_commit`
- `ci_run_id`
- `governance_commit`

The JSON schema mirrors the same distinction through separate source shapes.

## Security / invariants retained

This repair does not weaken:
- secret-like detail-key rejection;
- unsupported top-level event field rejection;
- unknown source-type rejection;
- ordinary-source extra-field rejection;
- conflict detection;
- supersedes validation;
- owner-directive confidence rule.

In particular, `L4_OWNER_DIRECTIVE` still requires exactly `owner_confirmed`.
`verified_evidence` does not satisfy that rule.

## Test proof required

Before merge:
1. the immutable visual-review event validates unchanged;
2. ordinary sources reject visual-review provenance fields;
3. unknown source types remain rejected;
4. L4 + verified_evidence remains rejected;
5. memory preflight rebuild succeeds on the repository;
6. Company Stage 0 succeeds;
7. existing memory tests remain green;
8. CodeQL succeeds.

## Merge rule

Do not rewrite the published event.
Do not merge unless exact-head CI proves the repository preflight is restored.
