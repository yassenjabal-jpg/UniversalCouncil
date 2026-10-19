namespace UniversalCouncil.CommandCenter.Application;

public sealed record OrchestrationCatalogDocument(
    string SchemaVersion,
    string SourceType,
    IReadOnlyList<SourceDocument> SourceFiles,
    CouncilDocument Council,
    StudioDocument Studio,
    ModelControlDocument ModelControl,
    RuntimeDocument Runtime);

public sealed record SourceDocument(string Path, string BlobSha);

public sealed record CouncilDocument(
    string GoverningVersion,
    string ContractsVersion,
    string ContractsStatus,
    string RoutingVersion,
    string RoutingStatus,
    string Objective,
    bool FreeTextKeywordRouting,
    IReadOnlyList<RoleDocument> CoreRoles,
    IReadOnlyList<RoleDocument> SpecialistRoles,
    IReadOnlyDictionary<string, string> DomainSpecialists,
    IReadOnlyList<string> CommercialMandatorySpecialists,
    IReadOnlyDictionary<string, object> ActivationRules);

public sealed record RoleDocument(
    string Id,
    string Name,
    string ActivationModel,
    string BlockerType,
    string BlockerDomain,
    bool MayExecuteTools,
    bool MayMutateAuthority,
    bool MaySelfApprove,
    IReadOnlyList<string> Tools);

public sealed record StudioDocument(
    string VisualSystem,
    string PrimaryLanguage,
    string PublicationAuthority,
    string OperatingMode,
    IReadOnlyList<string> MacroPhases,
    IReadOnlyList<string> ControlPlaneFunctions,
    IReadOnlyList<string> MandatoryClearanceFunctions,
    IReadOnlyList<DepartmentDocument> Departments,
    HandoffDocument HandoffContract,
    StageExecutionDocument StageExecutionContract,
    MasterPipelineDocument MasterPipelineContract,
    HumanAssistanceDocument HumanAssistance,
    IReadOnlyList<string> ReturnTicketRequiredFields);

public sealed record DepartmentDocument(
    string Id,
    string Name,
    IReadOnlyList<string> Functions);

public sealed record HandoffDocument(
    bool AcceptanceRequiredBeforeNextDepartment,
    bool DownstreamDirectRepairForbidden,
    string RejectionAction);

public sealed record StageExecutionDocument(
    bool ExactlyOnePrimaryProgram,
    bool SimultaneousSecondaryCraftProgramForbidden,
    bool ProgramSwitchRequiresNewStage,
    bool CheckpointBeforeStageExit,
    bool OutputVerificationRequired);

public sealed record MasterPipelineDocument(
    IReadOnlyList<string> PhaseSequence,
    IReadOnlyList<string> WritingExitRequires,
    string PreproductionEntryRequires,
    string PreproductionExitRequires,
    string ProductionEntryRequires,
    string FeedbackMode,
    bool PhaseSkipForbidden);

public sealed record HumanAssistanceDocument(
    bool Enabled,
    string Mode,
    string Coordinator);

public sealed record ModelControlDocument(
    bool RoleModelSeparation,
    bool OwnerControlledSelection,
    bool SilentFallbackAllowed,
    bool ProviderCallsConnected,
    IReadOnlyList<string> SelectionPrecedence);

public sealed record RuntimeDocument(
    string TaskState,
    IReadOnlyList<string> ActiveCouncilRoles,
    string? ActiveStudioDepartment,
    string? ActiveModel,
    bool ProviderCallInFlight);

public interface IOrchestrationCatalogReader
{
    OrchestrationCatalogDocument Read();
}

public sealed class OrchestrationCatalogReadException : Exception
{
    public OrchestrationCatalogReadException(string message) : base(message) { }

    public OrchestrationCatalogReadException(string message, Exception inner) : base(message, inner) { }
}
