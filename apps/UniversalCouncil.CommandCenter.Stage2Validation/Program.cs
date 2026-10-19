using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Infrastructure;

var root = Path.Combine(
    Path.GetTempPath(),
    "UniversalCouncil.CommandCenter.Stage2Validation",
    Guid.NewGuid().ToString("N"));
Directory.CreateDirectory(root);

try
{
    var validPath = Path.Combine(root, "valid.json");
    File.WriteAllText(validPath, ValidJson(executionEnabled: false));

    var service = new OperationalStateService(
        new JsonOperationalStateReader(validPath));

    var state = service.GetOperationalState();
    var shell = service.GetSnapshot();

    Require(state.Health == OperationalStateHealth.Healthy, "valid state must be healthy");
    Require(!state.ExecutionEnabled, "Stage 2 operational projection must never enable execution");
    Require(!shell.ExecutionEnabled, "Stage 2 shell must never enable execution");
    Require(state.Evidence.Count == 1, "valid fixture evidence receipt missing");
    Require(state.Approvals.Count == 2, "valid fixture approval ledger missing");
    Require(state.Usage.RecordedCostUsd is null, "unconnected usage must not invent zero cost");
    Require(shell.Modules.Any(item => item.Id == "execution" && item.State == ModuleState.Locked),
        "execution module must remain locked");

    var hostilePath = Path.Combine(root, "hostile-execution.json");
    File.WriteAllText(hostilePath, ValidJson(executionEnabled: true));
    var hostileService = new OperationalStateService(
        new JsonOperationalStateReader(hostilePath));
    var hostile = hostileService.GetOperationalState();
    Require(hostile.Health == OperationalStateHealth.Unavailable,
        "hostile execution enablement must fail closed");
    Require(!hostile.ExecutionEnabled,
        "hostile execution enablement must not propagate");

    var missingService = new OperationalStateService(
        new JsonOperationalStateReader(Path.Combine(root, "missing.json")));
    Require(missingService.GetOperationalState().Health == OperationalStateHealth.Unavailable,
        "missing state must fail closed");

    var malformedPath = Path.Combine(root, "malformed.json");
    File.WriteAllText(malformedPath, "{");
    var malformedService = new OperationalStateService(
        new JsonOperationalStateReader(malformedPath));
    Require(malformedService.GetOperationalState().Health == OperationalStateHealth.Unavailable,
        "malformed state must fail closed");

    var extraFieldPath = Path.Combine(root, "extra-field.json");
    File.WriteAllText(
        extraFieldPath,
        ValidJson(executionEnabled: false).Replace(
            "\"schema_version\": \"1.0\",",
            "\"schema_version\": \"1.0\", \"unexpected\": true,"));
    var extraFieldService = new OperationalStateService(
        new JsonOperationalStateReader(extraFieldPath));
    Require(extraFieldService.GetOperationalState().Health == OperationalStateHealth.Unavailable,
        "unknown root state fields must fail closed");

    var badUsagePath = Path.Combine(root, "bad-usage.json");
    File.WriteAllText(
        badUsagePath,
        ValidJson(executionEnabled: false)
            .Replace("\"state\": \"NOT_CONNECTED\"", "\"state\": \"CONNECTED\""));
    var badUsageService = new OperationalStateService(
        new JsonOperationalStateReader(badUsagePath));
    Require(badUsageService.GetOperationalState().Health == OperationalStateHealth.Unavailable,
        "connected usage without recorded cost must fail closed");

    Console.WriteLine("Command Center Stage 2 adversarial validation: PASS");
    return 0;
}
finally
{
    Directory.Delete(root, recursive: true);
}

static void Require(bool condition, string message)
{
    if (!condition)
    {
        throw new InvalidOperationException(message);
    }
}

static string ValidJson(bool executionEnabled) => $$"""
{
  "schema_version": "1.0",
  "source_type": "repository_projection",
  "source_label": "Stage2 validation fixture",
  "baseline_revision": "0123456789abcdef0123456789abcdef01234567",
  "project_id": "command-center",
  "project_label": "UniversalCouncil Command Center",
  "stage_id": "stage2",
  "stage_label": "Stage 2",
  "stage_state": "OPEN",
  "execution_enabled": {{executionEnabled.ToString().ToLowerInvariant()}},
  "phase_gate_label": "LOCKED BY PHASE 0",
  "evidence": [
    {
      "id": "E1",
      "category": "CI",
      "title": "fixture",
      "result": "SUCCESS",
      "reference": "run:1",
      "digest": null,
      "occurred_at": "2026-10-19T09:55:00+03:00"
    }
  ],
  "approvals": [
    {
      "id": "A1",
      "title": "Stage 2",
      "state": "APPROVED",
      "scope": "read model",
      "evidence_reference": "owner"
    },
    {
      "id": "A2",
      "title": "Execution",
      "state": "BLOCKED",
      "scope": "execution",
      "evidence_reference": "phase0"
    }
  ],
  "usage": {
    "state": "NOT_CONNECTED",
    "provider": "none",
    "recorded_model_calls": null,
    "recorded_cost_usd": null,
    "note": "not connected"
  },
  "execution_manifest": {
    "state": "NO_EXECUTION_AUTHORIZED",
    "gate": "Phase 0",
    "last_manifest_id": null,
    "note": "locked"
  }
}
""";
