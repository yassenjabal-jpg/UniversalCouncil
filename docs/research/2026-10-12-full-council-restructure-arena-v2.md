# Universal Council — Full Restructuring ARENA v2
Date: 2026-10-12
Status: PROVISIONAL_V0_4_PLUS — BAKE_OFF_REQUIRED
Mode: ARENA+
Decision Owner: Owner
Driver: Chair / Decision Controller
Source-of-truth preflight: PASS
Source main SHA at meeting start: 418fdc5f6e06bbad5f8db223941119b72b537784

## Honesty boundary
This is a structured Council deliberation executed inside one ChatGPT session using the Council's role contracts. It records independent role positions before cross-objection, but it does not pretend that all roles are already separate autonomous model processes. One purpose of the restructure is to make future role execution measurable and, where justified, independently instantiated.

## Why the meeting was reopened
The previous ARENA was materially changed by new verified capabilities:
- Capability Evidence Sync is now merged into UniversalCouncil.
- Council Preflight now imports bounded evidence receipts before material sessions.
- YASSIN Control Bridge is formally registered as:
  - desktop_computer_use.observe
  - desktop_computer_use.control
- Observe and Control are separately governed.
- CouncilVideoStudio now publishes a standardized capability receipt.
- UniversalCouncil verifies the receipt without allowing the subproject to grant itself authority.
- The Council can now observe and interact with full Windows applications, not only APIs, connectors and shell commands.

This changes the feasible organization. The Council is no longer only a deliberation layer with API tools; it can become a governed system that reasons, observes a real desktop, executes work in applications, verifies the result and turns successful one-off actions into reusable automation.

## Governing question
What Council structure best exploits full desktop Computer Use, APIs, connectors, shell/code and specialist reasoning while minimizing duplicated roles, accidental actions, stale evidence, permission sprawl, token/latency waste and human approval fatigue?

## Preflight evidence
Council Preflight returned:
- COUNCIL_PREFLIGHT_OK
- approved receipt imported: CouncilVideoStudio / desktop_computer_use
- unavailable_sources: []
- registry_changed: false

The Council therefore begins this meeting with the current central registry synchronized to the verified local capability.

## External research delta

### Multi-agent orchestration
- OpenAI Agents SDK supports specialists, tools, orchestration/handoffs, tracing, evals and human review.
- OpenAI Computer Use guidance emphasizes restricted environments, untrusted screen content, consequential-action confirmation, bounded runs and outcome verification.
- Microsoft Agent Framework 1.0 provides sequential, concurrent, handoff, group-chat and Magentic orchestration, checkpoints, human-in-the-loop and OpenTelemetry support.
- Microsoft explicitly recommends using deterministic functions/workflows rather than agents when the task can be reliably expressed as code.

### Desktop automation
- Microsoft UI Automation provides programmatic semantic access to most desktop UI elements.
- Power Automate Desktop uses UIA selectors, desktop flows, recorder support and has introduced AI-assisted selector repair and video logs.
- UiPath Delegate public preview demonstrates a general-purpose governed desktop AI agent with routines, approvals, permissions and audit controls.
- These tools support a strong pattern: use adaptive Computer Use for uncertain work, then promote stable repetitive work into deterministic routines.

### Agent system design
- Anthropic recommends simple composable workflows before complex autonomous systems.
- Anthropic's 2026 managed-agent architecture separates the "brain" from "hands" and durable session state, allowing each to fail or change independently.
- Recent multi-agent debate research warns that debate is not automatically superior to budget-matched sampling; redundant personas add cost and can reduce quality.
- Debate value is strongest when participants have truly distinct evidence, authority or failure lenses.

### Observability
- OpenTelemetry now has GenAI semantic conventions suitable for model/tool/token traces.
- DORA warns against treating raw token usage as productivity; outcome, rework, stability and verification overhead matter more.

## Meeting mechanism
The meeting used seven rounds:
1. independent first positions;
2. Computer Use impact review;
3. tool/method scouting;
4. cross-objection;
5. authority and safety red-team;
6. candidate architecture comparison;
7. forced recommendation with dissent preserved.

Every role must state:
- objection to the current structure;
- proposal;
- effect of Computer Use on its function;
- tool/method worth testing;
- structural vote.

# ROUND 1 — UNIVERSAL CORE

## Chair / Decision Controller
Objection:
The Chair still owns framing, routing and synthesis while Synthesis exists separately, creating two places where convergence can be shaped.

