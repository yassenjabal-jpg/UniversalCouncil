# Universal Council — Full Restructuring ARENA
Date: 2026-10-12
Status: PROVISIONAL_RESTRUCTURE_CANDIDATE — SANDBOX BAKE-OFF REQUIRED
Mode: ARENA
Decision Owner: Owner
Driver: Chair / Decision Controller
Scope: Universal Council + company operating layer + specialist federation + media venture layer

## Honesty boundary
This session uses the Council's current roles as structured independent position contracts inside one ChatGPT execution context. It does not claim that every role is already a physically independent AI process. A core objective of this review is to decide whether and how to implement a measurable multi-agent runtime.

## Trigger
The Council changed materially after v0.3:
- proactive capability scouting and tool-authority governance were added;
- GitHub/Linear/CodeQL/Ruff/coverage hardening was adopted;
- a media venture layer was added;
- CouncilVideoStudio and a verified YASSIN control bridge were created;
- After Effects motion assembly moved to RUNTIME_VERIFIED;
- a real evidence-lag incident occurred: UniversalCouncil still reported video editing as NEEDS_RUNTIME_VERIFICATION after the YASSIN runtime had already produced PASS evidence.

The restructure therefore targets role duplication, stale capability state, runtime measurability, tool routing, execution speed, and decision quality.

## Governing question
What is the smallest Council structure that preserves independent challenge and domain authority while improving speed, measurability, tool use, evidence freshness, and execution reliability?

## External research summary
1. OpenAI Agents SDK distinguishes manager-owned "agents as tools" from handoffs where a specialist owns the next response. It also provides tracing and agent workflow evals.
2. Microsoft Agent Framework provides sequential, concurrent, handoff, group-chat and Magentic orchestration plus checkpoints and human-in-the-loop.
3. Anthropic guidance recommends matching agentic complexity to business value and choosing single-agent, multi-agent, or workflow designs deliberately.
4. Recent multi-agent debate research reports that diversity of initial positions and calibrated confidence matter more than simply increasing agent count; homogeneous debate can preserve errors and majority pressure can suppress corrections.
5. GitHub supports repository-wide, path-specific and AGENTS.md instructions for agentic coding workflows.
6. Google SRE recommends measuring and eliminating repetitive toil rather than staffing repetitive work indefinitely.
7. DORA recommends measuring throughput, instability, rework and developer experience instead of treating process volume as productivity.
8. OWASP agentic guidance recommends minimum necessary tool access and explicit human approval for security-relevant changes.
9. Current practitioner discussions repeatedly report that additional agents can increase latency, token cost and failure surface without clear role boundaries or observability.

## Round 1 — role-by-role independent positions

### Universal Core

#### Chair / Decision Controller
Objection: Chair and Synthesis currently overlap in framing, trade-offs and final output ownership.
Proposal: merge Chair + Synthesis into one Decision Orchestrator while preserving a mechanically required dissent section.
Method/tool found: manager-orchestrator pattern; ADRs for durable decisions.
Position: MERGE Chair and Synthesis as a runtime seat, preserve synthesis as a workflow stage.

#### Evidence & Research Lead
Objection: evidence can become stale after execution changes, as demonstrated by the After Effects capability lag.
Proposal: add an Evidence Sync contract that ingests verified runtime receipts from implementation repositories and timestamps freshness.
Method/tool found: trace/eval records, provenance envelopes, GitHub evidence files and CI assertions.
Position: KEEP independent.

#### Red Team / Devil's Advocate
Objection: mandatory argument rounds can become ritualized and expensive.
Proposal: remain independent but activate deep challenge only on material disagreement, pivotal unknowns or irreversible actions; score whether objections changed tests or decisions.
Method/tool found: diversity-aware, confidence-modulated debate; adaptive stopping.
Position: KEEP independent, instrument contribution.

#### Practicality & Execution Reviewer
Objection: feasibility review overlaps Product & Delivery Operator and Technical Operator.
Proposal: retain one cross-domain Execution & Feasibility reviewer in governance; move product/technical operators to execution-side capabilities.
Method/tool found: DORA flow metrics, SRE toil measurement, checkpointed workflows.
Position: KEEP but absorb governance-side delivery review.

