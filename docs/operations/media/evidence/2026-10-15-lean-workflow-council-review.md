# Council Review — Lean Video Production Rebuild v2.0

**Date:** 2026-10-15  
**Reviewed HEAD:** `d69d634b0bc25b50a0dbe62066ac48c54e44c86c`  
**PR:** #30 — Draft / Open / Mergeable / Not merged  
**CI:** Company Stage 0 #387 PASS; CodeQL #303 PASS  
**Scope:** Review only. No implementation changes authorized by this document.

## Executive verdict

### **APPROVE THE ARCHITECTURE / DO NOT YET QUALIFY THE PRODUCTION SYSTEM**

The rebuild is a substantial improvement over the cancelled DAY24 ladder.

It successfully removes:
- P0/P1/P2/P3 escalation;
- retry-phase chains;
- per-frame Council review;
- critical-motion prototype queues as mandatory workflow;
- tool tournaments;
- long GUI retry loops;
- repeated Council voting on routine craft;
- multiple finishing gates.

It replaces them with:
- five production stages;
- exactly three gates;
- one final authority per stage;
- one system pilot only;
- one primary edit route and one backup;
- artifact/hash-bound approvals;
- explicit factual, rights, reference-fidelity and technical QC checks.

The architecture is therefore approved.

However, the system pilot is currently **Owner Art-Direction Rejected**, so the production system itself is not qualified for 8+ minute episodes yet.

---

# 1. Council role-by-role review

## Editorial Director / Showrunner

### APPROVE
Strong improvements:
- one script/treatment/asset-plan package at Preproduction Lock;
- maximum two script drafts;
- one consolidated rough-cut review instead of repeated micro-approvals;
- factual review remains independent;
- story/pacing authority is explicit.

This is much closer to a real production studio.

### Concern
The 235–360 active-minute target for an 8+ minute documentary is not demonstrated.

The workflow correctly labels it an unmeasured hypothesis, so it must stay a planning target only.

**Verdict:** APPROVE.

---

## Visual Art Director / Frame Curator

### APPROVE WITH CONDITION
Major positive correction:
- `DESIGN.md` correctly restores **Kinetic Editorial Surrealism / Mixed Media**;
- reference fidelity is now a required check at all three gates;
- palette agreement or generic coherence can no longer substitute for reference fidelity;
- simplification is explicitly forbidden from changing the channel identity;
- Owner-rejected exports are persisted and cannot pass Final QC later.

This fixes the largest failure of the previous attempt.

### Blocking fact
The delivered lean pilot was correctly rejected by the Owner because it became a flat infographic sequence.

Therefore:
> the new workflow has not yet proved that its speed improvements can coexist with the channel's actual artistic language.

**Verdict:** ARCHITECTURE APPROVED; SYSTEM QUALIFICATION PENDING A NEW ART-DIRECTION-COMPLIANT PILOT.

---

## Motion & Picture Editor

### PARTIAL APPROVE
The workflow is dramatically faster because:
- Descript receives one full assembly brief;
- only one normal revision round exists;
- AE fallback is native automation, not GUI looping;
- no multi-editor tournament exists.

The technical run showed the native AE fallback can build/render a 41.77s 1080p/30 clean export quickly.

### Major contradiction
The config still declares:

**Primary: Descript**

while its own measured pilot says:
- RTL order failed;
- 720p instead of requested 1080p;
- watermark;
- loudness/true-peak outside target;
- timeline export unavailable on current plan.

The runtime compensates by detecting the persisted `FAILED_` delivery status and routing to After Effects after a fresh probe.

That logic is safe, but it means the declared primary route is operationally known to fail the current Final QC contract.

This introduces avoidable latency:
- attempt/diagnose the known-failed primary;
- then activate AE.

### Recommendation
Before the next pilot, choose one of these:
1. reclassify Descript as **rough-edit/transcript utility**, with AE as current delivery editor; or
2. keep Descript primary only after a new test proves clean Arabic + 1080p + watermark-free delivery on the current plan.

**Verdict:** REQUIRED CORRECTION BEFORE NEXT SYSTEM PILOT.

---

## Media Producer / Production Coordinator

### APPROVE
The production budget is now bounded:
- two script drafts;
- one normal rough-cut revision;
- one asset-pack review;
- two attempts per missing generated asset;
- twelve generation jobs total;
- one backup activation;
- ten-minute primary diagnosis ceiling;
- no third tool.

This directly addresses the Owner's complaint about time consumption.

### Concern: generation ceiling
A hard maximum of 12 generation jobs may be too restrictive for some 8+ minute episodes.

For a well-sourced documentary this may be fine because archive, photography, diagrams and reusable systems should dominate.

But for an episode requiring many unique conceptual scenes, the current runtime can force a craft gap.

Recommendation:
- keep 12 as the **default budget**;
- do not silently exceed it;
- if real production evidence later shows it is too low, revise the system budget deliberately rather than degrading the art direction.

**Verdict:** APPROVE FOR PILOT.

---

## Independent Fact Checker

### STRONG APPROVE
The new runtime materially improves evidence integrity:
- script author cannot self-clear material facts;
- claims are checked inside Preproduction;
- rights ledger is separate;
- evidence/check files are SHA-256 bound;
- stale approvals fail automatically;
- synthetic documentary evidence remains forbidden.

This is one of the strongest parts of the redesign.

**Verdict:** APPROVE.

---

## Red Team / Anti-Slop

### APPROVE WITH TWO WARNINGS

