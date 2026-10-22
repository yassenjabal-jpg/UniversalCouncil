# Durable local review sessions (S2)

Opt in through CommandCenterComposition.CreateLocalReviewSessions(baseDirectory, absoluteStorageDirectory, optionalTimeProvider). Default WPF startup creates no storage. LocalReviewSessionService.Create(request, artifactSha256, lifetime) obtains a real local plan, copies caller arrays and persists a version-zero session. Lifetime must be positive and at most seven days. The artifact digest and source revision are supplied identifiers, not independently verified artifacts.

Read(id, currentRevision, currentArtifactSha256) rechecks freshly loaded policy and the complete recomputed plan. Record additionally requires expectedVersion, assigned role, attributed actor, known outcome, rationale and evidence references. One record per assigned role is append-only. Changing a report requires a new session rather than erasing dissent. Actor strings and references are unverified caller reports; the API does not assert a reviewer actually ran.

State precedence:
1. Persisted terminal EXPIRED or INVALIDATED (binding/policy/plan drift or clock rollback).
2. Any BLOCKED result.
3. Any RETURNED_FOR_CHANGES result.
4. Any OWNER_DECISION_REQUIRED result.
5. Every assigned reviewer has an ACCEPTED_REPORT: RESULTS_RECORDED.
6. Otherwise REVIEWING.

RESULTS_RECORDED is not acceptance or approval. EvidenceVerified, ApprovalGranted, ExecutionAuthority, LiveExecution and Stage8Opened remain false. A read may advance Version to persist its latest UTC observation, so callers must use the returned version for subsequent optimistic writes. Record on stale binding returns the persisted terminal session without adding a result. Missing or malformed freshness input throws; it never returns a current session.

The JSON store uses GUID filenames, an exclusive nonblocking per-session lock, a compare-and-swap version, strict required fields and duplicate/unknown-property rejection, a 4 MiB limit, validated immutable binding/history prefixes, file flush and same-directory atomic replacement. Conflicts and storage failures propagate explicitly and leave the preceding record available. No automatic backup recovery is attempted. Atomic replacement is a local filesystem/process-crash property, not a power-loss or distributed transaction guarantee.

Storage is same-user and trusted-process local state. The SHA256 envelope detects accidental corruption; it is neither a signature nor protection from deliberate local rewriting. The storage path is explicitly configured by the trusted host, not accepted from remote requests. Session files must not be used as an authorization gate.

Validation: run the existing SupervisionValidation executable. It uses temporary isolated stores, controllable UTC time, real policy copies, concurrent writers, corrupted JSON and induced write failures. No reviewer/provider execution, production approval file or parent-governance change occurs. Authenticated identity, evidence verification, signed approval receipts and durable execution remain later slices.