#### Risk & Consequence Analyst
Objection: overlaps strongly with company Assurance Reviewer.
Proposal: merge Risk + Assurance into Risk & Assurance, while security/legal specialists retain domain blocker authority.
Method/tool found: NIST AI RMF, OWASP agentic least privilege.
Position: MERGE with Assurance.

#### Human / User Advocate
Objection: user burden is easy to lose when finance, tooling and execution dominate.
Proposal: remain an independent core lens; add task-success/operator-burden metrics and human-error review.
Method/tool found: DORA DevEx/task-success style measures and explicit HITL gates.
Position: KEEP independent.

#### Cost-Benefit & Value Analyst
Objection: overlaps Commercial Operator and Finance Controller but owns a different question: whether an option is worth doing at all.
Proposal: retain universal decision economics; Finance remains an on-demand accounting/domain blocker and Commercial remains a venture operator.
Method/tool found: per-run usage/cost traces and opportunity-cost accounting.
Position: KEEP independent.

#### Synthesis & Alternatives Designer
Objection: a separate persistent synthesis seat can duplicate the Chair and can anchor later reasoning.
Proposal: cease being a permanent runtime seat; become a mandatory final workflow stage owned by Decision Orchestrator with minority preservation tests.
Method/tool found: manager pattern + structured decision record.
Position: MERGE into Chair as a seat; KEEP as protocol.

### Specialist Federation

#### Health & Medicine Specialist
Objection: should never be permanently activated for non-health work.
Proposal: on-demand only; mandatory for material health decisions.
Method/tool: domain connector/data only when user-authorized; evidence hierarchy preserved.
Position: KEEP as specialist capability.

#### Software & Systems Specialist
Objection: generic technical commentary duplicates Technical Operator when both attend.
Proposal: Software specialist owns architecture judgment; Technical Operator owns execution.
Method/tool: AGENTS.md/path-specific repo instructions, CI, code review agents.
Position: KEEP on demand; separate judgment from execution.

#### Cybersecurity & Privacy Specialist
Objection: security cannot be diluted into generic Risk for credential, permission or agent-tool changes.
Proposal: mandatory domain blocker for auth, credentials, permissions, MCP/tool scopes and external writes.
Method/tool: Codex Security, OWASP Agentic guidance, least-privilege tool allowlists.
Position: KEEP on demand with blocker authority.

#### Finance & Accounting Specialist
Objection: Value analysis cannot replace deterministic accounting.
Proposal: activate only when balances, taxes, payments, budgets or financial controls matter.
Method/tool: deterministic ledger/calculation paths; no LLM arithmetic as source of truth.
Position: KEEP on demand with financial blocker authority.

#### Business & Operations Specialist
Objection: overlaps Venture and Commercial operators if treated as a permanent member.
Proposal: use as analytical specialist for market/workflow/operations; operators execute after decision.
Method/tool: workflow mapping, current-alternative economics, process bottleneck analysis.
Position: KEEP on demand.

#### Product & Purchasing Specialist
Objection: overlaps Human and Value on generic decisions.
Proposal: activate for concrete product comparison, purchasing or product-market design only.
Method/tool: evidence-based comparison and switching-cost analysis.
Position: KEEP on demand.

#### Science & Research Methods Specialist
Objection: Evidence Lead may not detect experimental-design errors.
Proposal: independent specialist for experiments, causal claims and scientific methodology.
Method/tool: preregistration-style hypotheses, falsification criteria, power/uncertainty checks.
Position: KEEP on demand.

#### Legal & Regulatory Specialist
Objection: generic Risk cannot authoritatively interpret current law.
Proposal: on-demand only; mandatory when legal/regulatory exposure is material.
Method/tool: current primary legal sources and jurisdiction-specific verification.
Position: KEEP on demand.

