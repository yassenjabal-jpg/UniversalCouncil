# Command Center Context Drift Prevention Contract
Date: 2026-10-20
Status: OWNER-ADOPTED / BLOCKING QUALITY CONTRACT
Scope: all Command Center implementation, design, orchestration and generated artifacts

## 1. Problem
The primary systemic failure mode is not only tool failure. It is context drift: work remains technically competent while gradually departing from the Owner-approved target.

Examples include visual direction drifting away from approved references, downstream stages silently repairing upstream decisions, models using stale project assumptions, and generated outputs becoming de facto truth.

This contract makes drift a detectable build/runtime failure.

## 2. Principle
Do not ask a model to "remember the project correctly".

Instead:
PIN TRUTH -> COMPILE CONTEXT -> EXECUTE BOUNDED CHANGE -> VERIFY AGAINST PINNED TRUTH -> FAIL CLOSED ON DRIFT.

## 3. Immutable Context Capsule
Every material Job receives a Context Capsule created before execution.

A capsule contains:
- project id;
- source branch + exact SHA;
- checkpoint/lock id;
- owner directives;
- canonical artifact ids/hashes;
- canonical decision ids/hashes;
- approved reference set ids/hashes;
- allowed scope;
- explicit forbidden directions;
- required Skill/version;
- authority/risk policy version;
- expected outputs;
- acceptance tests;
- expiry/freshness rules.

The capsule is immutable for that Job.

If canonical truth changes during execution, the Job does not silently absorb the new state. It pauses as STALE_CONTEXT and must be replanned from a new capsule.

## 4. Canonical source hierarchy
For every Job the hierarchy is explicit:

1. exact repository/asset sources pinned in the capsule;
2. owner directives;
3. locked contracts and machine-readable policy;
4. accepted canonical artifacts;
5. current stage plan;
6. working drafts;
7. conversation context.

Lower levels may not override higher levels.

## 5. Canonical/Working/Output firewall
- SOURCE may be promoted to CANONICAL only through an acceptance gate.
- WORKING is never canonical.
- OUTPUT is never canonical by default.
- model summaries are derived views, never primary truth.
- generated images/prompts cannot alter the visual reference set.
- downstream artifacts cannot rewrite upstream locked artifacts.

Any promotion records provenance, reviewer, source hashes and reason.

## 6. Scope Freeze
Before execution, a typed Change Envelope states:
- what may change;
- what must not change;
- files/components/screens in scope;
- non-goals;
- acceptance criteria.

An executor cannot expand scope by interpretation.
A needed out-of-scope fix generates a Return Ticket or Change Request.

## 7. Plan-before-mutation
No material mutation begins from a free-form prompt.

Required sequence:
Request
-> Context Capsule
-> typed Plan
-> Plan validation
-> execution.

The Plan records expected touched surfaces and verification for each step.

Unplanned mutation is a blocking violation.

## 8. Delta-only implementation
Default rule:
make the smallest bounded delta necessary to satisfy the current contract.

Large opportunistic refactors, visual reinterpretations or architecture rewrites are forbidden unless explicitly in scope.

This reduces hidden assumption drift.

## 9. Machine-readable invariants
Critical product truths are duplicated as machine-readable invariants that CI/runtime can validate.

Examples:
- role != model;
- no silent model/tool fallback;
- no direct UI authority bypass;
- UNKNOWN != SUCCEEDED;
- output cannot auto-promote to canonical;
- owner-locked visual reference set cannot be replaced by generated material;
- each material execution has a context capsule and work receipt;
- exact source hashes are recorded;
- downstream locked-stage repair requires Return Ticket.

Human-readable docs alone are insufficient for critical invariants.

## 10. Drift Detection Gate
Each material output is compared against its governing capsule before acceptance.

Drift categories:
- CONTEXT_DRIFT: used wrong/stale source.
- SCOPE_DRIFT: changed something outside envelope.
- POLICY_DRIFT: violated authority/routing rule.
- VISUAL_DRIFT: diverged from locked visual system.
- SEMANTIC_DRIFT: output meaning no longer matches required behavior.
- DEPENDENCY_DRIFT: provider/model/tool/version differs without approved fallback.
- EVIDENCE_DRIFT: success claim exceeds available evidence.

Any material drift returns FAIL/RETURN, never "close enough".

## 11. Visual Direction Lock
Visual work gets a dedicated Visual Context Capsule.

It must contain:
- exact approved reference images;
- hashes/version ids;
- approved art-direction contract;
- semantic design tokens;
- positive characteristics;
- forbidden characteristics;
- screen-specific constraints;
- reference priority/order;
- required comparison views.