Proposal:
Merge the runtime seats into Decision Orchestrator. Keep synthesis as a required protocol stage, not a separate persistent speaker.

Computer Use impact:
The Orchestrator must never directly own the physical desktop "hand." It authorizes routing to an execution layer but should not both choose and execute consequential actions.

Tool/method:
Manager-agent / agent-as-tool orchestration; durable decision records; action-risk classification.

Vote:
MERGE Chair + Synthesis runtime seats.

## Evidence & Research Lead
Objection:
Evidence Sync solved one stale-capability failure, but ordinary GUI actions can still create unrecorded facts.

Proposal:
Require evidence receipts for material capability proofs and verified-action receipts for material desktop operations.

Computer Use impact:
Observation gives Evidence direct access to visible application state, but visible text remains untrusted data and cannot grant authority.

Tool/method:
Screenshot + semantic UI state + before/after diff + source commit + receipt IDs.

Vote:
KEEP INDEPENDENT; expand into Evidence & Verification.

## Red Team / Devil's Advocate
Objection:
A more capable desktop agent increases blast radius and creates new classes of mistaken action.

Proposal:
Red Team does not approve individual normal actions; instead it defines adversarial test suites, prompt-injection cases, stale-selector cases, wrong-window cases and rollback tests.

Computer Use impact:
Screen content can contain malicious or misleading instructions. Any instruction discovered on screen must be treated as untrusted unless it matches the Owner/Decision contract.

Tool/method:
Computer-use adversarial evals, injected UI text, wrong-focus tests, permission-boundary tests.

Vote:
KEEP INDEPENDENT; make contribution measurable.

## Practicality & Execution Reviewer
Objection:
Feasibility review still overlaps Product/Delivery Operator.

Proposal:
Own feasibility and execution-path selection; operators own actual implementation.

Computer Use impact:
Feasibility must choose among API, script, RPA, semantic UIA, visual computer use and raw physical input based on reliability and cost.

Tool/method:
Execution-path ladder and routine graduation.

Vote:
KEEP CORE, absorb governance-side Product/Delivery review.

## Risk & Consequence Analyst
Objection:
Risk and company Assurance still duplicate one another.

Proposal:
Merge into Risk & Assurance with separate security/legal escalation.

Computer Use impact:
Introduce action-risk tiers and blast-radius controls rather than asking for approval on every click.

Tool/method:
Containment, least privilege, allowlisted windows/processes, bounded actions, checkpoints.

Vote:
MERGE with Assurance.

## Human / User Advocate
Objection:
More autonomy can simply move workload from execution to constant approval prompts.

Proposal:
Measure approval fatigue, interruption rate and recovery burden; prefer fewer high-value approvals over hundreds of trivial prompts.

Computer Use impact:
Build visible current-state/next-action/stop controls so the Owner can intervene without reading logs.

Tool/method:
Human-in-the-loop at consequential boundaries, not every micro-action; operator dashboard.

Vote:
KEEP INDEPENDENT.

## Cost-Benefit & Value Analyst
Objection:
Agent frameworks, RPA suites and observability products can create tooling spend and meta-work without value.

Proposal:
Require economic comparison against current bridge and simple Python automation.

Computer Use impact:
Successful repeated GUI work should become cheaper deterministic automation when possible.

Tool/method:
Cost per completed task, verification cost, recovery cost, human-minutes saved.

Vote:
KEEP INDEPENDENT.

## Synthesis & Alternatives Designer
Objection:
Separate persistent seat duplicates Chair and increases anchoring risk.

Proposal:
Remain a required synthesis protocol that preserves minority positions and produces serious alternatives.

Computer Use impact:
Synthesis should combine decision evidence, not raw screenshots or action logs.

Tool/method:
Structured final decision record with dissent and reopen triggers.

Vote:
MERGE runtime seat into Decision Orchestrator; KEEP protocol.

# ROUND 2 — SPECIALIST FEDERATION

## Health & Medicine Specialist
Objection:
No value in permanent activation for general automation.
Proposal:
On-demand only; block consequential health actions without domain evidence.
Computer Use impact:
Can inspect health applications only when explicitly authorized; no silent entry/submission of sensitive health data.
Tool/method:
Read-only observation first, human confirmation before transmission.
Vote:
KEEP ON_DEMAND.