#### Education & Learning Specialist
Objection: no value in routine commercial/software meetings.
Proposal: route only education/learning questions.
Method/tool: learning-science methods and measurable outcomes.
Position: KEEP on demand.

#### Media & Content Specialist
Objection: now overlaps the new media venture cell.
Proposal: become the routing/editorial-domain specialist; production ownership moves to the venture cell.
Method/tool: media research + competitor analysis + packaging evidence.
Position: KEEP on demand, narrow scope.

#### Design & UX Specialist
Objection: Human Advocate catches burden but not visual/interaction craft.
Proposal: on-demand for UI/UX/design; use Figma capability when execution is authorized.
Method/tool: Figma, design-system rules, task-success review.
Position: KEEP on demand.

#### Travel & Local Planning Specialist
Objection: irrelevant to most Council operations.
Proposal: remain purely routed specialist.
Method/tool: current local search/maps/availability.
Position: KEEP on demand.

#### Data & Statistics Specialist
Objection: Evidence quality does not guarantee statistical correctness.
Proposal: on-demand for analysis, metrics, experiments and uncertainty.
Method/tool: deterministic data analysis and explicit confidence/assumption reporting.
Position: KEEP on demand.

#### Career & Work Specialist
Objection: no permanent governance value.
Proposal: remain routed specialist only.
Method/tool: current labor-market evidence and role-specific research.
Position: KEEP on demand.

#### Customer Skeptic
Objection: Commercial Operator is structurally incentivized to make a venture work.
Proposal: preserve an independent buyer-refusal lens for commercial selection, but instantiate it only for commercial gates.
Method/tool: do-nothing/DIY/free-AI/commitment evidence tests.
Position: KEEP as mandatory commercial challenge capability.

#### Commoditization & Moat Auditor
Objection: Customer Skeptic tests purchase resistance, not long-run substitutability.
Proposal: remain separate in high-stakes commercial ARENA; in lighter modes one Commercial Challenger runtime may execute both lenses sequentially.
Method/tool: Foundation Model Uplift Test, switching/accumulating advantage analysis.
Position: KEEP as commercial challenge capability.

### Company Operating Layer

#### Board
Objection: a separate Board function duplicates Universal Council itself.
Proposal: define Universal Council as the Board; remove Board as a second operational function.
Method/tool: one decision record and one authority chain.
Position: REMOVE duplicate function.

#### Venture Operator
Objection: execution owner should not be treated as a neutral reviewer.
Proposal: remain project Driver/WIP owner, provide constraints, but not count as an independent challenge voice.
Method/tool: Linear project state, milestone and WIP tracking.
Position: KEEP as operator, not Council seat.

#### Commercial Operator
Objection: overlaps Business specialist and Value analyst if included universally.
Proposal: activate only for revenue ventures; owns execution of commercial experiments, not final evidence judgment.
Method/tool: Linear experiment tracking, CRM/channel tools only after authority gates.
Position: KEEP as venture operator.

#### Product & Delivery Operator
Objection: duplicates governance Execution Reviewer.
Proposal: merge governance judgment into Execution & Feasibility; keep Product & Delivery as implementation owner only when a venture reaches execution.
Method/tool: DORA metrics, small-batch delivery, acceptance gates.
Position: REMOVE as separate Council voice; KEEP operational capability.

#### Finance Controller
Objection: duplicates Value in deliberation but has unique accounting authority.
Proposal: classify as domain-control function called on material financial actions; do not activate in every meeting.
Method/tool: deterministic budgets/ledger, reconciliation, spend gates.
Position: KEEP as control function, not permanent Council voice.

#### Assurance Reviewer
Objection: substantial overlap with Risk & Consequence Analyst.
Proposal: merge governance seat into Risk & Assurance; preserve specialized security/legal escalation.
Method/tool: NIST/OWASP control framework.
Position: MERGE.

#### Technical Operator
Objection: technical executor and architecture judge should not be the same voice.
Proposal: owns tool/runtime execution, automation and rollback; Software/Security specialists judge design and safety.
Method/tool: GitHub/CI, Remote Desktop Commander, capability registry.
Position: KEEP as operator, not deliberation seat.

