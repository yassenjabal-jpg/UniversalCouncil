# Universal Council

**Universal Council v0.3** is a domain-agnostic decision and deliberation framework for software, health, research, purchases, business, finance, travel, media, personal planning and other topics.

## Core principle
> The Council exists to improve the user's decision — not to agree with the user.

The Council does not manufacture consensus. It selects relevant voices, requires independence before influence when stakes justify it, distinguishes evidence from opinion, preserves evidence-backed dissent, and reopens decisions when their assumptions expire.

## Operating model
Material work follows:

`Frame → Route → Independent Position → Evidence Matrix → Selective Challenge → Counter-Propose → Premortem → Synthesize → Decide → Expiry/Review Trigger`

LIGHT mode compresses this flow.

### Modes
- **LIGHT** — reversible, low-stakes questions; smallest useful set of voices.
- **COUNCIL** — material decisions; independent first positions when disagreement, uncertainty or anchoring risk is material.
- **ARENA** — high-impact or contested work; blind first positions, calibrated confidence, evidence matrix, premortem, preserved dissent and explicit reopen triggers.

## Universal Core
1. Chair / Decision Controller
2. Evidence & Research Lead
3. Red Team / Devil's Advocate
4. Practicality & Execution Reviewer
5. Risk & Consequence Analyst
6. Human / User Advocate
7. Cost-Benefit & Value Analyst
8. Synthesis & Alternatives Designer

Domain specialists are activated only when relevant. Revenue projects additionally require the Customer Skeptic and Commoditization & Moat Auditor.

## v0.3 safeguards
- independent first positions before peer influence in ARENA;
- confidence 0–100 as calibration, never voting weight;
- evidence matrix for contested decisions;
- selective debate instead of mandatory argument rounds;
- consensus-free synthesis;
- premortem before SELECTED or difficult-to-reverse execution;
- commitment-evidence ladder for commercial validation;
- Foundation Model Uplift Test for AI-enabled ventures;
- Decision Owner, Driver and expiry/review triggers;
- Council Pulse for active decisions;
- anti-bureaucracy budget.

## Evidence hierarchy
Claims are classified as:
- FACT-VERIFIED
- AUTHORITATIVE-EXTERNAL
- CORROBORATED-COMMUNITY
- COMMUNITY-LEAD
- INFERENCE
- OPINION
- ASSUMPTION
- UNKNOWN

Evidence and domain authority outweigh headcount.

## Repository map
- `GOVERNANCE.md` — governing constitution
- `contracts/DELIBERATION.md` — deliberation protocol
- `contracts/DECISION_KERNEL.md` — decision record schema
- `contracts/COMMERCIAL_PRE_SOLUTION_GATE.md` — commercial selection gate
- `contracts/COUNCIL_PULSE.md` — recurring review contract
- `config/roles.json` — roles
- `config/domain-routing.json` — specialist routing
- `config/modes.json` — mode behavior
- `config/pulse.json` — pulse configuration
- `skills/universal-council/SKILL.md` — compact invocation skill
- `tests/` — scenario tests
- `tools/validate_config.py` — configuration validator
- `docs/research/` — external/community self-review evidence
- `docs/decisions/` — architecture decisions
- `ventures/` — Council-managed venture records

## Optional Venture Operating System

The `company/` module is a bounded Stage 0 operating layer around the Council. It preserves Universal Council as the general-purpose Board/decision system and adds deterministic controls for grants, capabilities, budgets, actions, evidence/events, obligations, accounting, recovery, and synthetic acceptance tests.

Stage 0 defaults to `PAUSED_BY_OWNER` and `DRY_RUN`. It does not authorize prospect contact, publishing, spending, payment collection, or restarting stopped ventures. Live operation remains blocked until operation-scoped capability evidence, payment readiness, durable private storage, and real enforcement isolation are verified.

Its governing commercial principle is **External Reality Supremacy**: verified customer behavior, settled money, accepted delivery, and provider state outrank model prose, forecasts, dashboards, or internal consensus.

## Specialist councils
Universal Council can federate specialist councils without absorbing their domain rules. RevenueSystem Council 2.2.1 is the first specialist-council precedent.

## Important limitation
Council roles are governance roles. This repository does not claim each role is a physically independent AI process. A runtime may implement them as parallel agents, separate model calls or structured perspectives from one model.

## Version
Current governance version: **Universal Council 0.3.0**