## Software & Systems Specialist
Objection:
Architecture judgment and Technical Operator execution are still conflated in practice.
Proposal:
Software judges architecture; Technical Operator executes.
Computer Use impact:
GUI automation should be wrapped behind stable execution interfaces; do not let code depend directly on pixel positions when semantic controls exist.
Tool/method:
Adapter pattern, AGENTS.md/path instructions, contract tests.
Vote:
KEEP ON_DEMAND with architecture authority.

## Cybersecurity & Privacy Specialist
Objection:
Desktop control plus screenshots expands attack surface and privacy exposure.
Proposal:
Mandatory security review for new control backends, credential paths, privilege elevation, external transmission and broad window access.
Computer Use impact:
Require process/window allowlists, credential isolation, screen-content distrust and egress controls.
Tool/method:
OWASP agentic security, sandboxing, vault/proxy credentials, blast-radius tests.
Vote:
KEEP ON_DEMAND with blocker authority.

## Finance & Accounting Specialist
Objection:
Visual reading of numbers is not a financial source of truth.
Proposal:
Computer Use may collect or enter values, but reconciliation and arithmetic remain deterministic.
Computer Use impact:
Before any financial write, compare target account, amount, currency and expected post-state.
Tool/method:
Double-entry/reconciliation checks and typed action receipts.
Vote:
KEEP ON_DEMAND with blocker authority.

## Business & Operations Specialist
Objection:
The Council risks automating inefficient processes.
Proposal:
Map and simplify the process before automating it.
Computer Use impact:
Use screen observation to study real workflows and identify unnecessary steps before building automation.
Tool/method:
Process mining/lightweight task mining; observed-workflow maps.
Vote:
KEEP ON_DEMAND.

## Product & Purchasing Specialist
Objection:
Tool enthusiasm can drive unnecessary product adoption.
Proposal:
Compare current bridge, Power Automate Desktop, UiPath and native APIs against real use cases.
Computer Use impact:
Desktop access reduces need for some connectors, but does not eliminate the value of safer APIs.
Tool/method:
Weighted tool scorecard: reliability, reversibility, cost, maintenance, permissions.
Vote:
KEEP ON_DEMAND.

## Science & Research Methods Specialist
Objection:
The planned bake-off can be biased if cases are selected after architecture choices.
Proposal:
Freeze evaluation cases and scoring before running candidates.
Computer Use impact:
Desktop tasks need repeatable initial states and objective pass/fail checks.
Tool/method:
Pre-registered eval set, randomized case order, confidence intervals where meaningful.
Vote:
KEEP ON_DEMAND, mandatory for bake-off design.

## Legal & Regulatory Specialist
Objection:
GUI capability can make external submissions that have legal effect.
Proposal:
Classify contracts, filings, acceptance of terms and account changes as consequential actions.
Computer Use impact:
No autonomous agreement acceptance or legally binding submission.
Tool/method:
Action taxonomy and jurisdiction-aware confirmation.
Vote:
KEEP ON_DEMAND with blocker authority.

## Education & Learning Specialist
Objection:
No permanent role value.
Proposal:
Remain routed.
Computer Use impact:
Can observe educational tools and create practice workflows but cannot change institutional records without authorization.
Tool/method:
Task decomposition and learning-outcome evaluation.
Vote:
KEEP ON_DEMAND.

## Media & Content Specialist
Objection:
Generic Media role overlaps venture Showrunner.
Proposal:
Own media-domain research and routing; Showrunner owns an approved production.
Computer Use impact:
Can inspect references and application state; production hands belong to the media execution cell.
Tool/method:
Reference boards, competitive packaging analysis, editorial rubric.
Vote:
KEEP ON_DEMAND, narrow scope.

## Design & UX Specialist
Objection:
Automation can be technically successful while visually wrong.
Proposal:
Own visual verification criteria for UI/design tasks.
Computer Use impact:
Screenshot evidence becomes a first-class design artifact; semantic state alone is insufficient for layout.
Tool/method:
Figma, screenshot diff, task-success heuristics.
Vote:
KEEP ON_DEMAND.

## Travel & Local Planning Specialist
Objection:
No permanent governance value.
Proposal:
Remain routed.
Computer Use impact:
May use booking/travel UIs for observation only until external-purchase authority exists.
Tool/method:
Current web/local search and confirmation boundaries.
Vote:
KEEP ON_DEMAND.

## Data & Statistics Specialist
Objection:
Role Contribution Ledger can become vanity metrics.
Proposal:
Define metrics that correlate with decision quality and later outcomes.
Computer Use impact:
Measure UI task success, accidental action rate, recovery and verification—not click count.
Tool/method:
Eval datasets, calibration, failure taxonomy.
Vote:
KEEP ON_DEMAND, mandatory for metric design.

