using UniversalCouncil.MotionKit.Core;

namespace UniversalCouncil.MotionKit.Runtime;

[Flags]
public enum MotionRenderCapability
{
    None = 0,
    StaticSettle = 1 << 0,
    Opacity = 1 << 1,
    Translation = 1 << 2,
    Scale = 1 << 3,
    Rotation = 1 << 4,
    PathGeometry = 1 << 5,
    DynamicDrawing = 1 << 6,
    StatefulVector = 1 << 7,
    PreauthoredTimeline = 1 << 8,
    HitTesting = 1 << 9,
    ColorBinding = 1 << 10
}

public enum MotionRenderStatus
{
    Started,
    NotSupported,
    RejectedInvalid,
    DuplicateInstance,
    NotActive,
    Cancelled,
    Settled
}

public enum MotionSettleMode
{
    Current,
    Final,
    StaticFallback
}

public enum MotionPreparationStatus
{
    Ready,
    RuleNotFound,
    RejectedInvalid
}

public sealed record MotionRenderIdentity(
    Guid InstanceId,
    string TargetId,
    string SemanticEventId,
    MotionAccessibilityMode AccessibilityMode);

public sealed record MotionVisualVariant(
    string VisualToken,
    TimeSpan Duration,
    MotionRenderCapability RequiredCapabilities);

public sealed record MotionVisualRule(
    string SemanticEventId,
    MotionVisualVariant Full,
    MotionVisualVariant Reduced);

public sealed record MotionProductProfile(
    string ProfileId,
    IReadOnlyDictionary<string, MotionVisualRule> Rules);

public sealed record MotionRenderCommand(
    MotionRenderIdentity Identity,
    string VisualToken,
    TimeSpan Duration,
    MotionRenderCapability RequiredCapabilities);

public sealed record MotionPreparationResult(
    MotionPreparationStatus Status,
    MotionRenderCommand? Command,
    string Reason);

public sealed record MotionRenderResult(
    MotionRenderStatus Status,
    Guid InstanceId,
    string AdapterId,
    string Reason);

public sealed record MotionRendererDiagnostics(
    string AdapterId,
    int ActiveCount,
    long StartedCount,
    long CancelledCount,
    long SettledCount,
    long UnsupportedCount,
    long RejectedCount,
    long DuplicateCount);

public interface IMotionRendererAdapter : IAsyncDisposable
{
    string AdapterId { get; }

    MotionRenderCapability Capabilities { get; }

    ValueTask<MotionRenderResult> BeginAsync(
        MotionRenderCommand command,
        CancellationToken cancellationToken = default);

    ValueTask<MotionRenderResult> CancelAsync(
        Guid instanceId,
        string reason,
        CancellationToken cancellationToken = default);

    ValueTask<MotionRenderResult> SettleAsync(
        Guid instanceId,
        MotionSettleMode mode,
        CancellationToken cancellationToken = default);

    MotionRendererDiagnostics SnapshotDiagnostics();
}
