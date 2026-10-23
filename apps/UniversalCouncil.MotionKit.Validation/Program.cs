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
CheckFutureTruthRejected();
CheckMissingReducedEquivalentRejected();
CheckUnknownEnumInputsRejected();
CheckTruthRevocationStopsMotion();
CheckStaleTruthRevocationCannotCancelNewerMotion();
CheckTruthRevocationReleasesNextQueuedIntent();
CheckContractSnapshotIsImmutable();
CheckQueueBound();
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

    var firstLease = first.StartedLease
        ?? throw new InvalidOperationException("first request should start");
    var secondLease = second.StartedLease
        ?? throw new InvalidOperationException("replacement request should start");
    Check(second.Disposition == MotionDisposition.ReplacedAndStarted, "second request should replace first");
    Check(second.CancelledInstances.Contains(firstLease.InstanceId), "replacement must identify cancelled instance");

    var stale = coordinator.Complete(firstLease.InstanceId);
    Check(stale.Disposition == MotionDisposition.StaleCompletionIgnored, "replaced completion must be stale");
    Check(coordinator.ActiveCount(target) == 1, "stale completion must not affect replacement");

    var completed = coordinator.Complete(secondLease.InstanceId);
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

    var handoffLease = first.StartedLease
        ?? throw new InvalidOperationException("handoff request should start");
    var release = coordinator.Complete(handoffLease.InstanceId);

    Check(release.Disposition == MotionDisposition.CompletedQueueReleased, "completion should release queued intent");
    var releasedPending = release.ReleasedPending
        ?? throw new InvalidOperationException("released queue item should be explicit");
    Check(coordinator.ActiveCount(target) == 0, "released queue item must not auto-start from stale truth");
    Check(coordinator.QueuedCount(target) == 0, "released queue item must leave the queue");

    var refreshed = coordinator.Submit(
        Request(
            releasedPending.RequestId,
            target,
            releasedPending.Contract,
            Truth("RETURN_EVENT_EXISTS", true, "state-v2"),
            releasedPending.AccessibilityMode),
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

    var reducedLease = result.StartedLease
        ?? throw new InvalidOperationException("reduced motion request should start a semantic lease");
    Check(
        reducedLease.AccessibilityMode == MotionAccessibilityMode.Reduced,
        "reduced mode must survive coordination");
}


void CheckFutureTruthRejected()
{
    var coordinator = NewCoordinator(13);
    var contract = Contract("WAITING_OWNER", MotionInterruptionMode.Replace, "PRODUCT_STATE_WAITING_OWNER");
    var futureTruth = new MotionTruthSnapshot(
        "PRODUCT_STATE_WAITING_OWNER",
        true,
        "state-v1",
        now.AddMilliseconds(1));

    var result = coordinator.Submit(
        Request(
            "r-future",
            "status:future",
            contract,
            futureTruth,
            MotionAccessibilityMode.Full),
        now);

    Check(result.Disposition == MotionDisposition.RejectedInvalid, "future-dated truth must fail closed");
    Check(coordinator.ActiveCount("status:future") == 0, "future truth must not create a lease");
}

void CheckMissingReducedEquivalentRejected()
{
    var coordinator = NewCoordinator(14);
    var invalidContract = new MotionContract(
        "SELECT",
        new HashSet<MotionPurpose> { MotionPurpose.Feedback },
        MotionInterruptionMode.Replace,
        "LOCAL_SELECTION_STATE",
        ReducedMotionEquivalent: "");

    var result = coordinator.Submit(
        Request(
            "r-no-reduced",
            "item:no-reduced",
            invalidContract,
            Truth("LOCAL_SELECTION_STATE", true),
            MotionAccessibilityMode.Full),
        now);

    Check(result.Disposition == MotionDisposition.RejectedInvalid, "Reduced Motion equivalent must be mandatory");
}


