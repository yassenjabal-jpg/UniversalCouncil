using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Application;

public sealed class OrchestrationService :
    IOrchestrationCatalogProvider,
    ICouncilPlanner
{
    private static readonly Dictionary<string, int> MaterialityRank = new(StringComparer.Ordinal)
    {
        ["LOW"] = 0,
        ["MATERIAL"] = 1,
        ["HIGH"] = 2,
        ["CRITICAL"] = 3
    };

    private static readonly Dictionary<string, int> UncertaintyRank = new(StringComparer.Ordinal)
    {
        ["LOW"] = 0,
        ["MEDIUM"] = 1,
        ["HIGH"] = 2
    };

    private static readonly Dictionary<string, int> RiskRank = new(StringComparer.Ordinal)
    {
        ["LOW"] = 0,
        ["MEDIUM"] = 1,
        ["HIGH"] = 2,
        ["CRITICAL"] = 3
    };

    private static readonly Dictionary<string, int> FreshnessRank = new(StringComparer.Ordinal)
    {
        ["LOW"] = 0,
        ["MEDIUM"] = 1,
        ["HIGH"] = 2
    };

    private readonly IOrchestrationCatalogReader reader;

    public OrchestrationService(IOrchestrationCatalogReader reader)
    {
        this.reader = reader;
    }

    public OrchestrationCatalogProjection GetCatalog()
    {
        try
        {
            var document = reader.Read();
            Validate(document);

            return new OrchestrationCatalogProjection(
                OrchestrationHealth.Healthy,
                string.Empty,
                document.Runtime.TaskState,
                new(
                    document.Council.GoverningVersion,
                    document.Council.ContractsVersion,
                    document.Council.ContractsStatus,
                    document.Council.RoutingVersion,
                    document.Council.RoutingStatus,
                    document.Council.Objective,
                    document.Council.FreeTextKeywordRouting,
                    document.Council.CoreRoles.Select(ProjectRole).ToArray(),
                    document.Council.SpecialistRoles.Select(ProjectRole).ToArray(),
                    new Dictionary<string, string>(document.Council.DomainSpecialists),
                    document.Council.CommercialMandatorySpecialists.ToArray()),
                new(
                    document.Studio.VisualSystem,
                    document.Studio.PrimaryLanguage,
                    document.Studio.PublicationAuthority,
                    document.Studio.OperatingMode,
                    document.Studio.MacroPhases.ToArray(),
                    document.Studio.ControlPlaneFunctions.ToArray(),
                    document.Studio.MandatoryClearanceFunctions.ToArray(),
                    document.Studio.Departments
                        .Select(item => new StudioDepartmentProjection(item.Id, item.Name, item.Functions.ToArray()))
                        .ToArray(),
                    document.Studio.ReturnTicketRequiredFields.ToArray(),
                    document.Studio.HumanAssistance.Enabled,
                    document.Studio.HumanAssistance.Mode,
                    document.Studio.HumanAssistance.Coordinator),
                new(
                    document.ModelControl.RoleModelSeparation,
                    document.ModelControl.OwnerControlledSelection,
                    document.ModelControl.SilentFallbackAllowed,
                    document.ModelControl.ProviderCallsConnected,
                    document.ModelControl.SelectionPrecedence.ToArray()));
        }
        catch (OrchestrationCatalogReadException exc)
        {
            return OrchestrationCatalogProjection.Unavailable(exc.Message);
        }
        catch (Exception exc)
        {
            return OrchestrationCatalogProjection.Unavailable(
                $"Unexpected orchestration-read failure: {exc.GetType().Name}");
        }
    }

    public CouncilPlanningResult Plan(CouncilPlanningRequest request)
    {
        var document = reader.Read();
        Validate(document);
        ValidateRequest(request);

        var roles = new HashSet<string>(StringComparer.Ordinal) { "chair" };

        foreach (var domain in request.Domains)
        {
            if (!document.Council.DomainSpecialists.TryGetValue(domain, out var roleId))
            {
                throw new OrchestrationCatalogReadException(
                    $"No explicit domain specialist route for: {domain}");
            }
            roles.Add(roleId);
        }

        if (AtLeast(request.Uncertainty, "HIGH", UncertaintyRank) ||
            AtLeast(request.Freshness, "HIGH", FreshnessRank))
        {
            roles.Add("evidence");
        }

        if (AtLeast(request.Materiality, "MATERIAL", MaterialityRank) ||
            AtLeast(request.Uncertainty, "MEDIUM", UncertaintyRank))
        {
            roles.Add("redteam");
        }

        if (AtLeast(request.Risk, "MEDIUM", RiskRank))
        {
            roles.Add("risk");
        }

        if (request.UserImpact)
        {
            roles.Add("human");
        }

        if (request.ExecutionFeasibility)
        {
            roles.Add("execution");
        }

        if (request.CostOrValueTradeoff)
        {
            roles.Add("value");
        }

        if (request.CommercialDecision)
        {
            foreach (var role in document.Council.CommercialMandatorySpecialists)
            {
                roles.Add(role);
            }
        }

        var knownRoles = document.Council.CoreRoles
            .Concat(document.Council.SpecialistRoles)
            .Select(item => item.Id)
            .ToHashSet(StringComparer.Ordinal);

        if (!roles.IsSubsetOf(knownRoles))
        {
            throw new OrchestrationCatalogReadException(
                "Council routing attempted to activate an unknown role.");
        }

        return new CouncilPlanningResult(
            roles.OrderBy(item => item, StringComparer.Ordinal).ToArray(),
            "OWNER_SELECTION_REQUIRED / PROVIDER NOT CONNECTED",
            false,
            "خطة أدوار للقراءة فقط؛ لا يوجد تنفيذ أو اختيار نموذج صامت.");
    }

    private static CouncilRoleProjection ProjectRole(RoleDocument role) =>
        new(
            role.Id,
            role.Name,
            role.ActivationModel,
            role.BlockerType,
            role.BlockerDomain,
            role.MayExecuteTools,
            role.MayMutateAuthority,
            role.MaySelfApprove,
            role.Tools.ToArray());

    private static void Validate(OrchestrationCatalogDocument document)
    {
        if (document.SchemaVersion != "1.0" ||
            document.SourceType != "repository_projection")
        {
            throw new OrchestrationCatalogReadException(
                "Unsupported orchestration catalog schema/source.");
        }

        if (document.SourceFiles.Count < 5 ||
            document.SourceFiles.Any(item =>
                string.IsNullOrWhiteSpace(item.Path) ||
                item.BlobSha.Length != 40))
        {
            throw new OrchestrationCatalogReadException(
                "Orchestration source integrity metadata is incomplete.");
        }

        var allRoles = document.Council.CoreRoles
            .Concat(document.Council.SpecialistRoles)
            .ToArray();

        if (allRoles.Select(item => item.Id).Distinct(StringComparer.Ordinal).Count() != allRoles.Length)
        {
            throw new OrchestrationCatalogReadException("Duplicate Council role id.");
        }

        if (allRoles.Any(item =>
            item.MayExecuteTools ||
            item.MayMutateAuthority ||
            item.MaySelfApprove))
        {
            throw new OrchestrationCatalogReadException(
                "Stage 3 role authority inflation detected.");
        }

        if (document.Council.FreeTextKeywordRouting)
        {
            throw new OrchestrationCatalogReadException(
                "Free-text authority routing is forbidden.");
        }

        if (!document.ModelControl.RoleModelSeparation ||
            !document.ModelControl.OwnerControlledSelection ||
            document.ModelControl.SilentFallbackAllowed ||
            document.ModelControl.ProviderCallsConnected)
        {
            throw new OrchestrationCatalogReadException(
                "Stage 3 model-control policy is unsafe.");
        }

        var expectedPrecedence = new[]
        {
            "TASK_OVERRIDE",
            "ROLE_OVERRIDE",
            "PROJECT_DEFAULT",
            "GLOBAL_DEFAULT"
        };

        if (!document.ModelControl.SelectionPrecedence.SequenceEqual(expectedPrecedence))
        {
            throw new OrchestrationCatalogReadException(
                "Model selection precedence drifted.");
        }

        if (document.Runtime.TaskState != "NO_LIVE_TASK" ||
            document.Runtime.ActiveCouncilRoles.Count != 0 ||
            document.Runtime.ActiveStudioDepartment is not null ||
            document.Runtime.ActiveModel is not null ||
            document.Runtime.ProviderCallInFlight)
        {
            throw new OrchestrationCatalogReadException(
                "Stage 3 must not fabricate live orchestration activity.");
        }

        if (!document.Studio.MasterPipelineContract.PhaseSequence
                .SequenceEqual(new[] { "writing", "pre_production", "production" }) ||
            !document.Studio.MasterPipelineContract.PhaseSkipForbidden)
        {
            throw new OrchestrationCatalogReadException(
                "Studio macro-phase contract drifted.");
        }

        if (!document.Studio.HandoffContract.AcceptanceRequiredBeforeNextDepartment ||
            !document.Studio.HandoffContract.DownstreamDirectRepairForbidden ||
            document.Studio.HandoffContract.RejectionAction != "RETURN_TICKET_TO_SOURCE_DEPARTMENT")
        {
            throw new OrchestrationCatalogReadException(
                "Studio handoff/return-ticket policy is unsafe.");
        }

        if (!document.Studio.StageExecutionContract.ExactlyOnePrimaryProgram ||
            !document.Studio.StageExecutionContract.SimultaneousSecondaryCraftProgramForbidden ||
            !document.Studio.StageExecutionContract.OutputVerificationRequired)
        {
            throw new OrchestrationCatalogReadException(
                "Studio serial-production contract drifted.");
        }

        if (document.Studio.ReturnTicketRequiredFields.Count < 9)
        {
            throw new OrchestrationCatalogReadException(
                "Return-ticket contract is incomplete.");
        }
    }

    private static void ValidateRequest(CouncilPlanningRequest request)
    {
        _ = Rank(request.Materiality, MaterialityRank, "materiality");
        _ = Rank(request.Uncertainty, UncertaintyRank, "uncertainty");
        _ = Rank(request.Risk, RiskRank, "risk");
        _ = Rank(request.Freshness, FreshnessRank, "freshness");

        if (request.Domains.Any(string.IsNullOrWhiteSpace) ||
            request.Domains.Distinct(StringComparer.Ordinal).Count() != request.Domains.Count)
        {
            throw new OrchestrationCatalogReadException(
                "Council planning domains must be explicit and unique.");
        }
    }

    private static bool AtLeast(
        string actual,
        string threshold,
        IReadOnlyDictionary<string, int> ranks) =>
        Rank(actual, ranks, "level") >= Rank(threshold, ranks, "threshold");

    private static int Rank(
        string value,
        IReadOnlyDictionary<string, int> ranks,
        string dimension)
    {
        if (!ranks.TryGetValue(value, out var rank))
        {
            throw new OrchestrationCatalogReadException(
                $"Unknown {dimension} level: {value}");
        }
        return rank;
    }
}
