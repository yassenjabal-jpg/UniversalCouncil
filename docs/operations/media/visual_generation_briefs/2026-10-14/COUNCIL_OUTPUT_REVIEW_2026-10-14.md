# Council Output Review — Three-Topic Visual Generation Pilot

**Date:** 2026-10-14  
**Branch:** `codex/channel-visual-identity-rebuild-reference-video-20261014`  
**Reviewed HEAD before this artifact:** `17fe56a096f0dc22e6a1d67367068e95bb22289a`  
**PR:** #30 — still Draft / open / not merged  
**CI at review start:** Company Stage 0 #325 PASS; CodeQL #241 PASS  
**Governing identity:** Modern Editorial Surrealism  
**Governing briefs:** `THREE_TOPIC_COUNCIL_GENERATION_BRIEFS_v1.0.md`

## 1. Reviewed outputs

The Council reviewed the actual generated images, not prompt summaries only.

Generation IDs reviewed:
- `82fa6fd1-6fc1-49af-92eb-26e083eb6e7e`
- `c3c32f28-3cef-422d-b63e-41bafabd756b`
- `00c34b27-bcae-4812-9d63-adf4384eb6fd`
- `58ca8dd2-eeab-4949-9a11-31d305fbf8e3`

All four attempts materially fused the three topics into a triptych/composite rather than honoring one approved prompt version per independent asset.

---

# 2. Council role-by-role review

## Visual Art Director / Frame Curator

### Positive findings
- The outputs show that the **underlying metaphor family is visually viable**.
- Baghdad's compass/circle motif has strong immediate recognition.
- Banking's transparent acrylic language is potentially distinctive and contemporary.
- The day/night segmented disc is the strongest purely surreal object among the three.
- Paper texture, cutout depth, strong field colors, and tactile surfaces can belong to the new identity when restrained.

### Rejections
- The generated work repeatedly returns to **spectacle before idea**.
- Baghdad becomes a miniature cinematic city rather than geometry becoming a plan.
- Banking becomes a mechanical display object with gears, coins, icons, houses, charts, books, people, and documents.
- Time becomes a decorative celestial wheel rather than one tactile day-object being partitioned.
- The three topics are visually over-connected by similar circular forms, warm brass, ivory paper, and dramatic compositing.

**Verdict:** CONCEPTS KEEP / GENERATED EXECUTION REJECT.

---

## Thumbnail & Packaging Designer

### Mobile-readability review
- Baghdad: the compass reads, but the city detail competes with it. The eye lands on “beautiful Baghdad miniature” rather than “the act of planning.”
- Banking: too many simultaneous cues. At mobile size, the mechanism becomes visual noise and loses the simple input → routing idea.
- 24 hours: the circle silhouette is strong, but detailed sun/moon landscapes make it look like a decorative time poster.

### Packaging risks
- Attempt 1 also introduced generated Arabic typography, directly violating the brief.
- The images are not independent thumbnails; they are panels in a composite.
- Negative space is inconsistent or consumed by extra detail.
- The channel risks template collapse: circular object + brass + paper + blue/green field across all three topics.

**Verdict:** NONE IS A TEST-READY THUMBNAIL.

---

## Synthesis & Alternatives Designer

The failures are not evidence that the three selected metaphors are wrong. They show that the generation surface **merged context across briefs and then optimized for a visually rich triptych**.

### Salvageable visual primitives
- Baghdad: **precision compass + circular line** only.
- Banks: **transparent acrylic routing junction** only.
- 24 hours: **single segmented tactile disc** only.

### Elements that must be discarded
- Baghdad: full city reconstruction, river, palms, domes, skyline, heavy blue.
- Banks: visible gears, multiple coins, houses, growth chart, education/health/industry icons, people, books, documents.
- 24 hours: hand, explicit moon/sun spectacle, landscape wedges, cosmic poster treatment, large blue celestial field.

**Synthesis decision:** do not redesign the concepts. Simplify execution back to the approved one-sentence metaphor.

---

## Red Team / Anti-Slop

### Primary failure
The output repeatedly satisfies “pretty AI editorial art” while violating the brief.

### AI-slop signatures detected
1. More objects than the concept requires.
2. Decorative brass/gold appearing because the model associates “premium editorial” with luxury materials.
3. Generic blue/green/gold color-field dramatization.
4. Miniature city/worldbuilding replacing abstraction.
5. Mechanical gears replacing a simple banking-flow metaphor.
6. Sun/moon/cosmic literalism replacing the deeper “why divide the day?” question.
7. Repeated radial/circular structures creating cross-episode sameness.
8. Generated text in an asset that explicitly forbade model-rendered text.
9. Triptych composition despite one-job/one-brief requirement.

