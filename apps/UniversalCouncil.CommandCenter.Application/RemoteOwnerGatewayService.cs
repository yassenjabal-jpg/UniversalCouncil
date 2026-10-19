using System.Security.Cryptography;
using System.Text;
using UniversalCouncil.CommandCenter.Core;

namespace UniversalCouncil.CommandCenter.Application;

public sealed class RemoteOwnerProjectionService : IRemoteOwnerGatewayProvider
{
    private readonly IRemoteOwnerGatewayReader reader;

    public RemoteOwnerProjectionService(IRemoteOwnerGatewayReader reader)
    {
        this.reader = reader;
    }

    public RemoteOwnerGatewayProjection GetGateway()
    {
        try
        {
            var document = reader.Read();
            RemoteOwnerPolicyValidator.ValidateDocument(document);

            return new RemoteOwnerGatewayProjection(
                RemoteOwnerHealth.Healthy,
                string.Empty,
                document.Gateway.Mode,
                document.Gateway.TargetHost,
                document.Gateway.AuthenticationBackendConnected,
                document.Gateway.LiveNetworkListenerEnabled,
                document.Gateway.LocalCliIngressEnabled,
                document.Gateway.TailscaleCompatibleArchitecture,
                document.Gateway.PublicInternetExposureAllowed,
                document.Gateway.RouterPortForwardingAllowed,
                document.Gateway.GithubQueueTransportEnabled,
                document.Gateway.ChatTransportEnabled,
                document.Gateway.Phase0RemoteTrustStatus,
                document.Gateway.LiveExecutionAuthorized,
                document.RuntimeTruth.RegisteredDevices,
                document.RuntimeTruth.RegisteredSessions,
                document.RuntimeTruth.QueueDepth,
                document.RuntimeTruth.PhoneConnected,
                document.RuntimeTruth.TailscaleConnected);
        }
        catch (RemoteOwnerGatewayException exc)
        {
            return RemoteOwnerGatewayProjection.Unavailable(exc.Message);
        }
        catch (Exception exc)
        {
            return RemoteOwnerGatewayProjection.Unavailable(
                $"Unexpected remote-owner gateway failure: {exc.GetType().Name}");
        }
    }
}

public sealed class RemoteCommandTrustService : IRemoteCommandTrustService
{
    private readonly IRemoteOwnerGatewayReader reader;
    private readonly IDeviceSessionRegistry registry;
    private readonly IRemoteReplayLedger replayLedger;
    private readonly IRemoteCommandQueue queue;
    private readonly Func<DateTimeOffset> utcNow;

    public RemoteCommandTrustService(
        IRemoteOwnerGatewayReader reader,
        IDeviceSessionRegistry registry,
        IRemoteReplayLedger replayLedger,
        IRemoteCommandQueue queue,
        Func<DateTimeOffset>? utcNow = null)
    {
        this.reader = reader;
        this.registry = registry;
        this.replayLedger = replayLedger;
        this.queue = queue;
        this.utcNow = utcNow ?? (() => DateTimeOffset.UtcNow);
    }

