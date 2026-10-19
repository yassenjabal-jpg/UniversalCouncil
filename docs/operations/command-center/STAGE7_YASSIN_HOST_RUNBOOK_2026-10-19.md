# Stage 7 — YASSIN Host Runbook
Date: 2026-10-19
Status: READY / NOT YET EXECUTED ON YASSIN

## Purpose

This runbook is the bounded real-host sequence for Stage 7.

It is not proof that any step has run.

Current truth at authoring:
- YASSIN remote agent was observed Online;
- Desktop Commander host commands are blocked by the current monthly tool-usage limit;
- Tailscale installation/login state is UNKNOWN;
- owner phone enrollment is NOT PROVEN;
- RemoteTransport deployment to YASSIN is NOT PROVEN.

## Required artifacts

Use the exact-head Stage 7 Host Kit artifact produced by the Stage 7 workflow.

The kit contains:
- `RemoteTransport/`
- `OwnerEnrollment/`
- `tools/stage7_yassin_probe.ps1`
- `tools/stage7_start_remote_transport.ps1`
- `tools/stage7_configure_tailscale_serve.ps1`
- this Stage 7 contract.

## Safety invariants

Never:
- bind RemoteTransport to `0.0.0.0`;
- enable Tailscale Funnel;
- open router ports;
- put the bearer token in GitHub;
- put a Tailscale auth key in GitHub;
- reuse a credential after revocation;
- treat Tailscale network identity as application Owner authority;
- start Execution Service work because transport succeeds.

## Sequence

### 1. Run sanitized host probe

Run in PowerShell:

`powershell -ExecutionPolicy Bypass -File .\tools\stage7_yassin_probe.ps1 -EvidencePath .\stage7-yassin-host-evidence.json`

Expected evidence is sanitized and must not contain:
- peer lists;
- account emails;
- auth keys;
- bearer tokens.

If Tailscale is absent:
- install the official Windows client;
- authenticate through the owner's approved Tailscale account;
- rerun the probe.

Do not use a reusable Tailscale auth key in this project unless separately approved and securely stored outside GitHub.

### 2. Enroll the owner phone identity

Create or choose an opaque Stage 7 device ID that does not expose private phone metadata.

Example:

`UniversalCouncil.CommandCenter.OwnerEnrollment.exe enroll-device <registry> owner-1 owner-phone-1 168`

This enrolls the application device identity for seven days.

This is separate from Tailscale device enrollment.

### 3. Issue a short-lived application session

Example:

`UniversalCouncil.CommandCenter.OwnerEnrollment.exe issue-session <registry> owner-1 owner-phone-1 30 studio PROJECT_WRITE`

The output bearer token is one-time sensitive material.

Rules:
- copy it only through an approved secure handoff;
- do not paste it into GitHub;
- do not store it in project notes;
- do not put it in screenshots;
- do not put it in ordinary logs.

The registry stores only the token SHA-256.

### 4. Start RemoteTransport on loopback

Run:

`powershell -ExecutionPolicy Bypass -File .\tools\stage7_start_remote_transport.ps1 -PublishDirectory .\RemoteTransport -RegistryPath <registry>`

Expected backend:

`http://127.0.0.1:47721`

Verify locally:

`http://127.0.0.1:47721/healthz`

No LAN/public listener is permitted.

### 5. Verify Tailscale

Run the host probe again.

Required:
- Tailscale installed;
- backend state Running;
- Funnel not configured;
- local RemoteTransport health true.

### 6. Configure private Tailscale Serve

Use an Administrator PowerShell session:

`powershell -ExecutionPolicy Bypass -File .\tools\stage7_configure_tailscale_serve.ps1`

The script may configure only:

`Tailscale Serve -> http://127.0.0.1:47721`

The script refuses:
- non-admin configuration;
- absent Tailscale;
- non-running Tailscale backend;
- failed local health;
- detected Funnel configuration.

### 7. Enroll the owner's phone in the same tailnet

Install the official Tailscale client on the owner phone and sign in to the same approved tailnet.

This is a user/account authentication step and cannot be inferred from repository state.

### 8. Real phone round trip

From the owner phone, call the private Serve URL with:
- `Authorization: Bearer <one-time-session-token>`
- `X-UC-Device-ID: owner-phone-1`
- `X-UC-Session-ID: <issued-session-id>`

First verify:
`GET /v1/status`

Required result:
- authenticated;
- execution state `BLOCKED_PHASE0`;
- live execution false.

Then send one bounded command:
`POST /v1/commands`

Required result:
- `QUEUED_TRUSTED`;
- `BLOCKED_PHASE0`.

### 9. Revocation proof

On YASSIN:

`UniversalCouncil.CommandCenter.OwnerEnrollment.exe revoke-session <registry> <session-id>`

Repeat the same phone request.

Required result:
`401 Unauthorized`

Only after this revocation round trip is Stage 7 eligible for final lock.

## Recovery

If RemoteTransport fails:
- do not switch to public bind;
- stop the failed process;
- preserve queue/replay evidence;
- restart only from the exact approved artifact.

If Tailscale Serve fails:
- do not use Funnel as fallback;
- inspect `tailscale status --json`;
- inspect `tailscale serve status --json`;
- leave Stage 7 unproven until the private path works.

## Exit condition

Stage 7 final lock requires real evidence for:
- YASSIN host probe;
- Tailscale private Serve;
- owner-phone authenticated status;
- owner-phone bounded command;
- execution still blocked;
- session revocation rejection.

Until all are present:
`STAGE7_REAL_HOST_EVIDENCE_PENDING`