#### HR & Capability Director
Objection: attending every decision would create meta-governance overhead.
Proposal: remain a meta-controller activated by capability gaps, role-performance review, scheduled Pulse or restructuring.
Method/tool: capability scouting registry, plugin directory, role contribution metrics.
Position: KEEP meta-role, not default Council seat.

#### Domain Specialists coordinator
Objection: a generic "Domain Specialists" function duplicates the actual specialist federation.
Proposal: replace it with a deterministic Specialist Router/registry, not a speaking role.
Method/tool: routing configuration + capability metadata.
Position: REPLACE role with mechanism.

### Media Venture Cell

#### Editorial Director / Showrunner
Objection: generic Media specialist cannot own story taste and final editorial coherence.
Proposal: keep venture-scoped and active for media pilot; no permanent Universal Core seat.
Method/tool: structured brief/script/storyboard/final-cut approval.
Position: KEEP venture-scoped.

#### AI Visual & Post-Production Producer
Objection: Technical Operator can automate tools but should not own visual taste.
Proposal: keep venture-scoped; owns storyboard translation, assets, After Effects/finishing workflow and technical export quality.
Method/tool: CouncilVideoStudio, After Effects bridge, Runway/OpenArt/Descript where validated.
Position: KEEP venture-scoped.

#### Audience Growth & Packaging Operator
Objection: making this permanent before published data creates speculative overhead.
Proposal: remain ON_DEMAND until packaging/retention bottlenecks are measured.
Method/tool: vidIQ/analytics, title-thumbnail testing and retention review.
Position: KEEP ON_DEMAND.

## Round 2 — cross-objections

### Red Team against aggressive consolidation
Do not merge Evidence, Red Team, Human and Value merely to reduce tokens. Research indicates initial viewpoint diversity is a material driver of debate quality. Accepted.

### HR against unmeasured permanent seats
No role should survive forever because it sounds useful. Add role-ablation and unique-contribution metrics. Accepted.

### Human Advocate against pure efficiency optimization
Latency/token reductions cannot justify removing the only role that routinely catches operator burden, accessibility or human error. Accepted.

### Technical Operator against immediate framework adoption
Do not migrate the Council to a fashionable agent framework before measuring the current deterministic harness as a baseline. Accepted.

### Evidence Lead against majority voting
No headcount voting. Evidence/domain authority remains superior to vote count. Accepted.

### Risk/Security against broad tool access
Each runtime role gets a least-privilege tool profile; write/permission/security operations require explicit gates. Accepted.

### Media cell against central creative synthesis
The Decision Orchestrator may govern the venture but cannot replace Showrunner editorial authority inside an approved media production task. Accepted.

## Round 3 — candidate structures

### Candidate A — Keep current structure and add more roles
Rejected.
Reason: maximizes duplication, context load and coordination surface without evidence of higher decision quality.

### Candidate B — Collapse to 3-4 generalist agents
Rejected.
Reason: loses independent evidence, adversarial, human and economic lenses; contrary to observed value of viewpoint diversity.

### Candidate C — Layered Council v0.4
SELECTED FOR SANDBOX BAKE-OFF.

Layer 0 — Owner
- final authority where user approval is required.

Layer 1 — Decision Orchestrator
- merges Chair + Synthesis runtime seats;
- owns framing, routing, convergence, decision record and dissent preservation;
- does not override domain blockers without resolving their evidence.

Layer 2 — Core challenge capabilities
1. Evidence & Verification
2. Red Team / Falsification
3. Execution & Feasibility
4. Risk & Assurance
5. Human & Adoption
6. Value & Economics

Activation:
- LIGHT: Orchestrator + 1-2 relevant capabilities.
- COUNCIL: Orchestrator + 2-4 relevant capabilities, always including one serious challenge.
- ARENA: Orchestrator + all decision-changing core capabilities; not automatically every specialist.

Layer 3 — Specialist Federation
- 16 current specialists remain callable capabilities.
- Customer Skeptic and Moat Auditor remain mandatory for applicable commercial gates.
- specialists have domain blocker authority only inside their evidence-backed scope.

