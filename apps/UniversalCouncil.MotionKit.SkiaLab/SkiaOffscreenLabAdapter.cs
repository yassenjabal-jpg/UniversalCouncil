using System.Security.Cryptography;
using System.Text;
using SkiaSharp;
using UniversalCouncil.MotionKit.Runtime;

namespace UniversalCouncil.MotionKit.SkiaLab;

public sealed class SkiaOffscreenLabAdapter : IMotionRendererAdapter
{
    private readonly object _gate = new();
    private readonly Dictionary<Guid, MotionRenderCommand> _active = [];
    private readonly Dictionary<Guid, string> _frameHashes = [];
    private bool _disposed;
    private long _started;
    private long _cancelled;
    private long _settled;
    private long _unsupported;
    private long _rejected;
    private long _duplicate;

    public const string LabAdapterId = "lab:skia-offscreen";
    public const string LabAdapterVersion = "SkiaSharp-4.153.1";

    public string AdapterId => LabAdapterId;

    public string AdapterVersion => LabAdapterVersion;

    public MotionRenderCapability Capabilities =>
        MotionRenderCapability.StaticSettle
        | MotionRenderCapability.Opacity
        | MotionRenderCapability.Translation
        | MotionRenderCapability.Scale
        | MotionRenderCapability.Rotation
        | MotionRenderCapability.PathGeometry
        | MotionRenderCapability.DynamicDrawing
        | MotionRenderCapability.ColorBinding;

    public ValueTask<MotionRenderResult> BeginAsync(
        MotionRenderCommand command,
        CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();

        lock (_gate)
        {
            ThrowIfDisposed();

            var invalid = MotionRendererContractGuard.ValidateCommand(command);
            if (invalid is not null)
            {
                _rejected++;
                return ValueTask.FromResult(Result(
                    MotionRenderStatus.RejectedInvalid,
                    command.Identity.InstanceId,
                    invalid));
            }

            if (!MotionRendererContractGuard.Supports(
                    Capabilities,
                    command.RequiredCapabilities))
            {
                _unsupported++;
                return ValueTask.FromResult(Result(
                    MotionRenderStatus.NotSupported,
                    command.Identity.InstanceId,
                    "Skia lab adapter does not claim the requested capabilities."));
            }

            if (_active.ContainsKey(command.Identity.InstanceId))
            {
                _duplicate++;
                return ValueTask.FromResult(Result(
                    MotionRenderStatus.DuplicateInstance,
                    command.Identity.InstanceId,
                    "Motion instance is already active."));
            }

            var frameHash = RenderDeterministicFrame(command);
            _active.Add(command.Identity.InstanceId, command);
            _frameHashes[command.Identity.InstanceId] = frameHash;
            _started++;

            return ValueTask.FromResult(Result(
                MotionRenderStatus.Started,
                command.Identity.InstanceId,
                "Skia offscreen frame rendered and retained."));
        }
    }

    public ValueTask<MotionRenderResult> CancelAsync(
        Guid instanceId,
        string reason,
        CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();

        lock (_gate)
        {
            ThrowIfDisposed();

            if (!_active.Remove(instanceId))
            {
                return ValueTask.FromResult(Result(
                    MotionRenderStatus.NotActive,
                    instanceId,
                    "Motion instance is not active."));
            }

            _frameHashes.Remove(instanceId);
            _cancelled++;
            return ValueTask.FromResult(Result(
                MotionRenderStatus.Cancelled,
                instanceId,
                string.IsNullOrWhiteSpace(reason) ? "Skia lab render cancelled." : reason));
        }
    }

    public ValueTask<MotionRenderResult> SettleAsync(
        Guid instanceId,
        MotionSettleMode mode,
        CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();

        lock (_gate)
        {
            ThrowIfDisposed();

            if (instanceId == Guid.Empty
                || !Enum.IsDefined(typeof(MotionSettleMode), mode))
            {
                _rejected++;
                return ValueTask.FromResult(Result(
                    MotionRenderStatus.RejectedInvalid,
                    instanceId,
                    "Settle request is invalid."));
            }

            if (!_active.Remove(instanceId))
            {
                return ValueTask.FromResult(Result(
                    MotionRenderStatus.NotActive,
                    instanceId,
                    "Motion instance is not active."));
            }

            _frameHashes.Remove(instanceId);
            _settled++;
            return ValueTask.FromResult(Result(
                MotionRenderStatus.Settled,
                instanceId,
                $"Skia lab render settled using {mode}."));
        }
    }

    public bool TryGetFrameHash(Guid instanceId, out string frameHash)
    {
        lock (_gate)
        {
            ThrowIfDisposed();
            return _frameHashes.TryGetValue(instanceId, out frameHash!);
        }
    }

    public MotionRendererDiagnostics SnapshotDiagnostics()
    {
        lock (_gate)
        {
            ThrowIfDisposed();
            return new MotionRendererDiagnostics(
                AdapterId,
                AdapterVersion,
                _active.Count,
                _started,
                _cancelled,
                _settled,
                _unsupported,
                _rejected,
                _duplicate);
        }
    }

    public ValueTask DisposeAsync()
    {
        lock (_gate)
        {
            if (!_disposed)
            {
                _active.Clear();
                _frameHashes.Clear();
                _disposed = true;
            }
        }

        return ValueTask.CompletedTask;
    }

    private static string RenderDeterministicFrame(MotionRenderCommand command)
    {
        const int size = 64;
        using var bitmap = new SKBitmap(
            new SKImageInfo(size, size, SKColorType.Rgba8888, SKAlphaType.Premul));
        using var canvas = new SKCanvas(bitmap);
        canvas.Clear(SKColors.Transparent);

        var tokenBytes = SHA256.HashData(Encoding.UTF8.GetBytes(
            $"{command.ProfileId}|{command.VisualToken}|{command.Identity.AccessibilityMode}"));

        var color = new SKColor(tokenBytes[0], tokenBytes[1], tokenBytes[2], 255);
        var radius = 8f + tokenBytes[3] % 20;
        var x = 20f + tokenBytes[4] % 24;
        var y = 20f + tokenBytes[5] % 24;

        using var fill = new SKPaint
        {
            Color = color,
            IsAntialias = true,
            Style = SKPaintStyle.Fill
        };
        canvas.DrawCircle(x, y, radius, fill);

        using var stroke = new SKPaint
        {
            Color = new SKColor(tokenBytes[6], tokenBytes[7], tokenBytes[8], 255),
            IsAntialias = true,
            Style = SKPaintStyle.Stroke,
            StrokeWidth = 2f
        };
        using var pathBuilder = new SKPathBuilder();
        pathBuilder.MoveTo(4, 60);
        pathBuilder.LineTo(20 + tokenBytes[9] % 20, 8 + tokenBytes[10] % 24);
        pathBuilder.LineTo(60, 56);
        using var path = pathBuilder.Detach();
        canvas.DrawPath(path, stroke);
        canvas.Flush();

        using var image = SKImage.FromBitmap(bitmap);
        using var data = image.Encode(SKEncodedImageFormat.Png, 100);
        return Convert.ToHexString(SHA256.HashData(data.ToArray()));
    }

    private MotionRenderResult Result(
        MotionRenderStatus status,
        Guid instanceId,
        string reason) =>
        new(status, instanceId, AdapterId, AdapterVersion, reason);

    private void ThrowIfDisposed() =>
        ObjectDisposedException.ThrowIf(_disposed, this);
}
