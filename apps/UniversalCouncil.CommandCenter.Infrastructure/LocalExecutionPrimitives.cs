using System.Text.Json;
using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Infrastructure;

public sealed class FileControllerLease : IControllerLease
{
    private readonly string path;
    private readonly string counterPath;
    private readonly TimeSpan ttl;
    private readonly Func<DateTimeOffset> utcNow;

    public FileControllerLease(
        string path,
        TimeSpan? ttl = null,
        Func<DateTimeOffset>? utcNow = null)
    {
        this.path = path;
        counterPath = path + ".fence";
        this.ttl = ttl ?? TimeSpan.FromMinutes(2);
        this.utcNow = utcNow ?? (() => DateTimeOffset.UtcNow);
    }

    public ControllerLeaseToken Acquire(
        string resource,
        string holder,
        string sessionId)
    {
        if (string.IsNullOrWhiteSpace(resource) ||
            string.IsNullOrWhiteSpace(holder) ||
            string.IsNullOrWhiteSpace(sessionId))
        {
            throw new InvalidOperationException(
                "Lease resource/holder/session are required.");
        }

        Directory.CreateDirectory(
            Path.GetDirectoryName(Path.GetFullPath(path))!);

        for (var attempt = 0; attempt < 6; attempt++)
        {
            if (File.Exists(path))
            {
                var current = Read();
                if (utcNow() - current.AcquiredAt <= ttl)
                {
                    if (current.Resource == resource &&
                        current.Holder == holder &&
                        current.SessionId == sessionId)
                    {
                        return current;
                    }

                    throw new InvalidOperationException(
                        "Controller lease is held by another session.");
                }

                File.Delete(path);
                continue;
            }

            var token = new ControllerLeaseToken(
                resource,
                holder,
                sessionId,
                NextFence(),
                utcNow());

            try
            {
                using var stream = new FileStream(
                    path,
                    FileMode.CreateNew,
                    FileAccess.Write,
                    FileShare.None);
                JsonSerializer.Serialize(stream, token);
                stream.Flush(flushToDisk: true);
                return token;
            }
            catch (IOException)
            {
                continue;
            }
        }

        throw new InvalidOperationException(
            "Controller lease acquisition exceeded bounded retries.");
    }

    public void AssertCurrent(ControllerLeaseToken token)
    {
        var current = Read();
        if (current != token)
        {
            throw new InvalidOperationException(
                "Controller lease fencing token is stale.");
        }

        if (utcNow() - current.AcquiredAt > ttl)
        {
            throw new InvalidOperationException(
                "Controller lease expired.");
        }
    }

    public void Release(ControllerLeaseToken token)
    {
        if (!File.Exists(path))
        {
            return;
        }

        var current = Read();
        if (current != token)
        {
            throw new InvalidOperationException(
                "Only the current fenced holder may release the lease.");
        }

        File.Delete(path);
    }

    private ControllerLeaseToken Read()
    {
        try
        {
            return JsonSerializer.Deserialize<ControllerLeaseToken>(
                File.ReadAllText(path))
                ?? throw new InvalidOperationException(
                    "Controller lease is empty.");
        }
        catch (Exception exc) when (
            exc is IOException or JsonException)
        {
            throw new InvalidOperationException(
                "Controller lease is unreadable.",
                exc);
        }
    }

    private long NextFence()
    {
        long previous = 0;
        if (File.Exists(counterPath))
        {
            if (!long.TryParse(
                    File.ReadAllText(counterPath).Trim(),
                    out previous) ||
                previous < 0)
            {
                throw new InvalidOperationException(
                    "Controller fencing counter is invalid.");
            }
        }

        var next = Math.Max(previous + 1, utcNow().UtcTicks);
        var temp = counterPath + "." + Guid.NewGuid().ToString("N") + ".tmp";
        File.WriteAllText(temp, next.ToString());
        File.Move(temp, counterPath, overwrite: true);
        return next;
    }
}

public sealed class AppendOnlyExecutionJournal : IExecutionJournal
{
    private readonly string path;

    public AppendOnlyExecutionJournal(string path)
    {
        this.path = path;
    }

    public void RecordIntent(ExecutionManifest manifest) =>
        Append(new JournalRecord(
            "intent",
            manifest.TaskId,
            manifest.ManifestId,
            null,
            DateTimeOffset.UtcNow));

    public void RecordReceipt(ExecutionReceipt receipt) =>
        Append(new JournalRecord(
            "receipt",
            receipt.TaskId,
            receipt.ManifestId,
            receipt.State,
            receipt.RecordedAt));

    public IReadOnlyList<string> PendingManifestIds(string taskId)
    {
        var pending = new HashSet<string>(StringComparer.Ordinal);

        foreach (var record in ReadAll())
        {
            if (record.TaskId != taskId)
            {
                continue;
            }

            if (record.Type == "intent")
            {
                pending.Add(record.ManifestId);
            }
            else if (record.Type == "receipt" &&
                     record.State != "UNKNOWN")
            {
                pending.Remove(record.ManifestId);
            }
        }

        return pending.OrderBy(item => item, StringComparer.Ordinal).ToArray();
    }

    private void Append(JournalRecord record)
    {
        Directory.CreateDirectory(
            Path.GetDirectoryName(Path.GetFullPath(path))!);

        using var stream = new FileStream(
            path,
            FileMode.Append,
            FileAccess.Write,
            FileShare.Read);
        using var writer = new StreamWriter(stream);
        writer.WriteLine(JsonSerializer.Serialize(record));
        writer.Flush();
        stream.Flush(flushToDisk: true);
    }

    private IReadOnlyList<JournalRecord> ReadAll()
    {
        if (!File.Exists(path))
        {
            return [];
        }

        var result = new List<JournalRecord>();
        foreach (var line in File.ReadLines(path))
        {
            if (string.IsNullOrWhiteSpace(line))
            {
                continue;
            }

            try
            {
                result.Add(
                    JsonSerializer.Deserialize<JournalRecord>(line)
                    ?? throw new InvalidOperationException(
                        "Execution journal record is empty."));
            }
            catch (JsonException exc)
            {
                throw new InvalidOperationException(
                    "Execution journal contains invalid JSON.",
                    exc);
            }
        }

        return result;
    }

    private sealed record JournalRecord(
        string Type,
        string TaskId,
        string ManifestId,
        string? State,
        DateTimeOffset RecordedAt);
}
