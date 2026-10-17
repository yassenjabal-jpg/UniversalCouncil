# Cinetic Integration — Motion Prototype & Product Demo Capability

**Date:** 2026-10-17  
**Status:** ADOPTED AS PROJECT-SCOPED EXTERNAL CAPABILITY  
**Upstream:** `Leonxlnx/cinetic`  
**Pinned upstream commit:** `bee5d7807205d5543472c38312507f9bf366cbbf`  
**License:** MIT for Cinetic itself

## 1. Role

Cinetic is adopted by the Council/Studio as a **Motion Prototype & Product Demo** capability.

It is **not**:
- a WPF UI framework;
- a substitute for Visual Studio or Blend;
- a RevenueSystem runtime dependency;
- a financial/business-logic implementation tool;
- proof that a proposed interaction is implementable in WPF.

It is used to make motion prototypes and product walkthroughs that help evaluate:
- workspace transitions;
- inspector opening/closing;
- command palette behavior;
- tab/work-item behavior;
- contextual state changes;
- reconciliation resolution flow;
- before/after product demonstrations;
- launch/demo films when the product is ready.

## 2. RevenueSystem 2.0 insertion point

Cinetic may be used only after a static UX concept has passed the product-design review.

Recommended pipeline:

`Static concept → Blend/WPF feasibility check → Cinetic motion prototype → Interaction review → WPF implementation`

A Cinetic prototype can reject or refine a workflow, but it cannot by itself approve implementation.

## 3. Engine policy

### Default: HyperFrames

Use HyperFrames first for Council prototypes because:
- it is Apache-2.0;
- it avoids a Remotion seat-count licensing decision;
- it is suitable for HTML/GSAP-style product motion;
- Cinetic provides a supported HyperFrames starter path.

### Remotion

Remotion may be used only when:
- its motion/render capabilities materially improve the artifact; and
- the applicable Remotion license has been confirmed for the actual user/company context.

Do not infer license eligibility from Cinetic's MIT license.

## 4. YASSIN environment

Verified on 2026-10-17:

- Node: 24.21.0 — PASS (requires 22+)
- Python: 3.13.3 — PASS (requires 3.11+)
- ffmpeg: 9.0.2 — PASS (requires 6+)
- ffprobe: 9.0.2 — PASS
- Git Bash: 5.3.15 — AVAILABLE
- Microsoft Edge Chromium: AVAILABLE
- WSL2: NOT INSTALLED
- upstream source checkout: `C:\Users\alnaseem\Desktop\CouncilVideoStudio\external\cinetic`
- pinned checkout: `bee5d7807205d5543472c38312507f9bf366cbbf`

An isolated Python virtual environment is used under:
`C:\Users\alnaseem\Desktop\CouncilVideoStudio\external\cinetic-venv`

## 5. Windows policy

Upstream officially targets Linux/macOS and names WSL2 as the likely Windows route, while noting Windows/WSL is not tested upstream.

Council policy:

1. Try **native Windows + Git Bash** only through an isolated smoke test.
2. Never claim Windows support until the first full HyperFrames test render passes all relevant gates.
3. If native compatibility fails because of shell/platform behavior, declare:
   `CAPABILITY_GAP_CINETIC_WINDOWS_RUNTIME`
4. WSL2 may then be installed only as the explicit compatibility fallback. A reboot/system-feature change must not be hidden inside a render task.

## 6. Verification gates

Before first real RevenueSystem motion prototype:

### C0 — Source Integrity
- upstream SHA pinned;
- Cinetic lint/tests run where platform permits;
- no unknown install script executed with elevated privileges.

### C1 — Runtime Preflight
- Node;
- Python environment;
- ffmpeg/ffprobe;
- browser/headless shell;
- HyperFrames CLI;
- bash compatibility.

### C2 — First Render
Create an isolated 1920×1080 starter with HyperFrames and verify:
- scaffold;
- lint;
- cues;
- audio build or intentional silent mode;
- preview render;
- probe/spec gate;
- output playable.

### C3 — RevenueSystem Motion Pilot
Animate one bounded flow only:
**Day Console → Open Cashier → Cashier Workbench → return**

No business logic is simulated as proof. The prototype is interaction evidence only.

### C4 — Council Review
UI/UX + Interaction + Architecture review:
- motion helps task clarity;
- no web-only interaction leaked into WPF requirements;
- keyboard path remains valid;
- motion is restrained;
- no financial state becomes ambiguous.

Only then may Cinetic become a normal pre-implementation tool for RevenueSystem.

## 7. Handoff artifacts

Every Cinetic prototype must deliver:
- brief;
- treatment/interaction intent;
- source project;
- preview MP4;
- contact sheet;
- QA reports available from the engine;
- mapping from animated interaction to planned WPF behavior;
- explicit list of anything that is illustrative rather than implementation-accurate.

## 8. Prohibitions

Do not:
- add Cinetic packages to RevenueSystem.csproj;
- bundle Node/Chromium into the RevenueSystem executable;
- replace Blend/WPF prototypes with Cinetic-only video;
- use generated motion as evidence of persistence/financial correctness;
- generate fake “working app” footage and label it runtime evidence;
- run long motion-blur masters during ordinary UX iteration;
- use Remotion without resolving license applicability.

## 9. Studio relationship

For the media Studio, Cinetic is also available as:
**PROGRAMMATIC MOTION DESIGN / PRODUCT DEMO / LAUNCH FILM**

It complements After Effects; it does not automatically replace it.

Route:
- product/UI motion that benefits from deterministic code/timeline → Cinetic;
- compositing, artist-led craft, complex Adobe asset workflow → After Effects;
- final picture edit → NLE;
- audio finishing → DAW/NLE audio stage.

## 10. Capability owner

Primary Council roles:
- UI/UX Specialist
- Interaction Specialist
- Studio Motion Director

Required reviewers for RevenueSystem:
- Architecture
- QA
- Workflow Efficiency

Finance/Data reviewers join when the prototype depicts financial state transitions.
