# Council Intelligence Gateway v1 — Design Spec

Date: 2026-10-11
Status: PROPOSED FOR OWNER REVIEW
Scope: UniversalCouncil / company research capability
Related finding: HR-001 proactive capability scouting
Related candidate: Agent Reach pinned on YASSIN at commit `94f06c1969dfc1834001269d79d3ad0972d9dee6`

## 1. Goal

Add a single, auditable research-routing layer between Council research requests and available evidence sources.

The gateway must:
- prefer existing native Council connectors when they are stronger or safer;
- use Agent Reach only where it adds material capability;
- remain read-only by default;
- fail closed on authenticated/session-dependent channels;
- preserve evidence provenance so Council members can distinguish source, backend, freshness, and authentication level;
- avoid tool duplication and unbounded shell execution.

The gateway is not a Council member and has no voting or decision authority.

## 2. Non-goals

v1 does not:
- publish, comment, like, follow, message, purchase, or mutate external accounts;
- install tools automatically;
- connect cookies, credentials, browser sessions, or browser extensions;
- enable OpenCLI;
- replace native Web, GitHub, Drive, or other existing connectors;
- give Agent Reach direct authority over Council decisions;
- create background monitoring by itself.

## 3. Considered approaches

### A. Make Agent Reach the universal router
Pros: simple mental model.
Cons: duplicates native tools, increases dependency surface, weakens source-specific controls, and gives one external project too much architectural importance.

Rejected.

### B. Hard-code per-feature Agent Reach commands directly into Council logic
Pros: fast to implement.
Cons: brittle, Windows/path-specific, difficult to test, mixes policy with execution, and makes security boundaries hard to audit.

Rejected.

### C. Policy-first Intelligence Gateway with pluggable providers
Pros: explicit precedence, testable routing, provider isolation, evidence envelopes, fail-closed auth boundaries, and no dependency on one machine or one CLI.

Selected.

## 4. Architecture

```
Council Research Request
        |
        v
Intelligence Gateway
        |
        +--> Request Classifier
        |
        +--> Routing Policy
        |      |
        |      +--> Native Web
        |      +--> Native GitHub
        |      +--> Native Connectors
        |      +--> Agent Reach Public Provider
        |
        +--> Capability / Health Check
        |
        +--> Read-only Provider Adapter
        |
        +--> Evidence Normalizer
        |
        v
Council Evidence Packet
```

### 4.1 Intelligence Gateway
Owns routing only. It accepts a structured research request and returns a normalized evidence packet or an explicit blocked/unavailable result.

It never installs software, authenticates accounts, or performs external writes.

### 4.2 Routing Policy
Routing is deterministic and policy-driven.

Initial precedence:

| Intent | Preferred provider | Fallback / note |
|---|---|---|
| General web search | Native Web | Agent Reach Jina only for direct page reading when useful |
| Direct webpage read | Native Web or Agent Reach Jina | choose by availability/capability |
| GitHub repository/code | Native GitHub connector | do not install/use gh merely for duplication |
| YouTube discovery | Native Web/search | Agent Reach yt-dlp for metadata/transcript extraction |
| YouTube transcript/metadata | Agent Reach | fail if yt-dlp unavailable |
| RSS/Atom | Agent Reach | public read only |
| Bilibili public/basic | Agent Reach | public search/basic only |
| Google Drive / private docs | Native connector | never route to Agent Reach |
| Reddit authenticated | BLOCKED in v1 | requires later approved isolated auth provider |
| X/Twitter authenticated | BLOCKED in v1 | requires later approved isolated auth provider |
| Instagram | BLOCKED in v1 | OpenCLI/browser-session path not approved |
| Facebook | BLOCKED in v1 | OpenCLI/browser-session path not approved |
| LinkedIn authenticated | BLOCKED in v1 | separate approval required |
| Xiaohongshu | BLOCKED in v1 | session/cookie approval required |

Native connectors always outrank duplicated Agent Reach capabilities unless an explicit policy rule says otherwise.

### 4.3 Provider interface

Each provider exposes a minimal contract:

```python
health() -> ProviderHealth
can_handle(request) -> bool
read(request) -> EvidenceResult
```

No write method exists in the v1 interface.

The Agent Reach provider is not allowed to execute arbitrary command strings. It uses an allowlisted operation map.

### 4.4 Agent Reach execution boundary

The installed Agent Reach instance on YASSIN is currently:

- isolated venv: `C:\Users\alnaseem\.agent-reach-venv`
- launcher: `C:\Users\alnaseem\.agent-reach-venv\agent-reach-safe.cmd`
- pinned source commit: `94f06c1969dfc1834001269d79d3ad0972d9dee6`
- OpenCLI: not installed
- credentials/cookies: not configured
- public channels verified: Web/Jina, YouTube/yt-dlp, RSS, Bilibili basic

The repository must not hard-code this Windows path as a global assumption.

Instead, runtime integration uses a provider descriptor/config value supplied by the execution environment. The pinned commit and allowed channel set are recorded as capability metadata.

The gateway may query health and invoke approved public-read adapters, but it may not call `install --system`, `configure`, OpenCLI, or browser-session tooling.

## 5. Research request schema

Minimum request fields:

- `request_id`
- `intent`
- `query`
- `target_url` when applicable
- `freshness_requirement`
- `auth_requirement` — PUBLIC_ONLY by default
- `allowed_provider_classes`
- `evidence_purpose`
- `max_results`