void CheckUnknownEnumInputsRejected()
{
    var unknownInterruption = (MotionInterruptionMode)999;
    var unknownAccessibility = (MotionAccessibilityMode)999;
    var unknownPurpose = (MotionPurpose)999;

    var coordinator = NewCoordinator(16);
    var badInterruption = coordinator.Submit(
        Request(
            "r-bad-interruption",
            "enum:interruption",
            Contract("SELECT", unknownInterruption, "LOCAL_SELECTION_STATE"),
            Truth("LOCAL_SELECTION_STATE", true),
            MotionAccessibilityMode.Full),
        now);
    Check(
        badInterruption.Disposition == MotionDisposition.RejectedInvalid,
        "unknown interruption mode must fail closed even when target is idle");

    var badAccessibility = coordinator.Submit(
        Request(
            "r-bad-accessibility",
            "enum:accessibility",
            Contract("SELECT", MotionInterruptionMode.Replace, "LOCAL_SELECTION_STATE"),
            Truth("LOCAL_SELECTION_STATE", true),
            unknownAccessibility),
        now);
    Check(
        badAccessibility.Disposition == MotionDisposition.RejectedInvalid,
        "unknown accessibility mode must fail closed");

    var badPurposeContract = new MotionContract(
        "SELECT",
        new HashSet<MotionPurpose> { unknownPurpose },
        MotionInterruptionMode.Replace,
        "LOCAL_SELECTION_STATE",
        "STATIC_EQUIVALENT");
    var badPurpose = coordinator.Submit(
        Request(
            "r-bad-purpose",
            "enum:purpose",
            badPurposeContract,
            Truth("LOCAL_SELECTION_STATE", true),
            MotionAccessibilityMode.Full),
        now);
    Check(
        badPurpose.Disposition == MotionDisposition.RejectedInvalid,
        "unknown motion purpose must fail closed");
}


void CheckTruthRevocationStopsMotion()
{
    var coordinator = NewCoordinator(17);
    const string target = "status:truth-revoke";

    var started = coordinator.Submit(
        Request(
            "r-truth-revoke",
            target,
            Contract("WAITING_OWNER", MotionInterruptionMode.Replace, "PRODUCT_STATE_WAITING_OWNER"),
            Truth("PRODUCT_STATE_WAITING_OWNER", true),
            MotionAccessibilityMode.Full),
        now);
    var lease = started.StartedLease
        ?? throw new InvalidOperationException("truth revocation test must start");

    var revoked = coordinator.ReconcileTruth(
        target,
        new MotionTruthSnapshot(
            "PRODUCT_STATE_WAITING_OWNER",
            false,
            "state-v2",
            now.AddMilliseconds(10)),
        now.AddMilliseconds(10));

    Check(revoked.Disposition == MotionDisposition.TruthRevoked, "false truth must produce explicit revocation");
    Check(revoked.CancelledInstances.Contains(lease.InstanceId), "truth revocation must cancel matching active motion");
    Check(coordinator.ActiveCount(target) == 0, "revoked truth must stop matching active motion");
}

void CheckStaleTruthRevocationCannotCancelNewerMotion()
{
    var coordinator = NewCoordinator(18);
    const string target = "status:truth-freshness";

    var started = coordinator.Submit(
        Request(
            "r-newer-truth",
            target,
            Contract("BLOCKED", MotionInterruptionMode.Replace, "PRODUCT_STATE_BLOCKED"),
            new MotionTruthSnapshot(
                "PRODUCT_STATE_BLOCKED",
                true,
                "state-v2",
                now.AddMilliseconds(20)),
            MotionAccessibilityMode.Full),
        now.AddMilliseconds(20));
    var lease = started.StartedLease
        ?? throw new InvalidOperationException("freshness test must start");

    var staleRevoke = coordinator.ReconcileTruth(
        target,
        new MotionTruthSnapshot(
            "PRODUCT_STATE_BLOCKED",
            false,
            "state-v1",
            now.AddMilliseconds(10)),
        now.AddMilliseconds(30));

    Check(staleRevoke.Disposition == MotionDisposition.TruthRevoked, "stale false truth is observed but not authoritative over newer lease");
    Check(!staleRevoke.CancelledInstances.Contains(lease.InstanceId), "older truth must not cancel motion backed by newer truth");
    Check(coordinator.ActiveCount(target) == 1, "newer active motion must survive stale truth revocation");
}

void CheckTruthRevocationReleasesNextQueuedIntent()
{
    var coordinator = NewCoordinator(19, 20);
    const string target = "handoff:truth-release";

    var active = coordinator.Submit(
        Request(
            "r-active-handoff",
            target,
            Contract("HANDOFF", MotionInterruptionMode.Replace, "HANDOFF_EVENT_EXISTS"),
            Truth("HANDOFF_EVENT_EXISTS", true),
            MotionAccessibilityMode.Full),
        now);
    _ = active.StartedLease
        ?? throw new InvalidOperationException("truth release test must start active handoff");

    var queued = coordinator.Submit(
        Request(
            "r-queued-return",
            target,
            Contract("RETURN", MotionInterruptionMode.Queue, "RETURN_EVENT_EXISTS"),
            Truth("RETURN_EVENT_EXISTS", true),
            MotionAccessibilityMode.Full),
        now);
    Check(queued.Disposition == MotionDisposition.QueuedAwaitingFreshTruth, "return intent should queue");

    var revoked = coordinator.ReconcileTruth(
        target,
        new MotionTruthSnapshot(
            "HANDOFF_EVENT_EXISTS",
            false,
            "state-v2",
            now.AddMilliseconds(5)),
        now.AddMilliseconds(5));

    Check(revoked.Disposition == MotionDisposition.TruthRevoked, "handoff truth must revoke active motion");
    var released = revoked.ReleasedPending
        ?? throw new InvalidOperationException("next queued intent must be released after active truth revocation");
    Check(released.RequestId == "r-queued-return", "released queued intent identity must be preserved");
    Check(coordinator.ActiveCount(target) == 0, "released intent must not auto-start");
    Check(coordinator.QueuedCount(target) == 0, "released intent must leave queue and await fresh resubmission");
}

