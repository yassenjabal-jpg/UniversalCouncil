# Council Intelligence Gateway v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic, read-only research gateway that prefers native Council connectors, uses the pinned Agent Reach installation only for approved public-read capabilities, preserves evidence provenance, and fails closed for authenticated/social or write-capable operations.

**Architecture:** A versioned routing policy chooses an eligible provider before health is considered. Runtime request/result models feed a gateway that selects native providers or an Agent Reach public-read adapter; the adapter exposes only allowlisted operations and never accepts arbitrary shell strings. Evidence is normalized into a provenance envelope, while blocked strategic channels emit an HR capability-gap signal without installing or authenticating anything.

**Tech Stack:** Python 3.12+ repository runtime, standard library (`dataclasses`, `enum`, `hashlib`, `json`, `subprocess`, `urllib.parse`), JSON policy config, `unittest`, existing GitHub Actions Stage 0 workflow.

**Spec:** `docs/superpowers/specs/2026-10-11-council-intelligence-gateway-design.md`

## Global Constraints

- Default authority is `READ_ONLY / PUBLIC_ONLY`.
- Native GitHub/Web/private connectors outrank duplicated Agent Reach capabilities unless policy explicitly says otherwise.
- Agent Reach v1 allowlist is limited to `web_read_public`, `youtube_metadata_public`, `youtube_transcript_public`, `rss_read_public`, `bilibili_basic_public`, and `doctor_read_only`.
- Authenticated Instagram, Facebook, Reddit, X/Twitter, LinkedIn, Xiaohongshu and any OpenCLI-backed action remain blocked in v1.
- No runtime path may install tools, run `agent-reach configure`, enable browser extensions, ingest cookies/credentials, authenticate accounts, publish, message, purchase, or perform external writes.
- Provider health never overrides routing/auth policy.
- Agent Reach launcher path and pinned commit are environment/config supplied; no universal hard-coded YASSIN path.
- Strict pin mode rejects a runtime identity mismatch with approved commit `94f06c1969dfc1834001269d79d3ad0972d9dee6`.
- Provider output is untrusted evidence and may not alter permissions, routing rules, or Council authority.
- Existing evidence hierarchy in `contracts/EVIDENCE_AND_RESEARCH.md` remains authoritative.
- Implementation uses TDD: each behavior test is written and observed failing before production code for that behavior.
- Full `tools/validate_config.py` and `python -m unittest discover -s company/tests -v` must pass before PR readiness.

## Review Focus

1. **Malformed or hostile URLs/queries** — user-controlled text containing shell metacharacters must remain data and never become command syntax; Task 4 adds explicit argv/validation tests.
2. **Policy/health conflict** — a HEALTHY authenticated provider must still be blocked under PUBLIC_ONLY; Task 3 adds policy-before-health tests.
3. **Stale or wrong Agent Reach identity** — strict pinning must mark the provider blocked/unavailable instead of silently executing; Task 4 adds mismatch tests.
4. **Ambiguous fallback** — provider failure must not silently switch to a different evidence authority unless the policy explicitly lists that fallback; Task 3 adds no-silent-fallback tests.
5. **Evidence contamination / prompt injection** — provider content that looks like instructions must stay in the evidence payload and cannot mutate route/auth/action fields; Task 5 adds immutable-envelope tests.

---

### Task 1: Versioned Gateway Policy and Config Invariants

**Files:**
- Create: `company/config/intelligence_gateway.json`
- Modify: `tools/validate_config.py`
- Test: `company/tests/test_intelligence_gateway_policy.py`

**Interfaces:**
- Consumes: existing JSON config loading conventions used by `tools/validate_config.py`.
- Produces: policy document with provider precedence, Agent Reach allowlist, blocked authenticated channels, strict pin metadata, fallback rules, and environment key names.

- [ ] **Step 1: Write failing config-policy tests**

