# المرتكز — Open-Source Integration Roadmap
Date: 2026-10-21
Status: APPROVED PLANNING PACKAGE / IMPLEMENTATION NOT STARTED
Parent technical audit: `14_OPEN_SOURCE_TECHNICAL_FIT_AUDIT_2026-10-21.md`
Baseline: `e201c50c091b90938ba0167037555903a63e0f10`

## Governing rule

No wave opens because the previous wave merely produced code.

A wave opens only when:
1. its exact-head tests/evidence pass;
2. security/license checks pass;
3. Murtakaz post-review accepts the evidence;
4. no authority or context invariant regresses.

Production/live execution remains blocked throughout this roadmap until a separate Owner-authorized change opens it.

---

# Wave 1 — Safety, Protocol and Evaluation Foundation

**Goal:** make external capabilities measurable and rejectable before connecting real power.

## W1-A — Contracts first
Deliverables:
- define a provider-neutral `IExternalCapabilityAdapter` contract beneath CapabilityRegistry;
- define MCP operation registration mapping, but use only fake/local test servers;
- define telemetry event schema using OpenTelemetry concepts without choosing a permanent backend;
- define external dependency manifest: project, version, license, checksum, transitive-risk state;
- define Murtakaz regression corpus categories:
  - owner authority;
  - silent fallback;
  - context staleness;
  - prompt-injection boundary;
  - capability TTL/health;
  - destructive action denial;
  - evidence overclaim;
  - memory self-promotion denial.

**Hard gate:** no network model call; no desktop action.

## W1-B — Isolated evaluation pilots
Pilot only:
- **MCP C# SDK** against a local fake server;
- **Promptfoo** against synthetic model/tool responses;
- **OpenTelemetry** local exporter/no external telemetry requirement;
- **Semgrep** custom rules for forbidden authority coupling and direct provider bypass;
- **Gitleaks vs Betterleaks** benchmark on synthetic seeded secrets, redaction, CI ergonomics and offline behavior;
- optional **Pydantic AI** worker proof using synthetic tools and disposable files.

Required evidence:
- deterministic pass/fail;
- no external framework can set capability health to HEALTHY by itself;
- no external framework can alter model fallback policy;
- test data contains no real secret.

## W1-C — Murtakaz review
Exit criteria:
- all adapter contracts are fail-closed;
- license manifest is artifact-specific;
- regressions run in CI;
- telemetry redaction policy is proven;
- one rollback path per dependency;
- no production dependency has been enabled by configuration.

**Wave 1 exit decision:** `FOUNDATION_ACCEPTED` or `RETURN_TICKET`.

---

# Wave 2 — Models, Observability and Isolated Workers

**Goal:** prove useful intelligence/workers while Murtakaz remains the governing brain.

## W2-A — Model transport pilot
Use **LiteLLM** only as a transport/gateway below `ModelBroker`.

Order:
1. mock provider;
2. local/test provider if available;
3. only later, separately authorized real external provider.

Contract:
- Murtakaz chooses model id/provider intent;
- LiteLLM cannot silently route to another model;
- fallback must be explicit allowlist + receipt;
- budgets/cost ceilings produce a typed block or owner decision;
- provider failure cannot mutate project defaults.

## W2-B — Observability + worker pilot
- self-hosted/test **Langfuse** or another OTel-compatible backend receives redacted traces;
- **Pydantic AI** executes a bounded typed worker task;
- **OpenHands Software Agent SDK** executes a coding task only inside ephemeral Docker/Kubernetes-style workspace;
- worker gets a bounded Change Envelope and cannot write governance locks.

Evidence:
- complete correlation id from Gateway -> Broker/Worker -> Tool -> Verification -> Receipt;
- cost/latency/model/tool metadata visible;
- prompts/secrets protected under redaction policy;
- sandbox escape / host-write negative tests;
- worker output remains proposal until verified.

