namespace UniversalCouncil.MotionKit.Runtime;

public static class MotionRendererContractGuard
{
    public const int MaxIdentifierLength = 256;
    public const int MaxProfileRules = 512;

    public static readonly TimeSpan MaxDuration = TimeSpan.FromSeconds(30);

    public const MotionRenderCapability KnownCapabilities =
        MotionRenderCapability.StaticSettle
        | MotionRenderCapability.Opacity
        | MotionRenderCapability.Translation
        | MotionRenderCapability.Scale
        | MotionRenderCapability.Rotation
        | MotionRenderCapability.PathGeometry
        | MotionRenderCapability.DynamicDrawing
        | MotionRenderCapability.StatefulVector
        | MotionRenderCapability.PreauthoredTimeline
        | MotionRenderCapability.HitTesting
        | MotionRenderCapability.ColorBinding;

    public static string? ValidateCommand(MotionRenderCommand command)
    {
        if (command.Identity.InstanceId == Guid.Empty)
        {
            return "Motion instance ID is empty.";
        }

        if (!ValidIdentifier(command.Identity.TargetId))
        {
            return "Motion target ID is invalid.";
        }

        if (!ValidIdentifier(command.Identity.SemanticEventId))
        {
            return "Semantic event ID is invalid.";
        }

        if (!Enum.IsDefined(
                typeof(UniversalCouncil.MotionKit.Core.MotionAccessibilityMode),
                command.Identity.AccessibilityMode))
        {
            return "Accessibility mode is unknown.";
        }

        if (!ValidIdentifier(command.VisualToken))
        {
            return "Visual token is invalid.";
        }

        if (command.Duration < TimeSpan.Zero || command.Duration > MaxDuration)
        {
            return "Motion duration is outside renderer-boundary limits.";
        }

        if (!KnownCapabilitySet(command.RequiredCapabilities))
        {
            return "Motion command contains unknown capability bits.";
        }

        return null;
    }

    public static string? ValidateAdapter(string adapterId, MotionRenderCapability capabilities)
    {
        if (!ValidIdentifier(adapterId))
        {
            return "Adapter ID is invalid.";
        }

        if (!KnownCapabilitySet(capabilities))
        {
            return "Adapter contains unknown capability bits.";
        }

        return null;
    }

    public static bool Supports(
        MotionRenderCapability available,
        MotionRenderCapability required) =>
        KnownCapabilitySet(available)
        && KnownCapabilitySet(required)
        && (available & required) == required;

    public static bool KnownCapabilitySet(MotionRenderCapability capabilities) =>
        (capabilities & ~KnownCapabilities) == MotionRenderCapability.None;

    public static bool ValidIdentifier(string? value)
    {
        if (string.IsNullOrWhiteSpace(value) || value.Length > MaxIdentifierLength)
        {
            return false;
        }

        return value.All(character => !char.IsControl(character));
    }
}
