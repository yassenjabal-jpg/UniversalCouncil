# المرتكز — Open-Source Technical Fit Audit
Date: 2026-10-21
Status: MURTAKAZ REVIEWED / PLANNING-ONLY / NO RUNTIME ADOPTION
Change: CC-OSS-FIT-2026-10-21
Canonical baseline: `e201c50c091b90938ba0167037555903a63e0f10`
Parent branch: `command-center/capability-registry-model-broker-20261021`

## 1. Executive decision

The audit rejects the idea of replacing **المرتكز** with a general agent framework.

The current project already has stronger project-local boundaries for authority, context freshness, explicit model fallback, capability health, owner control and exact-head evidence. External projects may provide **execution engines, protocol adapters, telemetry, evaluation, or isolated workers**, but none may become the authority source.

Adoption law:

`Murtakaz policy -> typed request -> bounded adapter -> external engine -> verified result -> Murtakaz receipt`

Never:

`external framework -> decides authority/policy/project truth`

## 2. Current architecture fit

The baseline already contains:
- `ModelBroker`: owner-controlled model selection; provider calls currently disconnected.
- `CapabilityRegistry`: operation/provider/host-specific health with TTL and fail-closed states.
- `ContextCapsuleCompiler`: immutable bounded task truth.
- `GatewayRouting`: staged routing rather than one opaque agent choice.
- `ExecutionFabric`: separate execution boundary with live execution locked.
- mandatory Murtakaz pre/post review and Change-of-Truth handling.

Therefore the correct strategy is **adapter-first integration**, not framework-first reconstruction.

## 3. Candidate matrix

