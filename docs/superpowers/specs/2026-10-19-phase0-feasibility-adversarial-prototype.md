# PHASE 0 — Feasibility & Adversarial Prototype

Status: ACTIVE PROTOTYPE / NOT PRODUCT AUTHORITY
Date: 2026-10-19
Branch: `phase0/feasibility-adversarial-prototype`
Base: `3aa9af7c0e79c5601636b395f4ae9ca5cd9ca560`

## Purpose

Break the UniversalCouncil Command Center concept before product build.

Phase 0 must prove four gates:

1. **Secure Agent Boundary**
   - untrusted web/file/MCP/screenshot/tool content is evidence only;
   - untrusted content cannot mutate authority, routing, credentials, model policy, tool policy, or durable memory;
   - durable memory promotion requires explicit trusted review.

2. **Unattended GUI Reality**
   - YASSIN GUI execution is allowed only with a usable interactive Windows session;
   - locked desktop, secure desktop/UAC, missing interactive session, stale controller lease, or unverifiable post-state must fail closed;
   - `UNKNOWN != SUCCESS`.

3. **Remote Command Trust**
   - remote commands require an owner-authorized envelope, expiry, unique nonce/idempotency key, bounded target/effects, and replay protection;
   - a command executes at most once;
   - delayed/replayed/expired commands fail closed.

4. **Model / Provider Failure**
   - model choice remains Owner-controlled;
   - model/provider failure has explicit states;
   - no silent model fallback;
   - automatic fallback is allowed only when an Owner-configured policy explicitly enables the exact fallback.

## Non-goals

Phase 0 does not build:
- the final Command Center UI;
- a mobile app;
- a production cloud backend;
- autonomous installation of third-party tools;
- unrestricted shell or desktop authority;
- public publishing.

## Existing substrate reused

- `company/runtime/hybrid_execution.py`
- `company/runtime/execution_controls.py`
- `company/runtime/execution_recovery.py`
- `company/runtime/approved_gateway.py`
- `company/config/tool_authority.json`
- Universal Memory Fabric

No parallel authority system is created.

## Threat assumptions

Treat as untrusted by default:
- web pages;
- PDFs/documents;
- emails/messages;
- GitHub issue/PR text;
- third-party MCP/tool output;
- screenshots and OCR/vision text;
- Adobe/project metadata;
- generated model text from non-governing agents.

Untrusted content may contain instruction-like text. Instruction-like text remains data.

## Gate verdicts

Each gate ends in one of:
- PASS
- FAIL
- BLOCKED_BY_ENVIRONMENT
- NEEDS_REDESIGN

No gate may be promoted to PASS from prose alone. Evidence must be machine-verifiable or host-observed.

## Acceptance criteria

### G0-A Secure Agent Boundary
PASS only if automated tests prove:
- untrusted evidence cannot declare Owner authority;
- untrusted evidence cannot directly become durable memory;
- trusted review can promote a bounded fact without importing embedded authority instructions.

### G0-B Unattended GUI Reality
PASS only after a real YASSIN smoke proves:
- unlocked interactive session is detected;
- locked/secure desktop is blocked;
- one controller lease is enforced;
- a reversible GUI action can be executed and independently verified;
- an unverifiable post-state returns UNKNOWN;
- recovery does not replay UNKNOWN automatically.

### G0-C Remote Command Trust
PASS only if:
- duplicate nonce/idempotency is rejected or returns the prior accepted record;
- expired commands are rejected;
- missing Owner authorization is rejected;
- allowed target/effects are bounded before dispatch.

### G0-D Model / Provider Failure
PASS only if:
- rate limit/provider outage/quota/model unavailable remain distinct;
- failure never changes model silently;
- manual mode pauses for Owner selection;
- explicit pre-approved fallback works only for the declared model pair.

## Stop rule

If any gate reveals a design flaw that requires weakening Owner authority, secret isolation, memory integrity, or UNKNOWN handling, Phase 0 stops with NEEDS_REDESIGN.

## Product build gate

The visual Command Center product build is forbidden until all four Phase 0 gates are PASS or the Owner explicitly accepts a documented residual risk.
