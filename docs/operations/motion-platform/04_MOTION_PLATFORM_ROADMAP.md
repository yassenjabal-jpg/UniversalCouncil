# Motion Platform / MotionKit — Roadmap

Date: 2026-10-23
Status: GOVERNING_DRAFT_FOR_IMPLEMENTATION_SEQUENCE
Reference application: UniversalCouncil Command Center
Universal scope: all future projects

## MP0 — Foundation Lock

### MP0.1 Charter
Freeze mission, non-goals and authority boundaries.

### MP0.2 Semantic Inventory
Normalize motion purposes and event families from existing Command Center laws.

### MP0.3 Capability Upgrade
Activate Motion Platform Cell roles and review boundaries.

Gate: MOTION_PLATFORM_FOUNDATION_LOCK

## MP1 — Semantic Kernel

### MP1.1 Contracts
Implement renderer-free semantic event and motion contract types.

### MP1.2 Orchestrator
Implement cancellation, interruption, instance ownership and deterministic settle.

### MP1.3 Reduced Motion Policy
Make Reduced Motion an explicit semantic mode with parity tests.

Gate: SEMANTIC_KERNEL_ACCEPTED

## MP2 — Adapter Boundary + Test Doubles

### MP2.1 Renderer Interface
Capabilities, begin, cancel, settle, diagnostics, disposal.

### MP2.2 Deterministic Fake Renderer
No graphics; used for state/race/re-entry tests.

### MP2.3 Product Motion Profile
Tokens/personality separate from semantic contracts.

Gate: RENDERER_BOUNDARY_ACCEPTED

## MP3 — Compatibility Lab

### MP3.1 Windows Native
Prototype Composition/native path.

### MP3.2 Specialist Engines
Prototype Rive, Lottie and SkiaSharp only for scenarios that match their strengths.

### MP3.3 Bake-off
Run S1..S5, performance and accessibility evaluation.

Gate: RENDERER_ROLE_MATRIX_ACCEPTED

No single-renderer winner is required.

## MP4 — Command Center Reference Integration

### MP4.1 In-screen Inventory
Map important icons, sigils, routes, state indicators and semantic objects.

### MP4.2 Event-backed Integration
Replace ad-hoc motion only where MotionKit improves reuse/truth/testability.

### MP4.3 Evidence
Full + Reduced Motion exact-head video, QA, owner review.

Gate: COMMAND_CENTER_MOTION_REFERENCE_ACCEPTED

PR #72 remains unmerged until its own governing gate is satisfied.

## MP5 — SDK + Packaging

### MP5.1 Package Boundaries
Core semantics, Windows adapters, optional specialist adapters, testing kit.

### MP5.2 Versioning
Semantic-versioning policy and compatibility matrix.

### MP5.3 Documentation
Recipes, anti-patterns, migration and adapter authoring.

Gate: MOTIONKIT_SDK_V1_CANDIDATE

## MP6 — Cross-project Proof

### MP6.1 Second Product
Integrate a non-Command-Center product without copying platform internals.

### MP6.2 Android Semantic Parity
Prove equivalent semantic outcomes on Android.

### MP6.3 Governance Lock
Finalize dependency, update, evidence and deprecation policy.

Gate: MOTION_PLATFORM_GENERAL_ADOPTION_APPROVED

## Permanent constraints

- OPEN_SOURCE_FIRST / INTEGRATION_OVER_INVENTION;
- MP1/MP2 are frozen for expansion after validation; only verified integration-driven corrections may change shared internals;
- no custom renderer/timeline/vector engine when an adopted maintained dependency already provides the capability;
- truth before motion;
- no fake activity;
- renderer replaceability;
- Reduced Motion parity;
- exact semantic final state after cancellation;
- no third-party engine directly owns product state;
- no dependency adoption without Compatibility Lab evidence;
- no visual-style homogenization across products;
- no threshold reduction to rescue a failing candidate;
- owner-visible failure reopens visual acceptance.

## Current position

MP0 foundation validated.
MP1 semantic kernel validated and frozen for expansion.
MP2 renderer boundary validated and frozen for expansion.
MP3 reference-Windows technical bake-off is complete on YASSIN for the currently assigned renderer roles.
S1, S3, S4 and S5 pass in Full and Reduced Motion; S2 is explicitly unassigned because no accepted renderer role currently claims STATEFUL_VECTOR.
Owner visual acceptance was explicitly granted on 2026-10-23; RENDERER_ROLE_MATRIX_ACCEPTED is now passed. No renderer is production-adopted.
See 10_MP3_REFERENCE_ACCEPTANCE.md and 11_MP3_OWNER_VISUAL_REVIEW.md for the exact scenario disposition, measurements, limits and approval record.
Execution priority: exact-head MP4 reference integration evidence; do not expand MotionKit abstractions.
Production renderer adoption is not authorized.
Command Center refactor is not authorized by this roadmap alone.
