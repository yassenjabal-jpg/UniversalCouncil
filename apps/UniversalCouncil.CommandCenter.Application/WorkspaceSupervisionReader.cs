using UniversalCouncil.CommandCenter.Core;
namespace UniversalCouncil.CommandCenter.Application;
public interface ILocalWorkspaceObserver { LocalWorkspaceObservation Observe(string configurationPath); }
public sealed class WorkspaceSupervisionReader(ILocalWorkspaceObserver observer,
    Func<string,LocalReviewSessionService> sessions)
{
    public WorkspaceSupervisionSnapshot Read(string configurationPath)
    {
        var observed=observer.Observe(configurationPath);
        var w=observed.Workspace;
        var session=sessions(w.StorageDirectory).ReadForProject(w.SessionId,w.ProjectId,w.ChangeId,
            observed.SourceRevision,observed.ArtifactSha256);
        return new(LocalSupervisionReader.Project(session),observed.SourceRevision,
            observed.ArtifactSha256,observed.ObservedAt);
    }
}
