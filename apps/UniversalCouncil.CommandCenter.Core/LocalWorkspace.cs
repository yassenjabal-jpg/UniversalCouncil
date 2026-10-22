namespace UniversalCouncil.CommandCenter.Core;
public sealed record LocalWorkspaceDescriptor(int SchemaVersion, string ProjectId, string ChangeId,
    Guid SessionId, string StorageDirectory, string RepositoryDirectory, string ArtifactPath);
public sealed record LocalWorkspaceObservation(LocalWorkspaceDescriptor Workspace,
    string SourceRevision, string ArtifactSha256, DateTimeOffset ObservedAt);
public sealed record WorkspaceSupervisionSnapshot(LocalSupervisionSnapshot Session,
    string ObservedSourceRevision, string ObservedArtifactSha256, DateTimeOffset ObservedAt);