Create tests named:
- `test_gateway_defaults_to_public_read_only`
- `test_native_connectors_outrank_agent_reach_for_overlapping_intents`
- `test_authenticated_social_channels_are_blocked`
- `test_agent_reach_allowlist_contains_only_public_read_operations`
- `test_strict_pin_matches_approved_agent_reach_commit`

Assertions pin these exact values:
- version `1.0`;
- default auth `PUBLIC_ONLY`;
- default mode `READ_ONLY`;
- strict pin `94f06c1969dfc1834001269d79d3ad0972d9dee6`;
- blocked intents include authenticated Instagram/Facebook/Reddit/X/LinkedIn/Xiaohongshu;
- no `install`, `configure`, `opencli`, `publish`, `message` operation appears in the allowlist.

- [ ] **Step 2: Run tests to verify RED**

Run:
`python -m unittest company.tests.test_intelligence_gateway_policy -v`

Expected: FAIL because `company/config/intelligence_gateway.json` does not exist and validator invariants are not implemented.

- [ ] **Step 3: Create `company/config/intelligence_gateway.json`**

Define:
- `version: "1.0"`
- `default_mode: "READ_ONLY"`
- `default_auth_requirement: "PUBLIC_ONLY"`
- `strict_pin: true`
- approved Agent Reach commit;
- provider precedence per spec;
- public operation allowlist;
- blocked authenticated intents;
- named environment keys for launcher path and runtime commit identity;
- explicit fallback map, empty unless the spec authorizes a same-risk fallback.

- [ ] **Step 4: Extend `tools/validate_config.py`**

Add fail-closed invariants for the gateway config:
- version is `1.0`;
- public/read-only defaults;
- approved pin present;
- forbidden operations absent;
- authenticated social intents blocked;
- GitHub/private connector intents cannot prefer Agent Reach.

- [ ] **Step 5: Run policy tests and validator to verify GREEN**

