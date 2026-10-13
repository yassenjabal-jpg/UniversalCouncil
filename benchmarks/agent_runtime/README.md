# Agent Runtime Bake-off

Status: PHASE 1 MECHANICS COMPLETE / PHASE 2 REMEDIATED / YASSIN EXECUTION REQUIRED

This benchmark compares the current Universal Council v0.3 baseline with OpenAI Agents SDK and Microsoft Agent Framework without allowing framework popularity, stale evidence, or mocked mechanics to select a runtime.

## Hard boundaries

- LIVE_DECISION execution is allowed on **YASSIN only**.
- No DESKTOP-RQUULE9 compute.
- No GitHub-hosted live bake-off compute.
- No paid model API.
- Ollama must be local on `127.0.0.1`.
- Financial cost must remain `USD 0`.
- `main` remains unchanged until all final gates pass.
- Old Phase 2 evidence is archived and is not valid for selection.

## Candidate runtimes

- `baseline`: faithful v0.3 governance execution. Existing deterministic routing is used, and governance perspectives are synthesized in one model call; the baseline is not given parallel agents.
- `openai_agents`: independent role execution through OpenAI Agents SDK using the same local Ollama model.
- `microsoft_agent_framework`: independent role execution through Microsoft Agent Framework using the same local Ollama model.

## Dataset

`cases.json` is grader-facing and contains the historical expected outcomes.

Models must not receive the raw grader source directly. Before LIVE execution, YASSIN builds:

`case_packets.json`

using:

`python tools/build_agent_bakeoff_packets.py`

The builder removes decision/status/verdict/result sections and known answer labels, then records source and packet hashes.

## Provenance

Every full result is tied to:
- experiment ID;
- git HEAD;
- config hash;
- cases hash;
- masked packets hash;
- live runner hash;
- evaluator hash;
- requirements hash;
- model name and Ollama digest;
- execution host;
- zero-cost receipt.

The evaluator rejects stale or mismatched provenance.

## YASSIN health gate

The canonical health script is:

`tools/yassin_bakeoff_health.ps1`

It requires 10 consecutive healthy probes covering:
- correct host and experiment branch;
- repository readability;
- Python/Git;
- NVIDIA GPU and VRAM;
- free space on E:;
- CouncilVideoStudio GUI bridge presence;
- local Ollama endpoint;
- selected local model.

## Staged live execution

Use one entrypoint only:

`tools/run_yassin_bakeoff.ps1`

Execution order:

1. `-Stage Preflight`
2. `-Stage Canary`
3. `-Stage Representative`
4. `-Stage Full`
5. attach YASSIN desktop evidence
6. `-Stage Evaluate`

Canary covers one case. Representative covers four cases. Full covers all 16.

Representative is blocked until a matching Canary receipt exists. Full is blocked until a matching Representative receipt exists.

Results are written atomically after every case. Completed cases resume only when the experiment provenance matches.

## Desktop hard gate

The two desktop-required cases are:
- `c02_gui_primary_hybrid`
- `c04_after_effects_runtime_status`

Desktop evidence is attached with:

`tools/record_agent_bakeoff_desktop.py`

Each runtime must pass both cases on YASSIN with:
- before evidence;
- semantic action receipt;
- after evidence;
- verified execution path;
- no unintended action.

Eligibility requires **2/2**, not an average across non-desktop cases.

## Mechanics evidence

Phase 1 deterministic mechanics tests remain separate from decision quality. They measure:
- independent run state;
- parallel first positions;
- fan-in;
- failure injection/recovery;
- checkpoint/resume;
- HITL pause/resume;
- usage capture;
- local trace capture.

A deterministic mechanics pass is never counted as LIVE_DECISION correctness.

## Winner rule

No runtime can win unless:
- all 16 full-stage cases completed;
- current provenance matches exactly;
- zero policy violations;
- Phase 1 hard mechanics pass;
- desktop gate is 2/2;
- financial cost is USD 0.

The final report must show decision quality, runtime reliability/recovery, governance compliance, and latency/token efficiency separately.