Layer 4 — Operators
- Venture Operator
- Commercial Operator
- Product/Delivery execution capability
- Technical Operator
- Finance Controller/control function
Operators execute and report evidence; they are not automatically independent judges of their own work.

Layer 5 — Venture cells / specialist councils
- Media cell: Showrunner + Visual/Post Producer + Growth/Packaging on demand.
- RevenueSystem specialist council remains federated.
- future specialist councils stay isolated from Universal Core unless routed.

Layer 6 — Meta-governance
- HR & Capability Director
- Capability Scout
- Role Contribution Ledger
- Council Pulse
These do not attend every decision.

## Required new mechanisms

### 1. Specialist Router
Replace generic "Domain Specialists" speaking role with deterministic routing metadata:
- task/domain signals;
- materiality;
- required blockers;
- allowed tools;
- required evidence freshness;
- activation cost budget.

### 2. Role Contribution Ledger
For every COUNCIL/ARENA run record:
- unique evidence added;
- unique objection added;
- decision/test changed? yes/no;
- duplicate-content score;
- token/cost estimate;
- latency;
- false blocker;
- missed blocker discovered later;
- human override.

Review each role after sufficient samples:
KEEP / NARROW / MERGE / ON_DEMAND / REMOVE.

### 3. Evidence Sync
Runtime projects can publish bounded evidence receipts back to UniversalCouncil:
- source repo + commit;
- host/runtime;
- test receipt;
- observed date;
- freshness/expiry;
- verified scope;
- unverified scope.
A CI test must fail if a capability record claims more than the evidence receipt proves.

### 4. Trace + Eval layer
A future multi-agent runtime must trace:
- routing;
- model calls;
- tool calls;
- handoffs;
- guardrails;
- cost/latency;
- final decision.
Build a regression dataset from historical Council decisions and grade:
- route correctness;
- evidence quality;
- dissent preservation;
- blocker precision;
- hallucinated authority;
- decision quality;
- cost/latency.

### 5. Tool profiles
Read-only by default.
Per-role allowlists.
Security/permission/infrastructure writes require explicit human approval.
No role gains authority because a connector exists.

### 6. Context discipline
Use a compact case packet and evidence IDs.
Specialists receive only relevant context plus governing constraints.
Avoid copying entire histories into every role.
Store durable technical truth in Git/ADRs, work state in Linear, runtime traces in the selected tracing layer.

### 7. Adaptive convergence
No fixed number of debate rounds.
Stop when another round is unlikely to add decision-changing evidence, objection or option.
Reopen only affected slices when new evidence arrives.

## Tool/runtime candidates

### Candidate R1 — Current deterministic Python harness
Role: baseline.
Strength: lowest complexity, provider-neutral governance source.
Weakness: roles are structured perspectives rather than independently measurable agents.
Decision: KEEP as baseline and fallback.

### Candidate R2 — OpenAI Agents SDK
Strengths:
- manager vs handoff patterns;
- tools/MCP/guardrails;
- built-in tracing;
- trace grading and eval workflow.
Risk:
- provider coupling and a new runtime layer.
Decision: SANDBOX CANDIDATE.

### Candidate R3 — Microsoft Agent Framework
Strengths:
- Python and C#;
- sequential/concurrent/handoff/group-chat/Magentic orchestration;
- checkpoints/resume;
- human-in-the-loop;
- observability.
Risk:
- additional framework/abstraction and integration cost.
Decision: SANDBOX CANDIDATE.

### Candidate R4 — LangGraph
Strength: explicit stateful graph control and durability.
Risk: current Council may not need the added state-machine complexity yet; practitioner reports emphasize debugging/operational overhead.
Decision: RESERVE CANDIDATE only if R2/R3 fail durability/control requirements.

### Candidate R5 — CrewAI / legacy conversational multi-agent choices
Strength: fast role-based prototyping.
Risk: abstraction can encourage role proliferation and opaque execution for this governance-heavy use case.
Decision: NOT FIRST-LINE CANDIDATE.

