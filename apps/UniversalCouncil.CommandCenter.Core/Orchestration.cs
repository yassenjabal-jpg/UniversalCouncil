namespace UniversalCouncil.CommandCenter.Core;

public enum OrchestrationHealth
{
    Healthy,
    Unavailable
}

public sealed record CouncilRoleProjection(
    string Id,
    string Name,
    string ActivationModel,
    string BlockerType,
    string BlockerDomain,
    bool MayExecuteTools,
    bool MayMutateAuthority,
    bool MaySelfApprove,
    IReadOnlyList<string> Tools);

public sealed record StudioDepartmentProjection(
    string Id,
    string Name,
    IReadOnlyList<string> Functions);

public sealed record ModelControlProjection(
    bool RoleModelSeparation,
    bool OwnerControlledSelection,
    bool SilentFallbackAllowed,
    bool ProviderCallsConnected,
    IReadOnlyList<string> SelectionPrecedence);

public sealed record StudioOrchestrationProjection(
    string VisualSystem,
    string PrimaryLanguage,
    string PublicationAuthority,
    string OperatingMode,
    IReadOnlyList<string> MacroPhases,
    IReadOnlyList<string> ControlPlaneFunctions,
    IReadOnlyList<string> MandatoryClearanceFunctions,
    IReadOnlyList<StudioDepartmentProjection> Departments,
    IReadOnlyList<string> ReturnTicketRequiredFields,
    bool HumanAssistanceEnabled,
    string HumanAssistanceMode,
    string HumanAssistanceCoordinator);

public sealed record CouncilOrchestrationProjection(
    string GoverningVersion,
    string ContractsVersion,
    string ContractsStatus,
    string RoutingVersion,
    string RoutingStatus,
    string Objective,
    bool FreeTextKeywordRouting,
    IReadOnlyList<CouncilRoleProjection> CoreRoles,
    IReadOnlyList<CouncilRoleProjection> SpecialistRoles,
    IReadOnlyDictionary<string, string> DomainSpecialists,
    IReadOnlyList<string> CommercialMandatorySpecialists);

public sealed record OrchestrationCatalogProjection(
    OrchestrationHealth Health,
    string ProblemLabel,
    string TaskStateLabel,
    CouncilOrchestrationProjection Council,
    StudioOrchestrationProjection Studio,
    ModelControlProjection ModelControl)
{
    public static OrchestrationCatalogProjection Unavailable(string problem) =>
        new(
            OrchestrationHealth.Unavailable,
            problem,
            "UNAVAILABLE",
            new(
                "UNKNOWN",
                "UNKNOWN",
                "UNAVAILABLE",
                "UNKNOWN",
                "UNAVAILABLE",
                "UNKNOWN",
                false,
                [],
                [],
                new Dictionary<string, string>(),
                []),
            new(
                "UNKNOWN",
                "UNKNOWN",
                "UNKNOWN",
                "UNKNOWN",
                [],
                [],
                [],
                [],
                [],
                false,
                "UNAVAILABLE",
                "UNKNOWN"),
            new(false, false, false, false, []));
}

public sealed record CouncilPlanningRequest(
    IReadOnlyList<string> Domains,
    string Materiality,
    string Uncertainty,
    string Risk,
    string Freshness,
    bool UserImpact,
    bool ExecutionFeasibility,
    bool CostOrValueTradeoff,
    bool CommercialDecision);

public sealed record CouncilPlanningResult(
    IReadOnlyList<string> ActivatedRoleIds,
    string ModelSelectionState,
    bool ExecutionAuthorized,
    string Summary);

public interface IOrchestrationCatalogProvider
{
    OrchestrationCatalogProjection GetCatalog();
}

public interface ICouncilPlanner
{
    CouncilPlanningResult Plan(CouncilPlanningRequest request);
}
