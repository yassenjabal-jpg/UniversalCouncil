# Living Operations Component Anatomy

Status: IMPLEMENTATION COMPONENT CONTRACT

Appearance must use the pinned parent image and the geometry in `19_REFERENCE_FIDELITY_AUDIT_AND_CONTRACT.md`. This semantic inventory does not authorize rearranging the screen or replacing the reference medallions.

## 1. Project Core

Purpose:
Primary identity object for an opened project.

Contains:
- title;
- project type;
- health/state;
- current stage;
- owner decision if any;
- Autopilot state.

Must not contain:
- every metric;
- raw logs;
- infrastructure trivia.

Click targets route to the corresponding semantic object.

## 2. Autopilot Rail

Visual:
past -> current -> future.

Required states:
- OFF
- READY
- RUNNING
- WAITING_OWNER
- BLOCKED
- RECOVERING
- SUSPENDED_RESOURCE_WAIT
- PAUSED
- COMPLETE

Required fields:
- stage;
- last verified checkpoint;
- current model/reasoning;
- elapsed time;
- current tool;
- recovered issue count;
- fallback state.

Primary interactions:
- current marker -> Live Execution Detail;
- checkpoint -> Checkpoint Inspector;
- Pause;
- Stop & Preserve;
- Review Activity.

## 3. Role Sigil

Layers:
1. role glyph;
2. semantic state ring;
3. reasoning rings when active;
4. small truth/blocker badge if needed.

States:
- idle;
- activated;
- thinking/reviewing;
- waiting;
- blocked;
- completed.

Do not personify the Sigil as a human unless a real human role is explicitly represented.

## 4. Project Filmstrip

Each frame contains:
- artifact preview;
- version/state;
- timestamp;
- truth badge;
- source role/tool.

States:
- before;
- revision;
- handoff;
- returned;
- rejected;
- verified;
- current.

Filmstrip is virtualized and horizontally navigable.

Click -> Version Inspector.

## 5. Decision Card

Layers:
- decision question;
- why now;
- recommendation;
- strongest dissent;
- evidence summary;
- impact columns;
- actions.

Density:
lower than normal project cards.

Truth:
must distinguish recommendation from Owner authority.

## 6. Evidence Peek

Compact contextual surface.

Required:
- source;
- source ID/path/run/commit when applicable;
- verification time;
- truth classification;
- short evidence summary;
- Open Full Evidence.

May not claim provenance that the evidence layer cannot provide.

## 7. Tool Dock

Groups:
- Active Now;
- Project Tools;
- All Tools.

Tool object:
- icon;
- name;
- state;
- optional active artifact.

Only active tool receives strong visual emphasis.

Click -> Tool Inspector.

## 8. Model / Reasoning Chip

Shows:
- model/provider;
- effort;
- fallback indicator when used.

Click -> Model & Reasoning Inspector.

The UI does not silently coerce unsupported effort levels.

## 9. Checkpoint

Contains:
- checkpoint ID;
- time;
- verification state;
- optional label.

Click -> Checkpoint Inspector.

## 10. Fork Node

Contains:
- branch name;
- parent checkpoint;
- purpose;
- status;
- truth badge.

Branch lines are functional, not decorative.

## 11. Pulse Object

Compact view:
- type ring;
- media/thumbnail;
- title;
- project;
- truth badge.

Detailed view:
- artifact/media;
- What changed;
- Why;
- What next;
- evidence;
- actions.

## 12. Work Receipt

Final result object.

Sections:
- Requested;
- Completed;
- Final Artifacts;
- Evidence;
- Models / Reasoning;
- Tools;
- Elapsed Time;
- Cost/Usage when known;
- Issues Recovered;
- Fallbacks;
- Checkpoints;
- Council Decisions;
- Next Recommended Action.

No fake cost or timing estimates are displayed as actual usage.

## 13. Since You Were Away

Condenses activity into:
- meaningful changes;
- why they matter;
- what needs Owner.

Must suppress duplicate low-value events.

## 14. Notification / Owner Action

Notification payload is minimal and privacy-safe.

Opening routes to exact:
- decision;
- blocker;
- artifact;
- project event.

Do not embed secrets or sensitive evidence in lock-screen content.

## 15. Adaptive project centers

### Software center
- diff;
- branch;
- build/test;
- CI;
- checkpoint/fork;
- runtime evidence.

### Video center
- player;
- timeline;
- waveform;
- marker comments;
- variants;
- render/QC;
- handoff.

### Design center
- canvas preview;
- before/after;
- variants;
- review comments;
- evidence.

Shared components retain identical truth semantics.

