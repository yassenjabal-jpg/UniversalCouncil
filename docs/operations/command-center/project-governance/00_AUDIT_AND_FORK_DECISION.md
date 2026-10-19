# Command Center — Council + Studio Project Audit and Fork Decision

Date: 2026-10-19  
Status: PROJECT-LOCAL GOVERNANCE AUDIT / OWNER-DIRECTED  
Project: UniversalCouncil Command Center + UniversalCouncil Owner for Android  
Parent branch lineage: Living Operations execution package  
Stage 8: NOT OPENED  
Execution authority: UNCHANGED / BLOCKED_PHASE0

## Question

The universal Council and the existing Studio were created to serve broader and materially different projects.

Should this project continue to use them directly, or should it create project-local versions without changing the parent systems?

## Joint verdict

**CREATE PROJECT-LOCAL DERIVATIVES. DO NOT MODIFY OR REPLACE THE PARENT COUNCIL OR PARENT STUDIO.**

The correct model is inheritance + specialization:

`Universal Council -> Command Center Project Council`

`Media/Production Studio principles -> Command Center Product Studio`

The local versions may specialize missions, routing, review gates and craft roles for this project.

They may not silently change:
- parent governance;
- parent role registry;
- parent Studio/media configuration;
- Owner authority;
- truth/evidence rules;
- execution authority;
- Stage 7/Stage 8 status;
- model fallback policy;
- security boundaries.

## Parent Council audit

Canonical sources reviewed:
- `GOVERNANCE.md`
- `config/roles.json` version 0.3.0
- `config/domain-routing.json`
- `config/modes.json`
- `company/config/council_role_contracts.json` candidate shadow contracts

### Strengths to inherit

1. Truth over agreement.
2. Evidence over vote count.
3. Independent challenge when uncertainty or anchoring risk matters.
4. Explicit dissent preservation.
5. User remains final decision owner.
6. Smallest useful set of roles instead of always activating everyone.
7. Evidence, Red Team, Risk, Human/User, Execution and Synthesis are already strong reusable capabilities.
8. ARENA mode is appropriate for difficult-to-reverse architecture/security decisions.
9. No role may silently self-authorize tools or authority.
10. Roles are governance functions, not assumed independent humans/processes.

### Gaps for this project

The generic Council does not natively encode this project's recurring concerns as first-class project lenses:

- WPF presentation-boundary discipline;
- Android companion semantics;
- cross-platform state consistency;
- long-running/durable Autopilot;
- checkpoint/recovery/fork correctness;
- remote Owner trust boundary;
- model/reasoning/fallback UX;
- Memory Fabric scope and replay;
- Event -> UI motion truth;
- no-dead-surface enforcement;
- motion performance and Reduced Motion;
- visual fidelity as a product constraint;
- prototype fixtures accidentally leaking into runtime truth;
- Studio implementation handoff quality.

Using the generic Council alone would repeatedly require manual specialist assembly and would risk inconsistent reviews.

## Parent Studio audit

Canonical sources reviewed:
- `company/config/media_venture.json` version 2.1
- `docs/operations/media/MEDIA_PRODUCTION_CELL.md`
- `docs/operations/media/STUDIO_MASTER_PIPELINE.md`
- Studio execution-recovery rules

### Strengths to inherit

1. Smallest effective team.
2. A persistent coordination/control function.
3. Phase-routed craft specialists rather than every role always active.
4. Verified handoffs.
5. Downstream functions do not silently repair locked upstream work.
6. One authoritative primary program/tool per stage where state-changing craft occurs.
7. Checkpoint before risky handoff.
8. `UNKNOWN != SUCCESS`.
9. Bounded recovery.
10. Bounded Human Assistance.
11. Owner-only gates for credentials, spend, irreversible actions and public publication.
12. Quality clearance may be independent from craft creation.

### Misalignment with this project

The parent Studio is a media production system.

