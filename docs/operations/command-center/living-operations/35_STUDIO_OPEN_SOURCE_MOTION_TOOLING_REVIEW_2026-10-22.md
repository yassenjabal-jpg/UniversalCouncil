# Command Center — Studio Review of Open-Source Motion / Capture Tooling
## مشغل المرتكز — مراجعة فكرة الاستفادة من مشاريع ومكتبات مفتوحة المصدر

Date: 2026-10-22  
Status: STUDIO REVIEW — ACCEPT_WITH_CONDITIONS  
Scope: W1.1 only / no W1.2 / no merge / no Stage 8

## Review trigger

W1.1 product motion is now visibly measurable, but the exact-head P1 evidence gate still fails because the current WPF capture path materially dilates real time.

Latest reviewed evidence on candidate `4f49d34899b98b67bb7afa204de447e5ca38ab0b`:

- Full Motion: 96 visibly changed frames;
- Full longest changed run: 10;
- Full independent motion runs: 18;
- required Full thresholds: 90 / 9 / 8;
- Reduced Motion: 25 changed frames / longest run 4 / 9 runs;
- WPF capture timing: 92.662s actual for a nominal 38.000s capture;
- P1 evidence gate: FAIL because recorder time dilation exceeded tolerance.

Therefore the open problem is no longer primarily “insufficient animation”.
The blocking problem is truthful, real-time owner-review capture.

## Activated Studio roles

- CC-ST-01 — Producer
- CC-ST-03 — Interaction Choreography Director
- CC-ST-05 — Motion Systems Director
- CC-ST-07 — Design Systems Engineer
- CC-ST-08 — Windows Experience Lead
- CC-ST-10 — Prototype & Interaction Engineer
- CC-ST-11 — Accessibility Reviewer
- CC-ST-12 — Visual Fidelity & QA Reviewer

Cross-clearance requested from:
- Architecture / Execution
- Product Truth / Evidence

## Options reviewed

### A. WKI-Clipper architecture
Repository: `WKImods/WKI-Clipper`  
License: MIT.

Relevant value:
- Windows capture architecture;
- D3D11 / hardware capture path;
- FFmpeg-oriented recording pipeline;
- separation between application rendering and evidence recording.

Studio view:
**USE AS ARCHITECTURAL REFERENCE, NOT AS A WHOLE-PRODUCT DEPENDENCY.**

Reason:
the project contains much more than Command Center needs. Importing the entire tool would add unrelated capture/overlay/audio/UI scope.

### B. WgcSharp
Repository: `Giltanas/WgcSharp`  
License: MIT.

Relevant value:
- capture by HWND;
- Windows.Graphics.Capture primary path;
- D3D11;
- DXGI fallback;
- .NET 9/10 WPF-oriented interop design;
- no CsWinRT/ComWrappers dependency in its WGC backend.

Studio view:
**BEST CANDIDATE FOR A SMALL W1.1 CAPTURE PILOT.**

Reason:
it is narrowly aligned with the blocker and can be isolated behind the evidence recorder boundary.

### C. ATC.Wpf
Repository: `atc-net/atc-wpf`  
License: MIT.

Studio view:
**DO NOT ADOPT FOR W1.1.**

Reason:
the current motion implementation already passes the motion-visibility thresholds. Introducing a broad WPF framework now would enlarge the change surface and risk visual/system drift without addressing the current blocker.

It may be reconsidered later for component architecture, outside W1.1.

### D. Microsoft.Xaml.Behaviors.Wpf
Repository: `microsoft/XamlBehaviorsWpf`  
License: MIT.

Studio view:
**VALID LATER REFACTOR OPTION, NOT CURRENT REMEDIATION.**

Reason:
Behaviors may help reduce code-behind coupling and make interaction triggers reusable, but it does not solve capture time dilation. It should not be introduced while W1.1 is still trying to close its evidence gate.

## Role findings

### Motion Systems Director
Decision:
**KEEP CURRENT MOTION DNA.**

The latest Full Motion metrics already clear the protected 90/9 acceptance floor.
Do not add more motion solely to compensate for a slow recorder.
Do not weaken Reduced Motion.

### Interaction Choreography Director
Decision:
**NO CHOREOGRAPHY REDESIGN.**