## Career & Work Specialist
Objection:
No permanent role value.
Proposal:
Remain routed.
Computer Use impact:
Can assist with job systems, but applications/submissions remain consequential external actions.
Tool/method:
Read-only research and user-confirmed submissions.
Vote:
KEEP ON_DEMAND.

## Customer Skeptic
Objection:
Computer Use can make a weak business feel operationally impressive without proving customer demand.
Proposal:
Continue forcing do-nothing/free-alternative comparison.
Computer Use impact:
Automation speed is not customer value.
Tool/method:
Commitment evidence and actual willingness-to-pay tests.
Vote:
KEEP mandatory in commercial gates.

## Commoditization & Moat Auditor
Objection:
GUI automation itself is rapidly commoditizing.
Proposal:
Do not treat YASSIN bridge as a moat; value lies in governance, evidence, domain workflows and accumulated routines.
Computer Use impact:
As platform-native computer use improves, custom bridge code may become replaceable.
Tool/method:
Foundation Model Uplift test; replaceability review every Pulse cycle.
Vote:
KEEP mandatory in commercial gates.

# ROUND 3 — COMPANY OPERATING LAYER

## Board
Objection:
Duplicates Universal Council.
Proposal:
Remove as a separate operational function.
Computer Use impact:
None; Board must not become a second approval queue.
Tool/method:
Single authority chain.
Vote:
REMOVE DUPLICATE FUNCTION.

## Venture Operator
Objection:
Cannot be an independent judge of work it owns.
Proposal:
Remain Driver/WIP owner.
Computer Use impact:
May request and use bounded desktop actions under execution policy.
Tool/method:
Linear milestones, acceptance receipts.
Vote:
KEEP OPERATOR, not default Council judge.

## Commercial Operator
Objection:
Automation increases outreach capacity before demand/channel quality is proven.
Proposal:
Operate only after commercial gates.
Computer Use impact:
No external send/publish authority by default even if desktop UI can technically perform it.
Tool/method:
Channel experiments with explicit owner grants.
Vote:
KEEP OPERATOR.

## Product & Delivery Operator
Objection:
Governance voice duplicates Execution Reviewer.
Proposal:
Keep implementation ownership only.
Computer Use impact:
Can convert approved workflows into deterministic routines.
Tool/method:
DORA flow metrics, small batches, acceptance tests.
Vote:
REMOVE as independent Council voice; KEEP execution capability.

## Finance Controller
Objection:
Should not attend every meeting.
Proposal:
Activate on financial exposure and budget controls.
Computer Use impact:
Any financial desktop write requires deterministic verification and owner policy.
Tool/method:
Budget gates, ledger reconciliation.
Vote:
KEEP CONTROL FUNCTION.

## Assurance Reviewer
Objection:
Duplicates Risk core role.
Proposal:
Merge governance seat into Risk & Assurance.
Computer Use impact:
Audit receipts become its execution evidence.
Tool/method:
Control tests, random receipt sampling.
Vote:
MERGE.

## Technical Operator
Objection:
Becoming the only holder of "the hands" could make this role too powerful.
Proposal:
Technical Operator manages execution infrastructure, but actual control authority is enforced mechanically by an Action Broker and policy engine.
Computer Use impact:
Own bridge reliability, not unilateral action authority.
Tool/method:
Control lease, adapters, health checks, rollback and selector repair.
Vote:
KEEP OPERATOR; reduce discretionary authority.

## HR & Capability Director
Objection:
Capability scouting can become tool-churn.
Proposal:
Evaluate role ROI and tool candidates only against measured gaps.
Computer Use impact:
Desktop observation can reveal real unused/duplicated tools and manual toil.
Tool/method:
Role Contribution Ledger + Capability Registry + tool deprecation review.
Vote:
KEEP META-ROLE.

## Domain Specialists coordinator
Objection:
Generic role duplicates the actual federation.
Proposal:
Replace with deterministic Specialist Router.
Computer Use impact:
Router also decides whether specialist gets observation only, not control.
Tool/method:
Domain signals + materiality + blocker map + tool profile.
Vote:
REPLACE ROLE WITH MECHANISM.

# ROUND 4 — MEDIA VENTURE CELL

