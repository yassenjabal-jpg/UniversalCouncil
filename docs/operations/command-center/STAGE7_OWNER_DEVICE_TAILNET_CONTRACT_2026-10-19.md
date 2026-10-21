# UniversalCouncil Command Center — Stage 7 Owner Device Enrollment + Tailnet Round Trip
Date: 2026-10-19
Status: OPEN / OWNER-AUTHORIZED
Branch: `command-center/stage7-owner-device-tailnet`
Parent product SHA: `3cc4df9b2fdd861fd903705a4206a2d6d3de69e9`
Parent lock: `COMMAND_CENTER_STAGE6_AUTHENTICATED_TRANSPORT_LOCK`

## Mission

Move from the Stage 6 authenticated loopback foundation to a real owner-device/tailnet pilot without granting execution authority.

Required end-state evidence:
1. owner device enrolled;
2. short-lived session credential issued;
3. plaintext token not persisted by the application;
4. YASSIN host probe confirms Tailscale state;
5. RemoteTransport deployed and listening only on loopback;
6. Tailscale Serve proxies only to `http://127.0.0.1:47721`;
7. Tailscale Funnel remains disabled;
8. real owner phone reaches the Stage 7 private endpoint;
9. authenticated `/v1/status` succeeds from the owner phone;
10. one bounded command reaches `QUEUED_TRUSTED`;
11. execution remains `BLOCKED_PHASE0`;
12. session revocation causes the same phone credential to fail.

## Current external blocker

Historical opening evidence recorded YASSIN as Online with agent version `0.3.0`.

Current access observation on 2026-10-21:
- target device: `YASSIN`;
- current state: `Offline`;
- Remote Desktop Commander monthly calls remaining: `0%`.

Therefore both device availability and remote-tool quota currently block real-host execution.

The service explicitly instructed:
- do not retry the side-effecting tool;
- do not reconnect the paired device.

Therefore:
- Stage 7 may continue with repository/product implementation and isolated CI;
- no Tailscale installation/status/Serve claim may be promoted to truth;
- no YASSIN deployment claim may be promoted to truth;
- no phone round-trip may be promoted to truth;
- the Stage 7 final lock must remain unavailable until real host/tool access is restored or another authorized real-host path is provided.

## Authority invariant

`TAILNET_SUCCESS != EXECUTION_AUTHORITY`

A real private phone round-trip may authenticate and enqueue a bounded command only.

It must not:
- start shell execution;
- drive GUI input;
- invoke model/provider execution;
- mutate authority;
- bypass Stage 5 replay/nonce/idempotency/scope checks.

Execution remains:
`BLOCKED_PHASE0`

## Enrollment

Stage 7 adds a local Owner Enrollment tool.

Device enrollment record contains only:
- owner ID;
- device ID;
- validity window;
- revoked flag.

Session enrollment record contains only:
- owner ID;
- device ID;
- session ID;
- validity window;
- revoked flag;
- token SHA-256;
- allowed targets;
- allowed effects.

The plaintext bearer token:
- is generated from at least 32 random bytes;
- is returned once to the caller;
- is never written to the registry;
- must not be committed to GitHub;
- must not be written to ordinary logs;
- expires within 60 minutes.

## Tailscale policy

Allowed private transport:
`Owner phone -> tailnet -> Tailscale Serve -> http://127.0.0.1:47721 -> RemoteTransport`

Forbidden:
- Tailscale Funnel;
- public IP binding;
- router port forwarding;
- exposing Kestrel directly to the LAN;
- binding RemoteTransport to `0.0.0.0`;
- storing auth keys/tokens in GitHub;
- deriving Owner authority from MagicDNS/Tailscale identity alone.

Tailscale narrows network reachability.
Application bearer + device/session authentication remains mandatory.

## Host probe

A Stage 7 host probe may read:
- Tailscale binary presence/version;
- `tailscale status --json`;
- `tailscale serve status --json`;
- local `/healthz`.

The persisted evidence must be sanitized.
It must not persist:
- peer lists;
- account emails;
- auth keys;
- bearer tokens;
- full raw Tailscale status payloads.

## Serve configuration

If owner-authorized host execution is available and Tailscale is already authenticated:

`tailscale serve --bg http://127.0.0.1:47721`

is permitted only after:
- local health passes;
- Tailscale connection is running;
- no Funnel configuration is active;
- Administrator context is present where Windows requires it.

Configuration must be verified afterward with:
`tailscale serve status --json`

No `tailscale funnel` command is allowed in Stage 7.

## Phone verification

The phone verification must use:
- the actual tailnet Serve URL;
- bearer token;
- device ID;
- session ID.

Required sequence:
1. authenticated status succeeds;
2. bounded command succeeds as `QUEUED_TRUSTED`;
3. command reports `BLOCKED_PHASE0`;
4. session is revoked locally;
5. same phone credential returns unauthorized.

## CI foundation acceptance

Before real host work, Stage 7 CI must prove:
- enrollment tool stores token hash only;
- issued token is >= 32 bytes entropy;
- TTL > 60 minutes fails closed;
- unknown/revoked device fails closed;
- revoked session fails closed;
- Stage 6 HTTP tests still pass;
- Stage 2/3/4/5/6 regressions pass;
- static boundary rejects Funnel/public bind/Execution Service coupling;
- UI truth does not fabricate host/phone success;
- CodeQL passes.

## Final Stage 7 lock

Final lock requires all real evidence:
- YASSIN probe;
- YASSIN deployment;
- private Serve;
- owner phone round-trip;
- revocation round-trip.

Until then:
`STAGE7_OPEN / REAL_HOST_EVIDENCE_PENDING`
