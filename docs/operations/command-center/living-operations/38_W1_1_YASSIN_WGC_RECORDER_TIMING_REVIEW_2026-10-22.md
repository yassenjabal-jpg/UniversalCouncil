# W1.1 — Al-Murtakaz Review of YASSIN WGC Recorder Timing

Date: 2026-10-22  
Status: APPROVE_TO_IMPLEMENT_NO_WAIT_DECOUPLED_SAMPLER  
Scope: W1.1 evidence recorder only  
PR: #72 — remains Draft / not merged

## Trigger

Real-host YASSIN evidence on candidate `21cbc9a4d22ea896e7f0545493a23d38dc9142c1`
proved the persistent WGC path is valid but exposed recorder interference:

- exact 1440x900 actual HWND;
- no fallback;
- source frame errors = 0;
- Full 1140 frames / 38s;
- Reduced 840 frames / 28s;
- Full max lateness 142.141ms;
- Reduced max lateness 165.152ms;
- Full longest changed run 8, below the protected minimum 9.

The failure was therefore not a geometry, WGC-source or product-truth failure.

## Architecture review

The blocking coupling was inside evidence infrastructure:

1. semantic motion steps ran on the WPF dispatcher;
2. dispatcher pumping also paced every sample;
3. WGC pixel copies, frame-delta work and large per-frame allocations shared the
   same process cadence;
4. recorder work could delay WPF rendering and then measure the disturbed output.

The approved direction is to separate responsibilities:

`WPF dispatcher -> product rendering + semantic steps only`

`dedicated sampling worker -> absolute Stopwatch 30Hz sample deadlines`

`persistent WGC -> latest actual HWND pixels`

`bounded pooled BGRA buffers -> background FFmpeg lossless PNG encoder`

No product/runtime layer receives a capture dependency.

## Exact-head decoupling result

Candidate `98bfb772af8fb6d1195da2d1d06c0e18ae62709a` implemented worker sampling
and pooled buffers.

Real YASSIN exact-head evidence bundle:

`sha256:c7a48fa7d241508418caaaeac5311d94bb94eb9e8525bfc4d7acad8d20181de6`

Objective validator: **PASS**.

Full:
- changed frames: 186;
- longest changed run: 18;
- motion runs: 44;
- max lateness: 43.175ms;
- mean lateness: 27.997ms;
- samples later than one 30fps frame: 420.

Reduced:
- changed frames: 27;
- longest changed run: 3;
- motion runs: 17;
- max lateness: 14.555ms;
- samples later than one 30fps frame: 0.

## Red Team objection

The Full path also introduced an 18ms `WaitForFrameAfter` budget before capture.

Although the validator passed, this is not accepted as the final recorder
contract because it biases sampling toward newly-arrived compositor frames and
causes 420 Full samples to occur more than one 30fps frame after their nominal
deadline.

The evidence requirement is truthful real-time sampling, not preferential
selection of fresh frames.

## Falsification test

A local diagnostic changed only:

`FullMotionFreshFrameWaitBudgetMs: 18 -> 0`

This diagnostic is explicitly **not exact-head acceptance evidence**.

Result on YASSIN:

- changed frames: 174;
- longest changed run: 10;
- motion runs: 53;
- max lateness: 13.794ms;
- mean lateness: 5.365ms;
- samples later than one 30fps frame: 0.

The protected Full thresholds still pass without fresh-frame waiting.

Therefore the 18ms wait is unnecessary.

## Al-Murtakaz decision

**RETURN the current 18ms wait for change.**

**APPROVE TO IMPLEMENT:**
- dedicated WGC sampling worker;
- pooled BGRA buffers;
- background FFmpeg encoder;
- zero fresh-frame wait.

**DO NOT CHANGE:**
- motion choreography;
- Motion Bible timing classes;
- Full 90 / 9 / 8 floors;
- Reduced Motion limits;
- 100ms lateness gate;
- actual HWND / 1440x900 requirement;
- no-fallback rule;
- Stage 7 truth;
- Stage 8 state;
- runtime authority;
- W1.2 state;
- PR merge state.

## Clear implementation sequence

1. Set the Full fresh-frame wait budget to zero.
2. Keep the decoupled worker and pooled-buffer implementation.
3. Build an exact-head YASSIN host kit from the resulting PR head.
4. Run Full + Reduced on YASSIN.
5. Require the unchanged validator to pass.
6. Inspect Full/Reduced videos visually through Al-Murtakaz Product Workshop.
7. Only after visual QA + Al-Murtakaz post-review may W1.1 be proposed to Owner
   for acceptance.
8. Do not start W1.2 and do not merge PR #72 during this sequence.

## Reopen rule

If the no-wait exact-head Full capture falls below `longest_changed_run >= 9`,
do not restore fresh-frame waiting and do not lower thresholds.

Return to Motion Systems + Visual QA to determine whether the product motion
itself violates the governing motion duration contract.