Rules:
1. only approved reference assets may define the visual direction;
2. generated experiments are OUTPUT, never reference material;
3. prompt text may explain references but never substitute for them;
4. "similar style" is not an acceptance criterion;
5. output is reviewed side-by-side against the pinned reference set;
6. if a design decision is not supported by the visual contract/reference, it is PROPOSAL, not adopted truth;
7. no later screen may infer a new visual language from a previous generated screen.

Visual acceptance requires:
- structural compliance;
- token compliance;
- forbidden-pattern scan;
- reference-set review;
- UX review;
- exact target-size review where relevant.

This is the direct control intended to prevent repetition of the prior visual-direction failure.

## 12. Two-key review for high-drift work
High-drift domains require two independent gates.

Examples:
- visual identity;
- architecture;
- security/authority;
- irreversible automation;
- commercial release.

For visual/UX:
Studio evaluates coherence/usability.
Murtakaz/Council evaluates contract, truth and scope.

One PASS cannot cancel the other's blocker.

## 13. Adversarial reviewer
For every stage, an independent reviewer receives:
- Context Capsule;
- output/diff;
- acceptance criteria;
- no executor chain-of-thought or persuasive narrative.

The reviewer tries to disprove compliance.

This avoids the same agent both creating and self-approving its interpretation.

## 14. Source-to-output traceability
Every material output must answer:
- Which owner directive authorized this?
- Which canonical source(s) did it use?
- Which Skill/version created it?
- Which model/provider ran?
- Which files/actions changed?
- Which verification proves success?
- Which reviewer accepted it?

If any answer is missing, the artifact is not release-ready.

## 15. Exact-head rule
Validation evidence is valid only for the exact commit/artifact/version under review.

Evidence from an older head cannot clear a newer head.

Any post-validation mutation invalidates the relevant gate.

## 16. No silent repair
A downstream stage discovering an upstream defect must not reinterpret or quietly patch the upstream contract.

It emits a Return Ticket including:
- failing invariant;
- evidence;
- affected downstream work;
- proposed source-stage repair.

The source stage is reopened, fixed, revalidated and relocked.

## 17. Failure is preserved
Failed attempts are retained as evidence.
Do not delete evidence merely to present a clean path.

The system should know which approaches caused drift so they are not rediscovered later.

## 18. Dependency and provider pinning
Critical execution must record:
- provider;
- version;
- model id;
- tool/plugin version;
- important configuration hash.

Fallback requires explicit policy eligibility and is recorded.
Silent replacement is prohibited.

## 19. Bounded context retrieval
The Context Resolver uses the Project Knowledge Map and retrieves only relevant canonical material.

It must not:
- treat all prior chat as equal authority;
- prefer recent generated output over older locked truth;
- inject unrelated project memory;
- merge conflicting canonical facts silently.

Conflicts produce CONTEXT_CONFLICT and stop material execution.

## 20. Owner directives
Owner directives are explicit typed records.

A directive has:
- id;
- text;
- scope;
- date;
- supersedes;
- status;
- affected artifacts.

New directives do not mutate history; they supersede prior records.

## 21. Confidence is not evidence
A model saying "I am confident" carries no acceptance weight.

Acceptance comes from:
contract compliance + evidence + verification + review.

## 22. Phase-size control
Large work is divided into bounded vertical slices.

Each slice must:
- fit one clear contract;
- produce inspectable evidence;
- be independently revertible where feasible;
- have explicit exit gate;
- avoid carrying unresolved drift into the next slice.

This is mandatory specifically because long, broad execution previously produced context loss.

## 23. Stop conditions
Execution must stop rather than improvise when:
- capsule sources are stale or missing;
- two canonical sources conflict;
- required reference is unavailable;
- owner lock is unclear;
- requested change exceeds scope;
- authority is missing;
- provider substitution is not approved;
- postcondition cannot be verified.

Result is BLOCKED / STALE_CONTEXT / UNKNOWN, not an invented success.

## 24. Quality target
Zero error cannot be guaranteed in an AI/software system.

The engineering target is instead:
- prevent undetected error;
- minimize blast radius;
- make drift machine-detectable;
- make every important decision traceable;
- make rollback/review cheap;
- ensure a wrong interpretation cannot silently propagate through later phases.

## 25. Blocking acceptance rule
No Command Center stage may lock unless all applicable anti-drift invariants pass.

A visually attractive or functionally working result cannot override a Context/Authority/Truth failure.