The source-exit / target-commit / target-entry / settle contract remains valid.
A capture-engine substitution must not alter semantic timing or interaction state.

### Windows Experience Lead
Decision:
**PREFER WINDOW CAPTURE OVER WPF RE-RENDER CAPTURE.**

The evidence path should observe the actual rendered window rather than repeatedly asking WPF to reconstruct the full visual tree with RenderTargetBitmap.

Primary experiment:
`Windows.Graphics.Capture by HWND`.

### Prototype & Interaction Engineer
Decision:
**BUILD A BOUNDED ADAPTER, NOT A FRAMEWORK MIGRATION.**

Recommended boundary:

`IMotionEvidenceCaptureSource`

Candidate implementations:
1. `WindowsGraphicsCaptureSource` — experimental preferred path;
2. existing WPF capture path — diagnostic fallback only until the pilot proves equivalence.

The product app must not depend on the recorder implementation.

### Visual Fidelity & QA
Conditions:
- capture actual Command Center window;
- preserve 1440x900 review target;
- no interpolation;
- no optical flow;
- no post-production;
- no hidden visual substitution;
- video must remain exact-head bound;
- final clean capture must be visually reviewable by Owner.

### Accessibility
Decision:
**NO BLOCKER** provided:
- Reduced Motion path is unchanged;
- no meaning becomes capture-dependent;
- recorder does not modify application animation state.

### Architecture / Execution clearance
Condition:
capture implementation stays in evidence/test infrastructure and does not introduce:
- runtime authority;
- live execution;
- global mutable capture state in product logic;
- DB/network coupling;
- Stage 8 dependency.

### Product Truth / Evidence clearance
Condition:
Windows Graphics Capture is acceptable only if evidence remains:
- actual application pixels;
- exact candidate SHA bound;
- unedited;
- deterministic enough to audit;
- hash/integrity protected.

## Red Team objections

1. WGC may behave differently on GitHub Actions Windows runners than on a normal interactive desktop.
2. Hardware GPU / D3D11 availability may differ between CI and YASSIN.
3. Minimized/occluded-window behavior must be explicitly verified rather than assumed.
4. DPI/window-border/client-area capture must not silently change the reviewed composition.
5. A DXGI fallback must not become an unreviewed semantic fallback that captures a different surface.
6. External dependency version must be pinned; upstream updates must not silently change evidence behavior.
7. License notice must be retained for any copied/substantially reused MIT source.

These are pilot acceptance conditions, not reasons to reject the concept.

## Studio decision

Outcome:

**ACCEPT_WITH_CONDITIONS — WGC CAPTURE PILOT ONLY**

Approved next experiment inside W1.1:

1. do not change motion implementation;
2. do not change 90/9 thresholds;
3. do not start W1.2;
4. do not merge PR #72;
5. create a small isolated Windows Graphics Capture proof-of-concept;
6. prefer WgcSharp for the first narrow pilot, while using WKI-Clipper only as an architectural reference;
7. compare its output against the existing exact-head evidence contract;
8. reject the pilot if capture timing, fidelity, integrity or CI portability cannot be proven.

## Pilot acceptance criteria

The WGC pilot may replace the current recorder only if all are true:

- actual capture duration is within the existing timing tolerance;
- 30 FPS owner-review target is real rather than nominal;
- Full Motion passes existing thresholds without threshold changes;
- Reduced Motion passes existing limits;
- all eight canonical navigation steps remain evidenced;
- exact-head SHA binding remains;
- clean video and raw/diagnostic evidence remain hash-bound;
- no interpolation or post-production;
- reference-first visual fidelity is unchanged;
- Stage 7 remains authoritative;
- Stage 8 remains closed;
- PR #72 remains Draft and unmerged.

## Explicit non-decisions

This review does **not** approve:
- ATC.Wpf migration;
- XAML Behaviors refactor;
- WKI-Clipper wholesale integration;
- motion redesign;
- threshold reduction;
- W1.2 start;
- merge;
- Stage 8;
- runtime authority.

## Final Studio recommendation

**Stop tuning the animation to compensate for the recorder.  
Prove a Windows.Graphics.Capture evidence path first.**

The Studio considers this the smallest change capable of resolving the remaining W1.1 blocker without visual reinvention or architecture expansion.