## Existing tools — Council findings
- GitHub: KEEP as technical/governance source of truth.
- Linear: KEEP as single work tracker; do not add Jira/ClickUp/monday in parallel.
- Codex Security: KEEP for security scanning/review.
- Superpowers: KEEP for structured software planning/TDD/debugging.
- Remote Desktop Commander: KEEP owner-gated as transport, shell and filesystem access to YASSIN.
- YASSIN Control Bridge / winapp UI Automation: PROMOTE TO FIRST-CLASS EXECUTION CAPABILITY. It provides screen observation, window/element inspection, screenshots, semantic UI Automation, click/hover/drag/send-keys physical input, scrolling/wait-for, recording, before/after verification and an audit log. It can therefore operate full Windows applications when native APIs/scripts are unavailable.
- Figma: KEEP design execution capability, routed through Design/UX.
- Descript/Runway/OpenArt/vidIQ: KEEP as media capabilities; validate per workflow rather than adding more media roles.
- Datadog: DO NOT INSTALL now; no justified production observability gap yet.
- GitHub AGENTS.md / path instructions: PILOT; can reduce repeated repository exploration for coding agents.

## Correction — full desktop / Computer Use capability

The first ARENA pass underweighted a material capability because `company/config/tool_authority.json` records Remote Desktop Commander mainly as `remote_shell.read` / `remote_shell.execute`, while the verified GUI capability lives in the separate local `CouncilVideoStudio` implementation repository.

Verified implementation:
- repository: `C:\Users\alnaseem\Desktop\CouncilVideoStudio`;
- commit: `42544d3a7bfb0fcced63962c45a40dcafd692572` — `feat: add verified YASSIN desktop control bridge`;
- control policy: `config/control_policy.json`;
- bridge: `bridge/yassin_control/control_bridge.py`;
- evidence/guide: `docs/YASSIN_CONTROL_BRIDGE.md`.

Control hierarchy:
1. application-native API/script (preferred);
2. Microsoft winapp UI Automation semantic actions;
3. pywinauto fallback;
4. injected keyboard/mouse only when semantic control is unavailable.

Supported modes:
- Observe: list windows, inspect/search UI, read values/properties, screenshot;
- Semantic control: invoke, set-value, focus, wait-for, scroll-into-view;
- Physical input: click, hover, drag, send-keys;
- Recording: window/element recording;
- Verification: before screenshot -> action -> after screenshot -> optional state verification;
- Audit: append underlying control actions to `control_logs/control_audit.jsonl`.

Policy boundaries already enforced:
- no credential/password automation;
- no security-setting bypass;
- no purchases;
- no external publish;
- no outbound message send;
- prefer semantic selectors over coordinate-only input.

### Structural impact on Council v0.4

This capability changes the execution architecture materially. The Council is not limited to APIs, connectors and shell commands: it can interact with complete desktop applications and visually verify their state.

Therefore:
1. add a first-class `desktop_computer_use` capability to the future tool-authority registry;
2. treat GUI control as an execution substrate, **not a new permanent Council member**;
3. route it primarily through Technical Operator and authorized venture operators, with Risk/Security policy gates;
4. allow specialists to request GUI observations but not silently gain write/control authority;
5. prefer native APIs/scripts first, semantic UIA second, physical mouse/keyboard last;
6. require before/after evidence for state-changing GUI operations;
7. include GUI-task success, selector robustness, recovery from stale UI, visual-state verification and accidental-action rate in the Role/Tool Contribution Ledger;
8. extend Evidence Sync so verified desktop actions can emit bounded evidence receipts to UniversalCouncil;
9. make full-application tasks part of the orchestration framework bake-off, because an agent runtime that cannot safely coordinate visual/GUI actions is incomplete for YASSIN;
10. re-evaluate whether some dedicated SaaS/API plugins are still necessary when the desktop application itself can be operated reliably — but never prefer GUI automation over a safer native API when both exist.