    public void Validate(
        RemoteCommandEnvelope envelope,
        OwnerAuthorizationContext authorization)
    {
        var document = reader.Read();
        RemoteOwnerPolicyValidator.ValidateDocument(document);
        var now = utcNow();

        Require(envelope.CommandId, nameof(envelope.CommandId));
        Require(envelope.Nonce, nameof(envelope.Nonce));
        Require(envelope.IdempotencyKey, nameof(envelope.IdempotencyKey));
        Require(envelope.OwnerId, nameof(envelope.OwnerId));
        Require(envelope.DeviceId, nameof(envelope.DeviceId));
        Require(envelope.SessionId, nameof(envelope.SessionId));
        Require(envelope.Target, nameof(envelope.Target));
        Require(envelope.Instruction, nameof(envelope.Instruction));
        Require(envelope.ApprovalIntent, nameof(envelope.ApprovalIntent));
        Require(envelope.CorrelationId, nameof(envelope.CorrelationId));

        if (envelope.Effects.Count == 0 ||
            envelope.Effects.Any(string.IsNullOrWhiteSpace))
        {
            throw new RemoteOwnerGatewayException(
                "Remote command requires at least one bounded effect.");
        }

        if (envelope.Instruction.Length > 8000)
        {
            throw new RemoteOwnerGatewayException(
                "Remote command instruction exceeds the Stage 5 bound.");
        }

        if (envelope.ExpiresAt <= envelope.IssuedAt)
        {
            throw new RemoteOwnerGatewayException(
                "Remote command expiry must be after issue time.");
        }

        var skew = TimeSpan.FromSeconds(
            document.TrustContract.MaxClockSkewSeconds);
        if (envelope.IssuedAt > now + skew)
        {
            throw new RemoteOwnerGatewayException(
                "Remote command issue time exceeds allowed clock skew.");
        }

        if (now > envelope.ExpiresAt)
        {
            throw new RemoteOwnerGatewayException(
                "Remote command expired.");
        }

        var ttl = envelope.ExpiresAt - envelope.IssuedAt;
        if (ttl > TimeSpan.FromSeconds(
                document.TrustContract.MaxCommandTtlSeconds))
        {
            throw new RemoteOwnerGatewayException(
                "Remote command TTL exceeds Stage 5 maximum.");
        }

        if (!authorization.Authenticated ||
            authorization.Revoked ||
            !string.Equals(
                authorization.Principal,
                document.Gateway.OwnerPrincipal,
                StringComparison.Ordinal))
        {
            throw new RemoteOwnerGatewayException(
                "Remote command requires authenticated OWNER context.");
        }

        Require(
            authorization.AuthenticationSource,
            nameof(authorization.AuthenticationSource));

        if (authorization.ValidFrom > now ||
            authorization.ExpiresAt <= now)
        {
            throw new RemoteOwnerGatewayException(
                "Owner authorization context is outside its validity window.");
        }

        if (authorization.OwnerId != envelope.OwnerId ||
            authorization.DeviceId != envelope.DeviceId ||
            authorization.SessionId != envelope.SessionId)
        {
            throw new RemoteOwnerGatewayException(
                "Owner/device/session identity mismatch.");
        }

        var allowedTargets = new HashSet<string>(
            authorization.AllowedTargets,
            StringComparer.Ordinal);
        if (!allowedTargets.Contains(envelope.Target))
        {
            throw new RemoteOwnerGatewayException(
                "Remote command target exceeds authenticated scope.");
        }

        var allowedEffects = new HashSet<string>(
            authorization.AllowedEffects,
            StringComparer.Ordinal);
        if (!envelope.Effects.All(allowedEffects.Contains))
        {
            throw new RemoteOwnerGatewayException(
                "Remote command effects exceed authenticated scope.");
        }

        registry.AssertTrusted(authorization, now);
    }

    public RemoteCommandReceipt EnqueueSynthetic(
        RemoteCommandEnvelope envelope,
        OwnerAuthorizationContext authorization) =>
        Enqueue(
            envelope,
            authorization,
            "LOCAL_SYNTHETIC_INGRESS_ONLY / PHASE0_REMOTE_COMMAND_TRUST_IN_TEST");

    public RemoteCommandReceipt EnqueueAuthenticatedTransport(
        RemoteCommandEnvelope envelope,
        OwnerAuthorizationContext authorization) =>
        Enqueue(
            envelope,
            authorization,
            "AUTHENTICATED_LOOPBACK_TRANSPORT / EXECUTION_BLOCKED_PHASE0");

    private RemoteCommandReceipt Enqueue(
        RemoteCommandEnvelope envelope,
        OwnerAuthorizationContext authorization,
        string reason)
    {
        Validate(envelope, authorization);

        var now = utcNow();
        var digest = StableDigest(envelope);
        var replay = replayLedger.Accept(
            envelope,
            authorization,
            digest,
            now);

        var trustState = replay.State == "DUPLICATE_SAME_COMMAND"
            ? "DUPLICATE_SAME_COMMAND"
            : "QUEUED_TRUSTED";

        if (trustState == "QUEUED_TRUSTED")
        {
            queue.Append(
                new RemoteCommandQueueRecord(
                    envelope.CommandId,
                    envelope.IdempotencyKey,
                    digest,
                    envelope.OwnerId,
                    envelope.DeviceId,
                    envelope.SessionId,
                    envelope.Target,
                    envelope.Effects.ToArray(),
                    trustState,
                    "BLOCKED_PHASE0",
                    now));
        }

        return new RemoteCommandReceipt(
            envelope.CommandId,
            envelope.IdempotencyKey,
            digest,
            trustState,
            "BLOCKED_PHASE0",
            reason,
            now);
    }

