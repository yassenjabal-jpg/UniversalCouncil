# Unified Event -> Animation Mapping

Status: CLIENT EVENT SEMANTICS CONTRACT

## Goal

Windows and Android should consume shared semantic events while rendering platform-specific motion.

The runtime emits facts/events.

The client chooses presentation.

The runtime does not request a named animation such as "play blue bounce".

## Event envelope

Conceptual envelope:

- event_id
- event_type
- project_id
- object_type
- object_id
- occurred_at
- truth_state
- payload
- evidence_ref when required
- sequence/version

Clients must tolerate unknown future event types without inventing state.

## Core mappings

### PROJECT_CREATED
Windows:
Command Composer -> Project identity transition.

Android:
Project appears in Active Projects.

No claim of active execution unless separate execution event exists.

### PROJECT_STAGE_CHANGED
Windows:
current rail marker transitions from old stage to new stage.

Android:
stage chip updates + short transition.

Required:
old/new stage supplied.

### AUTOPILOT_STARTED
Windows:
Autopilot rail becomes active; current marker begins low-frequency flow.

Android:
Autopilot status becomes RUNNING.

### AUTOPILOT_PAUSED
Stop active motion immediately.

### AUTOPILOT_WAITING_OWNER
Windows:
current rail stops on gold decision marker; Decision Stack receives card.

Android:
Decision Inbox + actionable notification if policy permits.

### AUTOPILOT_BLOCKED
Forward motion stops; coral blocker opens contextual route.

### AUTOPILOT_RECOVERY_STARTED
Windows:
focus last verified checkpoint; bounded rewind cue.

Android:
show "Recovery in progress" with checkpoint reference; no elaborate rewind required.

### CHECKPOINT_CREATED
Add marker.

### CHECKPOINT_VERIFIED
Marker receives verified state.

### CHECKPOINT_RESTORE_REQUESTED
Show intent only; do not animate restored success.

### CHECKPOINT_RESTORED_VERIFIED
Now complete restore transition.

### FORK_CREATED
Windows:
branch line grows from parent checkpoint.

Android:
branch card appears with parent relationship.

### BRANCH_SELECTED
Selected branch receives state emphasis. Original remains preserved.

### ROLE_ACTIVATED
Windows:
route path to Sigil appears.

Android:
role appears in active review list.

### ROLE_STATE_CHANGED
Update Sigil state; movement bounded by State/Motion Matrix.

### REASONING_EFFORT_CHANGED
Update reasoning rings + text.

Do not show unsupported effort as if active.

### TOOL_ACTIVE
Tool Dock emphasizes exact tool.

### TOOL_IDLE
Emphasis removed.

### TOOL_UNKNOWN
Stop activity animation and show UNKNOWN.

### ARTIFACT_CREATED
Artifact enters Filmstrip/Artifact area.

### ARTIFACT_HANDOFF_STARTED
Windows:
artifact object follows semantic path from source to destination.

Android:
handoff row/card transition.

### ARTIFACT_HANDOFF_ACCEPTED
Destination resolves verified/accepted state.

### ARTIFACT_RETURNED
Windows:
artifact route returns to source and Return Ticket becomes visible.

### ARTIFACT_VERIFIED
Apply verified badge only with evidence state.

### PULSE_DRAFT_CREATED
Add to Private Draft Shelf, not public Pulse.

### PULSE_PUBLISHED
Add to Pulse.

### PULSE_PROMOTED
Animate/indicate destination artifact only after destination creation succeeds.

### OWNER_DECISION_REQUIRED
Enter Decision Mode / Decision Inbox.

### OWNER_DECISION_RECORDED
Resolve decision UI into history.

Do not assume downstream execution resumed; wait for corresponding project/autopilot event.

### EVIDENCE_ATTACHED
Truth badge may gain Evidence Peek.

### PROJECT_COMPLETED_VERIFIED
Windows:
settle rail -> gather final artifacts -> Work Receipt.

Android:
completion screen/card + optional restrained haptic.

### CONNECTION_STATE_CHANGED
Update connection truth.

Do not animate "connected" before verified transport/session state.

## Event ordering

Clients must use sequence/version where available.

Rules:
- ignore duplicate event IDs;
- idempotent rendering;
- never replay destructive UI side effects;
- if an earlier event arrives late, do not regress current truth without explicit recovery/reset event;
- reconciliation can request a fresh snapshot.

## Snapshot + delta model

Preferred client pattern:

1. receive full project snapshot;
2. render stable state;
3. apply semantic deltas/events;
4. periodically reconcile;
5. on reconnect, refresh snapshot before resuming live event rendering.

This prevents animation from becoming the source of truth.

## Event -> navigation

Notifications contain semantic target:

- object_type;
- object_id;
- project_id;
- recommended view.

The client resolves to current object state instead of opening a stale static screen.

## Unknown event handling

Unknown event:
- no crash;
- no fabricated animation;
- log client compatibility notice;
- refresh relevant snapshot if needed.

## Security

Event payloads must not carry:
- bearer tokens;
- provider secrets;
- private credentials;
- unnecessary sensitive screenshots.