## W2-C — Broker/worker acceptance
Required adversarial scenarios:
- primary model unavailable;
- unallowlisted fallback offered;
- provider lies about model identity;
- worker attempts to edit policy/approval/capsule;
- tracing backend unavailable;
- sandbox process crashes;
- stale capability evidence;
- repeated idempotent request.

**Wave 2 exit decision:** select the minimum proven provider set. Do not keep redundant frameworks merely because pilots succeeded.

---

# Wave 3 — Computer Use and Durable Long-Running Execution

**Goal:** address the DC gap and restart-safe work only after authority/eval foundations are proven.

## W3-A — Computer-use sandbox
Pilot **Cua Driver** on an isolated Windows test profile/VM, not production YASSIN data.

Test sequence:
- read-only UI inspection;
- safe Calculator/Notepad-style actions;
- semantic/UIA-first action;
- visual fallback action;
- focus/background behavior;
- cancellation;
- wrong-window protection;
- bounded file picker interaction;
- explicit deny test for out-of-scope target.

Required contract:
`ExecutionFabric -> bounded action envelope -> Cua adapter -> observed result -> independent verification`.

Cua never receives open-ended authority such as “do whatever is necessary”.

## W3-B — Vision fallback and architecture extraction
- extract from **Microsoft UFO** only the patterns that outperform current architecture: Host/App separation, capability/device matching, hybrid GUI/API, controlled DAG concepts;
- benchmark whether **OmniParser** is actually needed for inaccessible controls;
- if needed, perform exact model-weight/license review before use;
- semantic/native API remains preferred over pure vision.

## W3-C — Durability decision gate
Compare existing orchestration against:
- **LangGraph** for agentic state graphs;
- **Temporal** for durable workflows/retries;
- native project implementation.

Adopt one only if measured requirements exist, e.g.:
- jobs survive process/host restarts;
- multi-hour waiting/retry;
- human approval pause/resume;
- exactly-once/idempotent effect coordination;
- current implementation shows material complexity or reliability gap.

If no measured gap exists: **adopt neither**.

---

# Cross-wave acceptance matrix

| Gate | Wave 1 | Wave 2 | Wave 3 |
|---|---|---|---|
| Exact-head CI | Required | Required | Required |
| Murtakaz pre/post review | Required | Required | Required |
| License artifact pin | Required | Required | Required |
| Prompt-injection tests | Required | Required | Required |
| Silent fallback denial | Contract | Runtime | Runtime |
| Secret redaction | Synthetic | Trace proven | Trace proven |
| Sandbox isolation | Optional worker | Required | Required |
| Live YASSIN actions | Forbidden | Forbidden | Forbidden until separate approval |
| External spend | Forbidden by default | Separate approval | Separate approval |
| Rollback | Required | Required | Required |

# Stop / return-ticket triggers

Stop immediately on:
- external library bypasses `ModelBroker` or `CapabilityRegistry`;
- tool discovery implicitly grants execute permission;
- fallback occurs without explicit receipt;
- external output promotes itself to canonical truth;
- telemetry leaks prompt credentials/private content beyond policy;
- computer-use provider acts outside target envelope;
- mixed/unclear license for distributed artifact;
- integration requires weakening existing Murtakaz invariant;
- a simpler native implementation demonstrably satisfies the requirement.

# Definition of done

This roadmap is complete when we have evidence for the **smallest useful stack**, not the largest stack.

Expected target stack if pilots validate:
- Murtakaz Governance Kernel — native/current;
- ModelBroker — native/current;
- CapabilityRegistry — native/current;
- MCP C# SDK — protocol adapter;
- LiteLLM — optional model transport;
- OpenTelemetry — observability interface;
- Langfuse — optional observability/eval backend;
- Promptfoo — regression/red-team gate;
- Semgrep + secret scanner — CI guards;
- Pydantic AI/OpenHands — isolated workers only where justified;
- Cua — bounded computer-use provider only after Wave 3 acceptance.

LangGraph, Temporal, Letta, UFO and OmniParser remain optional/reference until a measured gap justifies adoption.
