# UniversalCouncil Command Center — Stage 5 Remote Owner + Secure Command Gateway Contract
Date: 2026-10-19
Status: OPEN / OWNER-AUTHORIZED
Branch: `command-center/stage5-remote-owner-gateway`
Parent product SHA: `d43d2a6ef5a971c9049ca0ae314eafe48f00db1f`
Parent lock: `COMMAND_CENTER_STAGE4_EXECUTION_FABRIC_LOCK`

## Mission

Build the Remote Owner command-trust boundary as a real local gateway and durable queue without enabling YASSIN execution.

Stage 5 creates:
- Remote Command Envelope;
- out-of-band Owner authorization context contract;
- device + session identity contract;
- nonce / idempotency / expiry enforcement;
- persistent replay ledger;
- append-only trusted command queue;
- explicit approval-intent projection;
- Secure Command Gateway executable;
- Command Center Remote Owner surface;
- local-first / Tailscale-compatible transport architecture.

## Critical authority rule

`ACCEPTED_COMMAND != EXECUTION_AUTHORITY`

A command may become:
`QUEUED_TRUSTED`

but execution remains:
`BLOCKED_PHASE0`

Stage 5 must not dispatch to:
- YASSIN Execution Service;
- shell/process;
- GUI;
- provider/model;
- external service.

## Phase 0 source

Remote command trust is grounded in the Phase 0 prototype:
- branch: `phase0/feasibility-adversarial-prototype`
- head: `63a4a446bc1e87f5352915f1e86c463de82e9b81`
- source files:
  - `company/runtime/phase0_guardrails.py`
  - `company/config/phase0_feasibility.json`
  - `company/tests/test_phase0_feasibility.py`

Locked rules imported:
- authenticated OWNER required;
- authorization source required;
- authorization is out-of-band from instruction text;
- bounded target/effects;
- nonce required;
- idempotency key required;
- expiry required;
- persistent replay ledger;
- same idempotency + same command => duplicate/no re-execution;
- same idempotency + changed command => reject;
- nonce replay => reject;
- expired command => reject.

Phase 0 G0-C remains:
`IN_TEST`

No real transport round trip has passed yet.

## Envelope contract

Required:
- command_id
- nonce
- idempotency_key
- issued_at
- expires_at
- owner_id
- device_id
- session_id
- target
- effects
- instruction
- approval_intent
- correlation_id

Instruction text cannot grant authority.

The stable digest must include all command identity, scope and instruction fields.

## Authorization context

Required separately from the envelope:
- principal = OWNER;
- authenticated = true;
- authentication_source;
- owner_id;
- device_id;
- session_id;
- allowed_targets;
- allowed_effects;
- valid_from;
- expires_at;
- revoked = false.

A command cannot authenticate itself.

## Device/session registry

Stage 5 registry is local runtime state, not repository credentials.

Requirements:
- explicit device registration;
- explicit session registration;
- expiry;
- revocation;
- device/session/owner identity match;
- fail closed on missing or malformed registry state.

Stage 5 CI uses synthetic disposable registries only.

## Approval intent

The envelope may state an approval intent/reference.

That reference is not execution authority.

For T3/high-impact work a future dispatch layer must require an independently authenticated approval grant whose scope covers the command.

Stage 5 may validate approval records synthetically but may not authorize live dispatch.

## Replay ledger

Persistent across process restart.

Required uniqueness:
- nonce;
- idempotency_key.

Stored:
- command digest;
- accepted timestamp;
- owner/device/session identities;
- target;
- effects.

No secrets/tokens are stored.

## Queue

Append-only JSONL or equivalent durable local record.

Allowed states:
- QUEUED_TRUSTED
- DUPLICATE_SAME_COMMAND
- REJECTED
- BLOCKED_PHASE0

Stage 5 does not create:
- DISPATCHED
- RUNNING
- SUCCEEDED
- POSTCONDITION_VERIFIED

## Transport

Stage 5 executable may support local CLI/file ingress only.

It must not:
- listen on a public interface;
- open router ports;
- expose YASSIN directly to Internet;
- start a Tailscale process;
- depend on a paid cloud server;
- use GitHub text as executable shell input.

Architecture must remain compatible with a future authenticated local HTTPS/Tailscale transport.

## Security rules

- no secrets in repository;
- no credentials in envelope;
- no authority from instruction text;
- no implicit device trust;
- no implicit session trust;
- no silent fallback;
- no replay after UNKNOWN;
- no conversion from queue acceptance to execution.

## UI

Remote Owner must show:
- gateway mode;
- network listener disabled;
- device/session registration state;
- Phase 0 G0-C state;
- queue/trust state;
- execution remains blocked;
- no implication that phone/Tailscale is already connected.

## Acceptance

Stage 5 locks only if:
1. exact Stage 4 product base is preserved;
2. Phase 0 source pin is verified;
3. envelope + auth are separate;
4. replay/idempotency survives process restart;
5. device/session mismatch fails closed;
6. expiry/clock/TTL checks fail closed;
7. target/effect escalation fails closed;
8. changed command under reused idempotency fails closed;
9. nonce replay fails closed;
10. queue acceptance never grants execution;
11. no live network listener exists;
12. no provider/GUI/shell dispatch exists;
13. Stage 2/3/4 regressions pass;
14. Architecture Boundary Audit passes;
15. CodeQL passes;
16. exact-head UI evidence passes Council/Studio review.

Exit:
`COMMAND_CENTER_STAGE5_REMOTE_OWNER_GATEWAY_LOCK`
