# Hybrid Execution Slice 2 Evidence — 2026-10-12

Status: PASS
Host: YASSIN
Scope: deterministic batching, compact result projection, independent GUI post-state verification, reversible T2 smoke.

## Deterministic batching
The executor now supports bounded batches of up to the configured maximum (6 steps).

Behavior verified:
- one physical desktop controller lease is held across a GUI-control batch;
- the lease is released at batch completion/failure;
- the batch stops at the first non-SUCCEEDED state;
- DC/native-only batches do not acquire a desktop controller lease.

## Fail-closed T2 probe
A reversible Notepad buffer was created from a temporary test file containing:

HYBRID_ORIGINAL

First attempt:
- action: set_value -> HYBRID_CHANGED
- provider action returned success;
- independent UIA get_value returned HYBRID_CHANGED without the expected CR terminator;
- verifier returned UNKNOWN;
- batch stopped immediately before the restore step.

This is expected fail-closed behavior: provider success did not override a mismatched post-state.

Recovery:
- the buffer was restored to HYBRID_ORIGINAL;
- independent UIA get_value matched exactly;
- result: SUCCEEDED.

Corrected batch:
1. HYBRID_ORIGINAL -> HYBRID_CHANGED
2. HYBRID_CHANGED -> HYBRID_ORIGINAL

Both steps:
- classified T2_LOCAL_STATE_CHANGE;
- used desktop_computer_use.control;
- were independently verified through a separate get_value probe;
- returned SUCCEEDED.

The shared state contained exactly one controller_acquired and one controller_released event across the two-step batch.

Disk verification after the batch:
- temporary file remained HYBRID_ORIGINAL;
- no persistent file content change occurred.

The specific test Notepad window was then closed by matching its test-only window title; no matching test window remained.

## Compact Result Projection
The same live list_windows observation was measured in two forms without committing raw UI output.

Raw Control Bridge output:
- 13,062 bytes

Hybrid compact projection:
- 3,026 bytes

Reduction:
- 76.8%

The specialized list_windows projection retains:
- total window count;
- process-count summary;
- foreground process/class;
- action state and return code.

It omits:
- window titles;
- full repetitive window records;
- raw stdout from model-facing output.

Projection limits are now governed by company/config/hybrid_execution.json:
- enabled: true
- max_items: 6
- max_text_chars: 320
- raw_output_default: false

## Unit coverage
Targeted tests after this slice: 41 PASS.

Runtime coverage:
- company/runtime/hybrid_execution.py: 100% statements / 100% branches
- company/runtime/hybrid_projection.py: 100% statements / 100% branches
- company/runtime/hybrid_verification.py: 100% statements / 100% branches

## Security and authority boundary
This slice does not grant new authority.

Tool Authority remains re-checked before dispatch.
T2/T3 still require post-state verification.
UNKNOWN is never promoted to SUCCEEDED.
T3 owner-confirmation behavior is unchanged.
Raw coordinate execution remains disabled.
