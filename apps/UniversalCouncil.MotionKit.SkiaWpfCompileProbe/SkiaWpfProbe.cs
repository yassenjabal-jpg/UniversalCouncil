using SkiaSharp.Views.WPF;

namespace UniversalCouncil.MotionKit.SkiaWpfCompileProbe;

public static class SkiaWpfProbe
{
    public static Type ElementType => typeof(SKElement);

    public static SKElement CreateElement() => new();
}
