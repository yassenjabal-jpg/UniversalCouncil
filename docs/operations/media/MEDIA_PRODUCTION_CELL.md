> **SUPERSEDED — historical evidence only.** The DAY24 ladder, retry/prototype queues and long AE GUI method are cancelled. [Lean Workflow v2.0](LEAN_VIDEO_PRODUCTION_WORKFLOW.md) governs current production. Historical results below are preserved; do not resume these instructions or use their PASS as new-system proof.

﻿# Media Production Cell v1.2 â€” Studio-Benchmarked

## Principle

The Media Production Cell is modeled after professional explainer/documentary studios while remaining intentionally small.

Functions are not headcount.

During the pilot:
- one human/tool may cover multiple functions;
- critical approvals remain separate;
- role minutes and rework are measured;
- after three videos HR may recommend MERGE/KEEP/REPLACE.

## Hierarchy

Owner
â†’ Editorial Director / Showrunner
â†’ Media Producer / Production Coordinator
â†’ craft functions
â†’ Technical / Assurance / Finance support

The Producer manages execution.
The Showrunner manages story.
Neither replaces the other.

## 1. Media Producer / Production Coordinator

Owns:
- master schedule
- milestones
- dependencies
- review calendar
- resource plan
- vendor coordination
- production risk
- delivery readiness
- schedule/budget visibility

Does not own:
- factual clearance
- story truth
- brand veto

## 2. Editorial Director / Showrunner

Owns:
- topic/story fit
- thesis
- narrative architecture
- script lock
- visual-story coherence
- picture lock
- final editorial approval

## 3. Independent Fact Checker

Owns:
- material claim verification
- numbers/dates/names
- contradiction review
- uncertainty wording
- factual clearance

Rule:
the researcher/writer cannot be the sole approver of their own material claims.

## 4. Script & Voice Director

Owns:
- five-pass script development
- narration intent
- emotion
- pace/pitch/emphasis
- pronunciation
- recording direction
- pickup list
- narration continuity

## 5. Visual Art Director / Frame Curator

Owns:
- Visual Story Case
- key visual
- visual treatment
- reference-frame board
- palette/type/grid
- episode motifs
- visual continuity

## 6. Motion & Picture Editor

Owns:
- visual feasibility
- Story Skeleton review
- Visual Draft review
- first-30-second pacing
- storyboard timing
- animatic
- motion design
- editorial rough cut
- picture edit
- transition execution
- picture-lock conform

Rule:
the Editor enters during pre-production, not after script completion.

Cannot self-approve:
Picture Lock.

## 7. Music Supervisor & Sound Designer

Owns:
- sonic concept
- spotting
- music brief
- cue sheet
- music rights/provenance
- sound design
- sonic motifs
- silence
- transition SFX
- AV sync intent

## 8. Dialogue & Mix Engineer

Owns:
- dialogue cleanup/edit
- noise/EQ/de-ess
- automation
- music/dialogue balance
- stems
- mix/master
- technical audio QC
- dub parity

## 9. Audience Growth & Packaging Strategist

Owns:
- trend radar
- topic mining
- audience hypothesis
- title strategy
- first-30-second packaging
- CTR/retention learning
- A/B test design
- platform adaptation

## 10. Thumbnail & Packaging Designer

Owns:
- thumbnail concepts
- image selection/retouching
- compositing
- typography
- visual hierarchy
- brand consistency
- mobile legibility
- test-ready variants

## 11. Localization Producer

On demand.

Owns:
- translation adaptation
- dub script
- subtitle timing
- localized metadata
- localized thumbnail text
- language-version QC
- reconform requests



## Composed Capability — Visual Prompt / Generation Brief Compiler

This is **not** a permanent new role or headcount.

Composed by:
- Visual Art Director / Frame Curator
- Thumbnail & Packaging Designer
- Synthesis & Alternatives Designer

Produces:
- the complete, versioned, executable Visual Generation Brief;
- explicit allowed/forbidden elements;
- reference fidelity constraints;
- variant differentiation constraints;
- Anti-AI-Slop constraints;
- negative/rejection constraints.

Approval:
- Red Team / Anti-Slop must issue `APPROVED_BY_ANTI_SLOP`.

Execution:
- Technical Operator executes the approved artifact only.

Boundaries:
- **NO PROMPT, NO GENERATION**
- **NO ANTI-SLOP APPROVAL, NO EXECUTION**
- Technical Operator cannot creatively rewrite the brief
- generation tool cannot be allowed to materially reinterpret the brief
- material deviations return to the Council

Template:
`docs/templates/media/VISUAL_GENERATION_BRIEF.md`

## Shared support

### Evidence & Research Lead
Research, claim source sheet, synthesis, source freshness, expert-consultation trigger.

