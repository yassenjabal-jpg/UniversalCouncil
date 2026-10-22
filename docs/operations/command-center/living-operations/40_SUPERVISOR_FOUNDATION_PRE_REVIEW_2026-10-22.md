# Supervisor foundation — pre-change review

Baseline: 929c34c062f252cc6e850397eb8d68124908bdec. Branch: command-center/murtakaz-supervisor-foundation-20261022.

Decision: APPROVE_TO_IMPLEMENT bounded S0 provenance and S1 read-only local review planning. Source-only review by supervision_pre_review representing chair, product truth, architecture, security, AI runtime, Red Team and Workshop coordination. These are review lenses, not independently executed production roles.

Preserve Stage 7, Stage 8 closed, execution/live authority false. No provider calls, approval receipts, gateway changes, parent policy edits, UI or MotionKit. Source snapshots must use one captured commit and reject dirty governing sources. Planner must reject unknown inputs and unsafe policy, union mandatory reviewers with reasons, preserve mode risk floors and mandatory applicable Workshop clearances. Host and CLI expose planning only. Post-change evidence review is required before adoption; draft PR only, no merge.

Risks: local files are not authenticated approvals; request revision is a supplied binding, not verified Git authority. Reopen for expanded schemas, runtime behavior, authority, UI or parent changes. Baseline P1 Exit Evidence CI is failing and is not evidence against or for this slice.
