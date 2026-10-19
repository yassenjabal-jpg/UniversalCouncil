# UniversalCouncil Command Center — Stage 6 Authenticated Local / Tailscale Transport Pilot
Date: 2026-10-19
Status: OPEN / OWNER-AUTHORIZED
Branch: `command-center/stage6-authenticated-transport`
Parent product SHA: `e6769d1b6e4a061503deeb7ac94c18bbd36c7f47`
Parent lock: `COMMAND_CENTER_STAGE5_REMOTE_OWNER_GATEWAY_LOCK`

## Mission

Prove a real authenticated HTTP round trip into the Stage 5 Remote Owner trust boundary while keeping execution on YASSIN blocked.

Stage 6 introduces:
- a dedicated RemoteTransport executable;
- loopback-only Kestrel binding;
- bearer session-token authentication;
- device/session binding;
- hashed token persistence only;
- short-lived session enforcement;
- revocation enforcement;
- authenticated command POST;
- authenticated approval-validation POST;
- authenticated status endpoint;
- minimal health endpoint;
- real loopback HTTP integration evidence;
- architecture compatible with future Tailscale Serve proxying.

## Critical authority rule

`TRANSPORT_SUCCESS != EXECUTION_AUTHORITY`

Successful network transport may produce:
`QUEUED_TRUSTED`

but execution remains:
`BLOCKED_PHASE0`

Stage 6 may not call the Execution Service dispatch path.

## Binding policy

Product listener:
- loopback only;
- IPv4 `127.0.0.1` or IPv6 `::1`;
- no `0.0.0.0`;
- no `IPAddress.Any`;
- no `ListenAnyIP`;
- no router port forwarding;
- no public Internet exposure.

The Stage 6 product does not execute the Tailscale CLI.

Future tailnet access may proxy the loopback service through Tailscale Serve after separate host evidence and owner approval.

Tailscale Funnel is forbidden.

## Authentication

Protected endpoints require:
- `Authorization: Bearer <high-entropy-session-token>`;
- device identity header;
- session identity header.

Registry stores:
- owner ID;
- device ID;
- session ID;
- token SHA-256;
- target/effect scopes;
- valid-from;
- expiry;
- revoked state.

Plaintext token must not be persisted by the application.

Minimum token entropy: 32 bytes.

Maximum Stage 6 session TTL: 60 minutes.

The token is transport authentication only; it does not bypass command-level nonce/idempotency/expiry/target/effect validation.

## Endpoints

### GET /healthz
Minimal liveness only.
Must not reveal secrets, queue content, identity data or execution authority.

### GET /v1/status
Authenticated.
Returns bounded transport/trust state.

### POST /v1/commands
Authenticated.
Body is the Stage 5 RemoteCommandEnvelope.
The authenticated owner/device/session becomes the out-of-band AuthorizationContext.
On success:
- trust state may be `QUEUED_TRUSTED`;
- execution state must be `BLOCKED_PHASE0`.

### POST /v1/approvals/validate
Authenticated.
Validates an approval record.
The endpoint does not grant execution authority.

## Request constraints

- maximum body: 32 KiB;
- JSON only for POST endpoints;
- malformed JSON fails closed;
- unknown/expired/revoked session fails closed;
- mismatched device/session fails closed;
- missing bearer token fails closed;
- wrong bearer token fails closed;
- oversized body fails closed.

CORS remains disabled in Stage 6.

## Round-trip acceptance

Stage 6 must execute a real HTTP request through the product Kestrel pipeline on loopback during CI.

Required evidence:
1. server binds only to loopback;
2. authenticated status succeeds;
3. unauthenticated status fails;
4. authenticated command reaches trust service;
5. command is queued exactly once;
6. duplicate request deduplicates;
7. changed command with same idempotency fails;
8. revoked/expired/wrong token fails;
9. device/session mismatch fails;
10. execution remains `BLOCKED_PHASE0`;
11. no call to Execution Service occurs.

## Tailscale status

Stage 6 lock does not require a live Tailscale installation or phone.

Repository/runtime truth must remain:
- Tailscale connected: false unless actual host evidence exists;
- phone connected: false unless actual round-trip evidence exists;
- Tailscale Serve configured: false unless host configuration evidence exists.

No simulated fixture may promote those fields to live truth.

## Architecture

Preferred:
`Remote client -> RemoteTransport -> Authenticator -> Stage5 Trust Service -> Replay Ledger -> Trusted Queue`

Execution remains a separate downstream subsystem.

WPF is read-only projection.

RemoteTransport must not own:
- execution provider dispatch;
- GUI control;
- shell/process execution;
- model invocation;
- policy mutation.

## Security review

Mandatory checks:
- no plaintext tokens in repository;
- no token logging;
- constant-time token-hash comparison;
- fail closed on registry corruption;
- loopback-only binding;
- no CORS;
- no Funnel/public mode;
- no silent authentication fallback;
- no anonymous command/approval;
- body-size bound;
- no authority from HTTP headers beyond authenticated identity/scopes stored in registry.

## Acceptance

Stage 6 locks only if:
1. exact Stage 5 base preserved;
2. Stage 5 trust invariants still pass;
3. RemoteTransport builds;
4. real Kestrel loopback round trip passes;
5. authentication adversarial tests pass;
6. public binding mutations fail closed;
7. Stage 2/3/4/5 regressions pass;
8. CodeQL passes;
9. Architecture Boundary Audit passes;
10. exact-head UI evidence passes Council/Studio review;
11. repository-wide inherited blockers are not hidden.

Exit:
`COMMAND_CENTER_STAGE6_AUTHENTICATED_TRANSPORT_LOCK`