### Red Team ruling
- Baghdad output: **REJECT**
- Banks output: **REJECT**
- 24-hour output: **REJECT**
- Composite/triptych format: **REJECT**
- Identity direction itself: **KEEP**
- Approved written briefs: **KEEP**, with execution hardening below

---

# 3. Quantitative scorecard

Scale: 0 = fail, 5 = excellent.

| Criterion | Baghdad panel | Banks panel | 24-hour panel |
|---|---:|---:|---:|
| One clear metaphor | 2 | 1 | 3 |
| One hero | 2 | 1 | 3 |
| Mobile readability | 3 | 2 | 4 |
| Negative space discipline | 2 | 2 | 3 |
| Episode uniqueness | 3 | 3 | 3 |
| Reference-video design grammar | 3 | 2 | 3 |
| Anti-slop compliance | 1 | 0 | 2 |
| Brief fidelity | 1 | 0 | 1 |
| **Council average** | **2.1/5** | **1.4/5** | **2.8/5** |

The 24-hour panel is the strongest visual object, but it still fails the approved execution contract.

---

# 4. Cross-output identity review

## What is working
The new identity is beginning to show a coherent vocabulary:
- editorial paper fields;
- tangible hero objects;
- controlled surrealism;
- clean compositional geometry;
- tactile print/material feel.

## What is not working
The generator is turning coherence into sameness:
- repeated circles/radials;
- recurring brass/gold;
- heavy blue;
- large physical miniature objects;
- high-detail “AI showcase” rendering.

This is exactly the failure mode the Visual Bible was designed to prevent.

**Council conclusion:** the identity is not too diverse; the execution is not diverse enough.

---

# 5. Council-mandated execution hardening

Before the next generation attempt:

1. **ONE JOB = ONE PROMPT VERSION = ONE ASSET.** No multi-topic context may be supplied to the generation surface.
2. The execution environment must receive only:
   - the one approved final generation instruction;
   - its negative constraints;
   - the one prompt-version identifier.
3. Do not provide the other two briefs in the same generation context.
4. Explicitly require **one single 16:9 image, not a triptych, diptych, contact sheet, collage, storyboard, or multi-panel composition**.
5. Add an **object-count budget**:
   - Baghdad: one compass + one line transformation;
   - Banks: one routing mechanism + one token;
   - 24 hours: one segmented disc.
6. Add a **detail budget**: no decorative micro-scenes unless explicitly listed as allowed.
7. Add a **palette hard stop**:
   - Baghdad: ivory/charcoal + tiny oxidized green/copper; no dominant cobalt;
   - Banks: muted green/ivory + restrained brass token only;
   - 24 hours: ivory/charcoal + deep plum/mineral red; blue restricted to the night half of the disc only.
8. Any material deviation triggers immediate rejection; do not “salvage” by cropping a bad composite.
9. Typography remains deterministic post-production only.
10. The 24-segment exact count, if visible, must be created in deterministic vector post.

---

# 6. Episode-specific next-pass direction

## Baghdad — BAGHDAD-OM-v1.1 execution hardening
Do not change the concept. Make the image visually quieter:
- no city;
- no river;
- no palm trees;
- no architecture;
- no blue field;
- no historical atmosphere;
- the line itself carries the tiny plan texture.

**Target feeling:** precision, discovery, birth of an idea.

## Banks — BANKS-OM-v1.1 execution hardening
Do not change the concept. Remove all machine-language defaults:
- no gears;
- no pipes;
- no multiple coins;
- no icons;
- no house;
- no charts;
- no books/people/documents.

The mechanism should resemble a transparent contemporary design prototype, almost diagrammatic.

**Target feeling:** clarity, routing, controlled flow.

## 24 hours — DAY24-CS-v1.1 execution hardening
Keep the single segmented-disc idea, but make it less celestial:
- no hand;
- no moon object;
- no scenic landscapes inside each wedge;
- no cosmic poster;
- no giant blue field.

Use two abstract material states — warm daylight paper / deep night paper — rather than literal scenery.

**Target feeling:** a whole day physically divided by design.

---

# 7. Final Council decision

**UNANIMOUS RESULT: REJECT CURRENT OUTPUTS / KEEP IDENTITY / KEEP CORE CONCEPTS / HARDEN EXECUTION.**

The Council does **not** recommend another identity rebuild.

The next problem to solve is execution isolation and constraint fidelity, not visual ideation.

No current image may enter production, thumbnail A/B testing, reference-frame lock, or final packaging.

No merge to `main` is authorized by this review.