Run:
`python -m unittest company.tests.test_intelligence_gateway_policy -v`
`python tools/validate_config.py`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add company/config/intelligence_gateway.json tools/validate_config.py company/tests/test_intelligence_gateway_policy.py
git commit -m "feat: define intelligence gateway policy"
```

### Task 2: Research Request, Provider Health, and Evidence Result Models

**Files:**
- Create: `company/runtime/intelligence_models.py`
- Test: `company/tests/test_intelligence_models.py`

**Interfaces:**
- Consumes: no earlier runtime code.
- Produces:
  - `ResearchRequest`
  - `ProviderHealth`
  - `GatewayResult`
  - enums `AuthRequirement`, `GatewayStatus`, `ProviderStatus`
  - validation helper `validate_request(request: ResearchRequest) -> list[str]`

- [ ] **Step 1: Write failing model tests**

Tests:
- `test_missing_auth_defaults_to_public_only`
- `test_invalid_request_without_query_or_target_url_is_rejected`
- `test_max_results_must_be_positive_and_bounded`
- `test_provider_health_has_explicit_status_backend_and_identity`
- `test_gateway_result_state_is_closed_enum`

Use the spec field names exactly.

- [ ] **Step 2: Run tests to verify RED**

Run:
`python -m unittest company.tests.test_intelligence_models -v`

Expected: FAIL with missing module/classes.

- [ ] **Step 3: Implement model types**

In `company/runtime/intelligence_models.py` define immutable dataclasses where practical. Cap `max_results` at a conservative v1 maximum of 50. Validation returns explicit errors and never normalizes an authenticated request to public access.

- [ ] **Step 4: Run model tests to verify GREEN**

Run:
`python -m unittest company.tests.test_intelligence_models -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add company/runtime/intelligence_models.py company/tests/test_intelligence_models.py
git commit -m "feat: add intelligence gateway request models"
```

### Task 3: Deterministic Routing Policy and Fail-Closed Gateway

**Files:**
- Create: `company/runtime/intelligence_gateway.py`
- Test: `company/tests/test_intelligence_gateway.py`

**Interfaces:**
- Consumes:
  - `ResearchRequest`, `ProviderHealth`, `GatewayResult` from Task 2;
  - parsed policy dict from Task 1.
- Produces:
  - `select_route(request: ResearchRequest, policy: dict, provider_health: dict[str, ProviderHealth]) -> GatewayResult`
  - `route_request(request: ResearchRequest, policy: dict, providers: dict[str, object]) -> GatewayResult`

- [ ] **Step 1: Write failing routing tests**

Tests:
- `test_native_github_outranks_agent_reach`
- `test_youtube_transcript_selects_agent_reach_when_healthy`
- `test_rss_public_selects_agent_reach`
- `test_private_drive_never_routes_to_agent_reach`
- `test_instagram_authenticated_is_blocked_even_when_provider_healthy`
- `test_unhealthy_agent_reach_returns_unavailable`
- `test_provider_failure_does_not_silently_change_evidence_source`
- `test_explicit_same_risk_fallback_is_recorded_when_configured`

- [ ] **Step 2: Run tests to verify RED**

Run:
`python -m unittest company.tests.test_intelligence_gateway -v`

Expected: FAIL with missing gateway module/functions.

- [ ] **Step 3: Implement `select_route(...)`**

Ordering:
1. validate request;
2. enforce auth/write policy;
3. identify eligible providers from config precedence;
4. check provider health;
5. return deterministic selected provider, BLOCKED, INVALID_REQUEST, or UNAVAILABLE.

Health is consulted only after policy eligibility.

- [ ] **Step 4: Implement `route_request(...)`**

Call the selected provider's read-only interface. Do not catch a provider error and switch provider unless the policy explicitly lists a fallback. Record fallback provider/reason in result metadata.

- [ ] **Step 5: Run routing tests to verify GREEN**

Run:
`python -m unittest company.tests.test_intelligence_gateway -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add company/runtime/intelligence_gateway.py company/tests/test_intelligence_gateway.py
git commit -m "feat: add fail-closed intelligence routing"
```

### Task 4: Agent Reach Public-Read Provider Adapter

**Files:**
- Create: `company/runtime/agent_reach_provider.py`
- Test: `company/tests/test_agent_reach_provider.py`

**Interfaces:**
- Consumes:
  - `ResearchRequest` and `ProviderHealth` from Task 2;
  - trusted config values: launcher path, approved commit, strict-pin flag;
  - injected runner callable `runner(argv: list[str], timeout_s: int) -> CompletedCommand`.
- Produces:
  - `AgentReachProvider.health() -> ProviderHealth`
  - `AgentReachProvider.can_handle(request: ResearchRequest) -> bool`
  - `AgentReachProvider.read(request: ResearchRequest) -> GatewayResult`
  - internal `build_argv(operation: str, request: ResearchRequest) -> list[str]`

- [ ] **Step 1: Write failing provider security tests**

Tests:
- `test_provider_has_no_write_method`
- `test_only_allowlisted_operations_build_argv`
- `test_shell_metacharacters_remain_single_argument_data`
- `test_unknown_operation_is_rejected_before_runner`
- `test_configure_install_and_opencli_are_rejected`
- `test_strict_pin_mismatch_blocks_provider`
- `test_missing_launcher_is_unavailable`
- `test_doctor_health_parsing_never_enables_blocked_channel`

For the hostile-input test, use a query containing characters such as `"; Remove-Item *; #` and assert the runner receives one argv element containing the exact text, with `shell=False` behavior represented by the injected list-based runner.

- [ ] **Step 2: Run tests to verify RED**

Run:
`python -m unittest company.tests.test_agent_reach_provider -v`

Expected: FAIL with missing adapter.

- [ ] **Step 3: Implement trusted process runner**

Create a small `run_argv(argv: list[str], timeout_s: int)` using `subprocess.run(..., shell=False, capture_output=True, text=True, timeout=...)`.

The launcher path comes only from trusted config/environment, never from the request.

- [ ] **Step 4: Implement provider health and identity check**