### Risk & Assurance
Visual rights, copyright, music rights, AI disclosure, policy.

### Technical Operator
Specialized tool routing, project structure, render/export, automation, archive integrity.

For generated visual work, Technical Operator executes only an approved, versioned Visual Generation Brief and records the prompt/tool receipt. It has no authority to creatively rewrite the approved brief.

### Finance Controller
Time/cost/credits, cost per finished minute, budget visibility.

### Red Team
Anti-slop, generic-template challenge, Visual Story Case challenge.

### Owner
Voice identity, brand authority, L4 decisions, publish approval.

## RACI â€” benchmarked workflow

| Stage | Accountable | Responsible | Required consultation | Approval |
|---|---|---|---|---|
| Topic | Showrunner | Growth + Research | Producer | Showrunner |
| Evidence | Research | Research | Fact Checker | Fact Checker for material claims |
| Visual Story Case | Art Director | Art + Motion | Research, Showrunner | Showrunner |
| Packaging A | Growth | Growth + Thumbnail | Showrunner | Showrunner |
| Pre-production Craft Review | Producer | Producer | Showrunner, Research, Motion, Art, Sound, Growth | Showrunner |
| Script S0â€“S4 | Showrunner | Script/Voice | Research, Motion, Art | Showrunner |
| Independent Fact Check | Fact Checker | Fact Checker | Research, Script | Fact Checker |
| Visual/Sonic Treatment | Showrunner | Art + Sound | Motion | Showrunner |
| Visual Generation Brief | Art Director | Art + Thumbnail + Synthesis | Red Team / Anti-Slop | Red Team / Anti-Slop |
| Animatic | Motion | Motion | Showrunner, Growth, Sound | Showrunner |
| Production Readiness | Producer | Producer | all craft leads | Producer + Showrunner |
| Narration | Script/Voice | Owner narrator | Showrunner | Owner |
| Production | Producer | craft functions | Technical | Producer |
| Rough Cut | Showrunner | Motion | Growth, Art, Sound | Showrunner |
| Packaging B | Growth | Growth + Thumbnail | Showrunner | Showrunner |
| Picture Lock | Showrunner | Motion | Art, Sound | Showrunner |
| Music/SFX | Sound | Sound | Motion, Showrunner | Showrunner |
| Mix/Master | Mix Engineer | Mix Engineer | Sound, Showrunner | technical audio QC |
| AV Sync | Showrunner | Motion + Mix | Sound | Showrunner |
| Final Fact/Policy | Assurance | Fact Checker + Assurance | Showrunner | Assurance |
| Export | Technical | Technical | Motion, Mix | Technical |
| Publish | Owner | Technical when authorized | Growth, Assurance | Owner |

## Lock system

### Visual Story Case Pass
Story proved as video.

### Script Lock
S0â€“S4 complete.
Fact check passed.

### Production Readiness Lock
No expensive production starts before dependencies are clear.

### Picture Lock
Timing stable.
Any timing change after lock triggers audio reconform.

### Sound Lock
Only defect fixes after approval.

## Producer metrics

Track:
- schedule variance
- milestone slips
- blocked days
- review-delay days
- late dependency count
- production-readiness failures
- downstream rework caused by upstream changes

## Fact-check metrics

Track:
- material defects found before lock
- defects found after lock
- source contradictions
- expert consultations triggered
- factual corrections after rough cut

## Packaging metrics

Track:
- title hypotheses
- thumbnail hypotheses
- final variants
- mobile legibility failures
- A/B test results
- CTR by packaging version

## Staffing rule

Do not hire/add permanent seats merely because a benchmark studio has them.

Keep a function separate only when pilot evidence shows one of:
- distinct specialist craft
- independent clearance requirement
- project-control responsibility
- measurable quality/rework benefit

The goal is professional discipline without professional-studio bureaucracy.


---

## Production authority after visual lock

The production cell is not a design committee for every frame.

Before Visual System Lock, Council functions may challenge the system broadly.

After lock:
- **Visual Art Director / Frame Curator** has final frame-level visual authority within the approved kit.
- **Motion & Picture Editor** owns timing/motion execution inside the locked grammar.
- **Technical Operator** owns tool routing/execution only and may not creatively rewrite the visual contract.
- **Red Team / Anti-Slop** may block material drift but does not substitute its own art direction.
- **Council** returns at defined gates or material exceptions, not normal shot-by-shot production.

Pilot ladder:
1. P0 — reference-frame + production-kit lock;
2. P1 — 30–45 second coherence pilot;
3. P2 — 60–90 second repeatability pilot;
4. P3 — 8+ minute full episode.

P3 is forbidden before P2 PASS.