## Editorial Director / Showrunner
Objection:
Computer Use may tempt automation to overrule editorial judgment.
Proposal:
Maintain explicit editorial approval for story, pacing and final cut.
Computer Use impact:
Can inspect After Effects/Premiere state and request edits, but not replace editorial authority.
Tool/method:
Storyboard-to-cut acceptance rubric.
Vote:
KEEP VENTURE-SCOPED.

## AI Visual & Post-Production Producer
Objection:
Current bridge proves After Effects motion assembly, not complete post-production.
Proposal:
Create application profiles and routines for After Effects, Premiere and audio paths one at a time.
Computer Use impact:
This role benefits most from full desktop execution.
Tool/method:
Native scripts first, UIA second, vision third; save successful routines.
Vote:
KEEP VENTURE-SCOPED.

## Audience Growth & Packaging Operator
Objection:
No value in permanent activation before publishing/analytics exist.
Proposal:
Remain on demand.
Computer Use impact:
Can prepare titles/thumbnails and inspect analytics when available; publishing remains separate authority.
Tool/method:
vidIQ/analytics, packaging tests, retention evidence.
Vote:
KEEP ON_DEMAND.

# ROUND 5 — COMPUTER USE AUTHORITY DEBATE

## Debate A — Should specialists directly control the desktop?
Decision: NO by default.

Reason:
Expertise does not imply execution authority. Specialists may request observations and proposed actions. The Execution Fabric decides allowed tools and the Action Broker performs authorized actions.

Exception:
A venture-scoped operator may receive bounded control authority for a defined task profile.

## Debate B — Should every state-changing GUI action require Owner approval?
Decision: NO.

Reason:
Approval fatigue reduces meaningful supervision. Recent agent-safety work shows repeated permission prompts can become ineffective.

Replacement:
Action-risk tiers with approvals at meaningful boundaries.

## Debate C — Should Computer Use replace APIs/connectors?
Decision: NO.

Reason:
GUI is more general but less stable and harder to verify. Native APIs and deterministic scripts remain preferred when equivalent.

## Debate D — Should raw mouse coordinates remain available?
Decision: YES, but last-resort only.

Reason:
Some applications expose poor semantic accessibility. Coordinate input preserves reach but must be bounded by screenshot verification and target-window checks.

## Debate E — Should successful GUI workflows remain agentic forever?
Decision: NO.

Reason:
Repeated successful workflows should graduate into deterministic routines to reduce cost, latency and variance.

# ROUND 6 — EXECUTION FABRIC CANDIDATE

The previous Layered v0.4 proposal is upgraded to v0.4+ with a new non-human, non-member execution substrate.

## Layer 0 — Owner
Final authority for consequential actions and governance changes.

## Layer 1 — Decision Orchestrator
Merged Chair + Synthesis runtime seat.
Owns:
- framing;
- routing;
- mode;
- convergence;
- final decision record;
- dissent preservation.
Does not own:
- physical control;
- evidence self-certification;
- domain blocker override.

## Layer 2 — Core Challenge Council
1. Evidence & Verification
2. Red Team / Falsification
3. Execution & Feasibility
4. Risk & Assurance
5. Human & Adoption
6. Value & Economics

These remain independent because each answers a materially different question.

## Layer 3 — Specialist Federation
16 current specialist roles remain callable.
Activation is routed, not permanent.
Domain blocker authority applies only inside evidence-backed scope.

## Layer 4 — Execution Fabric
This is a mechanism, not a Council member.

### 4.1 Capability Router
Chooses:
API/connector → deterministic script/CLI → reusable routine/RPA → semantic UIA → visual Computer Use → raw coordinates.

### 4.2 Observer
Collects:
- windows;
- UI elements;
- values/properties;
- screenshots;
- visible state.
Observation does not grant action authority.

### 4.3 Action Planner
Transforms an approved task into bounded candidate actions.
Cannot execute directly.

### 4.4 Policy / Risk Gate
Classifies action tier, allowed process/window, data sensitivity, reversibility and external side effects.

### 4.5 Desktop Control Lease
Exactly one active physical controller at a time.
Multiple observers may exist.
Prevents two agents from fighting over focus, pointer or keyboard.

### 4.6 Action Broker
The only component allowed to invoke state-changing computer-use actions.
It receives approved structured actions, not open-ended role prose.

### 4.7 Verifier
Checks actual post-state semantically and visually.
Failure to verify means task state is UNKNOWN, not success.

### 4.8 Evidence Recorder
Writes action receipts:
- task/decision id;
- actor/requester;
- chosen execution path;
- target process/window;
- before state;
- action;
- after state;
- verification result;
- source artifacts;
- timestamps.