Its core stages and craft roles are optimized for:
- YouTube title development;
- script;
- narration;
- visual assets;
- cinematography;
- motion/compositing;
- picture editing;
- sound;
- thumbnails;
- publish/export.

Command Center instead requires a product-design-and-interaction pipeline for:
- product information architecture;
- Windows desktop UX;
- Android companion UX;
- motion semantics;
- Role Sigils/iconography;
- component states;
- event-driven UI;
- prototype engineering;
- accessibility;
- visual QA/fidelity;
- implementation handoff to software engineering.

Reusing the media role names would be misleading.

## Project domain map

This project spans these domains simultaneously:

1. Product architecture.
2. Software architecture.
3. Windows desktop UX/WPF.
4. Android UX/Compose.
5. AI orchestration and model routing.
6. Durable workflow/recovery.
7. Security/privacy/remote trust.
8. Evidence and observability.
9. Memory/replay/versioning.
10. Visual design.
11. Motion/interaction.
12. Accessibility.
13. Performance.
14. Cross-platform synchronization.
15. Human decision workflow.
16. Tool/application integration.
17. Cost/usage controls.
18. Future commercialization/productization.

## Project-specific risk register

### R1 — False activity
Animation may imply work is happening when the runtime is idle or unknown.

Required reviewer:
Product Truth + Red Team + Motion.

### R2 — Dead affordance
A Sigil, icon, card or animated object may look clickable without a real action.

Required reviewer:
UX + Interaction Studio.

### R3 — Cross-platform semantic drift
Windows and Android may show different states for the same project object.

Required reviewer:
Cross-platform Client Architecture.

### R4 — Authority leakage
Android approval, Tailscale reachability or UI interaction may be confused with server-side execution authority.

Required reviewer:
Security/Remote Trust.

### R5 — Prototype contamination
Fixture state may be promoted into Memory/Evidence/runtime truth.

Required reviewer:
Evidence/Truth + Reliability.

### R6 — Recovery theater
UI may animate a rewind/recovery before restore verification completes.

Required reviewer:
Durable Autopilot + Evidence.

### R7 — WPF architecture erosion
Presentation code may begin owning execution, filesystem, DB, HTTP or tool authority.

Required reviewer:
Architecture/Execution + Windows specialist.

### R8 — Motion performance regression
Animation may degrade responsiveness or consume excessive GPU/CPU.

Required reviewer:
Performance + Motion + Windows/Android lead.

### R9 — Accessibility regression
Meaning may depend on motion/color/gesture.

Required reviewer:
Accessibility clearance.

### R10 — Model control ambiguity
Model, reasoning effort, fallback and autonomy controls may be visually mixed or silently coerced.

Required reviewer:
AI Runtime/Model Policy + UX.

### R11 — Visual drift
Implementation may become generic SaaS or lose the adopted Living Operations identity.

Required reviewer:
Product Studio Visual Systems + Visual QA.

### R12 — Over-activation
Too many roles/animations may create noise and cost without changing a decision.

Required reviewer:
Project Chair + Red Team + Human/UX.

## Fork model

The project-local systems are overlays.

They inherit principles and selected capabilities.

They do not copy parent authority.

They can be upgraded/rebased when parent governance changes.

Parent files remain read-only from the project-local profile.

Project-local files live under:
- `docs/operations/command-center/project-governance/`
- `state/command-center/project-governance/`

## Final audit recommendation

Create:

1. **Command Center Project Council**
   - product/runtime/security/UX decision review;
   - project-specific specialist routing;
   - Owner remains final authority.

2. **Command Center Product Studio**
   - product design, interaction, motion and prototype craft;
   - Studio supervises Living Operations fidelity;
   - no execution authority.

3. **Council–Studio Collaboration Contract**
   - Studio produces/iterates craft;
   - Council challenges/clears risk/truth/architecture;
   - neither silently edits the other's locked responsibility;
   - material conflict escalates to Owner.

This project-local fork is **project-scoped and reversible**.

The parent Council and parent Studio remain untouched and available for other projects.