    public void ValidateApproval(RemoteApprovalRecord approval)
    {
        var document = reader.Read();
        RemoteOwnerPolicyValidator.ValidateDocument(document);
        var now = utcNow();

        Require(approval.ApprovalId, nameof(approval.ApprovalId));
        Require(approval.OwnerId, nameof(approval.OwnerId));
        Require(approval.DeviceId, nameof(approval.DeviceId));
        Require(approval.SessionId, nameof(approval.SessionId));
        Require(
            approval.AuthenticationSource,
            nameof(approval.AuthenticationSource));

        if (!approval.Authenticated || approval.Revoked)
        {
            throw new RemoteOwnerGatewayException(
                "Approval requires independently authenticated non-revoked Owner context.");
        }

        if (approval.ExpiresAt <= approval.IssuedAt ||
            approval.ExpiresAt <= now)
        {
            throw new RemoteOwnerGatewayException(
                "Approval record is expired or invalid.");
        }

        if (approval.AllowedTargets.Count == 0 ||
            approval.AllowedEffects.Count == 0)
        {
            throw new RemoteOwnerGatewayException(
                "Approval scope must be explicit.");
        }

        registry.AssertTrusted(
            new OwnerAuthorizationContext(
                document.Gateway.OwnerPrincipal,
                true,
                approval.AuthenticationSource,
                approval.OwnerId,
                approval.DeviceId,
                approval.SessionId,
                approval.AllowedTargets,
                approval.AllowedEffects,
                approval.IssuedAt,
                approval.ExpiresAt,
                false),
            now);
    }

    public RemoteApprovalRecord BuildAndValidateApproval(
        RemoteApprovalRequest request,
        OwnerAuthorizationContext authorization)
    {
        if (!authorization.Authenticated ||
            authorization.Revoked ||
            authorization.ExpiresAt <= utcNow())
        {
            throw new RemoteOwnerGatewayException(
                "Authenticated Owner session is required for transported approval.");
        }

        var targetScope = new HashSet<string>(
            authorization.AllowedTargets,
            StringComparer.Ordinal);
        if (request.AllowedTargets.Count == 0 ||
            !request.AllowedTargets.All(targetScope.Contains))
        {
            throw new RemoteOwnerGatewayException(
                "Approval target scope exceeds authenticated session.");
        }

        var effectScope = new HashSet<string>(
            authorization.AllowedEffects,
            StringComparer.Ordinal);
        if (request.AllowedEffects.Count == 0 ||
            !request.AllowedEffects.All(effectScope.Contains))
        {
            throw new RemoteOwnerGatewayException(
                "Approval effect scope exceeds authenticated session.");
        }

        var approval = new RemoteApprovalRecord(
            request.ApprovalId,
            authorization.OwnerId,
            authorization.DeviceId,
            authorization.SessionId,
            request.AllowedTargets.ToArray(),
            request.AllowedEffects.ToArray(),
            request.IssuedAt,
            request.ExpiresAt,
            true,
            authorization.AuthenticationSource,
            false);

        ValidateApproval(approval);
        return approval;
    }

    public static string StableDigest(RemoteCommandEnvelope envelope)
    {
        var fields = new[]
        {
            envelope.CommandId,
            envelope.Nonce,
            envelope.IdempotencyKey,
            envelope.IssuedAt.ToUniversalTime().ToString("O"),
            envelope.ExpiresAt.ToUniversalTime().ToString("O"),
            envelope.OwnerId,
            envelope.DeviceId,
            envelope.SessionId,
            envelope.Target,
            string.Join("\u001f", envelope.Effects),
            envelope.Instruction,
            envelope.ApprovalIntent,
            envelope.CorrelationId
        };

        var bytes = Encoding.UTF8.GetBytes(
            string.Join("\u001e", fields));
        return Convert.ToHexString(
            SHA256.HashData(bytes)).ToLowerInvariant();
    }

    private static void Require(string value, string name)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new RemoteOwnerGatewayException(
                $"Remote command field is required: {name}");
        }
    }
}

internal static class RemoteOwnerPolicyValidator
{
    private static readonly string[] RequiredCliCommands =
    [
        "status",
        "validate-envelope",
        "enqueue-synthetic",
        "inspect-queue",
        "validate-approval"
    ];

