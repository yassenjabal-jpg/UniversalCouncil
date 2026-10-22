# Supervisor completion implementation plan
Goal: a usable, truthful supervision cycle, followed by qualified reusable motion.
Architecture: Core contracts, Application coordination, Infrastructure adapters, explicit Host composition, WPF presentation. Product state owns truth.
Spec: 39 owner motion clarification, 45 durable sessions, 48 evidence verifier, approval policy.
Constraints: Stage7 authoritative; Stage8 closed; no runtime/live authority. Caller reports are unverified. Byte match is not semantic acceptance. Keep dissent and historical evidence.

- [ ] S4a read model: Core LocalSupervisionSnapshot and ReviewerReportView; Application LocalSupervisionReader.Read(Guid,string,string) invokes fresh LocalReviewSessionService.Read. Preserve pending roles, every outcome/rationale, binding/version and terminal states; never expose approval capability. Host opt-in factory; CLI --inspect-session. Tests restart, pending/blocker, expiry/drift, invalid binding and detached immutable collections.
- [ ] S4b WPF supervision inspector: bind the read model, show required/pending/reported roles, complete dissent and provenance. Open by explicit session identity and trusted storage config. Test keyboard/RTL, real commands, unavailable/corrupt session, reopen and stale writes; capture actual window evidence.
- [ ] S5 authenticated review: first define the trusted identity/credential issuer and threat model from actual available adapters. Implement identity validation and role authorization independently of actor display strings. Bind receipts to source/artifact/policy; reject stale/replayed/unknown issuers. No self-issued approval.
- [ ] S6 semantic evidence: typed adapters for existing CI/test/capture reports; validate schema, producer identity, source and report meaning. Keep content-match, capture attestation, semantic acceptance and approval distinct. Negative tests forged/missing/partial/stale results.
- [ ] P1 diagnostic: preserve exact failure logs; reproduce recorder timing on comparable hosts, measure UI/sampling/encoding boundaries, fix demonstrated cause, rerun original thresholds. Never tune movement to metrics.
- [ ] MotionKit selection: independent experiment branch; three Home elements x native/WPF behaviors+Lottie/behaviors+SkiaSVG. Inventory trigger/function/reduced behavior; package/license compatibility review; measured resource/frame quality and WGC tests; scoped Studio/truth/accessibility review before selection.
- [ ] Eight-screen rollout: element/trigger/motion/function/reduced inventory for each canonical screen; integrate selected shared abstraction incrementally, verify interaction and full/reduced captures.
- [ ] Acceptance: exact revision CI and runtime artifacts, scoped source/product reviews, owner presentation and normal PR merge. Completion of these tasks does not open Stage8.

Review focus: stale snapshots; untrusted reviewer identity; forged report semantics; erased dissent; fixture/prototype mistaken for runtime truth. Each slice owns its negative tests. Execution begins S4a; later slices need concrete designs against actual code before implementation.