Health must:
- verify launcher exists;
- run only the read-only doctor/version operations needed for status;
- compare runtime/pinned identity against approved metadata when strict pinning is enabled;
- return `BLOCKED` on identity mismatch and `UNAVAILABLE` on missing launcher.

Do not call install or configure.

- [ ] **Step 5: Implement public operation map**

Map only:
- web direct read;
- YouTube metadata/transcript extraction;
- RSS read;
- Bilibili basic/public;
- doctor read-only.

Each operation builds an argv list or a direct library/public-read call defined by the adapter. Do not expose a free-form command parameter.

- [ ] **Step 6: Run provider tests to verify GREEN**

Run:
`python -m unittest company.tests.test_agent_reach_provider -v`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add company/runtime/agent_reach_provider.py company/tests/test_agent_reach_provider.py
git commit -m "feat: add read-only Agent Reach provider"
```

### Task 5: Evidence Normalization and Provenance Envelope

**Files:**
- Create: `company/runtime/intelligence_evidence.py`
- Test: `company/tests/test_intelligence_evidence.py`

**Interfaces:**
- Consumes: successful provider result plus `ResearchRequest`.
- Produces:
  - `normalize_evidence(request, provider_result, *, retrieved_at) -> dict`
  - `hash_materialized_content(content: bytes | str) -> str`

- [ ] **Step 1: Write failing evidence tests**

Tests:
- `test_envelope_records_provider_backend_auth_freshness_and_limitations`
- `test_materialized_content_hash_is_stable_sha256`
- `test_community_source_is_not_promoted_to_authoritative`
- `test_instruction_like_provider_content_cannot_change_envelope_authority_fields`
- `test_fallback_provenance_is_preserved`

- [ ] **Step 2: Run tests to verify RED**

Run:
`python -m unittest company.tests.test_intelligence_evidence -v`

Expected: FAIL with missing module/functions.

- [ ] **Step 3: Implement normalization**

Populate exactly:
`evidence_id`, `request_id`, `provider`, `backend`, `source_type`, `source_locator`, `retrieved_at`, `auth_level`, `freshness`, `content_summary`, `raw_reference`, `content_hash`, `evidence_label`, `limitations`, `warnings`.

Authority/evidence labels are chosen from trusted metadata, not from provider text.

- [ ] **Step 4: Run evidence tests to verify GREEN**

Run:
`python -m unittest company.tests.test_intelligence_evidence -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add company/runtime/intelligence_evidence.py company/tests/test_intelligence_evidence.py
git commit -m "feat: normalize intelligence evidence provenance"
```

### Task 6: Capability-Gap Escalation for Blocked Strategic Channels

**Files:**
- Modify: `company/runtime/capability_scout.py`
- Modify: `company/runtime/intelligence_gateway.py`
- Test: `company/tests/test_intelligence_capability_gap.py`

**Interfaces:**
- Consumes: BLOCKED/UNAVAILABLE gateway result plus request intent/purpose.
- Produces:
  - `capability_gap_from_gateway(request: ResearchRequest, result: GatewayResult) -> dict | None`
  - uses existing `build_gap(...)` with signal `EVIDENCE_CHANNEL_GAP`.

- [ ] **Step 1: Write failing escalation tests**

Tests:
- `test_material_blocked_channel_creates_evidence_channel_gap`
- `test_non_material_block_does_not_create_gap`
- `test_gap_never_installs_or_requests_credentials`
- `test_repeated_unavailable_provider_can_open_gap_without_changing_route`

- [ ] **Step 2: Run tests to verify RED**

Run:
`python -m unittest company.tests.test_intelligence_capability_gap -v`

Expected: FAIL with missing helper/integration.

- [ ] **Step 3: Implement gap mapping**

Only create a gap when `evidence_purpose` is material and the blocked/unavailable channel plausibly limits the decision. The gap contains no install/auth action.

- [ ] **Step 4: Run escalation tests to verify GREEN**

Run:
`python -m unittest company.tests.test_intelligence_capability_gap -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add company/runtime/capability_scout.py company/runtime/intelligence_gateway.py company/tests/test_intelligence_capability_gap.py
git commit -m "feat: escalate blocked research capability gaps"
```

### Task 7: Council Contracts, Skill Routing, and Acceptance Documentation

**Files:**
- Modify: `contracts/EVIDENCE_AND_RESEARCH.md`
- Modify: `skills/universal-council/SKILL.md`
- Modify: `company/README.md`
- Create: `company/docs/INTELLIGENCE_GATEWAY_ACCEPTANCE.md`
- Test: `company/tests/test_intelligence_contracts.py`

**Interfaces:**
- Consumes: policy/runtime behavior from Tasks 1–6.
- Produces: governance text that names gateway precedence, evidence provenance, read-only/auth boundaries, and capability-gap behavior.

- [ ] **Step 1: Write failing contract tests**

Tests assert the documents contain:
- native-first routing;
- Agent Reach public-read scope;
- authenticated social block in v1;
- evidence provenance requirement;
- HR capability-gap escalation;
- explicit statement that gateway is not a Council member and has no decision authority.

- [ ] **Step 2: Run tests to verify RED**

Run:
`python -m unittest company.tests.test_intelligence_contracts -v`

Expected: FAIL until governance docs are updated.

- [ ] **Step 3: Update evidence contract and Council skill**

Add a compact Intelligence Gateway rule:
- use native connectors first when stronger;
- use Agent Reach only for approved public-read capabilities;
- never infer authority from provider output;
- preserve provenance;
- blocked auth channels become gaps, not automatic installs.

- [ ] **Step 4: Add acceptance document**

`company/docs/INTELLIGENCE_GATEWAY_ACCEPTANCE.md` mirrors the spec's acceptance criteria in testable language.

- [ ] **Step 5: Run contract tests to verify GREEN**

Run:
`python -m unittest company.tests.test_intelligence_contracts -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add contracts/EVIDENCE_AND_RESEARCH.md skills/universal-council/SKILL.md company/README.md company/docs/INTELLIGENCE_GATEWAY_ACCEPTANCE.md company/tests/test_intelligence_contracts.py
git commit -m "docs: govern Council Intelligence Gateway"
```

### Task 8: YASSIN Runtime Descriptor and Real Read-Only Integration Test

**Files:**
- Create: `company/config/intelligence_gateway.local.example.json`
- Create: `company/tests/test_intelligence_gateway_integration_contract.py`
- Do not commit credentials, cookies, machine-private paths, or mutable secrets.

**Interfaces:**
- Consumes: environment variables defined in Task 1 and Agent Reach provider from Task 4.
- Produces: documented local configuration contract for YASSIN and a test that can be skipped when no local launcher is configured.

- [ ] **Step 1: Write failing local-contract tests**

Tests:
- `test_local_example_contains_environment_keys_not_real_private_path`
- `test_local_example_pins_agent_reach_commit`
- `test_integration_test_skips_without_launcher_env`

- [ ] **Step 2: Run tests to verify RED**

Run:
`python -m unittest company.tests.test_intelligence_gateway_integration_contract -v`

Expected: FAIL until example/config contract exists.

- [ ] **Step 3: Add environment-based local descriptor example**

Use symbolic values such as:
- `COUNCIL_AGENT_REACH_LAUNCHER`
- `COUNCIL_AGENT_REACH_COMMIT`

Do not commit `C:\Users\alnaseem\...` as a universal runtime path.

- [ ] **Step 4: Add optional live integration probe**

When the launcher env is explicitly set, verify only:
- version/identity;
- doctor read-only;
- one public YouTube metadata request or one public RSS request.

The test must not authenticate, configure, install, or touch OpenCLI.

- [ ] **Step 5: Run local-contract tests to verify GREEN**

Run:
`python -m unittest company.tests.test_intelligence_gateway_integration_contract -v`

Expected: PASS with live probe skipped when env is absent.

- [ ] **Step 6: On YASSIN, run the live probe with the already-approved launcher**

Set the environment only for the test process:
- launcher: existing safe launcher in the isolated venv;
- commit: `94f06c1969dfc1834001269d79d3ad0972d9dee6`.

Expected: public-read probe PASS; no config/cookie files created.

- [ ] **Step 7: Commit**

```bash
git add company/config/intelligence_gateway.local.example.json company/tests/test_intelligence_gateway_integration_contract.py
git commit -m "test: add local intelligence gateway integration contract"
```

### Task 9: Full Verification, Security Regression Check, and PR Readiness

**Files:**
- Modify only if verification reveals a defect.
- Review: all files changed on `feat/council-intelligence-gateway-v1`.

**Interfaces:**
- Consumes: all Tasks 1–8.
- Produces: verified branch ready for whole-branch review and non-draft PR.

- [ ] **Step 1: Run focused gateway test suite**

Run:
`python -m unittest company.tests.test_intelligence_gateway_policy company.tests.test_intelligence_models company.tests.test_intelligence_gateway company.tests.test_agent_reach_provider company.tests.test_intelligence_evidence company.tests.test_intelligence_capability_gap company.tests.test_intelligence_contracts company.tests.test_intelligence_gateway_integration_contract -v`

Expected: all PASS, with only the documented optional live test skipped when its environment is absent.

- [ ] **Step 2: Run full company suite**

Run:
`python -m unittest discover -s company/tests -v`

Expected: 0 failures, 0 errors.

- [ ] **Step 3: Run config invariants**

Run:
`python tools/validate_config.py`

Expected: exit 0 and gateway invariants reported as enforced.

- [ ] **Step 4: Compile runtime**

Run:
`python -m compileall -q company`

Expected: exit 0.

- [ ] **Step 5: Security regression grep/review**

Inspect the diff for:
- `shell=True`;
- arbitrary `eval`/`exec`;
- `install --system`;
- `agent-reach configure`;
- OpenCLI install/use;
- cookie/credential extraction;
- hard-coded YASSIN private path in committed runtime code;
- write/publish/message methods.

Expected: none present outside documentation that explicitly names them as forbidden.

- [ ] **Step 6: Run real YASSIN public-read smoke test**

Use the approved isolated launcher and verify:
- Web/Jina public read;
- YouTube metadata/transcript path;
- RSS read;
- doctor reports no OpenCLI/browser credentials.

Expected: successful public reads and no new credential/config state.

- [ ] **Step 7: Whole-branch review**

Use a fresh reviewer against the full diff, focusing on:
- policy-before-health;
- shell/argv safety;
- auth isolation;
- evidence provenance;
- fallback behavior;
- capability-gap side effects.

Resolve all material findings before PR promotion.

- [ ] **Step 8: Mark PR #6 ready and update its body with verification evidence**

Do not merge if any required test or security check is red.

- [ ] **Step 9: Merge only after the verification and review gates are green**

Use squash merge and record the resulting `main` SHA in the final report.

## Self-Review

- **Spec coverage:** Every spec section is mapped: routing/policy (Tasks 1–3), provider isolation and pinning (Task 4), evidence envelope (Task 5), HR escalation/Pulse interaction (Task 6 plus contract update), governance/docs (Task 7), environment portability/live probe (Task 8), and acceptance/verification (Task 9).
- **Step scan:** Each implementation step names one file/signature/behavior or one verification command; no production body is pre-written except fixed configuration values from the spec.
- **Type consistency:** `ResearchRequest`, `ProviderHealth`, `GatewayResult`, `select_route`, `route_request`, `AgentReachProvider`, and `normalize_evidence` are introduced once and referenced consistently.
- **Review Focus:** All five high-risk input/failure classes have explicit tests in Tasks 3–5.
- **Proportion:** The plan is task-oriented rather than a code transcript; implementation bodies are left to the executor under pinned interfaces and tests.
