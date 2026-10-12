# Hybrid Execution Fabric Smoke Evidence — 2026-10-12

Status: PASS
Host: YASSIN
Prototype: company/runtime/hybrid_execution.py
Config: company/config/hybrid_execution.json

## Scope
This evidence covers the first bounded hybrid DC + GUI execution prototype only. It does not claim Council v0.4+ role governance is adopted.

## DC preference smoke
Input intentionally exposed both:
- DC-capable read path;
- GUI window-list path.

Observed plan:
- path: dc_control_plane
- risk: T0_OBSERVE
- authority: remote_shell.read

Observed execution result:
- HOST_DISPATCH_REQUIRED
- host payload requested a deterministic read of company/config/hybrid_execution.json.

The host Remote Desktop Commander read was then completed successfully.

Conclusion:
When both DC and GUI are available, the prototype prefers DC as designed.

## GUI observe smoke
Input exposed only the approved GUI semantic path.

Observed plan:
- path: gui_semantic_uia
- risk: T0_OBSERVE
- authority: desktop_computer_use.observe

Execution was run with explicit task approval, matching Tool Authority.

Observed result:
- YASSIN Control Bridge invoked winapp UI Automation list-windows;
- return code: 0;
- Hybrid result: SUCCEEDED;
- desktop controller lease: null, because T0 observation does not require control ownership;
- shared state persisted successfully.

No window titles, screenshot contents or other visual payloads are retained in this evidence document.

## Governance checks
- Hybrid execution does not create new authority.
- Tool Authority is enforced again immediately before dispatch.
- BLOCKED / UNAVAILABLE / ADMIN_BLOCKED operations fail closed.
- OWNER_EXPLICIT and ASK_BEFORE_WRITE require approved task state.
- T3 additionally requires explicit owner confirmation.
- T2/T3 cannot be SUCCEEDED without post-state verification.
- UNKNOWN is never treated as success.
- raw coordinate execution remains disabled.

## Unit coverage
At the time of this smoke:
- hybrid execution tests: 22 PASS;
- company/runtime/hybrid_execution.py statement coverage: 100%;
- branch coverage: 100%.

## Next slice
The next implementation slice is deterministic batching + compact result projection so large UI results are summarized before entering model context, followed by a real reversible T2 GUI action with independent post-state verification.