    public static void ValidateDocument(RemoteOwnerGatewayDocument document)
    {
        if (document.SchemaVersion != "1.0" ||
            document.SourceType != "repository_projection")
        {
            throw new RemoteOwnerGatewayException(
                "Unsupported Remote Owner gateway schema/source.");
        }

        if (document.Gateway.Mode != "LOCAL_TRUST_GATE_ONLY" ||
            document.Gateway.AuthenticationBackendConnected ||
            document.Gateway.LiveNetworkListenerEnabled ||
            document.Gateway.PublicInternetExposureAllowed ||
            document.Gateway.RouterPortForwardingAllowed ||
            document.Gateway.GithubQueueTransportEnabled ||
            document.Gateway.ChatTransportEnabled ||
            document.Gateway.LiveExecutionAuthorized)
        {
            throw new RemoteOwnerGatewayException(
                "Stage 5 remote ingress must remain local-only and non-live.");
        }

        if (document.Gateway.OwnerPrincipal != "OWNER" ||
            document.Gateway.TargetHost != "YASSIN" ||
            document.Gateway.Phase0RemoteTrustStatus != "IN_TEST")
        {
            throw new RemoteOwnerGatewayException(
                "Stage 5 Owner/target/Phase0 truth drifted.");
        }

        var trust = document.TrustContract;
        if (!trust.OwnerAuthorizationRequired ||
            !trust.AuthorizationContextMustBeOutOfBand ||
            !trust.DeviceIdRequired ||
            !trust.SessionIdRequired ||
            !trust.NonceRequired ||
            !trust.IdempotencyKeyRequired ||
            !trust.IssuedAtRequired ||
            !trust.ExpiryRequired ||
            !trust.TargetScopeRequired ||
            !trust.EffectScopeRequired ||
            !trust.ApprovalIntentRequired ||
            !trust.PersistentReplayLedgerRequired ||
            trust.ReplayPolicy != "FAIL_CLOSED" ||
            trust.MaxClockSkewSeconds < 0 ||
            trust.MaxClockSkewSeconds > 300 ||
            trust.MaxCommandTtlSeconds <= 0 ||
            trust.MaxCommandTtlSeconds > 3600)
        {
            throw new RemoteOwnerGatewayException(
                "Stage 5 remote command trust contract drifted.");
        }

        if (document.QueueContract.LiveDispatchAllowed ||
            !document.QueueContract.AppendOnly ||
            !document.QueueContract.UnknownIsNeverSuccess ||
            document.QueueContract.AcceptedState != "QUEUED_TRUSTED" ||
            document.QueueContract.DuplicateState != "DUPLICATE_SAME_COMMAND" ||
            document.QueueContract.ExecutionState != "BLOCKED_PHASE0")
        {
            throw new RemoteOwnerGatewayException(
                "Stage 5 queue authority contract drifted.");
        }

        if (document.ApprovalContract.DisplayRecordIsAuthority ||
            !document.ApprovalContract.OwnerApprovalMustBeOutOfBand ||
            !document.ApprovalContract.ApprovalExpiryRequired ||
            !document.ApprovalContract.ApprovalScopeMustCoverCommand)
        {
            throw new RemoteOwnerGatewayException(
                "Stage 5 approval contract drifted.");
        }

        if (!document.DeviceSessionContract.RegistrationRequired ||
            !document.DeviceSessionContract.UnregisteredDeviceFailsClosed ||
            !document.DeviceSessionContract.UnregisteredSessionFailsClosed ||
            !document.DeviceSessionContract.RevokedDeviceFailsClosed ||
            !document.DeviceSessionContract.RevokedSessionFailsClosed)
        {
            throw new RemoteOwnerGatewayException(
                "Stage 5 device/session contract drifted.");
        }

        if (!document.Service.AllowedCliCommands
                .SequenceEqual(RequiredCliCommands))
        {
            throw new RemoteOwnerGatewayException(
                "Stage 5 gateway CLI allowlist drifted.");
        }

        if (document.Service.ForbiddenCliCommands
            .Any(document.Service.AllowedCliCommands.Contains))
        {
            throw new RemoteOwnerGatewayException(
                "Forbidden gateway command leaked into allowlist.");
        }

        var truth = document.RuntimeTruth;
        if (truth.RegisteredDevices != 0 ||
            truth.RegisteredSessions != 0 ||
            truth.QueueDepth != 0 ||
            truth.PhoneConnected ||
            truth.TailscaleConnected ||
            truth.GithubTransportConnected ||
            truth.ChatTransportConnected)
        {
            throw new RemoteOwnerGatewayException(
                "Stage 5 repository projection may not fabricate live remote state.");
        }
    }
}
