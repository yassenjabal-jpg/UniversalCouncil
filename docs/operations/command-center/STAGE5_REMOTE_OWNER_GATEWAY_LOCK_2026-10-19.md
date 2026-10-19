# UniversalCouncil Command Center — Stage 5 Remote Owner Gateway Lock
Date: 2026-10-19
Status: PASS / LOCKED AS REMOTE COMMAND TRUST FOUNDATION

## Gate
`COMMAND_CENTER_STAGE5_REMOTE_OWNER_GATEWAY_LOCK`

## Product pin
- repository: `yassenjabal-jpg/UniversalCouncil`
- product branch: `command-center/stage5-remote-owner-gateway`
- exact product SHA:
  `e6769d1b6e4a061503deeb7ac94c18bbd36c7f47`
- Draft PR: `#46`
- base branch: `command-center/stage4-execution-fabric`
- base product SHA:
  `d43d2a6ef5a971c9049ca0ae314eafe48f00db1f`

## Locked Stage 5 behavior

Gateway mode:
`LOCAL_TRUST_GATE_ONLY`

Target host:
`YASSIN`

Authentication backend:
`NOT CONNECTED`

Live network listener:
`OFF`

Phone:
`NOT CONNECTED`

Tailscale:
`NOT CONNECTED`

GitHub transport:
`NOT CONNECTED`

Chat transport:
`NOT CONNECTED`

Phase 0 Remote Command Trust:
`G0-C = IN_TEST`

Live execution:
`NOT AUTHORIZED`

## Authority invariant

`ACCEPTED_COMMAND != EXECUTION_AUTHORITY`

Allowed trust progression:
`VALIDATED -> QUEUED_TRUSTED`

Execution projection:
`BLOCKED_PHASE0`

A trusted queue record is not a dispatch token.

## Remote command envelope

Required:
- command_id;
- nonce;
- idempotency_key;
- issued_at;
- expires_at;
- owner_id;
- device_id;
- session_id;
- target;
- effects;
- instruction;
- approval_intent;
- correlation_id.

Instruction text cannot grant authority.

## Authorization boundary

Authorization is out-of-band from the command envelope.

Required:
- principal = OWNER;
- authenticated = true;
- authentication source;
- matching owner/device/session;
- target scope;
- effect scope;
- validity window;
- non-revoked state.

The command cannot authenticate itself.

## Replay lock

Persistent replay protection is required.

Rules:
- same idempotency + same command:
  `DUPLICATE_SAME_COMMAND`
- same idempotency + changed command:
  `REJECT`
- reused nonce:
  `REJECT`
- expired command:
  `REJECT`
- excessive TTL:
  `REJECT`
- invalid clock skew:
  `REJECT`

Replay state survives service restart.

## Device/session lock

Explicit registration is required.

Fail closed on:
- unknown device;
- unknown session;
- revoked device;
- revoked session;
- expired device;
- expired session;
- owner/device/session mismatch.

No repository file contains live credentials or tokens.

## Approval lock

Display/UI approval records are not authority.

A future high-impact dispatch path must require an independently authenticated approval grant with:
- identity;
- scope;
- expiry;
- non-revoked status.

Stage 5 can validate approval records, but cannot dispatch work.

## Transport lock

Stage 5 supports local synthetic CLI/file ingress only.

It does not:
- open HTTP;
- open TCP;
- host Kestrel;
- open a public listener;
- open router ports;
- start Tailscale;
- expose YASSIN to the public Internet;
- use GitHub text as a shell command;
- use ChatGPT text as direct execution authority.

The architecture is merely compatible with a future authenticated local/Tailscale transport.

## CLI lock

Allowed:
- status
- validate-envelope
- enqueue-synthetic
- inspect-queue
- validate-approval

Forbidden:
- listen
- serve
- execute
- dispatch
- run-shell
- click
- type
- invoke-provider
- send-model-request

## Architecture lock

`View -> ViewModel -> Host -> Application Trust Service -> Infrastructure Local State`

Separate executables:
- `UniversalCouncil.CommandCenter`
- `UniversalCouncil.CommandCenter.ExecutionService`
- `UniversalCouncil.CommandCenter.RemoteGateway`

