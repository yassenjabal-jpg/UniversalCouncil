# PHASE 0 YASSIN Reality Test Runbook

Status: PENDING HOST EXECUTION
Date: 2026-10-19

## Rule

This runbook is evidence-only. Passing repository tests does not pass the real GUI gate.

## Test A — Session readiness

Record:
- host name;
- Windows session state;
- lock state;
- UAC/secure-desktop state;
- YASSIN Control Bridge version/evidence receipt;
- controller lease holder.

Expected:
- unlocked interactive session => READY;
- locked session => BLOCKED;
- secure desktop/UAC => BLOCKED.

## Test B — Single controller

1. Acquire GUI controller lease for Phase 0 test task.
2. Attempt a second state-changing controller acquisition.
3. Confirm second acquisition is rejected.
4. Release first lease.
5. Confirm a new controller may acquire it.

Expected: no focus/pointer race.

## Test C — Reversible GUI action

Use a harmless reversible action in an approved application:
- observe current window state;
- invoke one bounded action;
- verify the post-state independently;
- reverse/close without destructive changes.

Expected:
- verified post-state => SUCCEEDED;
- missing post-state evidence => UNKNOWN, never SUCCEEDED.

## Test D — Lock interruption

During a safe test:
1. checkpoint;
2. lock Windows;
3. attempt next GUI action;
4. confirm action is blocked and not retried blindly;
5. unlock;
6. re-observe current application state;
7. resume only from a verified checkpoint.

## Test E — UAC/elevation mismatch

Trigger only a benign elevation boundary, without installing or changing system settings.

Expected:
- secure desktop is detected or action is blocked;
- no coordinate clicking through the UAC boundary;
- no privilege widening.

## Test F — Crash / unknown

Use a disposable test application/process:
1. checkpoint;
2. dispatch a bounded state change;
3. interrupt the provider before postcondition verification;
4. confirm UNKNOWN;
5. confirm no automatic replay;
6. reconcile only after independent evidence.

## Evidence packet

Store only:
- timestamps;
- host/session identifiers;
- bridge/component versions;
- action IDs;
- result states;
- bounded screenshots of approved application windows;
- hashes/paths of non-sensitive artifacts.

Do not store:
- passwords;
- tokens;
- private desktop screenshots;
- unrelated windows;
- browser secrets.

## Verdict

G0-B UNATTENDED_GUI_REALITY remains BLOCKED_BY_ENVIRONMENT until all tests above have host evidence.
