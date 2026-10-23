using UniversalCouncil.MotionKit.Core;

var now = new DateTimeOffset(2026, 10, 23, 1, 0, 0, TimeSpan.Zero);

CheckFalseTruthRejected();
CheckWrongTruthIdentityRejected();
CheckReplaceAndStaleCompletion();
CheckCoalesce();
CheckIgnoreDuplicate();
CheckQueueRequiresFreshTruth();
CheckParallelSafe();
CheckReducedMotionPreserved();
CheckCancelTarget();

Console.WriteLine("MotionKit semantic kernel validation: PASS");

void CheckFalseTruthRejected()
{
    var coordinator = NewCoordinator(1);
    var request = Request(
        "r-false",
        "sigil:chair",
        Contract("ROLE_ACTIVATED", MotionInterruptionMode.Replace, "ROLE_STATE_ACTIVE"),
        Truth("ROLE_STATE_ACTIVE", false),
        MotionAccessibilityMode.Full);

    var result = coordinator.Submit(request, now);

    Check(result.Disposition == MotionDisposition.RejectedTruth, "false truth must reject motion");
    Check(coordinator.ActiveCount(request.TargetId) == 0, "false truth must not create a lease");
}

void CheckWrongTruthIdentityRejected()
{
    var coordinator = NewCoordinator(2);
    var request = Request(
        "r-wrong-truth",
        "route:a-b",
        Contract("ROUTE_TRANSFER", MotionInterruptionMode.Replace, "ROUTE_EVENT_EXISTS"),
        Truth("SOME_OTHER_REQUIREMENT", true),
        MotionAccessibilityMode.Full);

    var result = coordinator.Submit(request, now);

    Check(result.Disposition == MotionDisposition.RejectedInvalid, "truth identity mismatch must fail closed");
}

void CheckReplaceAndStaleCompletion()
{
    var coordinator = NewCoordinator(3, 4);
    const string target = "status:project";

    var first = coordinator.Submit(
        Request(
            "r-first",
            target,
            Contract("WAITING_OWNER", MotionInterruptionMode.Replace, "PRODUCT_STATE_WAITING_OWNER"),
            Truth("PRODUCT_STATE_WAITING_OWNER", true),
            MotionAccessibilityMode.Full),
        now);

    var second = coordinator.Submit(
        Request(
            "r-second",
            target,
            Contract("BLOCKED", MotionInterruptionMode.Replace, "PRODUCT_STATE_BLOCKED"),
            Truth("PRODUCT_STATE_BLOCKED", true),
            MotionAccessibilityMode.Full),
        now.AddMilliseconds(10));

    Check(first.StartedLease is not null, "first request should start");
    Check(second.Disposition == MotionDisposition.ReplacedAndStarted, "second request should replace first");
    Check(second.CancelledInstances.Contains(first.StartedLease.InstanceId), "replacement must identify cancelled instance");

    var stale = coordinator.Complete(first.StartedLease.InstanceId);
    Check(stale.Disposition == MotionDisposition.StaleCompletionIgnored, "replaced completion must be stale");
    Check(coordinator.ActiveCount(target) == 1, "stale completion must not affect replacement");

    var completed = coordinator.Complete(second.StartedLease!.InstanceId);
    Check(completed.Disposition == MotionDisposition.Completed, "current instance should complete");
    Check(coordinator.ActiveCount(target) == 0, "completed instance should leave no active lease");
}

void CheckCoalesce()
{
    var coordinator = NewCoordinator(5);
    var contract = Contract("SELECT", MotionInterruptionMode.Coalesce, "LOCAL_SELECTION_STATE");
    var truth = Truth("LOCAL_SELECTION_STATE", true);

    var first = coordinator.Submit(
        Request("r-select-1", "item:42", contract, truth, MotionAccessibilityMode.Full),
        now);
    var second = coordinator.Submit(
        Request("r-select-2", "item:42", contract, truth, MotionAccessibilityMode.Full),
        now);

    Check(first.Disposition == MotionDisposition.Started, "first coalescible event should start");
    Check(second.Disposition == MotionDisposition.Coalesced, "same active event should coalesce");
    Check(coordinator.ActiveCount("item:42") == 1, "coalesce must not duplicate active motion");
}

void CheckIgnoreDuplicate()
{
    var coordinator = NewCoordinator(6);
    var contract = Contract("INSPECT", MotionInterruptionMode.IgnoreDuplicate, "REAL_INSPECTABLE_TARGET");
    var truth = Truth("REAL_INSPECTABLE_TARGET", true);

    coordinator.Submit(
        Request("r-inspect-1", "artifact:1", contract, truth, MotionAccessibilityMode.Full),
        now);
    var duplicate = coordinator.Submit(
        Request("r-inspect-2", "artifact:1", contract, truth, MotionAccessibilityMode.Full),
        now);

    Check(duplicate.Disposition == MotionDisposition.IgnoredDuplicate, "duplicate inspect motion should be ignored");
    Check(coordinator.ActiveCount("artifact:1") == 1, "duplicate ignore must preserve one active lease");
}

