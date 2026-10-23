using System.Collections.Frozen;
using UniversalCouncil.MotionKit.Core;

namespace UniversalCouncil.MotionKit.Runtime;

public sealed class MotionProfileResolver
{
    private readonly string _profileId;
    private readonly FrozenDictionary<string, MotionVisualRule> _rules;

    public MotionProfileResolver(MotionProductProfile profile)
    {
        ArgumentNullException.ThrowIfNull(profile);

        if (!MotionRendererContractGuard.ValidIdentifier(profile.ProfileId))
        {
            throw new ArgumentException("Motion profile ID is invalid.", nameof(profile));
        }

        if (profile.Rules is null || profile.Rules.Count == 0)
        {
            throw new ArgumentException("Motion profile must contain at least one rule.", nameof(profile));
        }

        if (profile.Rules.Count > MotionRendererContractGuard.MaxProfileRules)
        {
            throw new ArgumentException("Motion profile contains too many rules.", nameof(profile));
        }

        var snapshot = new Dictionary<string, MotionVisualRule>(StringComparer.Ordinal);
        foreach (var pair in profile.Rules)
        {
            if (!MotionRendererContractGuard.ValidIdentifier(pair.Key))
            {
                throw new ArgumentException("Motion profile contains an invalid rule key.", nameof(profile));
            }

            var rule = pair.Value
                ?? throw new ArgumentException("Motion profile contains a null rule.", nameof(profile));

            if (!string.Equals(pair.Key, rule.SemanticEventId, StringComparison.Ordinal))
            {
                throw new ArgumentException("Motion profile key must match semantic event ID.", nameof(profile));
            }

            ValidateRule(rule);
            snapshot.Add(pair.Key, SnapshotRule(rule));
        }

        _profileId = profile.ProfileId;
        _rules = snapshot.ToFrozenDictionary(StringComparer.Ordinal);
    }

    public string ProfileId => _profileId;

    public MotionPreparationResult Resolve(MotionLease lease)
    {
        ArgumentNullException.ThrowIfNull(lease);

        if (lease.InstanceId == Guid.Empty
            || !MotionRendererContractGuard.ValidIdentifier(lease.TargetId)
            || !MotionRendererContractGuard.ValidIdentifier(lease.SemanticEventId)
            || !Enum.IsDefined(typeof(MotionAccessibilityMode), lease.AccessibilityMode))
        {
            return new MotionPreparationResult(
                MotionPreparationStatus.RejectedInvalid,
                Command: null,
                "Motion lease is invalid for rendering.");
        }

        if (!_rules.TryGetValue(lease.SemanticEventId, out var rule))
        {
            return new MotionPreparationResult(
                MotionPreparationStatus.RuleNotFound,
                Command: null,
                $"No visual rule exists for semantic event: {lease.SemanticEventId}");
        }

        var variant = lease.AccessibilityMode == MotionAccessibilityMode.Reduced
            ? rule.Reduced
            : rule.Full;

        var command = new MotionRenderCommand(
            new MotionRenderIdentity(
                lease.InstanceId,
                lease.TargetId,
                lease.SemanticEventId,
                lease.AccessibilityMode),
            variant.VisualToken,
            variant.Duration,
            variant.RequiredCapabilities);

        var invalid = MotionRendererContractGuard.ValidateCommand(command);
        if (invalid is not null)
        {
            return new MotionPreparationResult(
                MotionPreparationStatus.RejectedInvalid,
                Command: null,
                invalid);
        }

        return new MotionPreparationResult(
            MotionPreparationStatus.Ready,
            command,
            "Motion render command prepared.");
    }

    private static void ValidateRule(MotionVisualRule rule)
    {
        if (!MotionRendererContractGuard.ValidIdentifier(rule.SemanticEventId))
        {
            throw new ArgumentException("Semantic event ID is invalid.", nameof(rule));
        }

        ValidateVariant(rule.Full, "Full");
        ValidateVariant(rule.Reduced, "Reduced");
    }

    private static void ValidateVariant(MotionVisualVariant variant, string name)
    {
        if (variant is null)
        {
            throw new ArgumentException($"{name} visual variant is required.", nameof(variant));
        }

        if (!MotionRendererContractGuard.ValidIdentifier(variant.VisualToken))
        {
            throw new ArgumentException($"{name} visual token is invalid.", nameof(variant));
        }

        if (variant.Duration < TimeSpan.Zero
            || variant.Duration > MotionRendererContractGuard.MaxDuration)
        {
            throw new ArgumentException($"{name} duration is outside renderer-boundary limits.", nameof(variant));
        }

        if (!MotionRendererContractGuard.KnownCapabilitySet(variant.RequiredCapabilities))
        {
            throw new ArgumentException($"{name} variant contains unknown capability bits.", nameof(variant));
        }
    }

    private static MotionVisualRule SnapshotRule(MotionVisualRule rule) =>
        new(
            rule.SemanticEventId,
            new MotionVisualVariant(
                rule.Full.VisualToken,
                rule.Full.Duration,
                rule.Full.RequiredCapabilities),
            new MotionVisualVariant(
                rule.Reduced.VisualToken,
                rule.Reduced.Duration,
                rule.Reduced.RequiredCapabilities));
}
