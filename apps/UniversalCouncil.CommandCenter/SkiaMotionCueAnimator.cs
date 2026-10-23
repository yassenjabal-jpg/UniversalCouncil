using System.Diagnostics;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using SkiaSharp;

namespace UniversalCouncil.CommandCenter;

internal static class SkiaMotionCueAnimator
{
    private const double FrameMargin = 18;

    internal static void AnimateRouteReveal(
        Canvas host,
        Point origin,
        Point destination,
        Color accent,
        double durationMs,
        int zIndex)
    {
        Animate(
            host,
            origin,
            destination,
            accent,
            durationMs,
            zIndex,
            routeMode: RouteMode.Reveal,
            artifact: false);
    }

    internal static void AnimateArtifactHandoff(
        Canvas host,
        Point origin,
        Point destination,
        Color accent,
        double durationMs,
        int zIndex)
    {
        Animate(
            host,
            origin,
            destination,
            accent,
            durationMs,
            zIndex,
            routeMode: RouteMode.Static,
            artifact: true);
    }

    private static void Animate(
        Canvas host,
        Point origin,
        Point destination,
        Color accent,
        double durationMs,
        int zIndex,
        RouteMode routeMode,
        bool artifact)
    {
        if (durationMs <= 0 || !IsFinite(origin) || !IsFinite(destination))
        {
            return;
        }

        var left = Math.Floor(Math.Min(origin.X, destination.X) - FrameMargin);
        var top = Math.Floor(Math.Min(origin.Y, destination.Y) - FrameMargin);
        var right = Math.Ceiling(Math.Max(origin.X, destination.X) + FrameMargin);
        var bottom = Math.Ceiling(Math.Max(origin.Y, destination.Y) + FrameMargin);

        var pixelWidth = Math.Max(1, (int)(right - left));
        var pixelHeight = Math.Max(1, (int)(bottom - top));
        var localOrigin = new SKPoint((float)(origin.X - left), (float)(origin.Y - top));
        var localDestination = new SKPoint(
            (float)(destination.X - left),
            (float)(destination.Y - top));

        var image = new Image
        {
            Width = pixelWidth,
            Height = pixelHeight,
            Stretch = Stretch.None,
            IsHitTestVisible = false,
            SnapsToDevicePixels = true,
        };
        Canvas.SetLeft(image, left);
        Canvas.SetTop(image, top);
        Panel.SetZIndex(image, zIndex);
        host.Children.Add(image);

        var stopwatch = Stopwatch.StartNew();
        EventHandler? rendering = null;
        RoutedEventHandler? unloaded = null;
        var stopped = false;

        void Stop()
        {
            if (stopped)
            {
                return;
            }

            stopped = true;
            stopwatch.Stop();

            if (rendering is not null)
            {
                CompositionTarget.Rendering -= rendering;
            }

            if (unloaded is not null)
            {
                host.Unloaded -= unloaded;
            }

            host.Children.Remove(image);
            image.Source = null;
        }

        rendering = (_, _) =>
        {
            if (!host.Children.Contains(image))
            {
                Stop();
                return;
            }

            var linear = Math.Clamp(stopwatch.Elapsed.TotalMilliseconds / durationMs, 0, 1);
            var eased = artifact
                ? EaseInOutCubic(linear)
                : EaseOutCubic(linear);

            image.Source = RenderFrame(
                pixelWidth,
                pixelHeight,
                localOrigin,
                localDestination,
                accent,
                eased,
                routeMode,
                artifact);

            if (linear >= 1)
            {
                Stop();
            }
        };

        unloaded = (_, _) => Stop();
        host.Unloaded += unloaded;
        CompositionTarget.Rendering += rendering;

        image.Source = RenderFrame(
            pixelWidth,
            pixelHeight,
            localOrigin,
            localDestination,
            accent,
            progress: 0,
            routeMode,
            artifact);
    }

    private static BitmapSource RenderFrame(
        int pixelWidth,
        int pixelHeight,
        SKPoint origin,
        SKPoint destination,
        Color accent,
        double progress,
        RouteMode routeMode,
        bool artifact)
    {
        using var bitmap = new SKBitmap(
            new SKImageInfo(
                pixelWidth,
                pixelHeight,
                SKColorType.Bgra8888,
                SKAlphaType.Premul));
        using var canvas = new SKCanvas(bitmap);
        canvas.Clear(SKColors.Transparent);

        using var pathBuilder = new SKPathBuilder();
        pathBuilder.MoveTo(origin);
        pathBuilder.LineTo(destination);
        using var path = pathBuilder.Detach();

        using var dash = SKPathEffect.CreateDash([8f, 6f], 0);
        using var routePaint = new SKPaint
        {
            Color = ToSkColor(accent),
            StrokeWidth = 3,
            IsAntialias = true,
            Style = SKPaintStyle.Stroke,
        };

        if (routeMode == RouteMode.Reveal)
        {
            if (progress >= 1)
            {
                routePaint.PathEffect = dash;
                canvas.DrawPath(path, routePaint);
            }
            else if (progress > 0)
            {
                using var trim = SKPathEffect.CreateTrim(0, (float)progress);
                if (trim is not null)
                {
                    using var composed = SKPathEffect.CreateCompose(dash, trim);
                    routePaint.PathEffect = composed;
                    canvas.DrawPath(path, routePaint);
                }
            }
        }
        else
        {
            routePaint.PathEffect = dash;
            canvas.DrawPath(path, routePaint);
        }

        var x = Lerp(origin.X, destination.X, progress);
        var y = Lerp(origin.Y, destination.Y, progress);

        if (artifact)
        {
            using var artifactFill = new SKPaint
            {
                Color = new SKColor(accent.R, accent.G, accent.B, 255),
                IsAntialias = true,
                Style = SKPaintStyle.Fill,
            };
            using var artifactBorder = new SKPaint
            {
                Color = SKColors.White,
                IsAntialias = true,
                Style = SKPaintStyle.Stroke,
                StrokeWidth = 2,
            };

            var rect = new SKRect(x - 14, y - 11, x + 14, y + 11);
            canvas.DrawRoundRect(rect, 5, 5, artifactFill);
            canvas.DrawRoundRect(rect, 5, 5, artifactBorder);
        }
        else
        {
            using var endpoint = new SKPaint
            {
                Color = new SKColor(accent.R, accent.G, accent.B, 235),
                IsAntialias = true,
                Style = SKPaintStyle.Fill,
            };
            canvas.DrawCircle(x, y, 4, endpoint);
        }

        canvas.Flush();

        var source = BitmapSource.Create(
            bitmap.Width,
            bitmap.Height,
            96,
            96,
            PixelFormats.Bgra32,
            palette: null,
            bitmap.GetPixels(),
            bitmap.ByteCount,
            bitmap.RowBytes);
        source.Freeze();
        return source;
    }

    private static SKColor ToSkColor(Color color) =>
        new(color.R, color.G, color.B, color.A);

    private static bool IsFinite(Point point) =>
        double.IsFinite(point.X) && double.IsFinite(point.Y);

    private static float Lerp(float start, float end, double progress) =>
        (float)(start + (end - start) * progress);

    private static double EaseOutCubic(double value)
    {
        var inverse = 1 - value;
        return 1 - inverse * inverse * inverse;
    }

    private static double EaseInOutCubic(double value) =>
        value < 0.5
            ? 4 * value * value * value
            : 1 - Math.Pow(-2 * value + 2, 3) / 2;

    private enum RouteMode
    {
        Reveal,
        Static,
    }
}