Presentation does not own:
- filesystem trust state;
- replay ledger;
- queue;
- device/session registry;
- process execution;
- network transport;
- provider dispatch.

Architecture verdict:
`PASS_STAGE5_ARCHITECTURE_BOUNDARY`

## Phase 0 source pin

Branch:
`phase0/feasibility-adversarial-prototype`

Head:
`63a4a446bc1e87f5352915f1e86c463de82e9b81`

Blobs:
- guardrails:
  `56d76a96c0ab5d74e703f69a53b2cd51d0d2843c`
- config:
  `57b26c4d8fc65c9e866ddefd826784f7826c7f24`
- tests:
  `f0ac55efd4e3462e0a1a56b376140db07fd20739`

## Exact-head verification

Stage 5 workflow:
- run #8
- ID: `39222666295`
- conclusion: `SUCCESS`

CodeQL:
- run #507
- ID: `39222666292`
- conclusion: `SUCCESS`

Company Stage 0:
- run #590
- ID: `39222666286`
- conclusion: `FAILURE`

Stage 5 Python changes pass:
- Ruff lint;
- Ruff format;
- compile.

Remaining failure:
`MemoryFabricError: invalid memory source`

This is retained as a separate pre-existing repository blocker.

## Artifacts

Command Center:
- ID: `12172278209`
- digest:
  `sha256:4cb8886b4d4cf80945159541e0963fae3ab38ccc80a1526915f0c996e8e425ba`

Execution Service:
- ID: `12172258218`
- digest:
  `sha256:bb2d55b71e58cf99b74cb80f0e3ba37f39c619a78223281eb1e10875a46c275e`

Remote Gateway:
- ID: `12171949352`
- digest:
  `sha256:cd4b49455a8d6db75ef18ef9dc97a6c684a494badcf803caeafd3f3bb2fe1532`

UI evidence:
- ID: `12172521914`
- digest:
  `sha256:d547664d9c79737b7fe72e287ee3b5f90c95f522c2303f513d3e71d923a13b29`

Read-model hashes:
- operational state:
  `25edd5d30913bcc64ba839aa025cce66fcd1952ec9548517529464acc3a34e55`
- orchestration:
  `314027108bf7ff582a0e30faea6965210e00ca20652ed9ae51d126bf37a1ca88`
- execution fabric:
  `6b8b983e97334b417898b67af512c02d139f3f1b1324601f66063d0c2b31e42b`
- remote-owner gateway:
  `af016b384c46253c26dde06989492f9bd6a22efb0af49ef76dd8435fa8fc2798`

UI:
- 1440×900:
  `sha256:bfbdc0d63bc42abcdf2b0e9d13032053810f488a8a1eb0d07759eac284860472`
- 1180×720:
  `sha256:3636b8957f834cd4172c315d360f77b4e14857041a7d1ac63448f6a4c1097a06`

## Review locks

Council:
`PASS_STAGE5_REMOTE_COMMAND_TRUST_FOUNDATION`

Studio:
`PASS_STAGE5_REMOTE_OWNER_SURFACE`

Architecture:
`PASS_STAGE5_ARCHITECTURE_BOUNDARY`

Remote transport:
`NOT_CONNECTED / G0-C_IN_TEST`

Execution:
`BLOCKED_PHASE0`

## Downstream rule

Stage 6 may introduce a **bounded authenticated transport pilot**, such as:
- loopback/local authenticated HTTP or equivalent transport;
- Tailscale-compatible private endpoint binding;
- device enrollment flow;
- short-lived authenticated sessions;
- real command round-trip evidence;
- transport health/revocation;
- explicit Owner approval transport.

Stage 6 may not:
- expose a public listener;
- open router ports;
- turn Tailscale compatibility into a claim of connection without evidence;
- make GitHub/ChatGPT text direct execution authority;
- bypass the replay ledger;
- bypass device/session identity;
- bypass Phase 0;
- enable YASSIN execution merely because G0-C passes.

Real execution still requires the separate execution gates.

## Next stage

`PHASE 6 — Authenticated Local / Tailscale Transport Pilot`

State:
`AWAITING_OWNER_STAGE6_OPEN`