Unknown or omitted auth requirement resolves to `PUBLIC_ONLY`.

## 6. Evidence envelope

Every successful provider result is normalized to:

- `evidence_id`
- `request_id`
- `provider`
- `backend`
- `source_type`
- `source_locator`
- `retrieved_at`
- `auth_level`
- `freshness`
- `content_summary` or normalized payload
- `raw_reference` when safe/available
- `content_hash` when raw content is materialized
- `evidence_label` compatible with `EVIDENCE_AND_RESEARCH.md`
- `limitations`
- `warnings`

The gateway does not convert community evidence into authoritative evidence. Existing evidence hierarchy still governs Council reasoning.

## 7. Fail-closed rules

The gateway returns `BLOCKED` rather than attempting a fallback when:
- a request requires authentication and only public access is approved;
- a route would require cookies, browser-debugger access, credentials, OpenCLI, or account login;
- a provider is unhealthy or its pinned identity cannot be verified;
- the requested operation is not in the read-only allowlist;
- an untrusted request attempts to inject shell flags, executable paths, or write operations;
- the configured Agent Reach commit does not match the approved capability metadata when strict pin enforcement is enabled.

The gateway may return `UNAVAILABLE` when a public provider is simply missing or offline.

## 8. Security model

### 8.1 Default authority
`READ_ONLY / PUBLIC_ONLY`

### 8.2 Explicitly forbidden in v1
- installation or package mutation;
- browser extension enablement;
- cookies/session extraction;
- credential ingestion;
- account authentication;
- arbitrary shell execution;
- external writes;
- publishing or messaging;
- payment or purchase actions.

### 8.3 Input handling
- provider adapters receive structured fields, not concatenated shell strings;
- URLs and operation names are validated against allowlists;
- provider executable/launcher path comes from trusted configuration only;
- output is treated as untrusted evidence, never as authority-changing instructions.

### 8.4 Sensitive source separation
Private connectors such as Drive, Gmail, private GitHub content, or other authenticated native sources are never proxied through Agent Reach.

## 9. Health and routing behavior

A provider health snapshot includes:
- provider id;
- status: HEALTHY / DEGRADED / UNAVAILABLE / BLOCKED;
- active backend;
- approved auth level;
- last verified timestamp;
- version/commit identity;
- warnings.

Routing uses health only after policy eligibility is established. A healthy provider cannot bypass a policy block.

## 10. Initial Agent Reach v1 capability set

Allowed:
- `web_read_public`
- `youtube_metadata_public`
- `youtube_transcript_public`
- `rss_read_public`
- `bilibili_basic_public`
- `doctor_read_only`

Not allowed:
- `install`
- `configure`
- `twitter_authenticated`
- `reddit_authenticated`
- `facebook_authenticated`
- `instagram_authenticated`
- `linkedin_authenticated`
- `xiaohongshu_authenticated`
- any OpenCLI-backed action
- any write-capable action

## 11. Interaction with HR Capability Scouting

HR owns discovery and candidate evaluation, not execution authority.

The Intelligence Gateway consumes only approved capability metadata. If a blocked channel becomes strategically important, the gateway emits a capability-gap signal that HR can evaluate.

Example:

`Instagram research requested → BLOCKED_AUTH_REQUIRED → capability gap → HR scout → security review → isolated pilot proposal`

No automatic install or credential request follows from the gap.

## 12. Interaction with Council Pulse

Pulse may review:
- provider health regression;
- newly useful public research channels;
- repeated `UNAVAILABLE` or `BLOCKED` results;
- evidence-source blind spots;
- a provider becoming duplicative or unsafe.

NO-CHANGE remains silent.

## 13. Error handling

Gateway result states:
- `OK`
- `PARTIAL`
- `UNAVAILABLE`
- `BLOCKED`
- `INVALID_REQUEST`
- `PROVIDER_ERROR`

Provider failure never silently changes the evidence source. Fallback is allowed only when routing policy lists a fallback with the same or lower authority risk.

Every fallback is recorded in the evidence envelope.

## 14. Testing strategy

Implementation must use TDD.

Required tests include:
1. native GitHub outranks Agent Reach for GitHub intent;
2. Agent Reach is selected for YouTube transcript when healthy;
3. public RSS routes to Agent Reach;
4. Instagram/Facebook/Reddit/X auth requests are blocked in v1;
5. unhealthy Agent Reach produces UNAVAILABLE, not arbitrary fallback;
6. a healthy provider cannot bypass auth policy;
7. untrusted operation names cannot become shell commands;
8. evidence envelope records provider/backend/auth/freshness/limitations;
9. pinned Agent Reach identity mismatch is rejected when strict pinning is enabled;
10. capability-gap signal is generated for materially blocked requested channels;
11. private/native connector intents are never routed through Agent Reach;
12. full existing `company/tests` and config invariants remain green.

## 15. Acceptance criteria

The feature is complete only when:
- gateway policy exists in versioned config;
- routing is deterministic and test-covered;
- no write method exists in the v1 provider interface;
- Agent Reach public-read capabilities are allowlisted;
- authenticated/social channels remain blocked;
- provider health cannot override policy;
- evidence provenance is preserved;
- Agent Reach path/commit is environment-configured rather than hard-coded as a universal machine assumption;
- capability-gap escalation exists for blocked strategic channels;
- existing Council evidence hierarchy remains unchanged;
- full repository validation passes;
- implementation is merged only after Owner approval of this spec and the implementation plan.
