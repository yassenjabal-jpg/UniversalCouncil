# Universal Council

**Universal Council** is a domain-agnostic decision and deliberation framework designed for use across software, health, research, purchases, business, finance, travel, media, personal planning, and other topics.

It generalizes the strongest governance ideas developed in RevenueSystem Council 2.2.1 without coupling the framework to RevenueSystem.

## Core principle

> The Council exists to improve the user's decision — not to agree with the user.

The Council does not manufacture consensus. It selects only relevant voices, distinguishes evidence from opinion, preserves dissent, and escalates unresolved high-impact uncertainty instead of hiding it.

## Operating model

Every topic is routed through a lightweight domain router:

`Frame → Route → Evidence → Propose → Challenge → Counter-Propose → Synthesize → Decide`

Three default modes are available:

- **LIGHT** — everyday questions; 2–3 relevant voices and one compact challenge.
- **COUNCIL** — material decisions; 4–7 relevant voices, explicit alternatives and dissent.
- **ARENA** — high-impact, contested, uncertain, irreversible, or user-requested deliberation; independent positions before synthesis.

## Universal Core

1. Chair / Decision Controller
2. Evidence & Research Lead
3. Red Team / Devil's Advocate
4. Practicality & Execution Reviewer
5. Risk & Consequence Analyst
6. Human / User Advocate
7. Cost–Benefit & Value Analyst
8. Synthesis & Alternatives Designer

Domain specialists are activated only when relevant.

## Evidence hierarchy

The Council labels claims as one of:

- `FACT-VERIFIED`
- `AUTHORITATIVE-EXTERNAL`
- `CORROBORATED-COMMUNITY`
- `COMMUNITY-LEAD`
- `INFERENCE`
- `OPINION`
- `ASSUMPTION`
- `UNKNOWN`

Expert authority is weighted by domain and evidence, not by vote count.

## Repository map

- `GOVERNANCE.md` — governing constitution
- `contracts/` — decision, research, dissent and safety contracts
- `config/roles.json` — machine-readable roles
- `config/domain-routing.json` — specialist routing rules
- `config/modes.json` — deliberation modes
- `skills/universal-council/SKILL.md` — compact invocation skill
- `tests/` — non-software scenario tests
- `tools/validate_config.py` — configuration validator
- `docs/decisions/` — architecture decision records

## Specialist councils

The framework can host specialized councils without absorbing them into the universal core. RevenueSystem Council 2.2.1 is treated as the first external specialist council adapter.

## Important limitation

This repository defines governance, routing, evidence and deliberation behavior. It does **not** claim that each role is a physically independent AI process. A runtime may implement roles as independent agents, parallel model calls, or structured perspectives from one model; the governance contract remains the same.

## Version

Initial governance version: **Universal Council 0.1.0**
