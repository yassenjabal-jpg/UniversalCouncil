# المرتكز — UX State Contract
Date: 2026-10-21
Status: MACHINE-READABLE CONTRACT COMPANION / POST-REVIEW PENDING

## 1. Purpose

This contract defines how Agentic Work OS truth is presented to the Owner across Windows and Android.

It is not a visual design specification.
It does not define new colors, layout geometry or art direction.

## 2. Canonical primary Job states

### QUEUED
Arabic label: **في الانتظار**

Meaning:
The Job is accepted into a queue but material planning/execution has not begun.

Owner attention:
No, unless queue delay itself becomes material.

Primary action:
Inspect/cancel only when implemented and authorized.

### PLANNING
Arabic label: **يتم إعداد الخطة**

Meaning:
The system is resolving context, authority, skill and execution plan.

Owner attention:
No by default.

Forbidden claim:
Do not imply execution has started.

### WAITING_FOR_APPROVAL
Arabic label: **ينتظر قرارك**

Meaning:
A policy/authority gate prevents progress until an authorized decision is recorded.

Owner attention:
Yes when the Owner is the required approver.

Primary action:
Open Decision Mode.

### EXECUTING
Arabic label: **جارٍ التنفيذ**

Meaning:
An authorized action/work step is in progress.

Owner attention:
No by default.

Primary action:
View activity; Pause only when supported and authorized.

### VERIFYING
Arabic label: **جارٍ التحقق**

Meaning:
The action may have occurred, but the required post-condition has not yet been independently verified.

Owner attention:
No by default.

Forbidden claim:
Do not render as complete.

### BLOCKED
Arabic label: **متوقف بأمان**

Meaning:
A known blocker prevents safe progress.

Owner attention:
Only when Owner action can materially resolve it.

Required UX:
show reason + what unlocks it.

### FAILED
Arabic label: **فشل التنفيذ**

Meaning:
The attempted step/job did not satisfy its required outcome.

Owner attention:
Policy-dependent.

Required UX:
failure reason + preserved state + safe next actions.

### UNKNOWN
Arabic label: **النتيجة غير مؤكدة**

Meaning:
Available evidence cannot prove success or failure.

Owner attention:
High when the effect is material.

Required UX:
Verify First.

Forbidden:
UNKNOWN -> SUCCEEDED.

### STALE_CONTEXT
Arabic label: **تغيّر السياق**

Meaning:
The Job’s immutable Context Capsule no longer represents current canonical truth.

Owner attention:
Not automatically.

Required UX:
show what changed; preserve work; issue a new capsule/re-plan.

Owner interruption is required only if the change is itself material/Change-of-Truth.

### CONTEXT_CONFLICT
Arabic label: **تعارض في مصادر الحقيقة**

Meaning:
Two or more governing sources conflict and policy cannot safely choose one.

Owner attention:
Yes when deterministic governance cannot resolve it.

Required UX:
compare sources/provenance; resolve through typed decision.

Execution:
Fail closed.

### SUCCEEDED
Arabic label: **اكتمل وتم التحقق**

Meaning:
Required post-conditions were independently verified for the exact artifact/state under review.

Owner attention:
No urgent attention by default.

Required UX:
Work Receipt / artifact / evidence.

Forbidden:
tool success -> SUCCEEDED without verification.

---

# 3. Secondary overlays

Secondary overlays never replace the primary state.

## PAUSED
Control overlay.
Meaning:
Progress is intentionally suspended with state preserved.

## RECOVERING
Execution-mode overlay.
Meaning:
The system is attempting bounded recovery from a verified checkpoint or known failure.

It is not success.

## RETURNED_FOR_CHANGES
Review overlay.
Meaning:
A reviewer returned the artifact/change to its source stage.

## MURTAKAZ_REVIEW_REQUIRED
Governance overlay.
Meaning:
A material result exists but cannot be adopted until post-review.

## APPROVED_BY_AL_MURTAKAZ
Governance overlay.
Meaning:
The exact reviewed revision/artifact has explicit Murtakaz approval.

It does not independently grant live execution authority.

## FALLBACK_USED
Execution provenance overlay.
Meaning:
An explicitly permitted fallback was used.

Must disclose provider/tool/model and reason in details/receipt.

---

# 4. Presentation hierarchy

## Level 1 — Owner summary
Show:
- primary state;
- concise meaning;
- Owner action only when needed.

Used by:
- Home;
- notifications;
- project cards.

## Level 2 — Context
Show:
- why;
- current stage/step;
- checkpoint;
- source revision;
- last verified event;
- evidence summary.

Used by:
- Project Workspace;
- Decision Mode;
- Recovery;
- state drawers.

## Level 3 — Technical trace
Show:
- Context Capsule id;
- Skill/version;
- route decisions;
- model/provider/reasoning;
- tool effects;
- exact hashes;
- verification details;
- approvals.

