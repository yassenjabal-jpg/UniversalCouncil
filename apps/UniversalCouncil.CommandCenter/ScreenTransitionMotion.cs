using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Animation;

namespace UniversalCouncil.CommandCenter;

internal sealed record ScreenTransitionProfile(
    double ExitDurationMs,
    double EntryDurationMs,
    double EntryX,
    double EntryY,
    double EntryScale,
    double ReducedExitDurationMs = 90,
    double ReducedEntryDurationMs = 130);

internal static class ScreenTransitionMotion
{
    private const double ReducedHandoffOpacity = 0.52;

    internal static Task RunExitAsync(
        FrameworkElement surface,
        ScreenTransitionProfile profile,
        bool fullMotion)
    {
        surface.RenderTransformOrigin = new Point(0.5, 0.5);

        if (!fullMotion)
        {
            surface.RenderTransform = Transform.Identity;
            return AnimateOpacityAsync(
                surface,
                1,
                ReducedHandoffOpacity,
                profile.ReducedExitDurationMs,
                EasingMode.EaseIn);
        }

        var exitX = -profile.EntryX * 0.35;
        var exitY = -profile.EntryY * 0.35;
        return AnimateCompositeAsync(
            surface,
            fromOpacity: 1,
            toOpacity: 0.16,
            fromX: 0,
            toX: exitX,
            fromY: 0,
            toY: exitY,
            fromScale: 1,
            toScale: 0.996,
            durationMs: profile.ExitDurationMs,
            easingMode: EasingMode.EaseIn);
    }

    internal static async Task RunEntryAsync(
        FrameworkElement surface,
        ScreenTransitionProfile profile,
        bool fullMotion)
    {
        if (!fullMotion)
        {
            surface.RenderTransform = Transform.Identity;
            await AnimateOpacityAsync(
                surface,
                ReducedHandoffOpacity,
                1,
                profile.ReducedEntryDurationMs,
                EasingMode.EaseOut);
            Settle(surface);
            return;
        }

        await AnimateCompositeAsync(
            surface,
            fromOpacity: 0.18,
            toOpacity: 1,
            fromX: profile.EntryX,
            toX: 0,
            fromY: profile.EntryY,
            toY: 0,
            fromScale: profile.EntryScale,
            toScale: 1,
            durationMs: profile.EntryDurationMs,
            easingMode: EasingMode.EaseOut);
        Settle(surface);
    }

    internal static void Settle(FrameworkElement surface)
    {
        surface.BeginAnimation(UIElement.OpacityProperty, null);
        surface.Opacity = 1;
        surface.RenderTransform = Transform.Identity;
        surface.RenderTransformOrigin = new Point(0.5, 0.5);
    }

    private static Task AnimateOpacityAsync(
        FrameworkElement surface,
        double from,
        double to,
        double durationMs,
        EasingMode easingMode)
    {
        surface.BeginAnimation(UIElement.OpacityProperty, null);
        surface.Opacity = from;

        var completion = new TaskCompletionSource<bool>();
        var animation = new DoubleAnimation(from, to, TimeSpan.FromMilliseconds(durationMs))
        {
            EasingFunction = new CubicEase { EasingMode = easingMode },
            FillBehavior = FillBehavior.HoldEnd,
        };
        animation.Completed += (_, _) => completion.TrySetResult(true);
        surface.BeginAnimation(UIElement.OpacityProperty, animation);
        return completion.Task;
    }

    private static Task AnimateCompositeAsync(
        FrameworkElement surface,
        double fromOpacity,
        double toOpacity,
        double fromX,
        double toX,
        double fromY,
        double toY,
        double fromScale,
        double toScale,
        double durationMs,
        EasingMode easingMode)
    {
        surface.BeginAnimation(UIElement.OpacityProperty, null);
        surface.Opacity = fromOpacity;

        var scale = new ScaleTransform(fromScale, fromScale);
        var translate = new TranslateTransform(fromX, fromY);
        var group = new TransformGroup();
        group.Children.Add(scale);
        group.Children.Add(translate);
        surface.RenderTransform = group;

        var duration = TimeSpan.FromMilliseconds(durationMs);
        var ease = new CubicEase { EasingMode = easingMode };
        var completion = new TaskCompletionSource<bool>();

        var opacity = new DoubleAnimation(fromOpacity, toOpacity, duration)
        {
            EasingFunction = ease,
            FillBehavior = FillBehavior.HoldEnd,
        };
        opacity.Completed += (_, _) => completion.TrySetResult(true);
        surface.BeginAnimation(UIElement.OpacityProperty, opacity);

        scale.BeginAnimation(
            ScaleTransform.ScaleXProperty,
            new DoubleAnimation(fromScale, toScale, duration)
            {
                EasingFunction = ease,
                FillBehavior = FillBehavior.HoldEnd,
            });
        scale.BeginAnimation(
            ScaleTransform.ScaleYProperty,
            new DoubleAnimation(fromScale, toScale, duration)
            {
                EasingFunction = ease,
                FillBehavior = FillBehavior.HoldEnd,
            });
        translate.BeginAnimation(
            TranslateTransform.XProperty,
            new DoubleAnimation(fromX, toX, duration)
            {
                EasingFunction = ease,
                FillBehavior = FillBehavior.HoldEnd,
            });
        translate.BeginAnimation(
            TranslateTransform.YProperty,
            new DoubleAnimation(fromY, toY, duration)
            {
                EasingFunction = ease,
                FillBehavior = FillBehavior.HoldEnd,
            });

        return completion.Task;
    }
}
