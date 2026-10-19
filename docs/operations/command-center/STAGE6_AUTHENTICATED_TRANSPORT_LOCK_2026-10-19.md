# UniversalCouncil Command Center — Stage 6 Authenticated Transport Lock
Date: 2026-10-19
Status: PASS / LOCKED AS AUTHENTICATED LOOPBACK TRANSPORT FOUNDATION

## Gate
`COMMAND_CENTER_STAGE6_AUTHENTICATED_TRANSPORT_LOCK`

## Product pin
- repository: `yassenjabal-jpg/UniversalCouncil`
- product branch: `command-center/stage6-authenticated-transport`
- exact product SHA:
  `3cc4df9b2fdd861fd903705a4206a2d6d3de69e9`
- Draft PR: `#47`
- base branch: `command-center/stage5-remote-owner-gateway`
- base product SHA:
  `e6769d1b6e4a061503deeb7ac94c18bbd36c7f47`

## Locked transport behavior

Mode:
`LOOPBACK_AUTHENTICATED_PILOT`

Target host metadata:
`YASSIN`

Allowed bind architecture:
- `127.0.0.1`
- `::1`

Forbidden:
- public wildcard bind;
- router port forwarding;
- CORS;
- Tailscale Funnel;
- product-owned Tailscale CLI execution;
- direct shell/GUI/provider execution from RemoteTransport.

## Real round-trip proof

Exact-head CI started the Stage 6 Kestrel product path on:

`http://127.0.0.1:55911`

Result:
`PASS_LOOPBACK_AUTHENTICATED_ROUNDTRIP`

This port is ephemeral CI evidence only.
It is not a production YASSIN endpoint.

## Authentication lock

Transport authentication:
`LOCAL_HASHED_SESSION_TOKEN`

Required:
- bearer token;
- device ID;
- session ID;
- registered device;
- registered session;
- valid time window;
- non-revoked identity;
- stored target/effect scopes.

Token rules:
- minimum raw entropy: 32 bytes;
- plaintext token persistence: forbidden;
- stored token material: SHA-256 only;
- comparison: constant-time;
- maximum session TTL: 60 minutes.

## HTTP lock

Endpoints:
- `GET /healthz` — minimal liveness only;
- `GET /v1/status` — authenticated;
- `POST /v1/commands` — authenticated;
- `POST /v1/approvals/validate` — authenticated.

POST request body maximum:
`32768 bytes`

CORS:
`DISABLED`

Anonymous command:
`FORBIDDEN`

Anonymous approval:
`FORBIDDEN`

## Authority invariant

`TRANSPORT_SUCCESS != EXECUTION_AUTHORITY`

Authenticated command path:
`HTTP -> authenticated Owner context -> Stage5 trust validation -> replay guard -> trusted queue`

Allowed outcome:
`QUEUED_TRUSTED`

Execution outcome:
`BLOCKED_PHASE0`

Transported approval outcome:
`VALID_NOT_EXECUTION_AUTHORITY`

RemoteTransport has no Execution Service project reference.

## Replay/trust invariants retained

- nonce required;
- idempotency required;
- expiry required;
- target/effect scope required;
- duplicate same command does not append a second queue item;
- changed command under reused idempotency is rejected;
- nonce replay is rejected;
- revoked/expired/mismatched sessions are rejected;
- unknown is never success.

## Tailscale lock

Architecture is compatible with a future private Tailscale Serve proxy over the loopback service.

Current truth:
- Tailscale connected: `false`;
- Tailscale Serve configured: `false`;
- phone connected: `false`;
- Funnel allowed: `false`.

Stage 6 does not execute or configure Tailscale.

A future host-level Serve configuration requires separate owner authorization and real host evidence.

## Architecture lock

`Remote client -> RemoteTransport -> Authenticator -> Stage5 Trust Service -> Replay Ledger -> Trusted Queue`

Presentation:
read-only.

RemoteTransport:
HTTP composition only.

Application:
trust/auth policy.

Infrastructure:
registry/replay/queue persistence.

Execution Service:
separate downstream boundary.

