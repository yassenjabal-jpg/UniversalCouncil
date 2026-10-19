# المرتكز — بوابة ما قبل P1 Prototype

Status: OPEN  
Decision: CONDITIONAL_GO  
Scope: non-authoritative Living Project Workspace prototype only

## Purpose

Prevent the first Living Operations prototype from binding itself to obsolete project-local assumptions.

## Required closures

### MP-02 — Murtakaz orchestration projection

Create a generated read-only project projection from:
- inheritance-lock.json;
- project-council.json;
- product-studio.json;
- project review routing.

Requirements:
- source SHA/blob metadata;
- deterministic generation;
- CI drift check;
- no parent mutation;
- no live model/tool execution.

### MP-03 — Canonical Stage/Phase map

Publish one mapping that distinguishes:
- historical product roadmap phases;
- actual delivery stages;
- current Stage 7;
- future Stage 8+.

No ambiguous "Stage 7/Phase 7" UI labels after this gate.

### MP-04 — Stage 7 projection truth semantics

Separate:
- CI foundation state;
- host probe state;
- phone/tailnet state.

Known evidence:
Stage 7 exact-head CI is green.

Host/phone/tailnet remain unproven.

Do not conflate them.

## Already satisfied

### MP-01 — Identity
المرتكز / هيئة المرتكز / مشغل المرتكز adopted.

### MP-05 — Prototype fixture isolation
Specified by Living Operations P1.

### MP-06 — No Dead Surface
Specified by Interaction Choreography and acceptance gates.

## Gate exit

Exit label:

`AL_MURTAKAZ_P1_ALIGNMENT_LOCK`

This lock:
- permits non-authoritative P1 UI prototype work;
- does not open Stage 8;
- does not grant execution;
- does not prove Android/Tailscale;
- does not prove Autopilot runtime.

