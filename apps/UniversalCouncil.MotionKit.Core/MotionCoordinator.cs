using System.Collections.Frozen;

namespace UniversalCouncil.MotionKit.Core;

public sealed class MotionCoordinator
{
    private const int MaxIdentifierLength = 256;
    private const int MaxQueueDepthPerTarget = 32;

    private readonly object _gate = new();
    private readonly Func<Guid> _idFactory;
    private readonly Dictionary<string, List<MotionLease>> _active = new(StringComparer.Ordinal);
    private readonly Dictionary<string, Queue<PendingMotion>> _queued = new(StringComparer.Ordinal);
    private readonly HashSet<Guid> _issuedIds = [];

    public MotionCoordinator(Func<Guid>? idFactory = null)
    {
        _idFactory = idFactory ?? Guid.NewGuid;
    }

    public MotionTransition Submit(MotionRequest request, DateTimeOffset now)
    {
        lock (_gate)
        {
            var invalid = ValidateRequest(request, now);
            if (invalid is not null)
            {
                return Transition(MotionDisposition.RejectedInvalid, invalid);
            }

            if (!request.Truth.Satisfied)
            {
                return Transition(
                    MotionDisposition.RejectedTruth,
                    $"Truth requirement is not satisfied: {request.Contract.TruthRequirementId}");
            }

            if (RequestExists(request.RequestId))
            {
                return Transition(
                    MotionDisposition.IgnoredDuplicate,
                    $"Request already exists: {request.RequestId}");
            }

            request = request with { Contract = SnapshotContract(request.Contract) };

            if (!_active.TryGetValue(request.TargetId, out var active) || active.Count == 0)
            {
                return Start(request, now, MotionDisposition.Started, []);
            }

            return request.Contract.InterruptionMode switch
            {
                MotionInterruptionMode.Replace => Replace(request, now, active),
                MotionInterruptionMode.Queue => Queue(request),
                MotionInterruptionMode.Coalesce => Coalesce(request, now, active),
                MotionInterruptionMode.IgnoreDuplicate => IgnoreDuplicate(request, now, active),
                MotionInterruptionMode.ParallelSafe => Start(
                    request,
                    now,
                    MotionDisposition.Started,
                    []),
                _ => Transition(MotionDisposition.RejectedInvalid, "Unknown interruption mode.")
            };
        }
    }

    public MotionTransition Complete(Guid instanceId)
    {
        lock (_gate)
        {
            string? targetId = null;
            MotionLease? lease = null;

            foreach (var pair in _active)
            {
                var match = pair.Value.FirstOrDefault(item => item.InstanceId == instanceId);
                if (match is not null)
                {
                    targetId = pair.Key;
                    lease = match;
                    break;
                }
            }

            if (targetId is null || lease is null)
            {
                return Transition(
                    MotionDisposition.StaleCompletionIgnored,
                    $"Motion instance is not active: {instanceId}");
            }

            var active = _active[targetId];
            active.Remove(lease);
            if (active.Count == 0)
            {
                _active.Remove(targetId);
            }

            PendingMotion? released = null;
            if (!_active.ContainsKey(targetId)
                && _queued.TryGetValue(targetId, out var queue)
                && queue.Count > 0)
            {
                released = queue.Dequeue();
                if (queue.Count == 0)
                {
                    _queued.Remove(targetId);
                }
            }

            return new MotionTransition(
                released is null
                    ? MotionDisposition.Completed
                    : MotionDisposition.CompletedQueueReleased,
                StartedLease: null,
                ReleasedPending: released,
                CancelledInstances: [],
                released is null
                    ? "Motion instance completed."
                    : "Motion instance completed; queued semantic intent released and requires fresh truth.");
        }
    }


