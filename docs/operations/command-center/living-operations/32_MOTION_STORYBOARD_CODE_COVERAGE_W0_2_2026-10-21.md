# W0.2 — Storyboard-to-Code Coverage Contract
## CC-MOTION-W0-2-STORYBOARD-CODE-COVERAGE-2026-10-21

Status: **MOTION_STORYBOARD_CODE_COVERAGE_LOCK**

W0.1 prerequisite: **MOTION_RETURN_BASELINE_LOCK — PASS**

This contract turns the governing Motion Bible, State/Motion Matrix, Event Mapping, and P1 storyboard into an implementation/evidence contract. A signature family is not accepted because a similarly named animation method exists; it must be driven by the matching semantic event/state and have a Reduced Motion equivalent plus evidence step.

## Coverage matrix

| Signature family | Semantic event | Semantic object | Screen | Full Motion | Reduced Motion | Required code path | Evidence step |
|---|---|---|---|---|---|---|---|
| `ROLE_ACTIVATION` | `ROLE_ACTIVATED` | Role Sigil + route from Project Core | Home / Owner Workspace; Living Project Workspace; Studio Project; Owner Decision Mode | Project Core remains fixed; semantic route grows to only the participating Sigil; target Sigil resolves into active state; unrelated roles remain still. | Source focus -> crossfade/state emphasis -> destination Sigil focus; no route travel. | `ApplyMotionEvent -> AnimateRoleActivationEvent` | role-activated: capture source frame, route-growth run, active-Sigil settle; assert unrelated-role pixels remain stable outside bounded tolerance. |
| `ROLE_ACTIVATION` | `ROLE_STATE_CHANGED` | Active Role Sigil state | Same role-bearing screens | Bounded role-state transition only when the role state changes; stop immediately on idle/unknown. | Immediate state/icon/text update with short crossfade only. | `ApplyMotionEvent -> ApplyRoleStateMotion` | role-state-changed: record ACTIVE->IDLE and ACTIVE->UNKNOWN; assert motion stops on UNKNOWN. |
| `ARTIFACT_HANDOFF_RETURN` | `ARTIFACT_HANDOFF_STARTED` | Artifact + source role/stage + destination role/stage | Living Project Workspace; Studio Project; Pulse / Visual Project Story | Source highlight -> artifact detaches -> follows semantic route -> destination highlights while artifact arrives; source and destination identities remain visible. | Source focus -> artifact state crossfade -> destination focus; no travel. | `ApplyMotionEvent -> AnimateArtifactHandoffStarted` | handoff-started: timestamp source highlight, detach, route, destination focus; verify object identity persists. |
| `ARTIFACT_HANDOFF_RETURN` | `ARTIFACT_HANDOFF_ACCEPTED` | Arrived artifact + destination | Living Project Workspace; Studio Project | Destination resolves accepted/verified state only after accepted event; route fades after settlement. | Destination accepted badge/state appears with short crossfade. | `ApplyMotionEvent -> AnimateArtifactHandoffAccepted` | handoff-accepted: prove accepted state appears only after accepted event timestamp. |
| `ARTIFACT_HANDOFF_RETURN` | `ARTIFACT_RETURNED` | Artifact + reverse route + Return Ticket | Living Project Workspace; Studio Project; Pulse / Visual Project Story | Destination de-emphasizes -> artifact follows reverse semantic route -> source highlights -> Return Ticket becomes inspectable. | Destination focus -> crossfade returned artifact/source focus -> Return Ticket visible. | `ApplyMotionEvent -> AnimateArtifactReturned` | artifact-returned: prove reverse direction, source settlement, and visible Return Ticket with no accepted-state residue. |
| `OWNER_DECISION_FOCUS` | `OWNER_DECISION_REQUIRED` | Originating project context + Decision Card + evidence/dissent paths | Owner Decision Mode | Project context de-emphasizes without disappearing; Decision Card elevates; evidence/dissent paths become readable; motion settles into inspectable state. | Project context de-emphasis crossfade -> Decision Card focus -> evidence/dissent indicators visible. | `ApplyMotionEvent -> AnimateOwnerDecisionRequired` | decision-required: verify hierarchy shift and retained project context from pre-event to settled frame. |
| `OWNER_DECISION_FOCUS` | `OWNER_DECISION_RECORDED` | Decision Card + decision history | Owner Decision Mode | Decision Card resolves into recorded state/history; no downstream running animation until a separate project/autopilot event arrives. | Recorded state/history crossfade only. | `ApplyMotionEvent -> AnimateOwnerDecisionRecorded` | decision-recorded: prove recorded state and prove autopilot remains unchanged absent a resume event. |
| `RECOVERY` | `AUTOPILOT_RECOVERY_STARTED` | Current flow + last VERIFIED checkpoint | Software Autopilot Project; Checkpoint / Recovery / Fork | Forward flow stops -> current work de-emphasizes -> last VERIFIED checkpoint focuses -> bounded rewind toward that checkpoint -> pending recovery hold. | Forward activity stops -> last VERIFIED checkpoint focus -> pending recovery label/state; no rewind travel. | `ApplyMotionEvent -> AnimateRecoveryStarted` | recovery-started: assert running motion stops before rewind and pending state remains after rewind. |
| `RECOVERY` | `CHECKPOINT_RESTORE_REQUESTED` | Selected checkpoint + pending restore state | Checkpoint / Recovery / Fork | Intent cue only; selected checkpoint focuses and restore remains pending. Never animate success. | Selected checkpoint focus + pending label. | `ApplyMotionEvent -> AnimateRestoreRequested` | restore-requested: assert no RESTORED/VERIFIED visual before verified event. |
| `RECOVERY` | `CHECKPOINT_RESTORED_VERIFIED` | Verified restored checkpoint + project current state | Checkpoint / Recovery / Fork; Living Project Workspace | Pending hold resolves -> verified restored checkpoint settles -> project state reconciles -> only then may normal flow resume on a later running event. | Verified restored state crossfade; no travel. | `ApplyMotionEvent -> AnimateCheckpointRestoredVerified` | restore-verified: assert VERIFIED settle occurs after event and no fake running state is introduced. |
| `FORK_BRANCH` | `FORK_CREATED` | Parent checkpoint + preserved original + Branch A/B | Checkpoint / Recovery / Fork | Source checkpoint pauses -> branch grows from parent -> A/B identities emerge -> original remains visibly preserved -> equal compare state settles. | Parent focus -> A/B cards appear together -> original-preserved indicator remains. | `ApplyMotionEvent -> AnimateForkCreated` | fork-created: verify branch origin, simultaneous A/B availability, and preserved original. |
| `FORK_BRANCH` | `BRANCH_SELECTED` | Selected branch + unselected branch + original | Checkpoint / Recovery / Fork | Explicit selection emphasis resolves on chosen branch; unselected branch remains inspectable; original remains preserved. | Selected state/icon emphasis with no travel. | `ApplyMotionEvent -> AnimateBranchSelected` | branch-selected: prove only chosen branch gains selected state and comparison remains available. |
| `VERIFIED_COMPLETION_WORK_RECEIPT` | `PROJECT_COMPLETED_VERIFIED` | Verified stage rail + final artifacts + Work Receipt | Project Complete / Work Receipt | Verified stages settle -> final artifacts gather into receipt context -> active motion stops -> Work Receipt appears -> one restrained completion cue -> next actions become inspectable. | Verified states settle -> artifacts/receipt crossfade into final arrangement -> final status shown; no gather travel. | `ApplyMotionEvent -> AnimateProjectCompletedVerified` | project-completed-verified: prove event gating, artifact gather/settle, stopped activity, receipt appearance, and single restrained cue. |