void CheckQueueRequiresFreshTruth()
{
    var coordinator = NewCoordinator(7, 8);
    const string target = "handoff:artifact-7";

    var first = coordinator.Submit(
        Request(
            "r-handoff",
            target,
            Contract("HANDOFF", MotionInterruptionMode.Replace, "HANDOFF_EVENT_EXISTS"),
            Truth("HANDOFF_EVENT_EXISTS", true),
            MotionAccessibilityMode.Full),
        now);

    var queued = coordinator.Submit(
        Request(
            "r-return",
            target,
            Contract("RETURN", MotionInterruptionMode.Queue, "RETURN_EVENT_EXISTS"),
            Truth("RETURN_EVENT_EXISTS", true),
            MotionAccessibilityMode.Full),
        now);

    Check(queued.Disposition == MotionDisposition.QueuedAwaitingFreshTruth, "return should queue behind active handoff");
    Check(coordinator.QueuedCount(target) == 1, "queued intent should be retained");

    var release = coordinator.Complete(first.StartedLease!.InstanceId);

    Check(release.Disposition == MotionDisposition.CompletedQueueReleased, "completion should release queued intent");
    Check(release.ReleasedPending is not null, "released queue item should be explicit");
    Check(coordinator.ActiveCount(target) == 0, "released queue item must not auto-start from stale truth");
    Check(coordinator.QueuedCount(target) == 0, "released queue item must leave the queue");

    var refreshed = coordinator.Submit(
        Request(
            release.ReleasedPending.RequestId,
            target,
            release.ReleasedPending.Contract,
            Truth("RETURN_EVENT_EXISTS", true, "state-v2"),
            release.ReleasedPending.AccessibilityMode),
        now.AddSeconds(1));

    Check(refreshed.Disposition == MotionDisposition.Started, "released intent should start after fresh truth resubmission");
}

void CheckParallelSafe()
{
    var coordinator = NewCoordinator(9, 10);
    var contract = Contract("ROLE_ACTIVATED", MotionInterruptionMode.ParallelSafe, "ROLE_STATE_ACTIVE");
    var truth = Truth("ROLE_STATE_ACTIVE", true);

    coordinator.Submit(
        Request("r-role-a", "role-group:council", contract, truth, MotionAccessibilityMode.Full),
        now);
    coordinator.Submit(
        Request("r-role-b", "role-group:council", contract, truth, MotionAccessibilityMode.Full),
        now);

    Check(coordinator.ActiveCount("role-group:council") == 2, "parallel-safe contract should permit independent leases");
}

void CheckReducedMotionPreserved()
{
    var coordinator = NewCoordinator(11);
    var result = coordinator.Submit(
        Request(
            "r-reduced",
            "checkpoint:1",
            Contract("RECOVERY_FOCUS", MotionInterruptionMode.Replace, "VERIFIED_RECOVERY_TARGET_EXISTS"),
            Truth("VERIFIED_RECOVERY_TARGET_EXISTS", true),
            MotionAccessibilityMode.Reduced),
        now);

    Check(result.StartedLease is not null, "reduced motion request should start a semantic lease");
    Check(
        result.StartedLease.AccessibilityMode == MotionAccessibilityMode.Reduced,
        "reduced mode must survive coordination");
}

void CheckCancelTarget()
{
    var coordinator = NewCoordinator(12);
    var result = coordinator.Submit(
        Request(
            "r-cancel",
            "fork:1",
            Contract("FORK", MotionInterruptionMode.Replace, "FORK_STATE_EXISTS"),
            Truth("FORK_STATE_EXISTS", true),
            MotionAccessibilityMode.Full),
        now);

    var cancelled = coordinator.CancelTarget("fork:1", "state changed");

    Check(result.StartedLease is not null, "cancel test must start first");
    Check(cancelled.Disposition == MotionDisposition.TargetCancelled, "target cancellation must be explicit");
    Check(cancelled.CancelledInstances.Contains(result.StartedLease.InstanceId), "cancel result must identify active instance");
    Check(coordinator.ActiveCount("fork:1") == 0, "target cancellation must clear active motion");
}

MotionCoordinator NewCoordinator(params int[] ids)
{
    var queue = new Queue<Guid>(
        ids.Select(value => Guid.Parse($"00000000-0000-0000-0000-{value:D12}")));

    return new MotionCoordinator(() => queue.Dequeue());
}

MotionContract Contract(
    string eventId,
    MotionInterruptionMode interruption,
    string truthRequirement) =>
    new(
        eventId,
        new HashSet<MotionPurpose> { MotionPurpose.State },
        interruption,
        truthRequirement,
        "STATIC_EQUIVALENT");

MotionTruthSnapshot Truth(
    string requirement,
    bool satisfied,
    string sourceVersion = "state-v1") =>
    new(requirement, satisfied, sourceVersion, now);

MotionRequest Request(
    string requestId,
    string targetId,
    MotionContract contract,
    MotionTruthSnapshot truth,
    MotionAccessibilityMode accessibilityMode) =>
    new(requestId, targetId, contract, truth, accessibilityMode);

void Check(bool condition, string message)
{
    if (!condition)
    {
        throw new InvalidOperationException(message);
    }
}
