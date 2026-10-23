namespace UniversalCouncil.MotionKit.Core;

public enum MotionPurpose
{
    Navigation,
    State,
    Feedback,
    Routing,
    Handoff,
    Recovery
}

public enum MotionInterruptionMode
{
    Replace,
    Queue,
    Coalesce,
    IgnoreDuplicate,
    ParallelSafe
}

public enum MotionAccessibilityMode
{
    Full,
    Reduced
}

public enum MotionDisposition
{
    Started,
    ReplacedAndStarted,
    QueuedAwaitingFreshTruth,
    Coalesced,
    IgnoredDuplicate,
    RejectedTruth,
    RejectedInvalid,
    TruthObserved,
    TruthRevoked,
    Completed,
    CompletedQueueReleased,
    StaleCompletionIgnored,
    TargetCancelled
}

public sealed record MotionTruthSnapshot(
    string RequirementId,
    bool Satisfied,
    string SourceVersion,
    DateTimeOffset ObservedAt);

public sealed record MotionContract(
    string SemanticEventId,
    IReadOnlySet<MotionPurpose> Purposes,
    MotionInterruptionMode InterruptionMode,
    string TruthRequirementId,
    string ReducedMotionEquivalent,
    bool QuietWhenFalse = true);

public sealed record MotionRequest(
    string RequestId,
    string TargetId,
    MotionContract Contract,
    MotionTruthSnapshot Truth,
    MotionAccessibilityMode AccessibilityMode);

public sealed record PendingMotion(
    string RequestId,
    string TargetId,
    MotionContract Contract,
    MotionAccessibilityMode AccessibilityMode);

public sealed record MotionLease(
    Guid InstanceId,
    string RequestId,
    string TargetId,
    string SemanticEventId,
    string TruthRequirementId,
    string TruthSourceVersion,
    DateTimeOffset TruthObservedAt,
    MotionAccessibilityMode AccessibilityMode,
    DateTimeOffset StartedAt);

public sealed record MotionTransition(
    MotionDisposition Disposition,
    MotionLease? StartedLease,
    PendingMotion? ReleasedPending,
    IReadOnlyList<Guid> CancelledInstances,
    string Reason);