### 4.9 Routine Registry
Stores workflows that have graduated from exploratory Computer Use into reusable automation.

## Layer 5 — Operators
- Venture Operator
- Commercial Operator
- Product/Delivery execution capability
- Technical Operator
- Finance Controller

Operators may request execution but do not self-certify success.

## Layer 6 — Venture Cells
Media, RevenueSystem and future cells.
Each has domain-specific app profiles and acceptance checks.

## Layer 7 — Meta-governance
- HR & Capability Director
- Capability Scout
- Role Contribution Ledger
- Council Pulse
- Evidence Sync

# ACTION RISK TIERS

## T0 — Observe
Examples:
screenshot, inspect UI, read value, list windows.
Default:
read authority only.

## T1 — Local reversible navigation
Examples:
open app, change tab, focus field, scroll.
Default:
bounded operator authority after task approval.

## T2 — Local state change
Examples:
edit/save project file, rename local artifact, modify a local draft.
Default:
allowed only under app profile + before/after verification + rollback/backup when material.

## T3 — External consequential action
Examples:
send message, publish, submit form, account change, financial transaction, irreversible delete, legal acceptance.
Default:
explicit Owner confirmation at the consequential boundary.

## T4 — Prohibited or separately governed
Examples:
credential/password capture, security bypass, hidden credential entry, permission widening outside approved policy.
Default:
blocked unless a separately approved architecture changes the governing policy.

# AUTOMATION GRADUATION LADDER

## Stage A — Exploratory
Use flexible agentic Computer Use.
Goal:
understand task and UI.

## Stage B — Verified repeat
Run successfully multiple times with receipts.
Goal:
prove stable target state and selectors.

## Stage C — Structured routine
Extract stable semantic selectors, app scripts or deterministic steps.
Goal:
reduce model decisions.

## Stage D — Deterministic automation
Prefer native API/script/RPA where practical.
Goal:
lower variance, latency and token use.

## Stage E — Monitored production routine
Add health checks, failure classification, version/change detection, rollback and metrics.

Promotion rule:
Do not leave repetitive stable work in expensive open-ended Computer Use just because it works.

Demotion rule:
If UI drift breaks the routine, fall back to agentic Computer Use for diagnosis and repair, then regenerate the routine.

# TOOL / PROGRAM SCOUTING RESULTS

## OpenAI Agents SDK / Agents API
Finding:
Strong candidate for manager + specialists, tracing, evals, guardrails/human review and computer-use integration.

New 2026 relevance:
OpenAI's platform now exposes first-class Computer Use and recent multi-agent capabilities.

Council view:
KEEP AS BAKE-OFF CANDIDATE.
Do not couple governance to provider-specific APIs until it wins measured tests.

## Microsoft Agent Framework 1.0
Finding:
Strong fit for explicit workflows, handoffs, group chat, checkpoints, HITL and OpenTelemetry.

Council view:
KEEP AS BAKE-OFF CANDIDATE.
Particularly strong for recoverable workflows and C#/.NET integration.

## Current deterministic Python Council
Finding:
Lowest abstraction, already tested, easy to audit.
Weakness:
roles remain structured perspectives unless separately instantiated.

Council view:
KEEP AS BASELINE AND FALLBACK.

## Power Automate Desktop
Finding:
Useful benchmark/backend for stable Windows routines:
- UIA selectors;
- recorder;
- desktop flows;
- AI-assisted selector repair;
- versioning/video-log improvements.

Council view:
PILOT AS ROUTINE BACKEND CANDIDATE, not as Council brain.
Do not adopt until compared with existing YASSIN bridge on real repeated tasks.

## UiPath Delegate / UiPath automation
Finding:
Useful design reference for governed desktop AI:
- computer use;
- reusable routines;
- permissions;
- approvals;
- audit controls.

Council view:
BENCHMARK ARCHITECTURE, do not install/adopt by default due overlap/complexity until measured need exists.

## OpenTelemetry
Finding:
Provider-neutral trace schema for GenAI/tool operations.

Council view:
ADOPT AS OBSERVABILITY INTERFACE CANDIDATE before selecting Datadog or another backend.

## Datadog plugin
Finding:
Available but not installed.

Council view:
DEFER.
First produce useful local traces/metrics. Install an external observability backend only when trace volume and operational need justify it.

## TinyFish
Finding:
Already installed; useful for browser workflows.

Council view:
KEEP for browser-specific tasks.
Do not use it as a substitute for governed Windows desktop control.

