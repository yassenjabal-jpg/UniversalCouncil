# المرتكز — Context Drift Prevention and Delivery Playbook
Date: 2026-10-21
Status: BLOCKING PROJECT-LOCAL QUALITY CONTRACT

## Goal

The goal is not to promise zero AI/software errors.

The goal is to prevent an incorrect interpretation from silently becoming project truth and propagating downstream.

Engineering target:
- detect drift early;
- minimize blast radius;
- preserve evidence;
- stop on ambiguity;
- keep rollback cheap;
- prevent generated output from rewriting its own specification.

## Drift classes

### CONTEXT_DRIFT
Wrong, stale or unrelated source context was used.

### SCOPE_DRIFT
Work modified outside the approved Change Envelope.

### POLICY_DRIFT
Routing/authority/fallback violated governing policy.

### VISUAL_DRIFT
Output departed from the canonical reference system.

### SEMANTIC_DRIFT
UI/code/artifact still looks valid but behavior meaning changed.

### DEPENDENCY_DRIFT
Model/provider/tool/version changed without approved policy.

### EVIDENCE_DRIFT
Success claim exceeds the evidence actually available.

## Delivery law

```
PIN BASELINE
-> MURTAKAZ PRE-REVIEW
-> CHANGE ENVELOPE
-> CONTEXT CAPSULE
-> PLAN
-> SMALL DELTA
-> VERIFY
-> ADVERSARIAL REVIEW
-> MURTAKAZ POST-REVIEW
-> LOCK
```

## Baseline rule

Every material change records exact source branch/SHA or artifact version.

If the baseline moved materially before implementation:
- do not silently continue;
- classify STALE_CONTEXT;
- rebuild capsule/plan against the new baseline.

This rule exists because the first Agentic OS draft was correctly reasoned but applied to a baseline 259 commits behind the project-local Murtakaz branch.

## Change Envelope

Before mutation record:
- change id;
- project;
- base revision;
- scope;
- non-goals;
- affected artifacts;
- expected behavior;
- risk;
- reviewers;
- workshop reviewers;
- acceptance criteria;
- verification.

If execution discovers required out-of-scope work:
- do not “fix it while here”;
- create Return Ticket or new Change Envelope.

## Context Capsule

The capsule is the immutable task truth snapshot.

It contains only relevant governing material and explicit source authority.

It must distinguish:
- instructions with authority;
- canonical facts;
- accepted evidence;
- working data;
- untrusted retrieved data.

The model receives bounded context rather than undifferentiated history.

## Domain precedence

Precedence is compiled per domain.

Default:
1. typed Owner directive;
2. locked project-local policy;
3. canonical artifact;
4. accepted evidence;
5. working data;
6. conversation continuation context;
7. untrusted external data.

Visual:
1. eight pinned canonical reference images;
2. typed Owner visual directive;
3. interaction/motion contracts;
4. component/design-token documents;
5. generated exploration.

A visual directive that intentionally replaces a reference creates a new canonical version through Change-of-Truth; it does not silently alter precedence.

## AI-output firewall

Model output begins as WORKING or OUTPUT.

It cannot:
- become policy;
- become visual reference;
- become canonical project fact;
- grant authority;
- change fallback policy;
- approve itself.

Promotion is a separate typed event.

## Visual drift protection

Canonical UI production inherits the current hard gate.

Required before render:
- one canonical parent;
- actual parent bytes loaded;
- correct parent hash;
- object inventory;
- preflight job registration;
- reference-binding receipt;
- bounded allowed delta.

Forbidden:
- text-only reconstruction;
- new theme from prose;
- generated-output parent;
- multi-screen composite as canonical screen;
- generic “similar style” acceptance.

After render:
- output hash;
- structural comparison;
- side-by-side review;
- object inventory review;
- governance review;
- workshop fidelity review;
- explicit Murtakaz decision.

## Independent reviewer

For high-risk/high-drift change, reviewer sees:
- governing capsule;
- change envelope;
- diff/output;
- acceptance criteria;
- evidence.

Reviewer should not rely on executor persuasion or confidence.

The question is not “does this look good?”
It is “can compliance be disproved?”

## Exact-head evidence

Evidence belongs to the exact artifact/version it verified.

A later mutation invalidates relevant evidence.

Old screenshots/tests do not clear new code.

## No downstream repair

If a downstream phase finds an upstream locked defect:
- stop;
- create Return Ticket;
- reopen source stage;
- fix;
- revalidate;
- relock;
- continue.

Downstream silent repair is forbidden.

## Failure preservation

Failed and rejected attempts are retained as evidence.

This is especially important for visual drift:
rejected generations stay quarantined and cannot become accidental references later.

## Model/provider drift

Record:
- model id;
- provider;
- reasoning policy;
- tool/plugin version;
- significant config hash.

Fallback is allowed only when policy explicitly permits it and must appear in the Work Receipt.

## Result truth

Allowed important outcomes include:
- SUCCEEDED;
- FAILED;
- BLOCKED;
- UNKNOWN;
- STALE_CONTEXT;
- CONTEXT_CONFLICT.

No “almost successful” state may be rendered as success.

## Review cadence

Use small vertical slices.

A slice should:
- satisfy one clear contract;
- have bounded touched surfaces;
- be inspectable;
- be independently revertible when practical;
- produce evidence;
- pass Murtakaz review before the next dependent slice.

## Owner interruptions

Anti-drift is not permission spam.

Owner interruption is reserved for policy-defined decisions:
- Change-of-Truth;
- authority expansion;
- destructive/irreversible effect;
- public/external consequence;
- credentials/spend/subscription;
- material privacy tradeoff;
- locked art-direction change;
- unapproved model/provider fallback choice.

Safe internal steps within approved scope remain traceable without requiring constant prompts.

## Final quality rule

A result can be:
- visually beautiful;
- technically functional;
- CI green;
- generated by a strong model;

and still be rejected if it violates Context, Scope, Authority, Truth or canonical visual reference.

Correctness is:
`contract compliance + evidence + verification + independent review`.
