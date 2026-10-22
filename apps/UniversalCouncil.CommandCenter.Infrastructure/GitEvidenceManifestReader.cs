using System.Diagnostics;
using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Infrastructure;

public sealed class GitEvidenceManifestReader(string repository) : ICommittedEvidenceManifestReader
{
    private const int Limit = 1024 * 1024;
    public CommittedEvidenceManifest Read(EvidenceVerificationRequest request)
    {
        if (!EvidenceRules.Hex(request.SourceRevision,40) || !EvidenceRules.Hex(request.ManifestRevision,40))
            throw new InvalidDataException("FULL_COMMIT_IDS_REQUIRED");
        EvidenceRules.RelativePath(request.ManifestPath);
        if (!Path.IsPathFullyQualified(repository)) throw new InvalidDataException("ABSOLUTE_REPOSITORY_REQUIRED");
        var top = Encoding.UTF8.GetString(Run("rev-parse", "--show-toplevel")).Trim();
        if (!string.Equals(Path.GetFullPath(top), Path.GetFullPath(repository),
            OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal))
            throw new InvalidDataException("REPOSITORY_ROOT_MISMATCH");
        foreach (var revision in new[] { request.SourceRevision, request.ManifestRevision })
            if (Encoding.UTF8.GetString(Run("cat-file", "-t", revision)).Trim() != "commit")
                throw new InvalidDataException("COMMIT_OBJECT_REQUIRED");
        Run("merge-base", "--is-ancestor", request.SourceRevision, request.ManifestRevision);
        var reference = request.ManifestRevision + ":" + request.ManifestPath;
        var tree = Encoding.UTF8.GetString(Run("ls-tree", request.ManifestRevision, "--", request.ManifestPath));
        if (!tree.StartsWith("100644 blob ", StringComparison.Ordinal) &&
            !tree.StartsWith("100755 blob ", StringComparison.Ordinal))
            throw new InvalidDataException("REGULAR_MANIFEST_BLOB_REQUIRED");
        if (!long.TryParse(Encoding.UTF8.GetString(Run("cat-file", "-s", reference)).Trim(),
            NumberStyles.None, CultureInfo.InvariantCulture, out var size) || size is < 1 or > Limit)
            throw new InvalidDataException("MANIFEST_SIZE_LIMIT");
        var raw = Run("cat-file", "blob", reference);
        if (raw.LongLength != size) throw new InvalidDataException("MANIFEST_SIZE_CHANGED");
        using var document = JsonDocument.Parse(raw, new JsonDocumentOptions { MaxDepth = 16 });
        Duplicates(document.RootElement);
        var manifest = JsonSerializer.Deserialize<EvidenceManifest>(raw, new JsonSerializerOptions {
            UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow,
            RespectRequiredConstructorParameters = true, MaxDepth = 16
        }) ?? throw new InvalidDataException("MISSING_MANIFEST");
        var blob = Encoding.UTF8.GetString(Run("rev-parse", "--verify", reference)).Trim();
        if (!EvidenceRules.Hex(blob,40)) throw new InvalidDataException("INVALID_BLOB_ID");
        return new(manifest, request.ManifestRevision.ToLowerInvariant(), blob,
            Convert.ToHexString(SHA256.HashData(raw)));
    }

