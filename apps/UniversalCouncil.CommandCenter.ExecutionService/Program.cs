using System.Text.Json;
using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;
using UniversalCouncil.CommandCenter.Host;

var command = args.Length == 0 ? "status" : args[0];
var services = CommandCenterComposition.Create(AppContext.BaseDirectory);
var jsonOptions = new JsonSerializerOptions
{
    PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
    PropertyNameCaseInsensitive = false,
    WriteIndented = true
};

try
{
    switch (command)
    {
        case "status":
        {
            var fabric = services.ExecutionFabric.GetFabric();
            Console.WriteLine(JsonSerializer.Serialize(new
            {
                health = fabric.Health.ToString().ToUpperInvariant(),
                service_mode = fabric.ServiceMode,
                target_host = fabric.TargetHost,
                live_dispatch_enabled = fabric.LiveDispatchEnabled,
                phase0_gates = fabric.Phase0Gates,
                provider_count = fabric.Providers.Count
            }, jsonOptions));
            return fabric.Health == ExecutionFabricHealth.Healthy ? 0 : 3;
        }

        case "inspect-provider-registry":
        {
            var fabric = services.ExecutionFabric.GetFabric();
            Console.WriteLine(JsonSerializer.Serialize(fabric.Providers, jsonOptions));
            return fabric.Health == ExecutionFabricHealth.Healthy ? 0 : 3;
        }

        case "validate-manifest":
        {
            RequirePath(args);
            var manifest = JsonSerializer.Deserialize<ExecutionManifest>(
                File.ReadAllText(args[1]),
                jsonOptions)
                ?? throw new InvalidOperationException("Manifest file is empty.");

            services.ExecutionManifestValidator.Validate(manifest);
            var receipt = services.ExecutionManifestValidator.EvaluateForDispatch(manifest);
            Console.WriteLine(JsonSerializer.Serialize(receipt, jsonOptions));
            return 0;
        }

        case "validate-receipt":
        {
            RequirePath(args);
            var receipt = JsonSerializer.Deserialize<ExecutionReceipt>(
                File.ReadAllText(args[1]),
                jsonOptions)
                ?? throw new InvalidOperationException("Receipt file is empty.");

            ExecutionFabricService.ValidateReceipt(receipt);
            Console.WriteLine("VALID");
            return 0;
        }

        default:
            Console.Error.WriteLine(
                "Unsupported command. Allowed: status, validate-manifest, inspect-provider-registry, validate-receipt");
            return 2;
    }
}
catch (Exception exc)
{
    Console.Error.WriteLine($"{exc.GetType().Name}: {exc.Message}");
    return 4;
}

static void RequirePath(string[] arguments)
{
    if (arguments.Length != 2 ||
        string.IsNullOrWhiteSpace(arguments[1]) ||
        !File.Exists(arguments[1]))
    {
        throw new InvalidOperationException(
            "This command requires one existing JSON file path.");
    }
}
