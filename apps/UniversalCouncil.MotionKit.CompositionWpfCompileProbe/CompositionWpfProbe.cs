using System.Windows;
using System.Windows.Interop;
using Microsoft.UI.Composition;

namespace UniversalCouncil.MotionKit.CompositionWpfCompileProbe;

public static class CompositionWpfProbe
{
    public static Type CompositorType => typeof(Compositor);

    public static Type SpriteVisualType => typeof(SpriteVisual);

    public static nint GetWindowHandle(Window window) =>
        new WindowInteropHelper(window).Handle;

    public static ScalarKeyFrameAnimation CreateOpacityAnimation(
        Compositor compositor,
        TimeSpan duration)
    {
        ArgumentNullException.ThrowIfNull(compositor);

        var animation = compositor.CreateScalarKeyFrameAnimation();
        animation.Duration = duration;
        animation.InsertKeyFrame(0f, 0f);
        animation.InsertKeyFrame(1f, 1f);
        return animation;
    }

    public static SpriteVisual CreateSpriteVisual(Compositor compositor)
    {
        ArgumentNullException.ThrowIfNull(compositor);
        return compositor.CreateSpriteVisual();
    }
}
