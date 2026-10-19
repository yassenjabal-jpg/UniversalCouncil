# UniversalCouncil Command Center — Stage 3 Orchestration Lock
Date: 2026-10-19
Status: PASS / LOCKED AS PLANNING ORCHESTRATION FOUNDATION

## Gate
`COMMAND_CENTER_STAGE3_ORCHESTRATION_LOCK`

## Product pin
- Repository: `yassenjabal-jpg/UniversalCouncil`
- Product branch: `command-center/stage3-orchestration`
- Exact product SHA:
  `2073b0ff5800156e6d908efc43493715c83f22bc`
- Draft PR: `#44`
- Base product SHA:
  `448c5b7ce8bff6b9ec3875106922528036695b6c`

## Locked architecture

`App bootstrap -> View -> ViewModel -> Host -> Application -> Infrastructure -> read-only repository projection`

Locked responsibilities:
- App owns composition.
- View remains presentation-only.
- ViewModel exposes projections.
- Host composes read/planning services.
- Application owns deterministic orchestration rules.
- Infrastructure owns file/JSON access.
- Core owns contracts.
- no model/tool/provider/execution implementation exists in Presentation.

## Canonical Council/Studio source

The orchestration catalog is generated from:
- `config/roles.json`
- `company/config/council_role_contracts.json`
- `company/config/council_routing_candidate.json`
- `company/config/channel_operating_system.json`
- `company/config/media_venture.json`

CI regenerates the catalog and fails if it drifts.

Source identity uses Git blob SHA, not checkout-normalized bytes.

## Council lock

Projected registry:
- 8 core roles;
- 16 specialist roles.

Routing rules are deterministic and explicit.

Free-text keyword authority routing remains:
`DISABLED`

Role authority cannot be inflated by the catalog.

## Studio lock

Projected departments:
12.

Locked macro sequence:
`WRITING -> PRE_PRODUCTION -> PRODUCTION`

Locked invariants:
- one active craft department;
- one primary program per stage;
- accepted handoff before downstream activation;
- downstream direct repair forbidden;
- formal Return Ticket to source;
- Producer/control plane does not become craft executor;
- Human Assistance remains bounded/on-demand.

## Model-control lock

`ROLE != MODEL`

Required:
- Owner-controlled selection;
- no role-forced model;
- no silent fallback;
- stronger model grants no authority;
- provider disconnected in Stage 3.

Selection precedence:
`TASK_OVERRIDE -> ROLE_OVERRIDE -> PROJECT_DEFAULT -> GLOBAL_DEFAULT`

## Runtime truth lock

Stage 3 default:
`NO_LIVE_TASK`

The product may not fabricate:
- active Council roles;
- active Studio department;
- active model;
- provider call in flight;
- execution progress.

## Exact-head verification

Workflow:
- `Command Center Stage 3`
- run #14
- ID: `39216663102`
- conclusion: `SUCCESS`

Passed:
1. exact candidate checkout;
2. exact SHA assertion;
3. canonical orchestration regeneration;
4. projection drift check;
5. architecture/truth boundary;
6. restore;
7. WPF build;
8. Stage 2 fail-closed regression suite;
9. Stage 3 adversarial suite;
10. exact-head UI rendering;
11. UI artifact upload;
12. publish;
13. published read-model assertions;
14. application artifact upload.

CodeQL:
- run #500
- ID: `39216663046`
- conclusion: `SUCCESS`

## Artifacts

Application:
- ID: `12170340343`
- digest:
  `sha256:98b0fd75123f5605a9927155bd0c32d68614318e0e414bda7bd55ec27026c39d`

UI evidence:
- ID: `12169931611`
- digest:
  `sha256:cce3f88c08f8eef74dcdd3c56a30dddc9d7492bfcbec040d40bfdb1f91756a11`

Operational state SHA-256:
`1575a1c0fdcf93f7de1eadd1d1107ced7ad9b1f5802644b002b5f42b0c74fdf4`

Orchestration catalog SHA-256:
`314027108bf7ff582a0e30faea6965210e00ca20652ed9ae51d126bf37a1ca88`

1440×900 UI:
`sha256:c2a1945178866a79a695487ce8a05617b2a439152b49eee8cb19d60c4c141be2`

1180×720 UI:
`sha256:13e654562e84a3bd06b3869fd53d2174bd3477f008f6d6fd0052b7c4d0ad0d79`

## Review locks

Council:
`PASS_STAGE3_PLANNING_ORCHESTRATION`

Studio:
`PASS_STAGE3_COUNCIL_STUDIO_SURFACE`

Architecture:
`PASS_STAGE3_ARCHITECTURE_BOUNDARY`

## Retained blockers

### Phase 0
No live execution authority has been granted.

Stage 3 lock does not permit:
- YASSIN shell/process actions;
- GUI automation;
- remote commands;
- provider/model calls;
- credentials;
- provider fallback;
- approval writes.

### Company Stage 0
Repository-wide Company Stage 0 still fails due the pre-existing Memory Fabric compatibility defect tracked separately.

This lock does not waive that failure.

## Downstream Stage 4 rule

Stage 4 may introduce:
- YASSIN Execution Service interfaces;
- provider registry;
- controller lease;
- postcondition verification;
- execution receipts;
- native/GUI provider abstractions.

Stage 4 may not:
- put execution logic in WPF;
- use read-only Owner Desk records as authorization;
- enable a provider merely because it is installed;
- replay UNKNOWN;
- use silent model/provider fallback;
- bypass Phase 0 live execution gates.

## Next stage
`PHASE 4 — YASSIN Execution Service & Provider Fabric`

State:
`AWAITING_OWNER_STAGE4_OPEN`
