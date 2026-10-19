using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Application;

public sealed class ExecutionFabricService :
    IExecutionFabricProvider,
    IExecutionManifestValidator
{
    private static readonly string[] RequiredAllowedCommands =
    [
        "status",
        "validate-manifest",
        "inspect-provider-registry",
        "validate-receipt"
    ];

    private readonly IExecutionFabricReader reader;
    private readonly Func<DateTimeOffset> utcNow;

    public ExecutionFabricService(
        IExecutionFabricReader reader,
        Func<DateTimeOffset>? utcNow = null)
    {
        this.reader = reader;
        this.utcNow = utcNow ?? (() => DateTimeOffset.UtcNow);
    }

    public ExecutionFabricProjection GetFabric()
    {
        try
        {
            var document = reader.Read();
            ValidateDocument(document);

            return new ExecutionFabricProjection(
                ExecutionFabricHealth.Healthy,
                string.Empty,
                document.Service.Mode,
                document.Service.TargetHost,
                document.Service.LiveDispatchEnabled,
                document.Phase0.Gates
                    .OrderBy(item => item.Key, StringComparer.Ordinal)
                    .Select(item => new Phase0GateProjection(
                        item.Key,
                        item.Value.Name,
                        item.Value.Status))
                    .ToArray(),
                document.Providers
                    .Select(item => new ExecutionProviderProjection(
                        item.Id,
                        item.DisplayName,
                        item.Role,
                        item.State,
                        item.CanObserve,
                        item.CanExecute,
                        item.Source,
                        item.Note))
                    .ToArray(),
                document.Service.AllowedCliCommands.ToArray(),
                document.Service.ForbiddenCliCommands.ToArray(),
                document.Recovery.UnknownIsNeverSuccess,
                document.Recovery.SinglePhysicalController);
        }
        catch (ExecutionFabricReadException exc)
        {
            return ExecutionFabricProjection.Unavailable(exc.Message);
        }
        catch (Exception exc)
        {
            return ExecutionFabricProjection.Unavailable(
                $"Unexpected execution-fabric failure: {exc.GetType().Name}");
        }
    }

    public void Validate(ExecutionManifest manifest)
    {
        var document = reader.Read();
        ValidateDocument(document);

        Require(manifest.ManifestId, nameof(manifest.ManifestId));
        Require(manifest.TaskId, nameof(manifest.TaskId));
        Require(manifest.Requester, nameof(manifest.Requester));
        Require(manifest.AuthorityOperation, nameof(manifest.AuthorityOperation));
        Require(manifest.ActionKind, nameof(manifest.ActionKind));
        Require(manifest.ExpectedPostcondition, nameof(manifest.ExpectedPostcondition));
        Require(manifest.VerificationMethod, nameof(manifest.VerificationMethod));
        Require(manifest.ApprovalRef, nameof(manifest.ApprovalRef));
        Require(manifest.IdempotencyKey, nameof(manifest.IdempotencyKey));

        if (!string.Equals(
                manifest.TargetHost,
                document.Service.TargetHost,
                StringComparison.Ordinal))
        {
            throw new ExecutionFabricReadException(
                $"Manifest target host must be {document.Service.TargetHost}.");
        }

        if (manifest.ExpiresAt <= utcNow())
        {
            throw new ExecutionFabricReadException("Manifest is expired.");
        }

        var allowedEffects = new HashSet<string>(StringComparer.Ordinal)
        {
            "READ",
            "WRITE",
            "EXECUTE"
        };
        if (!allowedEffects.Contains(manifest.Effect))
        {
            throw new ExecutionFabricReadException("Unsupported manifest effect.");
        }

        var riskRank = manifest.RiskTier switch
        {
            "T0_OBSERVE" => 0,
            "T1_REVERSIBLE" => 1,
            "T2_LOCAL_STATE_CHANGE" => 2,
            "T3_HIGH_IMPACT" => 3,
            _ => throw new ExecutionFabricReadException("Unsupported manifest risk tier.")
        };

        if (manifest.Effect == "EXECUTE" && riskRank < 1)
        {
            throw new ExecutionFabricReadException(
                "EXECUTE effect cannot be downgraded to T0.");
        }

        if (manifest.Effect == "WRITE" && riskRank < 2)
        {
            throw new ExecutionFabricReadException(
                "WRITE effect cannot be downgraded below T2.");
        }

        if (manifest.ActionKind.Contains("credential", StringComparison.OrdinalIgnoreCase) ||
            manifest.ActionKind.Contains("password", StringComparison.OrdinalIgnoreCase) ||
            manifest.ActionKind.Contains("secret", StringComparison.OrdinalIgnoreCase))
        {
            throw new ExecutionFabricReadException(
                "Credential-bearing action kinds are forbidden in Stage 4.");
        }
    }

    public ExecutionReceipt EvaluateForDispatch(ExecutionManifest manifest)
    {
        Validate(manifest);
        var document = reader.Read();
        ValidateDocument(document);

        return new ExecutionReceipt(
            manifest.ManifestId,
            manifest.TaskId,
            "BLOCKED",
            "SAFE_DISABLED / PHASE0_NOT_PASS",
            manifest.TargetHost,
            utcNow());
    }

    public static void ValidateReceipt(ExecutionReceipt receipt)
    {
        if (string.IsNullOrWhiteSpace(receipt.ManifestId) ||
            string.IsNullOrWhiteSpace(receipt.TaskId) ||
            string.IsNullOrWhiteSpace(receipt.TargetHost))
        {
            throw new ExecutionFabricReadException(
                "Execution receipt identity is incomplete.");
        }

        var allowed = new HashSet<string>(StringComparer.Ordinal)
        {
            "PLANNED",
            "VALIDATED",
            "BLOCKED",
            "UNKNOWN",
            "FAILED",
            "POSTCONDITION_VERIFIED"
        };

        if (!allowed.Contains(receipt.State))
        {
            throw new ExecutionFabricReadException("Unsupported receipt state.");
        }

        if (receipt.State == "POSTCONDITION_VERIFIED")
        {
            throw new ExecutionFabricReadException(
                "Stage 4 cannot originate POSTCONDITION_VERIFIED receipts.");
        }
    }

    private static void ValidateDocument(ExecutionFabricDocument document)
    {
        if (document.SchemaVersion != "1.0" ||
            document.SourceType != "repository_projection")
        {
            throw new ExecutionFabricReadException(
                "Unsupported execution-fabric schema/source.");
        }

        if (document.Service.Mode != "SAFE_DISABLED" ||
            document.Service.LiveDispatchEnabled ||
            document.Phase0.LiveExecutionAuthorized)
        {
            throw new ExecutionFabricReadException(
                "Stage 4 live execution must remain disabled.");
        }

        if (document.Service.TargetHost != "YASSIN")
        {
            throw new ExecutionFabricReadException(
                "Unexpected Stage 4 execution target.");
        }

        if (!document.Service.AllowedCliCommands
                .SequenceEqual(RequiredAllowedCommands))
        {
            throw new ExecutionFabricReadException(
                "Stage 4 CLI command allowlist drifted.");
        }

        if (document.Service.ForbiddenCliCommands
            .Any(document.Service.AllowedCliCommands.Contains))
        {
            throw new ExecutionFabricReadException(
                "Forbidden execution command leaked into the allowlist.");
        }

        if (document.Providers.Any(item => item.CanExecute))
        {
            throw new ExecutionFabricReadException(
                "No Stage 4 provider may advertise execute capability.");
        }

        if (!document.Recovery.UnknownIsNeverSuccess ||
            !document.Recovery.StopOnUnknown ||
            !document.Recovery.UnknownRequiresReconciliation ||
            document.Recovery.ReplayCompletedActionDefault ||
            !document.Recovery.SinglePhysicalController)
        {
            throw new ExecutionFabricReadException(
                "Execution recovery invariants drifted.");
        }

        if (document.Phase0.Gates.Count != 4 ||
            document.Phase0.Gates.Values.All(item => item.Status == "PASS"))
        {
            throw new ExecutionFabricReadException(
                "Stage 4 expects retained non-PASS Phase 0 execution gates.");
        }

        if (document.SourceFiles.Count < 5 ||
            document.SourceFiles.Any(item =>
                string.IsNullOrWhiteSpace(item.Path) ||
                item.BlobSha.Length != 40))
        {
            throw new ExecutionFabricReadException(
                "Execution-fabric source identity is incomplete.");
        }
    }

    private static void Require(string value, string name)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new ExecutionFabricReadException(
                $"Manifest field is required: {name}");
        }
    }
}