void CheckContractSnapshotIsImmutable()
{
    var coordinator = NewCoordinator(21);
    const string target = "route:immutable-contract";

    var active = coordinator.Submit(
        Request(
            "r-snapshot-active",
            target,
            Contract("ROUTE_TRANSFER", MotionInterruptionMode.Replace, "ROUTE_EVENT_EXISTS"),
            Truth("ROUTE_EVENT_EXISTS", true),
            MotionAccessibilityMode.Full),
        now);
    var activeLease = active.StartedLease
        ?? throw new InvalidOperationException("contract snapshot test must start active motion");

    var mutablePurposes = new HashSet<MotionPurpose> { MotionPurpose.Handoff };
    var mutableContract = new MotionContract(
        "RETURN",
        mutablePurposes,
        MotionInterruptionMode.Queue,
        "RETURN_EVENT_EXISTS",
        "STATIC_RETURN");

    var queued = coordinator.Submit(
        Request(
            "r-snapshot-queued",
            target,
            mutableContract,
            Truth("RETURN_EVENT_EXISTS", true),
            MotionAccessibilityMode.Full),
        now);
    Check(queued.Disposition == MotionDisposition.QueuedAwaitingFreshTruth, "mutable contract should queue after snapshot");

    mutablePurposes.Clear();
    mutablePurposes.Add(MotionPurpose.Feedback);

    var completed = coordinator.Complete(activeLease.InstanceId);
    var released = completed.ReleasedPending
        ?? throw new InvalidOperationException("snapshotted queued contract should be released");
    Check(released.Contract.Purposes.Contains(MotionPurpose.Handoff), "queued contract must retain snapshotted original purpose");
    Check(!released.Contract.Purposes.Contains(MotionPurpose.Feedback), "external mutation must not alter queued contract");
}

void CheckQueueBound()
{
    var coordinator = NewCoordinator(15);
    const string target = "route:queue-bound";

    var active = coordinator.Submit(
        Request(
            "r-queue-active",
            target,
            Contract("ROUTE_TRANSFER", MotionInterruptionMode.Replace, "ROUTE_EVENT_EXISTS"),
            Truth("ROUTE_EVENT_EXISTS", true),
            MotionAccessibilityMode.Full),
        now);
    Check(active.Disposition == MotionDisposition.Started, "queue-bound test must start an active motion");

    var queuedContract = Contract("RETURN", MotionInterruptionMode.Queue, "RETURN_EVENT_EXISTS");
    for (var index = 0; index < 32; index++)
    {
        var queued = coordinator.Submit(
            Request(
                $"r-queue-{index:D2}",
                target,
                queuedContract,
                Truth("RETURN_EVENT_EXISTS", true),
                MotionAccessibilityMode.Full),
            now);

        Check(
            queued.Disposition == MotionDisposition.QueuedAwaitingFreshTruth,
            $"queue item {index} should remain within the bounded queue");
    }

    var overflow = coordinator.Submit(
        Request(
            "r-queue-overflow",
            target,
            queuedContract,
            Truth("RETURN_EVENT_EXISTS", true),
            MotionAccessibilityMode.Full),
        now);

    Check(overflow.Disposition == MotionDisposition.RejectedInvalid, "queue overflow must fail closed");
    Check(coordinator.QueuedCount(target) == 32, "queue overflow must not mutate the bounded queue");
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

    var cancelLease = result.StartedLease
        ?? throw new InvalidOperationException("cancel test must start first");
    Check(cancelled.Disposition == MotionDisposition.TargetCancelled, "target cancellation must be explicit");
    Check(cancelled.CancelledInstances.Contains(cancelLease.InstanceId), "cancel result must identify active instance");
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
