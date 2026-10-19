using UniversalCouncil.CommandCenter.Core;

var modules = new[]
{
    new ModuleStatus("execution", "Execution", "Phase 0 gate", ModuleState.Locked, "LOCKED"),
    new ModuleStatus("runtime", "Runtime", "Stage 2 integration", ModuleState.NotConnected, "NOT CONNECTED")
};

var snapshot = new CommandCenterSnapshot(
    "UniversalCouncil Command Center",
    "Stage 1",
    "Phase 0 incomplete",
    ExecutionEnabled: false,
    "LOCKED BY PHASE 0",
    "No live approvals connected",
    modules);

if (snapshot.ExecutionEnabled)
{
    throw new InvalidOperationException("Stage 1 must never enable execution.");
}

if (!snapshot.Modules.Any(module => module.Id == "execution" && module.State == ModuleState.Locked))
{
    throw new InvalidOperationException("Execution module must be explicitly locked in Stage 1.");
}

if (snapshot.Modules.Any(module => module.State == ModuleState.ReadyForIntegration))
{
    throw new InvalidOperationException("Stage 1 validation fixture may not claim a live integration.");
}

Console.WriteLine("Command Center Stage 1 validation: PASS");
