# Navigation and Interaction Flow Maps

Status: OWNER WORKFLOW CONTRACT

## Flow 1 — First useful task

Home
-> Command Composer
-> short route/plan preview
-> Start
-> Project Workspace
-> Active Work / Autopilot
-> Pulse if meaningful progress
-> Decision Mode only when required
-> Work Receipt

Acceptance:
Owner starts useful work without entering System or understanding transport/runtime internals.

## Flow 2 — Inspect a Role

Project Workspace
-> click Role Sigil
-> Role Context drawer

From drawer:
- Evidence -> Evidence Peek/full evidence
- Finding -> Ask This
- Dissent -> Decision/Dissent Context
- Model/Reasoning -> Model Inspector

Back/close returns to exact project state.

## Flow 3 — Inspect reasoning

Role Sigil / Model Chip
-> click reasoning rings
-> Model & Reasoning Inspector

Possible actions:
- change task effort;
- change role override;
- inspect fallback;
- view usage.

Only authorized/supported controls enabled.

## Flow 4 — Inspect visual project history

Project
-> Filmstrip
-> select frame
-> Version Inspector

From Version Inspector:
- Compare
- Open Artifact
- Ask
- Evidence
- Fork from valid checkpoint/version

No destructive restore as the default action.

## Flow 5 — Checkpoint to fork

Autopilot Rail / Checkpoint timeline
-> Checkpoint Inspector
-> Create Fork
-> define branch purpose
-> branch created
-> Branch Workspace
-> compare branch outputs
-> select preferred branch through governed project action

Original remains preserved.

## Flow 6 — Recovery

Failure/no-progress detected
-> Autopilot state = RECOVERING
-> last verified checkpoint highlighted
-> Recovery Inspector

If verified recovery succeeds:
-> CHECKPOINT_RESTORED_VERIFIED
-> current work resumes

If state remains unknown:
-> UNKNOWN / HOLD
-> Owner alert if escalation policy requires.

## Flow 7 — Owner decision

Project/Pulse/notification
-> Decision Mode

Owner can:
- inspect strongest dissent;
- inspect evidence;
- ask question;
- approve;
- request changes;
- reject.

After recording decision:
-> decision enters history
-> project waits for actual downstream state update.

## Flow 8 — Tool inspection

Tool Dock
-> Tool Icon
-> Tool Inspector

Show:
- state;
- last verified timestamp;
- active artifact;
- current project;
- recent outputs.

Open tool only when there is an authorized implemented path.

## Flow 9 — Pulse to Action

Pulse Detail
-> Create Task / Decision / Research / Return Ticket
-> destination artifact creation
-> confirmation
-> original Pulse remains linked as source.

If creation fails:
Pulse remains unchanged and failure is shown.

## Flow 10 — Android notification

Push notification
-> app authentication/session check
-> refresh target object
-> open exact Decision/Pulse/Project object

Do not trust stale notification payload as current state.

## Flow 11 — Android media review

Notification/Pulse
-> Media Review
-> preview proxy
-> marker/timestamp feedback
-> optional voice comment
-> approve/request change

Approval intent travels to gateway and remains subject to server-side authorization.

## Flow 12 — Project complete

PROJECT_COMPLETED_VERIFIED
-> Work Receipt
-> final artifact preview
-> evidence
-> costs/usage where known
-> models/tools
-> recovered issues
-> next recommendation

Owner can:
- open/download artifact;
- start follow-up;
- archive;
- publish/deploy only through separately governed action.

## Flow 13 — Context-preserving Ask This

Any semantic object
-> Ask This
-> question composer inherits:
  - project;
  - object;
  - evidence references;
  - current state.

Answer returns in contextual panel.

No need to manually re-explain object context.

## Flow 14 — Blocked/disabled interaction

User clicks disabled-looking or blocked control
-> do not silently ignore
-> show:
  - why blocked;
  - current state;
  - what unlocks it;
  - whether Owner action is needed.

## Navigation laws

- Home is command-first.
- Projects are work-first.
- Waiting for You is decision-first.
- System is infrastructure-first.
- deep infrastructure never hijacks normal project flow.
- first-level inspection uses drawers/peeks.
- full navigation is reserved for sustained work.
- all interactions are keyboard-reachable on Windows.
- Android back returns to prior context.

