using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Infrastructure;

// Same-user local storage. SHA256 detects corruption, not deliberate edits or authentic approval.
public sealed class JsonLocalReviewSessionStore : ILocalReviewSessionStore
{
    private readonly string root;
    private static readonly JsonSerializerOptions Options = new() {
        UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow,
        RespectRequiredConstructorParameters = true
    };
    private sealed record Envelope(int SchemaVersion, string Payload, string Sha256);
    public JsonLocalReviewSessionStore(string directory)
    {
        if (!Path.IsPathFullyQualified(directory)) throw new ArgumentException("Absolute store path required");
        root = Path.GetFullPath(directory);
        Directory.CreateDirectory(root);
        if ((File.GetAttributes(root) & FileAttributes.ReparsePoint) != 0)
            throw new InvalidDataException("Reparse store directory refused");
    }
    private string FilePath(Guid id)
    {
        if (id == Guid.Empty) throw new InvalidDataException("Empty session identifier");
        return Path.Combine(root, id.ToString("N") + ".json");
    }
    private FileStream Lock(Guid id) => new(FilePath(id) + ".lock", FileMode.OpenOrCreate,
        FileAccess.ReadWrite, FileShare.None);

    public LocalReviewSession Create(LocalReviewSession session)
    {
        LocalReviewSessionService.Validate(session);
        if (session.Version != 0 || session.Results.Length != 0 || session.TerminalReason is not null)
            throw new InvalidDataException("New session must be empty");
        using var held = Lock(session.Id);
        var path = FilePath(session.Id);
        if (File.Exists(path)) throw new IOException("Review session already exists");
        Write(path, session, false);
        return Load(path, session.Id);
    }
    public LocalReviewSession Transact(Guid id, int? expectedVersion,
        Func<LocalReviewSession, LocalReviewSession> mutation)
    {
        using var held = Lock(id);
        var path = FilePath(id);
        var before = Load(path, id);
        if (expectedVersion is not null && before.Version != expectedVersion)
            throw new IOException("Review session version conflict");
        var preimage = JsonSerializer.Serialize(before, Options);
        var binding = Binding(before);
        var priorResults = JsonSerializer.Serialize(before.Results, Options);
        var priorTerminal = before.TerminalReason;
        var priorVersion = before.Version;
        var priorTime = before.LastObservedAt;
        var priorCount = before.Results.Length;
        var after = mutation(before);
        LocalReviewSessionService.Validate(after);
        if (after.Id != id || after.Version < priorVersion || after.Version > priorVersion + 1 ||
            Binding(after) != binding || after.LastObservedAt < priorTime ||
            priorTerminal is not null && after.TerminalReason != priorTerminal ||
            after.Results.Length < priorCount ||
            JsonSerializer.Serialize(after.Results.Take(priorCount).ToArray(), Options) != priorResults)
            throw new InvalidDataException("Invalid session update version");
        if (after.Version == priorVersion && JsonSerializer.Serialize(after, Options) != preimage)
            throw new InvalidDataException("Changed session must advance version");
        if (after.Version != priorVersion)
        {
            if (after.Version != priorVersion + 1) throw new InvalidDataException("Version must advance");
            Write(path, after, true);
        }
        return Load(path, id);
    }
    private static LocalReviewSession Load(string path, Guid id)
    {
        if ((File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0)
            throw new InvalidDataException("Reparse session file refused");
        using var file = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
        if (file.Length > 4 * 1024 * 1024) throw new InvalidDataException("Session record too large");
        try
        {
            using var reader = new StreamReader(file, Encoding.UTF8, true);
            var text = reader.ReadToEnd();
            using var document = JsonDocument.Parse(text);
            NoDuplicates(document.RootElement);
            var envelope = JsonSerializer.Deserialize<Envelope>(text, Options)
                ?? throw new InvalidDataException("Missing envelope");
            if (envelope.SchemaVersion != 1 || envelope.Payload is null || envelope.Sha256 != Digest(envelope.Payload))
                throw new InvalidDataException("Session integrity mismatch");
            using var payload = JsonDocument.Parse(envelope.Payload);
            NoDuplicates(payload.RootElement);
            var session = JsonSerializer.Deserialize<LocalReviewSession>(envelope.Payload, Options)
                ?? throw new InvalidDataException("Missing session");
            LocalReviewSessionService.Validate(session);
            if (session.Id != id) throw new InvalidDataException("Session identifier mismatch");
            return session;
        }
        catch (JsonException ex) { throw new InvalidDataException("Malformed session JSON", ex); }
    }
    private static string Binding(LocalReviewSession session) => JsonSerializer.Serialize(
        new { session.SchemaVersion, session.Id, session.Request, session.Plan,
            session.ArtifactSha256, session.CreatedAt, session.ExpiresAt }, Options);
    private static string Digest(string text) =>
        Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(text)));
    private static void Write(string path, LocalReviewSession session, bool overwrite)
    {
        var payload = JsonSerializer.Serialize(session, Options);
        var bytes = JsonSerializer.SerializeToUtf8Bytes(new Envelope(1, payload, Digest(payload)), Options);
        if (bytes.Length > 4 * 1024 * 1024) throw new InvalidDataException("Session record too large");
        var temp = path + "." + Guid.NewGuid().ToString("N") + ".tmp";
        try
        {
            using (var file = new FileStream(temp, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            {
                file.Write(bytes);
                file.Flush(true);
            }
            File.Move(temp, path, overwrite);
        }
        finally { if (File.Exists(temp)) File.Delete(temp); }
    }
    private static void NoDuplicates(JsonElement element)
    {
        if (element.ValueKind == JsonValueKind.Object)
        {
            var keys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var property in element.EnumerateObject())
            {
                if (!keys.Add(property.Name)) throw new InvalidDataException("Duplicate session property");
                NoDuplicates(property.Value);
            }
        }
        else if (element.ValueKind == JsonValueKind.Array)
            foreach (var child in element.EnumerateArray()) NoDuplicates(child);
    }
}
