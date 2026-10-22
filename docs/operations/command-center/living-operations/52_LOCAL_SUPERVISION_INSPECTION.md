# Local supervision inspection (S4a)
LocalSupervisionReader.Read(id,currentRevision,currentArtifactSha256) obtains the freshly validated session through S2. It preserves its state precedence, binding, version, every report and pending roles. Arrays and nested references are copied into read-only collections. Actors, reports and references remain caller-reported and unauthenticated.
The read may persist an observation/version or terminal invalidation. Do not call it a zero-write operation or cache an old success after errors.
Host: CreateLocalSupervisionReader(baseDirectory,trustedStorageDirectory,optionalClock).
CLI: --inspect-session STORAGE GUID SOURCE_SHA ARTIFACT_SHA256. Exit0 means a session snapshot was obtained, including BLOCKED/EXPIRED/INVALIDATED states; inspect State. It never means acceptance. Unavailable returns1; malformed usage2.
No evidence bytes are checked by this inspector. EvidenceVerified/ApprovalGranted/ExecutionAuthority/LiveExecution/Stage8Opened remainfalse. No production session path is chosen implicitly.
This slice supplies a local inspection contract; WPF UI, authenticated identity and semantic evidence remain later tasks in51.
