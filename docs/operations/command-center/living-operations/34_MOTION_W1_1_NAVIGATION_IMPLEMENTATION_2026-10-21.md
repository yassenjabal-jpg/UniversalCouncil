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

Full Motion uses restrained Translate + Scale + Opacity. Entry travel is 18–38 design pixels depending on the canonical screen and settles in 320–390ms after a 150–175ms source exit.

This is bounded navigation choreography, not continuous dashboard motion.

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

## Protected truth

Stage 7 remains authoritative. Stage 8 remains closed. PR #72 remains Draft and non-mergeable. The visual identity and eight canonical reference files are unchanged.

## Next gate

This implementation is **not yet W1.1-approved**. It must pass exact-head CI/evidence and Studio + Al-Murtakaz post-review before W1.2 can start.