Used by:
- Evidence;
- System;
- Work Receipt;
- advanced inspectors.

---

# 5. Owner attention rules

An Owner notification/Decision Stack entry requires:
1. the Owner can make a meaningful decision now; and
2. the issue is material enough to interrupt.

Do not interrupt merely because:
- planning started;
- a router selected a path;
- a model call completed;
- a tool opened;
- verification is ongoing.

Typical Owner-attention states:
- WAITING_FOR_APPROVAL;
- CONTEXT_CONFLICT requiring Owner;
- material UNKNOWN;
- BLOCKED when Owner can unlock;
- Change-of-Truth;
- destructive/irreversible action;
- authority expansion;
- material privacy/spend/fallback choice.

---

# 6. Interaction contract by state

QUEUED:
- View queue context.
- Cancel if supported.

PLANNING:
- View plan preview.
- No fake execution animation.

WAITING_FOR_APPROVAL:
- Open Decision Mode.
- Ask.
- Inspect evidence.
- Approve/Reject/Request Changes when typed action permits.

EXECUTING:
- View activity.
- Pause if supported.

VERIFYING:
- View verification.
- No completion action yet.

BLOCKED:
- Why blocked?
- What unlocks it?
- Owner action only when applicable.

FAILED:
- View failure.
- Preserve current work.
- Safe retry or Return Ticket when policy allows.

UNKNOWN:
- Inspect evidence.
- Verify again.
- Preserve/hold.
- Never blind retry after potentially consequential effect.

STALE_CONTEXT:
- Compare old capsule vs current truth.
- Preserve current output.
- Re-plan on latest.
- Escalate only if Change-of-Truth/Owner decision is required.

CONTEXT_CONFLICT:
- Compare conflicting sources.
- Inspect provenance.
- Resolve through typed decision.
- Execution remains blocked.

SUCCEEDED:
- Open Work Receipt.
- Open artifact.
- Start follow-up.
- Publish/deploy only through separately governed action.

---

# 7. Cross-platform semantic parity

Windows and Android must use the same meaning for:
- Job state;
- approval state;
- context state;
- truth state;
- checkpoint;
- artifact/version.

Layouts may differ.

Android may compress:
- EXECUTING -> “قيد العمل”
- WAITING_FOR_APPROVAL -> “ينتظر قرارك”
- SUCCEEDED -> “مكتمل ومتحقق”

but may not merge:
- UNKNOWN into FAILED or COMPLETE;
- STALE_CONTEXT into generic BLOCKED;
- CONTEXT_CONFLICT into generic WAITING_OWNER without explanation.

---

# 8. Notification contract

Notifications are state-change summaries, not raw logs.

Allowed examples:
- “مشروع X يحتاج قرارك.”
- “تغيّر سياق مشروع X ويجري إعداد خطة جديدة.”
- “هناك تعارض في مصادر الحقيقة لمشروع X.”
- “نتيجة X غير مؤكدة وتحتاج تحققًا.”
- “اكتمل X وتم التحقق.”

Do not include:
- credentials;
- raw private evidence;
- sensitive screenshots by default;
- misleading “success” before verification.

---

# 9. Accessibility

State may never depend on color alone.

Every state requires:
- text label;
- semantic icon or structural cue;
- accessible name;
- keyboard/focus path on Windows;
- screen-reader semantics;
- Reduced Motion equivalent when state transition uses motion.

---

# 10. Motion

Motion communicates state change only.

Examples:
- EXECUTING -> VERIFYING: restrained transition.
- VERIFYING -> SUCCEEDED: completion settle only after verification.
- EXECUTING -> STALE_CONTEXT: stop/hold indication, not failure explosion.
- CONTEXT_CONFLICT: static attention state; no alarm-like continuous animation.

No decorative continuous activity.

---

# 11. Truth and freshness

Every visible operational state should be backed by:
- source;
- timestamp/freshness;
- evidence level when material.

Stale provider/device state must be labeled stale/unknown rather than reused as current truth.

---

# 12. Completion semantics

“Complete” is reserved for:
`SUCCEEDED`.

A project may have a receipt for:
- FAILED;
- BLOCKED;
- UNKNOWN;

but those use non-completion receipt variants.

The verified-success hero belongs only to SUCCEEDED.

---

# 13. Visual inheritance

All state rendering must map onto existing semantic tokens/components from the eight-reference visual system.

This contract does not authorize:
- new palette;
- new card system;
- new visual theme;
- new navigation;
- human role avatars;
- generic SaaS status dashboards.

---

# 14. Engineering dependency

Context Resolver and Context Capsule Compiler must expose enough structured truth for the UI to derive:
- STALE_CONTEXT;
- CONTEXT_CONFLICT;
- source revision;
- capsule id;
- current canonical sources;
- freshness;
- conflict provenance.

This is why the UX State Contract is locked before those components are implemented.
