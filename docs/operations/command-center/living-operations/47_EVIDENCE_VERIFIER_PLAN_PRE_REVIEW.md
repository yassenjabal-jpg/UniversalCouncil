# S3 EvidenceVerifier plan and pre-change review

Baseline: 67c6b7dfb87d1e3b6572d4f7cb8a0a4040e6ec8c, verified locally and PR75 source head before edits. Working tracked files clean.

Decision: APPROVE_TO_IMPLEMENT by evidence_review, source-only review representing truth, architecture, security and Red Team; no executed production roles, approval grant, merge or Stage8 permission. Reviewed doc45, approval policy and architecture invariants.

Goal: compare bounded local file bytes with an immutable Git-committed manifest declaring expected project/change/source. It is not capture attestation, test-result parsing, authentic approval or evidence-semantic acceptance.

Architecture: Core typed manifest/request/snapshot/result; Application binding/limit checks; Infrastructure fixed bounded Git subprocess and Windows file hashing; Host opt-in factory; validation CLI and isolated temporary Git fixtures. S2 remains unchanged and EvidenceVerified=false.

Tasks:
- Add failing behavioral checks for committed-vs-working manifest, wrong/missing/noncommit/source ancestry, strict malformed/unknown/duplicate JSON, fixturedefault refusal, file path/hash/size/count/byte limits, Windows reparse boundaries and no authority.
- Implement strict schema1, canonical full SHA1 commit IDs, regular committed manifest blob <=1MiB, count<=100, eachfile<=256MiB, aggregate<=1GiB. Fixed argv no shell, no replacement objects, bounded Git time/output.
- Trusted absolute local root; reject traversal/ADS/ambiguous Windows names/reparse ancestors. Read/hash the same locked stream; final handle path containment on Windows. No hostile concurrent-process or cryptographic-authenticity claim.
- Only CONTENT_MATCH / FIXTURE_CONTENT_MATCH establish byte matches; missing/unknown/errors fail closed. Return committed manifest SHA256/blob identity and measured file hashes. CaptureRevisionIndependentlyVerified/SemanticEvidenceAccepted/ApprovalGranted/ExecutionAuthority/Stage8Opened stay false.
- Verify .NET10 behavioral runner, existingPython21, contract validator and WPF build; independent post-source review; publish to draft PR75 and inspect exact-head CI.

Material scope changes reopen review. No provider calls, default startup filesystem activity, parent governance edits, UI/Motion changes, session truth promotion or merge.

## Narrow resource amendment — 2026-10-23 Asia/Baghdad

Evidence review APPROVE_TO_IMPLEMENT: 1GiB/file and 2GiB/bundle, count100/manifest1MiB unchanged; cooperative per-file120seconds, not hard OS interruption. Needed for existing archive freshly statted at1008242257bytes. Expected original SHA256 remains7f8c8e428f334ee7d370652b40181e4ba2c35eb22ce3fb71ac0fdb6f9ccf15ae and sourcec8dfc2415e6e81ec05d85378a64520196e871c15. CommittedREALdeclaration plus actualread-onlyverification permitted; no capture, semantic, motion, runtime or approval promotion. Boundarytests and finalpostreviewrequired.