## Family coverage

- `ROLE_ACTIVATION`: 2 required semantic event row(s).
- `ARTIFACT_HANDOFF_RETURN`: 3 required semantic event row(s).
- `OWNER_DECISION_FOCUS`: 2 required semantic event row(s).
- `RECOVERY`: 3 required semantic event row(s).
- `FORK_BRANCH`: 2 required semantic event row(s).
- `VERIFIED_COMPLETION_WORK_RECEIPT`: 1 required semantic event row(s).

All six signature families have at least one required event row. Handoff/Return, Decision, Recovery, and Fork are intentionally multi-event because a single visual cue cannot truthfully represent their complete lifecycle.

## Mandatory implementation law

1. Runtime/event source emits facts; the WPF client selects presentation.
2. Signature acceptance requires event backing; hotspot-only cues cannot satisfy this contract.
3. Full Motion and Reduced Motion must represent the same semantic state transition.
4. Unknown events do not animate fabricated state.
5. Duplicate/late events must be idempotent and must not replay destructive UI effects.
6. State snapshot reconciliation remains authoritative over animation.
7. The eight-screen visual identity remains locked.

## Planned client seam

The implementation seam is `ApplyMotionEvent`. It may be backed initially by deterministic evidence fixtures while Stage 8 remains closed, but fixtures must emit the same semantic event envelope and may never claim live runtime authority.

This distinction is critical: **event-backed prototype evidence is allowed; fabricated live execution is not.**

## Evidence law

Every row has an explicit evidence step. W0.3 must make those steps timestamped and exact-head. Metrics can reject coverage, but only later human/owner review can approve perceptual clarity.

## Gate

`MOTION_STORYBOARD_CODE_COVERAGE_LOCK`

This gate authorizes W0.3 evidence-pipeline work only. It does not authorize merge, owner motion acceptance, Stage 8, runtime authority, or live execution.

W0.3 status here: **NOT STARTED**.
