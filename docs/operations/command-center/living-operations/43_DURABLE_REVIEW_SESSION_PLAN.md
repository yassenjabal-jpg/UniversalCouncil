# Durable local review sessions implementation plan

> For agentic workers: execute natively with a separate source review before and after implementation.

Goal: retain review plans and attributed result reports across process restarts, without granting approval.
Architecture: Core records; Application state machine and optimistic-version service; Infrastructure atomic JSON store; explicit Host factory. Existing read-only planning remains unchanged.
Tech: .NET 10 and System.Text.Json, no added packages.
Spec: 41_SUPERVISOR_FOUNDATION.md subsequent ReviewSession slice; mandatory approval policy.

Constraints: Stage7; Stage8 closed; execution/approval false. Actor identity and evidence refs are caller reports, not authenticated or independently verified. SHA256 binding is supplied, not a claim that artifacts were verified. No automatic provider invocation.

Review focus: stale version races; truncated/corrupt persisted files; missing reviewers; expiry/clock rollback; changed revision/artifact/policy.

Task1: create Core ReviewSession/ReviewResult/ReviewBinding and Application IReviewSessionStore/LocalReviewSessionService. Create from real planner only. Result submission checks assigned role, known outcome, nonempty actor/rationale and bounded references. Missing reviewers remain pending; all reported accepted results means RESULTS_RECORDED, never APPROVED. Negative results retain blockers. Expiry or binding mismatch permanently invalidates further recording.
Task2: JsonReviewSessionStore with safe GUID filenames, exclusive lock, expected-version CAS, atomic replacement, Flush(true), max input bytes, integrity SHA256 and strict JSON. Treat digest as corruption detection, not authentication. Load through Application validation; no directory scanning or arbitrary file refs.
Task3: expose explicit Host factory requiring storage directory; add isolated behavioral checks in validation project. Cover restart, every outcome, missing reviewers, unknown role/outcome, duplicate role result, version conflict and two-store concurrent update, malformed file, digest mismatch, expiry, binding drift, no authority.
Task4: run existing61 checks plus session checks, WPF build, Python21, contract validator. Pre/post source review. Commit/push PR75 draft and inspect exact-head CI; record known full-suite baseline failures. No merge.
