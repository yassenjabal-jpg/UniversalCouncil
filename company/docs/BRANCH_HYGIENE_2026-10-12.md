# Branch Hygiene Review - 2026-10-12

Status: CLASSIFIED
Repository: `yassenjabal-jpg/UniversalCouncil`
Reference branch: `origin/main@bfc08b5ea98f352f595029f62fcefe6cc93395fb`

This review classifies remote branches before cleanup. No branch is deleted by name or age alone.

## Classification rules

- `MERGED_EQUIVALENT`: branch head is an ancestor of `origin/main`; safe to delete after recording evidence.
- `SUPERSEDED`: tree is identical to `origin/main`; safe to delete after recording evidence.
- `ACTIVE`: current hardening branch; keep.
- `UNMERGED_REQUIRES_REVIEW`: branch is not an ancestor, tree differs, and it has unique commits; keep until a dedicated review decides how to reconcile it.

## Results

| Branch | Head SHA | Ancestor of main | Same tree | Changed files | Unique commits | Classification | Action |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| `origin/codex/company-governance-hardening-v1` | `446335d4aeb1fc3bf4830e209dba1d00b0622232` | no | no | 52 | 19 | UNMERGED_REQUIRES_REVIEW | KEEP/REVIEW |
| `origin/codex/market-reality-definition-gate-v1` | `ab8733bbed9aac79e01e33e45dc0bac78d9b502e` | no | no | 43 | 16 | UNMERGED_REQUIRES_REVIEW | KEEP/REVIEW |
| `origin/codex/media-venture-capability-v1` | `56b102321ce5186f9270c7a49134ed4a138bfa9d` | no | no | 36 | 15 | UNMERGED_REQUIRES_REVIEW | KEEP/REVIEW |
| `origin/codex/venture-operating-system-v1` | `fa445dc412f959df608296a3ff838985c9766242` | no | no | 57 | 63 | UNMERGED_REQUIRES_REVIEW | KEEP/REVIEW |
| `origin/feat/council-intelligence-gateway-v1` | `b0435ac34f358fa1757d0bccdd98d1007091ed84` | yes | no | 21 | 0 | MERGED_EQUIVALENT | DELETE_SAFE |
| `origin/feat/hr-proactive-capability-scouting-v1` | `e8fa6987bde9e4f41dd8503bbda63151b4985639` | no | no | 23 | 18 | UNMERGED_REQUIRES_REVIEW | KEEP/REVIEW |
| `origin/feat/work-environment-hardening-v1` | `dd926f765b5d25a3a2c26a158d6275b0a41b6963` at classification time | no | no | 15 | 33 | ACTIVE | KEEP |

The symbolic remote name `origin` is not treated as a branch and is excluded from cleanup.

## Non-ancestor review notes

- `codex/company-governance-hardening-v1`: unique commits include HR accountability and capability-control work; diff spans company governance/config/runtime files. Not safe to infer supersession.
- `codex/market-reality-definition-gate-v1`: unique commits include Market Reality gate acceptance and HR local-market capability work. Not safe to delete without semantic reconciliation.
- `codex/media-venture-capability-v1`: unique commits include media venture production capability and publishing-boundary tests. Not safe to delete without semantic reconciliation.
- `codex/venture-operating-system-v1`: 63 unique commits remain and broad Stage 0 governance/runtime paths differ. Must remain.
- `feat/hr-proactive-capability-scouting-v1`: unique commits affect capability scouting plus Intelligence Gateway/runtime tests. Must remain until explicitly reconciled.

## Safe cleanup decision

Only `feat/council-intelligence-gateway-v1` is approved for remote deletion in this pass because:

1. its head is an ancestor of `origin/main`;
2. it has zero unique commits relative to `main`;
3. the Council Intelligence Gateway implementation is already represented in current `main`.

All other historical branches remain untouched.

## Post-delete readback

PENDING until the safe branch deletion is executed and `git fetch origin --prune` confirms absence.
