# W0.3 — Evidence System Reset
## CC-MOTION-W0-3-EVIDENCE-PIPELINE-2026-10-21

Status: **MOTION_EVIDENCE_PIPELINE_LOCK**

Prerequisites:
- W0.1 `MOTION_RETURN_BASELINE_LOCK` — PASS
- W0.2 `MOTION_STORYBOARD_CODE_COVERAGE_LOCK` — PASS

## Locked evidence contract

The owner-review capture is now **30 FPS at 1440×900**. The CI floor remains **20 FPS**.

Every WPF motion artifact must be:
- actual WPF;
- exact candidate HEAD;
- unedited;
- Full Motion plus Reduced Motion;
- backed by raw PNG frames;
- SHA-256 bound at raw-frame and encoded-video levels;
- bound to the candidate SHA in both manifest and video-integrity record;
- timestamped with evidence event/object metadata;
- free of optical flow, frame interpolation, or post-produced animation.

## Anti-gaming normalization

Increasing capture rate must not make a weak motion candidate pass merely because it is sampled more often.

The old full-motion floor was **60 changed frames at 20 FPS**. At 30 FPS the equivalent floor is:

`ceil(60 × 30 / 20) = 90 changed frames`

The previous continuous-run floor **6@20** becomes **9@30**.

Reduced Motion thresholds are scaled by the same FPS ratio. Semantic motion-run count remains event-based and is not multiplied.

Therefore W0.3 improves evidence legibility without relaxing acceptance.

## Candidate binding

The Windows evidence workflow verifies `git rev-parse HEAD == CANDIDATE_SHA` before capture. The recorder writes `candidate_sha` into each motion manifest, and the encoder writes the same SHA into video integrity. The final evidence gate rejects a mismatch.

## Raw evidence integrity

Each PNG frame is listed in the manifest with its SHA-256. The evidence gate verifies that each raw frame exists and that its bytes match the manifest digest before using motion metrics.

Encoded Full/Reduced videos also retain SHA-256 and duration checks.

## Semantic timeline

Each evidence action records:
- `evidence_step_id`;
- frame;
- seconds;
- `occurred_at_seconds`;
- event type;
- semantic object;
- human-readable step name.

Current W0 fixture actions are truthfully labeled as evidence navigation/inspection/intent previews unless they actually represent a governed semantic event. Later W1–W3 evidence must replace preview-only actions with the exact event-backed sequences from the W0.2 coverage contract.

## What this gate does not mean

`MOTION_EVIDENCE_PIPELINE_LOCK` approves the **evidence mechanism**, not the current product motion.

The current product is still expected to fail perceptual/semantic motion acceptance until W1–W3 implement the missing choreography. A red motion-quality gate after a successful 30 FPS capture is therefore a valid result, not a pipeline failure.

PR #72 remains Draft and non-mergeable. Stage 7 truth remains unchanged. Stage 8 stays closed.

## W0 exit

Gate: `MOTION_EVIDENCE_PIPELINE_LOCK`

This completes Wave 0 and authorizes **W1.1 — Eight-Screen Navigation Choreography** only after the new pipeline and governance validators pass.
