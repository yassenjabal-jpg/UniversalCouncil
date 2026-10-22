using System.Text.Json;
using System.Text.Json.Serialization;
using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;
namespace UniversalCouncil.CommandCenter.Infrastructure;

// Explicitly selected same-user local configuration, not authenticated project identity.
public sealed class LocalWorkspaceObserver : ILocalWorkspaceObserver
{
    public LocalWorkspaceObservation Observe(string configurationPath)
    {
        var config=Local(configurationPath,false);
        using var stream=new FileStream(config,FileMode.Open,FileAccess.Read,FileShare.Read);
        var raw=new byte[32769]; var total=0;
        while(total<raw.Length) { var read=stream.Read(raw,total,raw.Length-total);if(read==0)break;total+=read; }
        if(total==0||total>32768)throw new InvalidDataException("WORKSPACE_SIZE_LIMIT");
        using var document=JsonDocument.Parse(raw.AsMemory(0,total),new JsonDocumentOptions{MaxDepth=8});
        if(document.RootElement.ValueKind!=JsonValueKind.Object)throw new InvalidDataException("WORKSPACE_OBJECT_REQUIRED");
        var keys=new HashSet<string>(StringComparer.Ordinal);
        foreach(var field in document.RootElement.EnumerateObject())
            if(!keys.Add(field.Name))throw new InvalidDataException("DUPLICATE_WORKSPACE_FIELD");
        var w=JsonSerializer.Deserialize<LocalWorkspaceDescriptor>(raw.AsSpan(0,total),
            new JsonSerializerOptions{UnmappedMemberHandling=JsonUnmappedMemberHandling.Disallow,
                RespectRequiredConstructorParameters=true,MaxDepth=8})
            ??throw new InvalidDataException("WORKSPACE_REQUIRED");
        if(w.SchemaVersion!=1||w.SessionId==Guid.Empty||!Identifier(w.ProjectId)||!Identifier(w.ChangeId))
            throw new InvalidDataException("INVALID_WORKSPACE_BINDING");
        var storage=Local(w.StorageDirectory,true);var repo=Local(w.RepositoryDirectory,true);
        var artifact=Local(w.ArtifactPath,false);
        w=w with{StorageDirectory=storage,RepositoryDirectory=repo,ArtifactPath=artifact};
        var git=new GitEvidenceManifestReader(repo);
        var before=git.ReadCurrentRevision();
        var root=Path.GetDirectoryName(artifact)!;var name=Path.GetFileName(artifact);
        var measured=new WindowsEvidenceContentReader(root).Measure(name,new FileInfo(artifact).Length);
        var after=git.ReadCurrentRevision();
        if(before!=after)throw new InvalidDataException("WORKSPACE_CHANGED_DURING_OBSERVATION");
        return new(w,after,measured.Sha256,DateTimeOffset.UtcNow);
    }
    private static bool Identifier(string? value)=>!string.IsNullOrWhiteSpace(value)&&
        value.Length<=256&&!value.Any(char.IsControl);
    private static string Local(string? input,bool directory)
    {
        if(string.IsNullOrWhiteSpace(input)||input.Length>32767||!Path.IsPathFullyQualified(input)||
            input.StartsWith(@"\\",StringComparison.Ordinal))
            throw new InvalidDataException("ABSOLUTE_LOCAL_WORKSPACE_PATH_REQUIRED");
        var path=Path.TrimEndingDirectorySeparator(Path.GetFullPath(input));
        if(path.StartsWith(@"\\",StringComparison.Ordinal)||
            new DriveInfo(Path.GetPathRoot(path)!).DriveType==DriveType.Network)
            throw new InvalidDataException("LOCAL_WORKSPACE_PATH_REQUIRED");
        for(var current=path;current is not null;current=Path.GetDirectoryName(current))
            if((File.GetAttributes(current)&FileAttributes.ReparsePoint)!=0)
                throw new InvalidDataException("WORKSPACE_REPARSE_PATH");
        var isDirectory=(File.GetAttributes(path)&FileAttributes.Directory)!=0;
        if(isDirectory!=directory)throw new InvalidDataException("WORKSPACE_PATH_TYPE_MISMATCH");
        return path;
    }
}