## Sandbox bake-off
Run the same 12-20 historical Council cases through:
A. current deterministic v0.3 baseline;
B. Layered v0.4 prototype using OpenAI manager + specialist tools;
C. Layered v0.4 prototype using Microsoft Agent Framework.

Measure:
- final decision correctness against later-known evidence where available;
- blocker precision/recall;
- unique contribution per role;
- duplicate-content ratio;
- routing accuracy;
- dissent preservation;
- human override rate;
- tool-policy violations;
- completion rate;
- recovery after injected tool failure;
- full-desktop task completion using YASSIN Control Bridge;
- screenshot/visual-state verification accuracy;
- UI selector stability and stale-selector recovery;
- accidental or unintended UI action rate;
- correct choice of native API vs semantic UIA vs physical input;
- latency;
- token/cost.

The bake-off must include real desktop workflows, not only API/tool-call simulations: open and inspect an application, perform a bounded state change, verify the result visually/semantically, recover from one UI change, and preserve an audit receipt.

Kill a runtime candidate if it is materially more expensive/slower without improving decision quality, recovery, or safe desktop execution.

## Preliminary restructuring recommendation
1. Merge Chair + Synthesis as one runtime seat, while keeping synthesis as a required protocol stage.
2. Merge Risk + Assurance as one governance function.
3. Remove Board as a duplicate function; Universal Council is the Board.
4. Replace generic Domain Specialists company function with a Specialist Router.
5. Keep Evidence, Red Team, Execution, Human and Value independent.
6. Move Venture/Commercial/Product-Delivery/Technical/Finance Controller to operator/control layers rather than default Council seats.
7. Keep the 16 specialist federation on demand.
8. Keep commercial Customer Skeptic + Moat Auditor as mandatory challenge capabilities where applicable.
9. Keep the media production cell venture-scoped, not permanent Universal Core.
10. Add Role Contribution Ledger, Evidence Sync, trace/eval layer and least-privilege tool profiles.
11. Do not add a permanent "Observability Agent", "Prompt Engineer", "AI Engineer" or "Agent Manager" role yet; implement these as Technical/HR capabilities and measure the bottleneck first.
12. Promote YASSIN full-desktop Computer Use to a first-class execution capability with separate observe/control authority, verified-action receipts and least-privilege routing.
13. Do not adopt a new orchestration framework until the bake-off beats the current baseline on both decision quality and safe full-desktop execution.

## Material dissent preserved
- Red Team: consolidation must not reduce viewpoint diversity.
- Human Advocate: efficiency metrics must not erase human/operator burden.
- Technical Operator: framework adoption must be reversible and evidence-driven.
- Risk/Security: tool access must remain least privilege even if that increases friction.
- Media Showrunner: generic Council synthesis cannot override editorial authority inside an approved production task.
- HR: any permanent role without measurable unique contribution should be downgraded to on-demand.

## Decision state
PROVISIONAL_RESTRUCTURE_CANDIDATE.

Do not change the governing role files yet.
Next gate: implement the bake-off harness and collect comparative evidence, then reconvene a shorter ARENA to accept, modify or reject Council v0.4.

## External references reviewed
- OpenAI Agents SDK — orchestration/handoffs, tracing, evals: https://developers.openai.com/api/docs/guides/agents/
- Microsoft Agent Framework — workflows/orchestrations/HITL: https://learn.microsoft.com/en-us/agent-framework/
- Anthropic — Building Effective AI Agents: https://resources.anthropic.com/building-effective-ai-agents
- GitHub — custom instructions and AGENTS.md: https://docs.github.com/en/copilot/
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
- OWASP Agentic AI guidance: https://cornucopia.owasp.org/edition/companion/AAI9
- Google SRE — Eliminating Toil: https://sre.google/workbook/eliminating-toil/
- DORA software delivery metrics: https://dora.dev/guides/dora-metrics/
- Zhu et al. 2026, Demystifying Multi-Agent Debate: https://arxiv.org/abs/2601.19921
- Wu et al. 2025, Can LLM Agents Really Debate?: https://arxiv.org/abs/2511.07784