#### Warning A — speed must not become identity simplification
The first lean pilot already demonstrated the risk:
when the workflow optimized for the easiest native shapes/text, the result became an educational infographic rather than the adopted identity.

The new `DESIGN.md` and reference-fidelity checks now defend against this correctly.

#### Warning B — “three gates” must remain three gates
The rebuild currently avoids hidden extra gates.

Art Director reference fidelity is embedded inside existing gates rather than creating another approval queue.

This must remain true.

**Verdict:** APPROVE.

---

## Independent QC Reviewer

### STRONG APPROVE
Final QC is fail-closed and bound to the exact export.

It verifies:
- exact export SHA;
- independent reviewer;
- facts/rights;
- Arabic readability;
- accepted voice;
- sync;
- audio intelligibility;
- visual coherence;
- reference fidelity;
- watermark-free output;
- >=1920×1080;
- >=24fps;
- pilot 30–45s or episode >=480s;
- -14 LUFS ±1;
- <= -1 dBTP.

Owner-rejected exports are explicitly prohibited from passing technical QC later.

**Verdict:** APPROVE.

---

# 2. Architectural scorecard

| Dimension | Score | Council view |
|---|---:|---|
| Workflow simplicity | 9/10 | Large improvement |
| Role clarity | 9/10 | One authority per stage |
| Review overhead | 9/10 | Three gates only |
| Evidence integrity | 10/10 | Hash-bound, independent checks |
| Tool sprawl control | 10/10 | Primary + one backup |
| Anti-GUI-loop protection | 10/10 | Explicitly forbidden |
| Art-direction protection | 8/10 | Corrected after Owner rejection |
| Current editor routing | 5/10 | Known-failed Descript still called primary |
| Proven speed for 8+ min | 3/10 | Only short technical pilot measured |
| Proven artistic output | 2/10 | Pilot was Owner rejected |
| **Architecture overall** | **8.5/10** | Approved |
| **Production readiness today** | **5/10** | Not yet qualified |

---

# 3. What the Council believes should remain unchanged

Keep:
1. **five stages**;
2. **exactly three gates**;
3. **one authority per stage**;
4. **no per-frame Council review**;
5. **no prototype ladder**;
6. **no tool tournament**;
7. **one 30–45s system pilot only**;
8. **hash-bound approvals**;
9. **independent fact check**;
10. **independent Final QC**;
11. **Owner brand/art veto**;
12. **reference fidelity as a formal gate check**;
13. **no automatic publishing or main merge**.

These are strong design decisions.

---

# 4. Required corrections before the next pilot

## P0 — Editor-route truth
Highest priority.

Resolve the contradiction:
- Descript is configured as primary,
- but persisted evidence says it currently fails the delivery contract.

Council recommendation:
**do not spend another pilot rediscovering this known failure.**

Preferred current routing:
- Descript: script/transcript/rough-prep utility;
- After Effects native automation: pilot picture/motion/final technical render;
- re-promote Descript only if a later plan/runtime test clears RTL, watermark and 1080p.

This is not a request for a third tool.

## P1 — Next pilot must test art direction, not transport
The previous pilot already proved:
- native automation speed;
- AE 1080p/30 export;
- compliant loudness.

Do not repeat those as the main experiment.

The next 30–45s pilot must specifically prove:
- mixed-media treatment;
- motif transformation;
- meaningful object/human motion;
- authentic evidence integration;
- authored Arabic typography;
- reference-faithful transitions;
- full continuous playback.

## P2 — Use a real asset pack
The Owner-rejected pilot used easy shapes because the asset pack was insufficient.

The new Preproduction Lock must refuse to start Edit/Motion unless the pack actually contains the media needed by the Art Director's treatment.

Missing craft must be marked as a gap, not replaced by centered bars/diagrams.

## P3 — Measure workflow time honestly
Record:
- active operator minutes;
- wall time;
- service queue;
- render time;
- cost;
- revision count.

Do not convert the short-pilot automation latency into a claim that an 8-minute film takes 4–6 hours.

## P4 — Keep the 12-generation-job budget provisional
Use it in the pilot.
Do not change it now.
Review after real full-episode evidence.

---

# 5. Proposed next-pilot success criteria

The next system pilot should pass only if all three gates PASS and the Owner does not reject the art direction.

Minimum creative proof:
- >=4 meaningful media/treatment families;
- recurring episode motif changes medium/state rather than repeating one diagram;
- at least one authentic evidence beat;
- at least one meaningful object/human-caused transition where appropriate;
- Arabic type is an authored visual element;
- no repeated centered-headline/centered-diagram template;
- no technical simplification that materially changes the locked identity.

Minimum technical proof:
- 30–45s;
- >=1920×1080;
- >=24fps;
- no watermark;
- accepted human voice before Final QC;
- -14 LUFS ±1;
- <= -1dBTP;
- clean exact-export QC;
- full playback review.

---

# 6. Final Council decision

### Architecture
**APPROVED**

### Old workflow
**REMAIN SUPERSEDED / DO NOT RESUME**

### Current lean system pilot
**REJECTED AS ART DIRECTION PROOF / KEEP AS TECHNICAL EVIDENCE**

### Full 8+ minute production
**BLOCKED UNTIL ONE NEW LEAN SYSTEM PILOT PASSES**

### Required implementation changes before that pilot
**ONE HIGH-PRIORITY ROUTING CORRECTION:** stop treating the known-failed Descript delivery route as the practical first finishing attempt.

Everything else should remain stable until the next pilot supplies real evidence.

### Merge
PR #30 must remain Draft and must not merge to `main` without explicit Owner authorization.
