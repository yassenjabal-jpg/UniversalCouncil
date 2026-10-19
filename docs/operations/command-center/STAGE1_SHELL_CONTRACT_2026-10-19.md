# Command Center — Stage 1 Shell Contract
Date: 2026-10-19
Status: OPEN
Branch: command-center/stage1-shell-foundation
Parent: phase0/feasibility-adversarial-prototype

## Mission
Create the real Windows application shell without granting it operational authority.

Stage 1 proves the product can exist as a clean Windows control surface while preserving a hard architecture boundary between presentation and execution.

## Allowed
- WPF application shell.
- navigation and static/prototype read model.
- truthful lock/status presentation.
- Core domain records for read-only shell state.
- deterministic validation.
- Windows CI build.

## Forbidden in Stage 1 UI
- Process.Start / direct process control.
- PowerShell/cmd execution.
- filesystem mutation outside normal application UI resource loading.
- HTTP/API calls.
- GitHub mutation.
- model API calls.
- credentials/secrets.
- MCP/plugin execution.
- remote commands.
- desktop clicking/typing.
- provider fallback logic.
- production data.

## Truthfulness rule
A disconnected capability must display as disconnected/locked/not integrated.

No fake:
- ACTIVE agent;
- running job;
- cost;
- approval;
- evidence;
- provider health;
- YASSIN state.

## UX constraints inherited from recent product review
- avoid stacked title bars;
- one persistent navigation rail;
- one dominant page title;
- dense operational content without card-wall excess;
- explicit state labels, not color-only meaning;
- Arabic-first RTL surface with technical English identifiers only where useful;
- desktop minimum 1180×720 for Stage 1;
- execution lock must be visible without opening Settings.

## Architecture boundary
Presentation may depend on CommandCenter.Core.

Presentation must not directly depend on:
- UniversalCouncil Python runtime internals;
- shell/process providers;
- network clients;
- database clients;
- model providers;
- GitHub clients;
- credential stores.

Future integrations enter through explicit application/runtime adapters introduced in later stages.

## Acceptance
Stage 1 can be locked only when:
1. WPF and Core build on Windows .NET 10.
2. static boundary validator passes.
3. prototype validation executable passes.
4. Phase 0 lock is visible in shell.
5. no fake runtime status exists.
6. Council architecture/security review = PASS.
7. Studio UX/visual review = PASS or PASS_WITH_BOUNDED_CORRECTIONS.
8. unresolved Phase 0 blockers remain visible and do not become success by implication.
