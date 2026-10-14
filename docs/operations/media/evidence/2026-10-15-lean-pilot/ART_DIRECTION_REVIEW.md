# Art direction review — Owner rejects the delivered native pilot

**Disposition: ART_DIRECTION_REJECTED.** The Owner states that the video has no connection to the channel's artistic direction. Artifact SHA-256: `9eaa0fcbdecda1eae94ecb5071cda38cdf072ba44634ad1c4311bf5f842e049f`.

The previous successful measurements remain valid solely as evidence of native-control latency and sampled technical output. They are not a channel-style sample, creative approval or full Final QC PASS. The video, receipts, scripts and prior measured findings are retained as historical test evidence.

## Review basis

Current PR#30 head before this review: `dc090fa95d17e7de2e2a0ec8dc7d5913e57afc21`. Directly inspected: delivered native contact sheet and `build_lean_pilot.jsx`/`repair_native_pilot.jsx`. Governing style sources: the locked v1.1Visual Production Kit and the reference's documented temporal grammar.

The original `1000061003.mp4` was not found in the checked task/reference/download locations. Detailed reference descriptions below come from repository evidence, not a new claimed direct viewing of that video. The mismatch is independently visible in the delivered artifact and confirmed by the Owner's rejection.

## Concrete mismatch

| Aspect | Documented artistic direction | Native delivered pilot |
|---|---|---|
| Source/media language | Mixed media linked by one transforming motif | Mostly flat native rectangles, marks and text; one archaeological image |
| Motif | Division changes medium, scale, material or state |24marks/rows of bars repeated as explanatory symbols |
| Human/object action | Meaningful interaction can create the next scene | No human/object interaction or material action |
| Transitions | Object reveal, macro bridge, shape/object match, drawing-to-object | Scene backgrounds swap; layers mostly appear/disappear through opacity |
| Editorial composition | Varied, often asymmetric hierarchy and scale | Repeated centered headline over centered diagram |
| Typography | Primary visual medium with deliberate editorial character | Readable temporary system font used as labels |
| Rhythm | Continuous authored visual evolution with meaningful holds | Seven5–8second scene blocks, mostly static after the initial reveals |
| Depth/texture | Source photography, macro material, print/halftone or sculptural treatment | Flat graphic fields and diagram geometry dominate |
| Evidence | Source-faithful evidence integrated through editorial grammar | Image content preserved correctly, but placed as an isolated simple mount |

This is not a small color/font/pacing defect. It is a different visual language: a simple educational infographic sequence in place of a kinetic mixed-media editorial film.

## Where the implementation diverged

1. The lean workflow allowed reusable layouts and restrained object/text motion without expressly preserving the locked mixed-media/transition grammar.
2. The native fallback was authored around the easiest available shapes and text. The absence of an adequate asset pack was allowed to change the art direction instead of being recorded as a craft gap.
3. Runtime checked `visual_coherence`, which can pass for any consistent style, but did not require evidenced `reference_fidelity`.
4. Sampled readability, dimensions, audio and watermark checks answered technical questions; they could not approve this artistic direction. The prior review already withheld full production qualification, but the result still needed explicit artistic rejection.

## Required correction to the method

The five stages, three gates, native execution and measured latency benefits remain. The channel's art grammar must become a mandatory constraint inside those existing gates. Define the sequence's causal motif transformations first, then obtain/reuse the necessary meaningful media. If assets or craft capability are missing, hold the affected work; do not substitute a diagram-only film and call it a simplified realization of the identity.

A possible DAY24 treatment illustrates the correction, without authorizing generation: a segment is physically separated, becomes a macro division, matches into source-faithful evidence, is extracted as an explanatory line, then transforms into a new material/sculptural arrangement before the final editorial synthesis. The exact objects and sources belong to the Art Director's one treatment; this is not a new storyboard/prototype approval ladder.

`docs/operations/media/DESIGN.md` consolidates the governing artistic hierarchy. Runtime now requires Art Director reference-fidelity evidence at the three existing gates and rejects this Owner-rejected export even if technical measurements pass. No new video, frame board, prototype queue or alternative channel identity is created by this review.
