# Local supervisor foundation

This slice adds a read-only review planner, not a review execution engine. Product truth remains Stage 7, Stage 8 closed; all result authority flags are false. No approval or completed review is issued.

Core holds data contracts. Application selects and unions reviewer assignments. Infrastructure reads the two existing project-local profiles and rejects malformed, duplicate, unknown or weakened version-1 policy catalogs. Host exposes a separate ILocalReviewPlanner; existing ICouncilPlanner is unchanged. The WPF package copies the two profiles for the service; no UI has been added.

Run `dotnet run --project apps/UniversalCouncil.CommandCenter.SupervisionValidation -c Release` for behavioral checks using actual profiles and isolated negative mutations. To print a plan: append `-- --plan request.json`. JSON request uses ChangeId, ProjectId, SourceRevision, ChangeClass, Routes, Surfaces, WorkshopFunctions. Arrays are required. SourceRevision is a 40-character Git SHA binding supplied by the caller, not verified by the planner. Profile fingerprints identify local bytes, not signed approvals or an atomic repository snapshot.

Supported change classes come from default_modes. Every plan includes chair governance and Workshop coordination. LIGHT reversible craft defaults to Visual Systems review only when no craft function is supplied, plus mandatory Workshop clearances. Explicit craft functions are reviewers; authoritative artifact ownership remains unresolved. UX routes add experience and interaction reviewers. All surface changes retain Workshop clearances. Any route or surface has at least COUNCIL mode; security/durability assignments and authority, remote, recovery, agentic architecture, memory and model-routing semantics require ARENA. This conservative floor is independent of caller classification.

The caller must provide all applicable routes and surfaces. This planner cannot discover omissions from source diffs and must not be used as an authorization gate. Owner gates, durable review sessions, artifact ownership/acceptance, independently verified evidence, signed approval receipts, expiry/revocation and execution mediation remain future slices.

The projection builder captures one committed Git revision, rejects source index/worktree dirt and reads all governing JSON bytes from that revision. Source blob IDs are calculated from the bytes read. Unrelated changes and generated output do not block it. Failure occurs before output writing.

Validation disclosure: the full Windows/Python 3.13 suite has an existing SQLite cleanup failure in test_persistent_replay_guard_survives_process_restart, reproduced on unchanged baseline 929c34c. Baseline PR72 P1 Exit Evidence CI is also failing. Neither is accepted as success. This slice requires its dedicated CI and post-change review and is delivered as a draft without merge.