| Candidate | Primary fit | Disposition | Why | Boundary / risk |
|---|---|---|---|---|
| [LiteLLM](https://github.com/BerriAI/litellm) | Provider gateway beneath ModelBroker | **PILOT-A** | Unified multi-provider invocation, spend/guardrail/gateway capabilities | Disable/ignore autonomous routing/fallback unless mapped from explicit Murtakaz policy. OSS is MIT outside enterprise-scoped code; pin exact components. |
| [Pydantic AI](https://github.com/pydantic/pydantic-ai) | Typed Python worker runtime / eval harness | **PILOT-A** | Typed tools/outputs, durable-execution hooks, agent/eval primitives; matches Python 3.12 repo tooling | Do not put it above C# Gateway or let agent harness rewrite authority. Best first use is bounded worker/eval process. MIT. |
| [MCP C# SDK](https://github.com/modelcontextprotocol/csharp-sdk) | Native .NET Capability Bus | **PILOT-A / HIGH PRIORITY** | Direct fit with Command Center C#; client/server, DI/hosting, HTTP/stdio, task extensions | MCP tool metadata is capability description, not authorization. Every tool must resolve through CapabilityRegistry + authority policy. Recheck package/license/version at implementation. |
| [Langfuse](https://github.com/langfuse/langfuse) | LLM/agent tracing and evaluation backend | **PILOT-A** | Strong observability, self-host option, trace/cost/eval visibility | Telemetry must redact secrets and never become canonical evidence by itself. MIT outside enterprise directories. |
| [Promptfoo](https://github.com/promptfoo/promptfoo) | Regression / red-team gate | **PILOT-A** | Local evals, model comparisons, red-team and CI gating | Evaluation configuration must be pinned; model-as-judge cannot self-approve governance. MIT. |
| [Cua](https://github.com/trycua/cua) | Computer-use provider beneath ExecutionFabric | **PILOT-B** | Windows/macOS/Linux desktop automation; CLI/MCP/SDK; useful DC alternative | Highest operational risk. Sandbox/throwaway test profile only; no YASSIN live dispatch until explicit later approval. Licensing is component-sensitive despite MIT core; recheck exact packages. |
| [OpenHands Software Agent SDK](https://github.com/OpenHands/software-agent-sdk) | Isolated coding worker | **PILOT-B** | Ephemeral Docker/Kubernetes workspaces and code-agent SDK | Never run unsandboxed on project host by default. Worker receives bounded workspace/change envelope, not whole-machine authority. |
| [LangGraph](https://github.com/langchain-ai/langgraph) | Long-running stateful orchestration | **DEFER** | Durable execution + human-in-loop + persistence is valuable | Current project already has typed orchestration. Adopt only if a measured workflow cannot be expressed cleanly without it; avoid duplicate state machines. |
| [Temporal](https://github.com/temporalio/temporal) | Durable workflow engine | **DEFER** | Mature retry/resume semantics | Operational weight is unjustified before we prove need for multi-hour/restart-safe jobs. MIT. |
| [Microsoft UFO](https://github.com/microsoft/UFO) | Architecture reference for GUI/device orchestration | **REFERENCE** | Hybrid GUI/API, Windows agent separation, dynamic DAG/capability matching | Study patterns only first; do not introduce a second governing orchestrator. MIT. |
| [Letta Code](https://github.com/letta-ai/letta-code) | Memory architecture reference | **REFERENCE WITH HARD FIREWALL** | Git-backed memory, searchable context, long-horizon agent memory | Its self-modifying memory/prompts/harness conflict with immutable project truth. Borrow versioned-memory ideas only; no autonomous promotion to canonical state. Apache-2.0 reported by repo. |
| [OmniParser](https://github.com/microsoft/OmniParser) | Vision fallback for inaccessible GUI | **DEFER / LICENSE GATE** | Screen parsing can rescue cases where UIA/semantic APIs fail | Repository license and model-weight licenses are mixed/nuanced; earlier detectors include AGPL lineage, newer weights differ. No dependency until exact artifact license review. |
| [Gitleaks](https://github.com/gitleaks/gitleaks) | Secret scanning | **USE CONSERVATIVELY** | Mature detector and CI/pre-commit integration | Upstream states feature development is complete and future releases focus on security fixes. Keep as stable baseline, not sole future strategy. MIT. |
| [Betterleaks](https://github.com/betterleaks/betterleaks) | Next-generation secret scanning candidate | **EVALUATE IN WAVE 1** | Active successor direction; supports validation/analysis modes | Newer project; must benchmark false positives, offline behavior, credential validation safety and CI ergonomics before replacement. |
| [Semgrep](https://github.com/semgrep/semgrep) | Static architecture/security rules | **PILOT-A** | C#, Python, JSON/YAML and CI support; custom rules can enforce Murtakaz invariants | Community engine has analysis limits; repo licensing is not simple MIT (LGPL-2.1 core in current repository). Use CLI separation and review redistribution obligations. |
| [OpenTelemetry Python](https://github.com/open-telemetry/opentelemetry-python) and .NET ecosystem | Vendor-neutral telemetry substrate | **ADOPT AS INTERFACE, BACKEND LATER** | Prevents observability lock-in and can feed Langfuse/other backends | Telemetry is evidence-supporting metadata, never authority. Prefer OTel API boundary before backend-specific calls. |

## 4. Fit scores

Scale: 5 = excellent. Risk is inverse: 5 = highest risk.

| Candidate | Architecture fit | Immediate value | Lock-in resistance | Operational cost | Risk | Murtakaz verdict |
|---|---:|---:|---:|---:|---:|---|
| MCP C# SDK | 5 | 5 | 5 | 2 | 2 | Start first |
| Promptfoo | 5 | 5 | 5 | 2 | 2 | Start first |
| OpenTelemetry | 5 | 4 | 5 | 2 | 2 | Interface first |
| LiteLLM | 5 | 5 | 4 | 3 | 3 | Controlled sidecar pilot |
| Langfuse | 4 | 5 | 4 | 3 | 2 | Self-host pilot |
| Pydantic AI | 4 | 4 | 4 | 3 | 3 | Worker/eval pilot |
| Semgrep | 4 | 4 | 4 | 2 | 2 | CI-only pilot |
| Cua | 4 | 5 | 4 | 3 | 5 | Sandbox only |
| OpenHands SDK | 4 | 4 | 4 | 4 | 4 | Sandboxed coding worker |
| UFO | 4 | 3 | 5 | 4 | 4 | Pattern extraction |
| LangGraph | 3 | 3 | 3 | 4 | 3 | Defer |
| Temporal | 4 | 2 | 4 | 5 | 3 | Defer |
| Letta Code | 2 | 3 | 3 | 3 | 5 | Memory ideas only |
| OmniParser | 3 | 3 | 3 | 4 | 5 | License + benchmark gate |

## 5. Non-negotiable adapter contracts

### 5.1 Model providers
- `ModelBroker` remains the only selector visible to project logic.
- LiteLLM may execute a selected provider/model, but may not silently choose a different model.
- Any LiteLLM retry/fallback must be disabled or constrained to an explicit Murtakaz-issued allowlist and surfaced in the Work Receipt.
- Cost/budget telemetry is advisory input; exceeding a threshold produces a typed blocked/owner-decision state, not an invisible downgrade.

### 5.2 MCP
- Tool discovery != authorization.
- MCP server content is untrusted capability metadata until registered.
- Each operation maps to CapabilityRegistry fields: provider, operation, effect, risk, host, auth, version, health, TTL, evidence.
- A newly discovered MCP tool starts `IN_TEST` or `BLOCKED`, never `HEALTHY` by discovery alone.

### 5.3 Computer use
- Cua/GUI provider cannot decide target, authority, or destructive scope.
- ExecutionFabric issues a bounded action envelope.
- Computer provider returns action/evidence/observed state.
- Verification must be separate from execution for material actions.
- No pilot touches production data or live owner sessions.

### 5.4 Agent runtimes
- Pydantic AI/OpenHands agents cannot edit governing policy, approval records or canonical Context Capsules.
- They operate in disposable workspaces/worktrees with explicit file/tool allowlists.
- Their outputs are proposals until Murtakaz verification promotes them.

### 5.5 Memory
- External memory systems may suggest updates.
- Canonical project memory/history stays append/supersede, never autonomous rewrite.
- Letta-style self-editing is forbidden for governance and locked truth.

## 6. License and supply-chain gate

Before any implementation dependency:
1. pin repository + release/version + artifact checksum;
2. capture the exact license for the consumed package, not only repository badge;
3. enumerate transitive dependencies and model weights;
4. reject unclear mixed licensing for production use;
5. produce SBOM for any distributable component;
6. run secret/static/dependency scans in CI;
7. record upstream update policy and rollback path.

Special cases:
- LiteLLM and Langfuse contain enterprise-scoped directories under separate terms; consume only clearly OSS surfaces unless separately approved.
- OmniParser has nuanced repository/model-weight licensing; no production adoption without artifact-level review.
- Semgrep Community Edition is useful but is not equivalent to paid cross-file/security engines; treat coverage claims conservatively.
- Cua includes multiple components/products; verify the exact component license before packaging.

## 7. Rejected approaches

The audit rejects:
- replacing the Murtakaz orchestration core with CrewAI/AutoGen/LangGraph/Letta/OpenHands;
- letting LiteLLM own model policy;
- using Cua as an unrestricted Desktop Commander replacement;
- using autonomous memory mutation as project truth;
- adding all frameworks simultaneously;
- connecting a real provider merely to prove the integration works;
- accepting a GitHub star count/demo as evidence of production suitability.

## 8. Decision

Proceed with the three-wave roadmap in the companion document.

No runtime dependency is approved by this audit itself.

The first implementation wave must remain a **contract + sandbox + CI** wave and must pass Murtakaz post-review before any live provider connection or desktop control is considered.
