using UniversalCouncil.MotionKit.Runtime;

namespace UniversalCouncil.MotionKit.Testing;

public sealed class DeterministicFakeRenderer : IMotionRendererAdapter
{
    private readonly object _gate = new();
    private readonly Dictionary<Guid, MotionRenderCommand> _active = [];
    private bool _disposed;
    private long _started;
    private long _cancelled;
    private long _settled;
    private long _unsupported;
    private long _rejected;
    private long _duplicate;

    public DeterministicFakeRenderer(
        string adapterId,
        string adapterVersion,
        MotionRenderCapability capabilities)
    {
        var invalid = MotionRendererContractGuard.ValidateAdapter(
            adapterId,
            adapterVersion,
            capabilities);
        if (invalid is not null)
        {
            throw new ArgumentException(invalid, nameof(adapterId));
        }

        AdapterId = adapterId;
        AdapterVersion = adapterVersion;
        Capabilities = capabilities;
    }

    public string AdapterId { get; }

    public string AdapterVersion { get; }

    public MotionRenderCapability Capabilities { get; }

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
                    "Adapter does not satisfy required renderer capabilities."));
            }

            if (_active.ContainsKey(command.Identity.InstanceId))
            {
                _duplicate++;
                return ValueTask.FromResult(Result(
                    MotionRenderStatus.DuplicateInstance,
                    command.Identity.InstanceId,
                    "Motion instance is already active in this adapter."));
            }

            _active.Add(command.Identity.InstanceId, command);
            _started++;

            return ValueTask.FromResult(Result(
                MotionRenderStatus.Started,
                command.Identity.InstanceId,
                "Motion render command accepted."));
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

            if (instanceId == Guid.Empty)
            {
                _rejected++;
                return ValueTask.FromResult(Result(
                    MotionRenderStatus.RejectedInvalid,
                    instanceId,
                    "Motion instance ID is empty."));
            }

            if (!_active.Remove(instanceId))
            {
                return ValueTask.FromResult(Result(
                    MotionRenderStatus.NotActive,
                    instanceId,
                    "Motion instance is not active."));
            }

            _cancelled++;
            return ValueTask.FromResult(Result(
                MotionRenderStatus.Cancelled,
                instanceId,
                string.IsNullOrWhiteSpace(reason) ? "Motion cancelled." : reason));
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

            if (!_active.ContainsKey(instanceId))
            {
                return ValueTask.FromResult(Result(
                    MotionRenderStatus.NotActive,
                    instanceId,
                    "Motion instance is not active."));
            }

            if (mode == MotionSettleMode.StaticFallback
                && !MotionRendererContractGuard.Supports(
                    Capabilities,
                    MotionRenderCapability.StaticSettle))
            {
                _unsupported++;
                return ValueTask.FromResult(Result(
                    MotionRenderStatus.NotSupported,
                    instanceId,
                    "Static fallback requires StaticSettle capability."));
            }

            _active.Remove(instanceId);
            _settled++;
            return ValueTask.FromResult(Result(
                MotionRenderStatus.Settled,
                instanceId,
                $"Motion settled using mode {mode}."));
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
                _disposed = true;
            }
        }

        return ValueTask.CompletedTask;
    }

    private MotionRenderResult Result(
        MotionRenderStatus status,
        Guid instanceId,
        string reason) =>
        new(status, instanceId, AdapterId, AdapterVersion, reason);

    private void ThrowIfDisposed() =>
        ObjectDisposedException.ThrowIf(_disposed, this);
}
