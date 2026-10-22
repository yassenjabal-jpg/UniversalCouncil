# S3 committed-declaration evidence content verification

Create through CommandCenterComposition.CreateEvidenceVerifier(absoluteRepositoryRoot, absoluteArtifactRoot, allowFixtures:false). It is an opt-in, read-only service and does not run on default WPF startup. The current local content adapter is Windows-specific. Invoke on a background worker; the synchronous API may perform bounded Git processes and local file IO.

Request fields are ProjectId, ChangeId, SourceRevision, ManifestRevision and ManifestPath. Both revisions must be full 40-hex SHA1 commit IDs (this repository object format). ManifestRevision is the evidence-manifest commit and may be later than SourceRevision. Git must prove SourceRevision is its ancestor. Missing commits/shallow history fail closed; there is no network fetch or working-tree manifest fallback.

Schema1 JSON uses these exact case-sensitive fields:
- SchemaVersion: 1
- ProjectId, ChangeId and SourceRevision: exact expected binding (revision comparison ignores hex case)
- EvidenceKind: REAL or FIXTURE
- Entries: nonempty array of { Path, Sha256, SizeBytes }

The manifest is read as a regular committed blob, with its Git blob ID and raw-byte SHA256 retained. Unknown/duplicate/missing/null fields, excess JSON depth and unsupported schema/kinds fail closed. Limits: 1 MiB manifest, 100 entries, 1 GiB per file and 2 GiB aggregate. Limits are validated before content reads. Relative artifact paths use slash separators, Windows case-insensitive uniqueness and no traversal, device names, ADS, trailing dots/spaces or absolute paths.

The artifact root is trusted Host configuration. UNC/mapped-network roots and reparse ancestors are refused. The same file stream is measured and hashed while locked against writers/deletion; its final Windows handle path must match the intended path. A successful result describes the bytes read at that time, not an atomic snapshot of the whole bundle or a guarantee against later changes. Same-user trusted local processes are the boundary; this is not a hostile multiuser filesystem sandbox.

Git subprocesses use fixed argument arrays, literal pathspecs, no replacement objects/lazy fetch, bounded stdout/stderr and a ten-second cancellation budget per command. File reading has a cooperative 120-second per-file deadline checked between synchronous reads; it cannot interrupt a single blocked OS read. There is no hard whole-bundle latency guarantee.

Statuses:
- CONTENT_MATCH: bytes match a committed manifest declared REAL.
- FIXTURE_CONTENT_MATCH: explicitly allowed fixture bytes match; the fixture label is retained.
- UNAVAILABLE: a failed/missing/unknown binding, IO/Git failure, unsupported manifest, rejected fixture or mismatched artifact. Partial measured entries never make the overall result successful.

ContentMatchesDeclaration is narrow. BindingKind is COMMITTED_DECLARATION_NOT_CAPTURE_ATTESTATION. CaptureRevisionIndependentlyVerified, SemanticEvidenceAccepted, ApprovalGranted, ExecutionAuthority and Stage8Opened remain false. A Git declaration can be wrong about capture provenance or test results. This verifier does not parse report semantics, certify actor identity, issue approval, change S2 EvidenceVerified, or open any stage.

CLI:
dotnet run --project apps/UniversalCouncil.CommandCenter.SupervisionValidation -c Release -- --verify-evidence REPOSITORY ARTIFACT_ROOT SOURCE_SHA MANIFEST_SHA MANIFEST_PATH PROJECT_ID CHANGE_ID
Append --allow-fixtures only for explicit fixture inspection. JSON output retains hashes, revisions, kind and failure reasons; exit0 means byte match only, exit1 means unavailable.

Validation uses isolated temporary Git repositories and artifact directories. The REAL-kind positive test is a synthetic branch test, not production evidence. Cases include working-tree disagreement, malformed/null/missing JSON, wrong source/type/ancestry, hash/size/count limits, directory junction escapes and explicit fixture mode. Source review is separate from executed validation. Existing P1 evidence CI failure is not reclassified as success.