    public MotionTransition ReconcileTruth(
        string targetId,
        MotionTruthSnapshot truth,
        DateTimeOffset now)
    {
        lock (_gate)
        {
            if (!ValidIdentifier(targetId))
            {
                return Transition(MotionDisposition.RejectedInvalid, "Target ID is invalid.");
            }

            var invalid = ValidateTruthSnapshot(truth, now);
            if (invalid is not null)
            {
                return Transition(MotionDisposition.RejectedInvalid, invalid);
            }

            if (truth.Satisfied)
            {
                return Transition(
                    MotionDisposition.TruthObserved,
                    $"Truth remains satisfied: {truth.RequirementId}");
            }

            var cancelled = new List<Guid>();
            if (_active.TryGetValue(targetId, out var active))
            {
                for (var index = active.Count - 1; index >= 0; index--)
                {
                    var lease = active[index];
                    if (string.Equals(
                            lease.TruthRequirementId,
                            truth.RequirementId,
                            StringComparison.Ordinal)
                        && truth.ObservedAt >= lease.TruthObservedAt)
                    {
                        cancelled.Add(lease.InstanceId);
                        active.RemoveAt(index);
                    }
                }

                if (active.Count == 0)
                {
                    _active.Remove(targetId);
                }
            }

            if (_queued.TryGetValue(targetId, out var queued))
            {
                var retained = queued
                    .Where(item => !string.Equals(
                        item.Contract.TruthRequirementId,
                        truth.RequirementId,
                        StringComparison.Ordinal))
                    .ToArray();

                if (retained.Length == 0)
                {
                    _queued.Remove(targetId);
                }
                else if (retained.Length != queued.Count)
                {
                    _queued[targetId] = new Queue<PendingMotion>(retained);
                }
            }

            PendingMotion? released = null;
            if (!_active.ContainsKey(targetId)
                && _queued.TryGetValue(targetId, out var remaining)
                && remaining.Count > 0)
            {
                released = remaining.Dequeue();
                if (remaining.Count == 0)
                {
                    _queued.Remove(targetId);
                }
            }

            return new MotionTransition(
                MotionDisposition.TruthRevoked,
                StartedLease: null,
                ReleasedPending: released,
                CancelledInstances: cancelled,
                released is not null
                    ? $"Truth revoked; matching motion stopped and next intent released for fresh truth: {truth.RequirementId}"
                    : cancelled.Count == 0
                        ? $"Truth revoked with no eligible active instance: {truth.RequirementId}"
                        : $"Truth revoked; matching motion stopped: {truth.RequirementId}");
        }
    }

    public MotionTransition CancelTarget(string targetId, string reason)
    {
        lock (_gate)
        {
            if (!ValidIdentifier(targetId))
            {
                return Transition(MotionDisposition.RejectedInvalid, "Target ID is invalid.");
            }

            var cancelled = _active.TryGetValue(targetId, out var active)
                ? active.Select(item => item.InstanceId).ToArray()
                : [];

            _active.Remove(targetId);
            _queued.Remove(targetId);

            return new MotionTransition(
                MotionDisposition.TargetCancelled,
                StartedLease: null,
                ReleasedPending: null,
                CancelledInstances: cancelled,
                string.IsNullOrWhiteSpace(reason) ? "Target cancelled." : reason);
        }
    }

    public int ActiveCount(string targetId)
    {
        lock (_gate)
        {
            return _active.TryGetValue(targetId, out var active) ? active.Count : 0;
        }
    }

    public int QueuedCount(string targetId)
    {
        lock (_gate)
        {
            return _queued.TryGetValue(targetId, out var queue) ? queue.Count : 0;
        }
    }

    private MotionTransition Replace(
        MotionRequest request,
        DateTimeOffset now,
        List<MotionLease> active)
    {
        var cancelled = active.Select(item => item.InstanceId).ToArray();
        active.Clear();
        return Start(request, now, MotionDisposition.ReplacedAndStarted, cancelled);
    }

    private MotionTransition Queue(MotionRequest request)
    {
        if (!_queued.TryGetValue(request.TargetId, out var queue))
        {
            queue = new Queue<PendingMotion>();
            _queued.Add(request.TargetId, queue);
        }

        if (queue.Count >= MaxQueueDepthPerTarget)
        {
            return Transition(
                MotionDisposition.RejectedInvalid,
                $"Queue depth exceeded for target: {request.TargetId}");
        }

        queue.Enqueue(new PendingMotion(
            request.RequestId,
            request.TargetId,
            request.Contract,
            request.AccessibilityMode));

        return Transition(
            MotionDisposition.QueuedAwaitingFreshTruth,
            "Queued semantic intent will require fresh truth when released.");
    }

    private MotionTransition Coalesce(
        MotionRequest request,
        DateTimeOffset now,
        List<MotionLease> active)
    {
        if (active.Any(item => item.SemanticEventId == request.Contract.SemanticEventId))
        {
            return Transition(
                MotionDisposition.Coalesced,
                $"Semantic event already active: {request.Contract.SemanticEventId}");
        }

        return Replace(request, now, active);
    }

    private MotionTransition IgnoreDuplicate(
        MotionRequest request,
        DateTimeOffset now,
        List<MotionLease> active)
    {
        if (active.Any(item => item.SemanticEventId == request.Contract.SemanticEventId))
        {
            return Transition(
                MotionDisposition.IgnoredDuplicate,
                $"Duplicate semantic event ignored: {request.Contract.SemanticEventId}");
        }

        return Replace(request, now, active);
    }