Architecture verdict:
`PASS_STAGE6_ARCHITECTURE_BOUNDARY`

## Exact-head verification

Stage 6 workflow:
- run #14
- ID: `39226538632`
- conclusion: `SUCCESS`

CodeQL:
- run #514
- ID: `39226538731`
- conclusion: `SUCCESS`

Company Stage 0:
- run #597
- ID: `39226538561`
- conclusion: `FAILURE`

Final Stage 6 Python changes:
- Ruff lint: PASS
- Ruff format: PASS
- compile: PASS

Retained repository failure:
`MemoryFabricError: invalid memory source`

This remains a separate inherited blocker.

## Artifacts

Command Center:
- ID: `12173708528`
- digest:
  `sha256:0c96b688e339a1fdc33c5af560101e1b8546e96c89b9b751830d579eae1c69b2`

Execution Service:
- ID: `12173789333`
- digest:
  `sha256:030a64c3c6b8b36a3e2d20e1e6b47789d25a924746e4a557f186fd026cd94ca3`

Remote Gateway:
- ID: `12173968249`
- digest:
  `sha256:4286b2e337cd0bb15890f8dff70fce362310cf649e0d56663aa53e6832010637`

Remote Transport:
- ID: `12173399799`
- digest:
  `sha256:2bf39b8eb0d9faf6a0e5ff4cc86616689d9116204b036c9e5af9c2c3434c6185`

UI evidence:
- ID: `12173429540`
- digest:
  `sha256:9f363c1e53e249697beabd7d3caf228261f84abd87b3ecb7073ea23d090ecdfb`

Read-model hashes:
- operational state:
  `913798a97de487e0b8175ff9c48156a3321234c6aa7c6b22f4bc795f2a152191`
- orchestration:
  `314027108bf7ff582a0e30faea6965210e00ca20652ed9ae51d126bf37a1ca88`
- execution fabric:
  `6b8b983e97334b417898b67af512c02d139f3f1b1324601f66063d0c2b31e42b`
- remote owner:
  `af016b384c46253c26dde06989492f9bd6a22efb0af49ef76dd8435fa8fc2798`
- remote transport:
  `f2e1d12eccfe3ea5a6f51aa26b3a06034dc95be86a6e452e718ab31961181330`

UI:
- 1440×900:
  `sha256:c5914ee4e817c557a8f3c76b08badf22ab2e96b65b3cea146f70398aeb5dff28`
- 1180×720:
  `sha256:220b745afacfaba06a2f8953221464e564d86ad2283a8b21561d4f917215daea`

## Review locks

Council:
`PASS_STAGE6_AUTHENTICATED_TRANSPORT_FOUNDATION`

Studio:
`PASS_STAGE6_AUTHENTICATED_TRANSPORT_SURFACE`

Architecture:
`PASS_STAGE6_ARCHITECTURE_BOUNDARY`

Transport:
`PASS_LOOPBACK_AUTHENTICATED_ROUNDTRIP`

Phone:
`NOT_CONNECTED`

Tailscale:
`NOT_CONNECTED`

Execution:
`BLOCKED_PHASE0`

## Downstream rule

Stage 7 may introduce a bounded real-owner device/tailnet pilot:
- explicit owner-device enrollment;
- generation and delivery of a short-lived session credential through an approved secure handoff;
- actual YASSIN host deployment evidence;
- Tailscale installation/status verification if owner authorizes it;
- Tailscale Serve over loopback only;
- real owner-phone tailnet round-trip;
- session revocation from the Command Center;
- host health and recovery evidence.

Stage 7 may not:
- use Tailscale Funnel;
- open router ports;
- expose the endpoint publicly;
- store plaintext bearer tokens in GitHub;
- derive authority from GitHub/ChatGPT text;
- bypass Stage 5 trust rules;
- enable shell/GUI/provider execution merely because transport works.

Real YASSIN execution remains separately gated.

## Next stage

`PHASE 7 — Owner Device Enrollment + Tailnet Round Trip`

State:
`AWAITING_OWNER_STAGE7_OPEN`