## Superpowers
Finding:
Installed and useful for planning/TDD/debugging.

Council view:
KEEP; route through technical workflows.

# ROUND 7 — CROSS-OBJECTIONS

## Red Team vs Execution Fabric
Objection:
A polished Action Broker could become a single point of dangerous power.

Resolution:
Policy is deny-by-default; action tiers, app profiles, target checks, control lease and verification are independent gates.

## Human Advocate vs approvals
Objection:
Too many confirmations make users approve reflexively.

Resolution:
Approve boundaries, not clicks. T0/T1 can run inside an approved task; T3 requires explicit confirmation.

## Security vs screenshot evidence
Objection:
Screenshots can capture unrelated private data.

Resolution:
Prefer app/window-scoped capture, process allowlists and minimal evidence retention. Full-screen capture is exception, not default.

## Evidence vs vision
Objection:
A screenshot can be ambiguous.

Resolution:
Prefer semantic state plus screenshot. Vision alone is weaker evidence when machine-readable state exists.

## Technical Operator vs Power Automate
Objection:
Adding PAD duplicates YASSIN Control Bridge.

Resolution:
No adoption now. Test only as a routine backend on tasks where selector repair/recording/versioning may lower maintenance.

## Value vs framework bake-off
Objection:
Running many frameworks can become meta-work.

Resolution:
Freeze a small benchmark set and terminate candidates early if they cannot beat baseline on reliability/recovery.

## Science vs multi-agent debate
Objection:
More roles do not imply better results; recent studies show debate can lose to matched-budget sampling.

Resolution:
Role Contribution Ledger becomes a removal mechanism. Every persistent role must prove unique decision value.

## Moat Auditor vs custom bridge
Objection:
Platform-native Computer Use may overtake custom UI code.

Resolution:
Design Execution Fabric around stable interfaces so the hand can be swapped without changing Council governance.

# SELECTED CANDIDATE — COUNCIL v0.4+ EXECUTION FABRIC

Status:
SELECTED_FOR_BAKE_OFF, not yet governing.

Key differences from previous v0.4 candidate:
1. Computer Use is now central architecture, not merely a tool.
2. Brain, session/evidence and hands are explicitly separated.
3. Observe and Control are different authorities.
4. One controller holds the desktop lease.
5. Execution success requires independent verification.
6. Repeated GUI workflows must graduate into deterministic routines.
7. App profiles and action-risk tiers replace blanket per-click approvals.
8. Screen content is explicitly untrusted input.
9. OpenTelemetry becomes the preferred observability interface candidate.
10. Power Automate Desktop is added as a routine-backend benchmark.
11. UiPath Delegate is treated as an architecture reference, not an automatic dependency.
12. Debate itself must prove ROI against simpler sampling/independent review.

# REVISED BAKE-OFF

## Candidates
A. Current deterministic Council v0.3 + existing tools.
B. v0.4+ logic on current Python harness + Execution Fabric prototype.
C. OpenAI Agents SDK orchestration + same Execution Fabric interfaces.
D. Microsoft Agent Framework orchestration + same Execution Fabric interfaces.

Power Automate Desktop is evaluated separately as an execution/routine backend, not as an orchestration candidate.

## Evaluation corpus
Freeze before execution:
- 12 historical Council decisions with later evidence.
- 6 software/repository tasks.
- 6 Windows desktop tasks.
- 4 media/After Effects tasks.
- 4 injected-failure tasks.
- 4 security/prompt-injection desktop tasks.

## Desktop task requirements
At least:
- inspect an application without changing state;
- perform a reversible local change;
- save and verify a project artifact;
- recover from stale selector/UI movement;
- handle wrong-window focus;
- detect malicious instruction visible on screen;
- refuse/route a consequential external action;
- survive controller restart using durable state.

## Metrics
Decision:
- correctness;
- evidence quality;
- dissent preservation;
- blocker precision/recall;
- human override.

Execution:
- task success;
- verified success;
- accidental action rate;
- unknown-result rate;
- recovery success;
- selector robustness;
- wrong-window prevention;
- rollback success.

Efficiency:
- wall-clock latency;
- token/model cost;
- human attention minutes;
- approval count;
- repeated work converted to routine;
- rework.

Governance:
- authority violations;
- permission escalation attempts;
- untrusted-screen instruction compliance;
- evidence freshness;
- audit completeness.

