# ADR-0002 — Proactive HR Capability Scouting

Date: 2026-10-11  
Status: ADOPTED BY OWNER REQUEST

## Problem
The HR & Capability Director already owned skills, plugins/connectors, tools and work-environment quality, but the operating model did not require proactive ecosystem scanning. In practice the role could remain reactive until a missing tool was named externally.

Finding: **HR-001 — Insufficient proactive capability scouting.**

## Decision
Keep the existing HR & Capability Director. Do not add a permanent Council member.

Add a bounded internal function named **Technology & Capability Scout** with:
- event-driven capability-gap triggers;
- a weekly bounded scan while the company/council is active and a 30-day scan while inactive;
- a capability-gap register and candidate dossier;
- source, maintenance, license/terms, permissions, data, security, cost, duplication, rollback and measurable-outcome checks;
- supply-chain pinning for pilots;
- Security, Architecture/Duplication, Council, Sandbox and Owner gates before adoption.

HR may perform read-only discovery without a separate adoption grant. HR may not unilaterally install tools, connect credentials, authenticate accounts, purchase, change permissions, enable browser extensions, write externally, publish or message.

## Trigger rule
Open a capability gap when a required capability is unavailable, manual work repeats, a tool repeatedly fails, an evidence channel is missing, human handoffs repeat, a workflow is materially slow/friction-heavy, duplicate tooling is detected, security/cost materially regresses, or the external ecosystem gains a capability that can plausibly change performance.

## Anti-bureaucracy rule
There is no quota for recommendations or installations. NO-CHANGE scans remain silent. The purpose is to discover material capability improvements early, not to create tool churn.

## Consequences
- HR becomes accountable for early discovery, not merely reactive provisioning.
- Adoption authority remains separated from scouting.
- New tools cannot bypass security, architecture, duplication or Owner controls.
- The Council gains a repeatable route for tools such as social-intelligence connectors without making them permanent members.