    private MotionTransition Start(
        MotionRequest request,
        DateTimeOffset now,
        MotionDisposition disposition,
        IReadOnlyList<Guid> cancelled)
    {
        var lease = new MotionLease(
            NextUniqueInstanceId(),
            request.RequestId,
            request.TargetId,
            request.Contract.SemanticEventId,
            request.Contract.TruthRequirementId,
            request.Truth.SourceVersion,
            request.Truth.ObservedAt,
            request.AccessibilityMode,
            now);

        if (!_active.TryGetValue(request.TargetId, out var active))
        {
            active = [];
            _active.Add(request.TargetId, active);
        }

        active.Add(lease);

        return new MotionTransition(
            disposition,
            lease,
            ReleasedPending: null,
            CancelledInstances: cancelled,
            disposition == MotionDisposition.ReplacedAndStarted
                ? "Existing target motion replaced by fresh semantic request."
                : "Semantic motion lease started.");
    }

    private Guid NextUniqueInstanceId()
    {
        for (var attempt = 0; attempt < 16; attempt++)
        {
            var candidate = _idFactory();
            if (candidate != Guid.Empty && _issuedIds.Add(candidate))
            {
                return candidate;
            }
        }

        throw new InvalidOperationException("Unable to allocate a unique motion instance ID.");
    }

    private bool RequestExists(string requestId)
    {
        if (_active.Values.SelectMany(items => items).Any(item => item.RequestId == requestId))
        {
            return true;
        }

        return _queued.Values.SelectMany(items => items).Any(item => item.RequestId == requestId);
    }

    private static string? ValidateRequest(MotionRequest request, DateTimeOffset now)
    {
        if (!ValidIdentifier(request.RequestId))
        {
            return "Request ID is invalid.";
        }

        if (!ValidIdentifier(request.TargetId))
        {
            return "Target ID is invalid.";
        }

        if (!ValidIdentifier(request.Contract.SemanticEventId))
        {
            return "Semantic event ID is invalid.";
        }

        if (request.Contract.Purposes is null || request.Contract.Purposes.Count == 0)
        {
            return "Motion purpose set is empty.";
        }

        if (request.Contract.Purposes.Any(
                purpose => !Enum.IsDefined(typeof(MotionPurpose), purpose)))
        {
            return "Motion purpose set contains an unknown value.";
        }

        if (!Enum.IsDefined(typeof(MotionInterruptionMode), request.Contract.InterruptionMode))
        {
            return "Interruption mode is unknown.";
        }

        if (!Enum.IsDefined(typeof(MotionAccessibilityMode), request.AccessibilityMode))
        {
            return "Accessibility mode is unknown.";
        }

        if (!ValidIdentifier(request.Contract.TruthRequirementId))
        {
            return "Truth requirement ID is invalid.";
        }

        var truthInvalid = ValidateTruthSnapshot(request.Truth, now);
        if (truthInvalid is not null)
        {
            return truthInvalid;
        }

        if (!string.Equals(
                request.Contract.TruthRequirementId,
                request.Truth.RequirementId,
                StringComparison.Ordinal))
        {
            return "Truth snapshot does not match the semantic contract requirement.";
        }

        if (string.IsNullOrWhiteSpace(request.Contract.ReducedMotionEquivalent))
        {
            return "Reduced Motion equivalent is required.";
        }

        return null;
    }


    private static string? ValidateTruthSnapshot(
        MotionTruthSnapshot truth,
        DateTimeOffset now)
    {
        if (!ValidIdentifier(truth.RequirementId))
        {
            return "Truth requirement ID is invalid.";
        }

        if (!ValidIdentifier(truth.SourceVersion))
        {
            return "Truth source version is invalid.";
        }

        if (truth.ObservedAt > now)
        {
            return "Truth snapshot is future-dated.";
        }

        return null;
    }

    private static MotionContract SnapshotContract(MotionContract contract) =>
        contract with
        {
            Purposes = contract.Purposes.ToFrozenSet()
        };

    private static bool ValidIdentifier(string? value)
    {
        if (string.IsNullOrWhiteSpace(value) || value.Length > MaxIdentifierLength)
        {
            return false;
        }

        return value.All(character => !char.IsControl(character));
    }

    private static MotionTransition Transition(MotionDisposition disposition, string reason) =>
        new(
            disposition,
            StartedLease: null,
            ReleasedPending: null,
            CancelledInstances: [],
            reason);
}