    public string ReadCurrentRevision()
    {
        if (!Path.IsPathFullyQualified(repository)) throw new InvalidDataException("ABSOLUTE_REPOSITORY_REQUIRED");
        var top=Encoding.UTF8.GetString(Run("rev-parse","--show-toplevel")).Trim();
        if(!string.Equals(Path.GetFullPath(top),Path.GetFullPath(repository),
            OperatingSystem.IsWindows()?StringComparison.OrdinalIgnoreCase:StringComparison.Ordinal))
            throw new InvalidDataException("REPOSITORY_ROOT_MISMATCH");
        var revision=Encoding.UTF8.GetString(Run("rev-parse","--verify","HEAD")).Trim();
        if(!EvidenceRules.Hex(revision,40)||Encoding.UTF8.GetString(Run("cat-file","-t",revision)).Trim()!="commit")
            throw new InvalidDataException("HEAD_COMMIT_REQUIRED");
        if(Run("status","--porcelain=v1","-z","--untracked-files=all","--ignore-submodules=none").Length!=0)
            throw new InvalidDataException("WORKSPACE_REPOSITORY_DIRTY");
        var index=Encoding.UTF8.GetString(Run("ls-files","-v","-z"));
        if(index.Split('\0',StringSplitOptions.RemoveEmptyEntries).Any(entry =>
            entry.Length<3 || entry[0]!='H' || entry[1]!=' '))
            throw new InvalidDataException("UNSUPPORTED_WORKSPACE_INDEX_FLAGS");
        if(Encoding.UTF8.GetString(Run("rev-parse","--verify","HEAD")).Trim()!=revision)
            throw new InvalidDataException("WORKSPACE_CHANGED_DURING_OBSERVATION");
        return revision.ToLowerInvariant();
    }

    private byte[] Run(params string[] args)
    {
        var start = new ProcessStartInfo("git") {
            WorkingDirectory = repository, UseShellExecute = false,
            RedirectStandardOutput = true, RedirectStandardError = true, CreateNoWindow = true
        };
        start.ArgumentList.Add("-c"); start.ArgumentList.Add("core.fsmonitor=false");
        start.ArgumentList.Add("--no-replace-objects");
        start.ArgumentList.Add("--literal-pathspecs");
        foreach (var arg in args) start.ArgumentList.Add(arg);
        foreach (var name in new[] { "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
            "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_TRACE", "GIT_TRACE_PACKET",
            "GIT_TRACE_PERFORMANCE", "GIT_TRACE_SETUP", "GIT_TRACE2", "GIT_TRACE2_EVENT", "GIT_TRACE2_PERF" })
            start.Environment.Remove(name);
        start.Environment["GIT_TERMINAL_PROMPT"] = "0";
        start.Environment["GIT_NO_LAZY_FETCH"] = "1";
        using var process = Process.Start(start) ?? throw new IOException("GIT_UNAVAILABLE");
        using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(10));
        try
        {
            var stdout = Bounded(process.StandardOutput.BaseStream, Limit, timeout.Token);
            var stderr = Bounded(process.StandardError.BaseStream, 65536, timeout.Token);
            Task.WhenAll(stdout, stderr, process.WaitForExitAsync(timeout.Token)).GetAwaiter().GetResult();
            if (process.ExitCode != 0) throw new InvalidDataException("GIT_LOOKUP_OR_ANCESTRY_FAILED");
            return stdout.Result;
        }
        catch
        {
            if (!process.HasExited) process.Kill(true);
            process.WaitForExit(5000);
            throw new InvalidDataException("GIT_READ_FAILED_OR_TIMED_OUT");
        }
    }
    private static async Task<byte[]> Bounded(Stream stream, int limit, CancellationToken token)
    {
        using var output = new MemoryStream();
        var buffer = new byte[8192];
        while (true)
        {
            var count = await stream.ReadAsync(buffer, token);
            if (count == 0) return output.ToArray();
            if (output.Length + count > limit) throw new InvalidDataException("GIT_OUTPUT_LIMIT");
            output.Write(buffer, 0, count);
        }
    }
    private static void Duplicates(JsonElement element)
    {
        if (element.ValueKind == JsonValueKind.Object)
        {
            var keys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var property in element.EnumerateObject())
            {
                if (!keys.Add(property.Name)) throw new InvalidDataException("DUPLICATE_MANIFEST_FIELD");
                Duplicates(property.Value);
            }
        }
        else if (element.ValueKind == JsonValueKind.Array)
            foreach (var child in element.EnumerateArray()) Duplicates(child);
    }
}
