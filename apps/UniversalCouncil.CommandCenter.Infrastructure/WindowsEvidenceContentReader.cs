using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Win32.SafeHandles;
using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Infrastructure;

// Windows local trusted-process boundary. No evidence files are executed or parsed.
public sealed class WindowsEvidenceContentReader(string artifactRoot) : ILocalEvidenceContentReader
{
    public EvidenceMeasurement Measure(string relativePath, long expectedSize)
    {
        if (!OperatingSystem.IsWindows()) throw new NotSupportedException("WINDOWS_FILE_READER_REQUIRED");
        EvidenceRules.RelativePath(relativePath);
        if (!Path.IsPathFullyQualified(artifactRoot) || artifactRoot.StartsWith(@"\\") ||
            expectedSize < 0 || expectedSize > EvidenceRules.MaxFileBytes)
            throw new InvalidDataException("INVALID_TRUSTED_ROOT_OR_SIZE");
        var root = Path.TrimEndingDirectorySeparator(Path.GetFullPath(artifactRoot));
        if (root.StartsWith(@"\\", StringComparison.Ordinal) ||
            new DriveInfo(Path.GetPathRoot(root)!).DriveType == DriveType.Network)
            throw new InvalidDataException("LOCAL_ARTIFACT_ROOT_REQUIRED");
        var path = Path.GetFullPath(Path.Combine(root, relativePath.Replace('/', Path.DirectorySeparatorChar)));
        if (!path.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("ARTIFACT_OUTSIDE_ROOT");
        for (var current = path; current is not null; current = Path.GetDirectoryName(current))
            if ((File.GetAttributes(current) & FileAttributes.ReparsePoint) != 0)
                throw new InvalidDataException("ARTIFACT_REPARSE_PATH");
        if ((File.GetAttributes(path) & FileAttributes.Directory) != 0)
            throw new InvalidDataException("REGULAR_ARTIFACT_REQUIRED");
        using var file = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read,
            65536, FileOptions.SequentialScan);
        var resolved = new StringBuilder(32768);
        var length = GetFinalPathNameByHandle(file.SafeFileHandle, resolved, (uint)resolved.Capacity, 0);
        if (length == 0 || length >= resolved.Capacity)
            throw new Win32Exception(Marshal.GetLastWin32Error());
        var actual = resolved.ToString();
        if (actual.StartsWith(@"\\?\", StringComparison.Ordinal)) actual = actual[4..];
        if (!string.Equals(actual, path, StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("ARTIFACT_HANDLE_PATH_MISMATCH");
        if (file.Length != expectedSize) throw new InvalidDataException("ARTIFACT_SIZE_MISMATCH");
        using var digest = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
        var buffer = new byte[65536];
        long total = 0;
        var deadline = System.Diagnostics.Stopwatch.StartNew();
        while (true)
        {
            if (deadline.Elapsed > TimeSpan.FromSeconds(120))
                throw new InvalidDataException("ARTIFACT_READ_TIMEOUT");
            var count = file.Read(buffer, 0, buffer.Length);
            if (count == 0) break;
            total += count;
            if (total > expectedSize || total > EvidenceRules.MaxFileBytes)
                throw new InvalidDataException("ARTIFACT_READ_SIZE_LIMIT");
            digest.AppendData(buffer, 0, count);
        }
        if (total != expectedSize || file.Length != total)
            throw new InvalidDataException("ARTIFACT_CHANGED_DURING_READ");
        return new(relativePath, Convert.ToHexString(digest.GetHashAndReset()), total);
    }
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern uint GetFinalPathNameByHandle(SafeFileHandle file,
        StringBuilder path, uint capacity, uint flags);
}
