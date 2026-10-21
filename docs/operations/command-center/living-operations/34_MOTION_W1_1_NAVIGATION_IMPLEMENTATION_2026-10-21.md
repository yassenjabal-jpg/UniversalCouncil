# W1.1 — Eight-Screen Navigation Choreography

Status: **VERIFY**

## Implemented

The eight canonical screens now use one bounded navigation sequence:

**SOURCE EXIT → TARGET COMMIT → TARGET ENTRY → SETTLE**

The animated surface is `ReferenceHost`, so the approved reference image, native reconstruction and its interactive overlay move as one screen rather than producing disconnected micro-animation.

### Interaction rules

- same-screen navigation is a no-op;
- a transition disables hit-testing until settle;
- reentrant navigation stores only the latest requested target;
- transitions never overlap;
- after settle, opacity and transform return to canonical rest geometry.

### Full Motion

Full Motion uses bounded Translate + Scale + Opacity with a less front-loaded quadratic ease. Routine screen handoffs now use 42–68 design-pixel entry travel and 580–600ms total choreography (M3). Decision, Recovery and Work Receipt use 660ms total choreography (M4), where the Motion Bible explicitly permits stronger project-event emphasis. Source exit remains directional and bounded; every transition returns to canonical rest geometry.

This is bounded navigation choreography, not continuous dashboard motion. The remediation changes the actual WPF motion only; frame-delta thresholds remain unchanged.

### Reduced Motion

Reduced Motion performs the same source/target handoff using opacity only:

**source focus loss → crossfade handoff → target focus**

No translation or scale travel is used.

## Architecture Boundary Audit

Boundary: WPF presentation/navigation.

Baseline debt: `MainWindow.xaml.cs` is already large and owns navigation.

Introduced delta: queue/orchestration only remains in `MainWindow`.

Smallest safe extraction: pure WPF animation mechanics are isolated in `ScreenTransitionMotion.cs`.

No DB access, network dependency, runtime authority, mutable static state or business rule was added.

## Evidence update

The deterministic WPF evidence path now visits all eight canonical screens in both Full Motion and Reduced Motion:

1. Home
2. Living Project Workspace
3. Software Autopilot Project
4. Studio Project
5. Owner Decision Mode
6. Checkpoint / Recovery / Fork
7. Pulse / Visual Project Story
8. Project Complete / Work Receipt
9. return to Home to prove settled round-trip navigation

Evidence remains 30 FPS, 1440×900, actual WPF, exact-head and unedited.

The recorder now samples WPF against a real-time Stopwatch cadence and writes BGRA render buffers during the live capture. PNG compression happens only after the live motion window has finished, preventing recorder-induced time dilation. The evidence gate rejects captures whose actual live capture duration drifts by more than 1.25 seconds from the nominal duration or whose maximum frame lateness exceeds 100ms. Motion visibility thresholds remain unchanged. A separate lightweight owner-review artifact contains only the Full/Reduced videos and their manifests/integrity files; the complete raw-frame artifact remains authoritative.

## Protected truth

Stage 7 remains authoritative. Stage 8 remains closed. PR #72 remains Draft and non-mergeable. The visual identity and eight canonical reference files are unchanged.

## Next gate

This implementation is **not yet W1.1-approved**. It must pass exact-head CI/evidence and Studio + Al-Murtakaz post-review before W1.2 can start.