## Kill criteria
Reject a candidate if:
- it increases authority violations;
- it cannot resume safely after interruption;
- it cannot preserve a single-controller desktop lease;
- it falsely reports success without post-state verification;
- it is materially slower/costlier without measurable quality or recovery improvement;
- it requires role proliferation without unique contribution;
- it couples governance to one execution hand so tightly that the hand cannot be replaced.

# ROLE RESTRUCTURE RECOMMENDATION AFTER v2

## Persistent runtime Council
- Decision Orchestrator
- Evidence & Verification
- Red Team / Falsification
- Execution & Feasibility
- Risk & Assurance
- Human & Adoption
- Value & Economics

Total persistent runtime seats: 7.

## On-demand specialist federation
Keep all 16 specialist capabilities, with routing and domain blocker rules.

## Operators
Keep operators separate from neutral deliberation:
- Venture
- Commercial
- Technical
- Product/Delivery execution
- Finance control

## Venture cells
Keep media and future domain cells scoped to active projects.

## Mechanisms, not members
Do NOT add permanent roles for:
- Computer Use Agent
- Mouse/Keyboard Agent
- Observability Agent
- Prompt Engineer
- Agent Manager
- Domain Specialists coordinator
- Board duplicate

Represent these needs as Execution Fabric, observability, routing and meta-governance mechanisms.

# MATERIAL DISSENT

Red Team:
Would prefer stricter sandboxing before increasing autonomy on the real YASSIN desktop.

Human Advocate:
Warns that a sophisticated approval system still fails if the user cannot quickly understand what is happening.

Security:
Wants process/window allowlists before any future autonomous T2 desktop actions.

Technical Operator:
Warns against prematurely integrating Power Automate or UiPath when the current bridge can still be hardened.

Value:
Wants the bake-off capped so the Council does not spend more time evaluating frameworks than doing useful work.

Science:
Insists the benchmark and scoring rules be committed before candidates are run.

Media Showrunner:
Rejects any architecture where an orchestration agent can declare a creative edit "approved" based only on technical success.

Moat Auditor:
Expects platform-native computer use to improve quickly, so all custom hand implementations must remain replaceable.

# FINAL MEETING DECISION

Verdict:
PIVOT-RECOMMENDED from "Layered Council v0.4" to "Council v0.4+ with Execution Fabric."

Confidence:
88/100.

Why not 100:
The role restructure is still supported by structured deliberation rather than a real measured multi-runtime bake-off. The new desktop capability is verified, but the proposed Action Broker, desktop lease, app profiles, risk tiers, routine graduation and tracing layer have not yet been implemented or benchmarked.

Immediate next gate:
Build the smallest Execution Fabric prototype and frozen bake-off specification WITHOUT changing the governing role files.

Do not yet:
- replace config/roles.json;
- delete existing roles;
- install Power Automate/UiPath/Datadog;
- grant external publish/send;
- widen credential or security permissions.

Reopen trigger:
The decision must be reopened if the bake-off shows that the existing v0.3 structure outperforms v0.4+, or if one runtime candidate materially improves quality/recovery at acceptable cost.

# External references reviewed

OpenAI:
- https://developers.openai.com/api/docs/guides/agents/sdk
- https://developers.openai.com/api/docs/guides/agents/guardrails-approvals
- https://developers.openai.com/api/docs/guides/tools-computer-use
- https://developers.openai.com/api/docs/changelog

Microsoft:
- https://learn.microsoft.com/agent-framework/overview
- https://learn.microsoft.com/agent-framework/workflows/orchestrations/
- https://learn.microsoft.com/en-us/agent-framework/journey/workflows
- https://learn.microsoft.com/en-us/windows/win32/winauto/entry-uiauto-win32
- https://learn.microsoft.com/en-us/power-automate/desktop-flows/ui-elements
- https://learn.microsoft.com/en-us/power-platform/released-versions/power-automate-desktop/2607

UiPath:
- https://docs.uipath.com/delegate/standalone/latest/release-notes/august-2026
- https://www.uipath.com/ai/what-is-computer-use

Anthropic:
- https://www.anthropic.com/engineering/building-effective-agents
- https://www.anthropic.com/engineering/managed-agents
- https://www.anthropic.com/engineering/how-we-contain-claude
- https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

Observability / delivery:
- https://opentelemetry.io/blog/2026/genai-observability/
- https://dora.dev/insights/

Research:
- https://arxiv.org/abs/2601.19921
- https://arxiv.org/abs/2609.35875
- https://arxiv.org/abs/2609.00683
- https://arxiv.org/abs/2607.26212
